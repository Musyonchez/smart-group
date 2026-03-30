"""
Tests – Participation Tracker
Covers: record_session, get_student_report, get_group_report

The tracker module handles recording study sessions and calculating attendance.
It has three public functions:

  record_session(group, date, attendee_ids)
      → creates and returns a Session object for a group meeting
      → only records students who are actual members of the group
      → auto-assigns a unique session ID (SES-1, SES-2, ...)

  get_student_report(student, sessions)
      → returns an AttendanceReport for one student across all sessions
      → only counts sessions belonging to groups the student is in
      → fields: sessions_expected, sessions_attended, attendance_rate, missed_session_ids

  get_group_report(group, sessions)
      → returns a dict { student_id → AttendanceReport } for every group member
      → each member gets their own individual report
"""

import pytest
from src.models import Group, Student
from src.tracker import (
    get_group_report,
    get_student_report,
    record_session,
    reset_session_counter,
)


# ---------------------------------------------------------------------------
# Helpers – keep test bodies short and focused
# ---------------------------------------------------------------------------

def make_student(id):
    # Minimal student — tracker tests only care about the student ID
    return Student(id=id, name=f"Student {id}", courses=["COMP101"],
                   weak_topics=[], available_slots=["MON-09:00"])


def make_group(members):
    # Single reusable group — all tracker tests operate on GRP-1 unless overridden
    return Group(id="GRP-1", course="COMP101", members=members, time_slot="MON-09:00")


# Resets the session ID counter before every test so IDs are predictable (SES-1, SES-2 ...)
@pytest.fixture(autouse=True)
def reset():
    reset_session_counter()


# ---------------------------------------------------------------------------
# record_session – creates a Session for a group meeting
#
# Key behaviours:
#   - Assigns a sequential ID (SES-1, SES-2, ...)
#   - Only records attendees who are actual group members (non-members ignored)
#   - Allows zero attendees (everyone absent is a valid state)
#   - Stores the date exactly as provided
# ---------------------------------------------------------------------------

class TestRecordSession:

    def test_session_id_assigned(self):
        # First session ever recorded after a counter reset must get SES-1
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A"])
        assert session.id == "SES-1"

    def test_valid_attendees_stored(self):
        # Both A and B are group members → both should appear in attendee_ids
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A", "B"])
        assert set(session.attendee_ids) == {"A", "B"}

    def test_non_member_attendee_excluded(self):
        """Students not in the group cannot be recorded as attendees."""
        # X is not a member of the group → should be silently dropped
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A", "X"])  # X not in group
        assert "X" not in session.attendee_ids   # outsider excluded
        assert "A" in session.attendee_ids        # legitimate member kept

    def test_empty_attendees_allowed(self):
        """A session can be recorded with zero attendees (everyone absent)."""
        # Empty attendance list is valid — it means everyone was absent that day
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", [])
        assert session.attendee_ids == []

    def test_session_date_stored(self):
        # The date string must be stored exactly as passed — no reformatting
        group = make_group([make_student("A")])
        session = record_session(group, "2026-03-17", [])
        assert session.date == "2026-03-17"

    def test_multiple_sessions_unique_ids(self):
        # Each call to record_session must produce a different ID (SES-1, SES-2)
        group = make_group([make_student("A")])
        s1 = record_session(group, "2026-03-10", [])
        s2 = record_session(group, "2026-03-17", [])
        assert s1.id != s2.id   # IDs must never collide


# ---------------------------------------------------------------------------
# get_student_report – calculates one student's attendance across sessions
#
# attendance_rate = sessions_attended / sessions_expected
# sessions_expected = number of sessions belonging to groups the student is in
# missed_session_ids = IDs of sessions where the student was absent
# ---------------------------------------------------------------------------

class TestGetStudentReport:

    def test_perfect_attendance(self):
        # Student attended every session → rate should be 1.0, no missed sessions
        s = make_student("A")
        group = make_group([s, make_student("B")])
        sessions = [
            record_session(group, "2026-03-10", ["A", "B"]),
            record_session(group, "2026-03-17", ["A", "B"]),
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_expected == 2
        assert report.sessions_attended == 2
        assert report.attendance_rate == 1.0
        assert report.missed_session_ids == []   # nothing missed

    def test_zero_attendance(self):
        # Student never attended → rate should be 0.0, all sessions missed
        s = make_student("A")
        group = make_group([s, make_student("B")])
        sessions = [
            record_session(group, "2026-03-10", ["B"]),   # A absent
            record_session(group, "2026-03-17", ["B"]),   # A absent
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_attended == 0
        assert report.attendance_rate == 0.0
        assert len(report.missed_session_ids) == 2   # both sessions missed

    def test_partial_attendance(self):
        # Student attended 2 of 4 sessions → rate == 0.5
        s = make_student("A")
        group = make_group([s, make_student("B")])
        sessions = [
            record_session(group, "2026-03-10", ["A"]),   # attended
            record_session(group, "2026-03-17", []),       # absent
            record_session(group, "2026-03-24", ["A"]),   # attended
            record_session(group, "2026-03-31", []),       # absent
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_expected == 4
        assert report.sessions_attended == 2
        assert report.attendance_rate == 0.5
        assert len(report.missed_session_ids) == 2

    def test_no_sessions_recorded(self):
        """Student in a group with no sessions → report with zeros, no crash."""
        # Edge case: group exists but no sessions have been held yet
        s = make_student("A")
        report = get_student_report(s, [])
        assert report.sessions_expected == 0
        assert report.attendance_rate == 0.0   # no division-by-zero error

    def test_sessions_from_other_groups_ignored(self):
        """Sessions from groups the student doesn't belong to are not counted."""
        # A is in group_a only; session from group_b must not affect A's report
        s = make_student("A")
        other_student = make_student("B")
        group_a = make_group([s])
        group_b = Group(id="GRP-2", course="COMP101",
                        members=[other_student], time_slot="TUE-10:00")
        sessions = [
            record_session(group_a, "2026-03-10", ["A"]),   # A's group
            record_session(group_b, "2026-03-10", ["B"]),   # different group — must be ignored
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_expected == 1   # only the group_a session counts
        assert report.sessions_attended == 1

    def test_report_student_id_matches(self):
        # The report should reference the correct student — not a default or wrong ID
        s = make_student("A")
        report = get_student_report(s, [])
        assert report.student_id == "A"


# ---------------------------------------------------------------------------
# get_group_report – produces individual AttendanceReport for every group member
#
# Returns: { student_id: AttendanceReport, ... }
# Each member gets their own report; sessions from other groups are excluded.
# ---------------------------------------------------------------------------

class TestGetGroupReport:

    def test_report_contains_all_members(self):
        # Every member of the group must have an entry in the report dict
        members = [make_student("A"), make_student("B"), make_student("C")]
        group = make_group(members)
        sessions = [record_session(group, "2026-03-10", ["A", "C"])]
        report = get_group_report(group, sessions)
        assert set(report.keys()) == {"A", "B", "C"}   # all three present, including absentee B

    def test_individual_rates_correct(self):
        # A attended both sessions (rate=1.0); B only attended one (rate=0.5)
        a, b = make_student("A"), make_student("B")
        group = make_group([a, b])
        sessions = [
            record_session(group, "2026-03-10", ["A", "B"]),   # both present
            record_session(group, "2026-03-17", ["A"]),          # B absent
        ]
        report = get_group_report(group, sessions)
        assert report["A"].attendance_rate == 1.0   # A: 2/2
        assert report["B"].attendance_rate == 0.5   # B: 1/2

    def test_sessions_from_other_groups_excluded(self):
        # Sessions belonging to group2 must not inflate group1's expected count
        a = make_student("A")
        group1 = make_group([a])
        group2 = Group(id="GRP-2", course="COMP101",
                       members=[make_student("B")], time_slot="TUE-10:00")
        sessions = [
            record_session(group1, "2026-03-10", ["A"]),   # group1 session
            record_session(group2, "2026-03-10", ["B"]),   # group2 session — must not count
        ]
        report = get_group_report(group1, sessions)
        assert report["A"].sessions_expected == 1   # only group1's session counted

    def test_empty_sessions_all_zero(self):
        # No sessions recorded yet → every member should show 0% attendance, no crash
        members = [make_student("A"), make_student("B")]
        group = make_group(members)
        report = get_group_report(group, [])
        for r in report.values():
            assert r.attendance_rate == 0.0   # graceful zero, not an error
