"""
Tests – Participation Tracker
Covers: record_session, get_student_report, get_group_report
"""

import pytest
from src.models import Group, Student
from src.tracker import (
    get_group_report,
    get_student_report,
    record_session,
    reset_session_counter,
)


def make_student(id):
    return Student(id=id, name=f"Student {id}", courses=["COMP101"],
                   weak_topics=[], available_slots=["MON-09:00"])


def make_group(members):
    return Group(id="GRP-1", course="COMP101", members=members, time_slot="MON-09:00")


@pytest.fixture(autouse=True)
def reset():
    reset_session_counter()


# ---------------------------------------------------------------------------
# record_session
# ---------------------------------------------------------------------------

class TestRecordSession:

    def test_session_id_assigned(self):
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A"])
        assert session.id == "SES-1"

    def test_valid_attendees_stored(self):
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A", "B"])
        assert set(session.attendee_ids) == {"A", "B"}

    def test_non_member_attendee_excluded(self):
        """Students not in the group cannot be recorded as attendees."""
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", ["A", "X"])  # X not in group
        assert "X" not in session.attendee_ids
        assert "A" in session.attendee_ids

    def test_empty_attendees_allowed(self):
        """A session can be recorded with zero attendees (everyone absent)."""
        group = make_group([make_student("A"), make_student("B")])
        session = record_session(group, "2026-03-10", [])
        assert session.attendee_ids == []

    def test_session_date_stored(self):
        group = make_group([make_student("A")])
        session = record_session(group, "2026-03-17", [])
        assert session.date == "2026-03-17"

    def test_multiple_sessions_unique_ids(self):
        group = make_group([make_student("A")])
        s1 = record_session(group, "2026-03-10", [])
        s2 = record_session(group, "2026-03-17", [])
        assert s1.id != s2.id


# ---------------------------------------------------------------------------
# get_student_report – attendance rate
# ---------------------------------------------------------------------------

class TestGetStudentReport:

    def test_perfect_attendance(self):
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
        assert report.missed_session_ids == []

    def test_zero_attendance(self):
        s = make_student("A")
        group = make_group([s, make_student("B")])
        sessions = [
            record_session(group, "2026-03-10", ["B"]),
            record_session(group, "2026-03-17", ["B"]),
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_attended == 0
        assert report.attendance_rate == 0.0
        assert len(report.missed_session_ids) == 2

    def test_partial_attendance(self):
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
        s = make_student("A")
        report = get_student_report(s, [])
        assert report.sessions_expected == 0
        assert report.attendance_rate == 0.0

    def test_sessions_from_other_groups_ignored(self):
        """Sessions from groups the student doesn't belong to are not counted."""
        s = make_student("A")
        other_student = make_student("B")
        group_a = make_group([s])
        group_b = Group(id="GRP-2", course="COMP101",
                        members=[other_student], time_slot="TUE-10:00")
        sessions = [
            record_session(group_a, "2026-03-10", ["A"]),
            record_session(group_b, "2026-03-10", ["B"]),  # different group
        ]
        report = get_student_report(s, sessions)
        assert report.sessions_expected == 1
        assert report.sessions_attended == 1

    def test_report_student_id_matches(self):
        s = make_student("A")
        report = get_student_report(s, [])
        assert report.student_id == "A"


# ---------------------------------------------------------------------------
# get_group_report
# ---------------------------------------------------------------------------

class TestGetGroupReport:

    def test_report_contains_all_members(self):
        members = [make_student("A"), make_student("B"), make_student("C")]
        group = make_group(members)
        sessions = [record_session(group, "2026-03-10", ["A", "C"])]
        report = get_group_report(group, sessions)
        assert set(report.keys()) == {"A", "B", "C"}

    def test_individual_rates_correct(self):
        a, b = make_student("A"), make_student("B")
        group = make_group([a, b])
        sessions = [
            record_session(group, "2026-03-10", ["A", "B"]),
            record_session(group, "2026-03-17", ["A"]),      # B absent
        ]
        report = get_group_report(group, sessions)
        assert report["A"].attendance_rate == 1.0
        assert report["B"].attendance_rate == 0.5

    def test_sessions_from_other_groups_excluded(self):
        a = make_student("A")
        group1 = make_group([a])
        group2 = Group(id="GRP-2", course="COMP101",
                       members=[make_student("B")], time_slot="TUE-10:00")
        sessions = [
            record_session(group1, "2026-03-10", ["A"]),
            record_session(group2, "2026-03-10", ["B"]),
        ]
        report = get_group_report(group1, sessions)
        assert report["A"].sessions_expected == 1

    def test_empty_sessions_all_zero(self):
        members = [make_student("A"), make_student("B")]
        group = make_group(members)
        report = get_group_report(group, [])
        for r in report.values():
            assert r.attendance_rate == 0.0
