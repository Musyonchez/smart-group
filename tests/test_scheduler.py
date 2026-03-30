"""
Tests – Schedule Suggester
Covers: parse_slot, generate_schedule, format_schedule

The scheduler module turns a list of formed groups into a human-readable
weekly timetable. It has three public functions:

  parse_slot(slot)         → splits "MON-09:00" into ("MON", "09:00")
                             raises ValueError for malformed input

  generate_schedule(groups) → converts groups into ScheduleEntry objects,
                              sorted by day-of-week then by time

  format_schedule(groups)   → returns a formatted multi-line string of the
                              full weekly schedule, ready to print or display
"""

import pytest
from src.models import Group, Student
from src.scheduler import (
    ScheduleEntry,
    format_schedule,
    generate_schedule,
    parse_slot,
)


# ---------------------------------------------------------------------------
# Helpers – keep test bodies short and readable
# ---------------------------------------------------------------------------

def make_student(id):
    # Minimal student — only the ID matters for scheduling tests
    return Student(id=id, name=f"Student {id}", courses=["COMP101"],
                   weak_topics=[], available_slots=["MON-09:00"])


def make_group(gid, course, slot, member_ids):
    members = [make_student(mid) for mid in member_ids]
    return Group(id=gid, course=course, members=members, time_slot=slot)


# ---------------------------------------------------------------------------
# parse_slot – splits a "DAY-HH:MM" string into a (day, time) tuple
# Valid days: MON TUE WED THU FRI SAT SUN
# ---------------------------------------------------------------------------

class TestParseSlot:

    def test_valid_monday_slot(self):
        # Standard weekday morning slot — the most common format
        day, time = parse_slot("MON-09:00")
        assert day == "MON"
        assert time == "09:00"

    def test_valid_friday_slot(self):
        # Afternoon slot with non-zero minutes — checks the time part is preserved exactly
        day, time = parse_slot("FRI-14:30")
        assert day == "FRI"
        assert time == "14:30"

    def test_all_day_codes_accepted(self):
        # Iterates through every valid day code to ensure none are rejected
        for code in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
            day, _ = parse_slot(f"{code}-10:00")
            assert day == code

    def test_invalid_format_no_hyphen_raises(self):
        # Missing hyphen between day and time — should not silently succeed
        with pytest.raises(ValueError):
            parse_slot("MON09:00")

    def test_unknown_day_raises(self):
        # "XYZ" is not a recognised day code — parser must reject it
        with pytest.raises(ValueError):
            parse_slot("XYZ-09:00")

    def test_empty_string_raises(self):
        # Completely empty input — the most degenerate case
        with pytest.raises(ValueError):
            parse_slot("")


# ---------------------------------------------------------------------------
# generate_schedule – converts Group objects into sorted ScheduleEntry objects
#
# Each ScheduleEntry exposes:
#   .group_id    – the group's ID string
#   .course      – the course name
#   .day         – three-letter day code ("MON", "TUE", …)
#   .time        – time string ("09:00")
#   .member_ids  – list of student IDs in the group
#   .day_label   – full day name ("Monday", "Tuesday", …)
#   .display     – a summary string combining group, course, day, and time
# ---------------------------------------------------------------------------

class TestGenerateSchedule:

    def test_empty_groups_returns_empty(self):
        # No groups → no schedule entries; function should not crash
        assert generate_schedule([]) == []

    def test_single_group_entry_fields(self):
        # Checks every field of the resulting ScheduleEntry for correctness
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["A", "B"])
        entries = generate_schedule([group])
        assert len(entries) == 1
        e = entries[0]
        assert e.group_id == "GRP-1"
        assert e.course == "COMP101"
        assert e.day == "MON"
        assert e.time == "09:00"
        assert set(e.member_ids) == {"A", "B"}

    def test_sorted_by_day_order(self):
        # WED group is given first but MON should appear first in the sorted output
        g1 = make_group("GRP-1", "COMP101", "WED-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert entries[0].day == "MON"   # Monday sorts before Wednesday
        assert entries[1].day == "WED"

    def test_sorted_by_time_within_same_day(self):
        # Both groups are on Monday; earlier time must come first
        g1 = make_group("GRP-1", "COMP101", "MON-14:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert entries[0].time == "09:00"   # 09:00 before 14:00
        assert entries[1].time == "14:00"

    def test_multiple_groups_same_slot(self):
        # Two groups at the exact same day+time should both appear as separate entries
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert len(entries) == 2
        # Both entries should share the same day and time
        assert entries[0].day == entries[1].day == "MON"
        assert entries[0].time == entries[1].time == "09:00"

    def test_member_ids_match_group_members(self):
        # Verifies that all member IDs are correctly carried over to the schedule entry
        group = make_group("GRP-1", "COMP101", "TUE-10:00", ["X", "Y", "Z"])
        entries = generate_schedule([group])
        assert set(entries[0].member_ids) == {"X", "Y", "Z"}

    def test_day_label_property(self):
        # day_label should convert "FRI" → "Friday" for display purposes
        group = make_group("GRP-1", "COMP101", "FRI-08:00", ["A"])
        entry = generate_schedule([group])[0]
        assert entry.day_label == "Friday"

    def test_display_property_contains_key_info(self):
        # The display string should be human-readable and include all key identifiers
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["A", "B"])
        entry = generate_schedule([group])[0]
        assert "GRP-1" in entry.display      # group ID visible
        assert "COMP101" in entry.display    # course visible
        assert "Monday" in entry.display     # full day name, not code
        assert "09:00" in entry.display      # time visible


# ---------------------------------------------------------------------------
# format_schedule – renders the schedule as a formatted string
#
# Groups entries under day+time headers, sorted Mon→Sun then by time.
# Each group appears once per header block.
# ---------------------------------------------------------------------------

class TestFormatSchedule:

    def test_empty_groups_message(self):
        # With no groups there's nothing to show — returns a specific placeholder message
        result = format_schedule([])
        assert result == "No groups scheduled."

    def test_output_contains_header(self):
        # The top-level heading "Weekly Meeting Schedule" must be present
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        result = format_schedule([group])
        assert "Weekly Meeting Schedule" in result

    def test_output_contains_day_and_time(self):
        # The formatted output must show the full day name and time for each block
        group = make_group("GRP-1", "COMP101", "WED-14:00", ["A"])
        result = format_schedule([group])
        assert "Wednesday" in result   # full name, not "WED"
        assert "14:00" in result

    def test_output_contains_group_id(self):
        # Each group's ID must appear in the schedule so it can be identified
        group = make_group("GRP-42", "COMP101", "MON-09:00", ["A"])
        result = format_schedule([group])
        assert "GRP-42" in result

    def test_output_contains_member_ids(self):
        # Member IDs must be visible in the schedule output
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["Alice", "Bob"])
        result = format_schedule([group])
        assert "Alice" in result
        assert "Bob" in result

    def test_multiple_days_sorted_in_output(self):
        # Monday must appear before Friday in the output string
        g1 = make_group("GRP-1", "COMP101", "FRI-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        result = format_schedule([g1, g2])
        mon_pos = result.index("Monday")
        fri_pos = result.index("Friday")
        assert mon_pos < fri_pos   # Monday section comes before Friday section

    def test_same_slot_groups_under_one_header(self):
        # Two groups sharing the exact same slot should share one header, not two
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        result = format_schedule([g1, g2])
        # "Monday 09:00" header printed exactly once — no duplicate headers
        assert result.count("Monday 09:00") == 1

    def test_different_times_different_headers(self):
        # Two groups on the same day but different times → two separate headers
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-14:00", ["B"])
        result = format_schedule([g1, g2])
        assert "Monday 09:00" in result    # first time block header
        assert "Monday 14:00" in result    # second time block header
