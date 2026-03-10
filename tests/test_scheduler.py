"""
Tests – Schedule Suggester
Covers: parse_slot, generate_schedule, format_schedule
"""

import pytest
from src.models import Group, Student
from src.scheduler import (
    ScheduleEntry,
    format_schedule,
    generate_schedule,
    parse_slot,
)


def make_student(id):
    return Student(id=id, name=f"Student {id}", courses=["COMP101"],
                   weak_topics=[], available_slots=["MON-09:00"])


def make_group(gid, course, slot, member_ids):
    members = [make_student(mid) for mid in member_ids]
    return Group(id=gid, course=course, members=members, time_slot=slot)


# ---------------------------------------------------------------------------
# parse_slot
# ---------------------------------------------------------------------------

class TestParseSlot:

    def test_valid_monday_slot(self):
        day, time = parse_slot("MON-09:00")
        assert day == "MON"
        assert time == "09:00"

    def test_valid_friday_slot(self):
        day, time = parse_slot("FRI-14:30")
        assert day == "FRI"
        assert time == "14:30"

    def test_all_day_codes_accepted(self):
        for code in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
            day, _ = parse_slot(f"{code}-10:00")
            assert day == code

    def test_invalid_format_no_hyphen_raises(self):
        with pytest.raises(ValueError):
            parse_slot("MON09:00")

    def test_unknown_day_raises(self):
        with pytest.raises(ValueError):
            parse_slot("XYZ-09:00")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_slot("")


# ---------------------------------------------------------------------------
# generate_schedule
# ---------------------------------------------------------------------------

class TestGenerateSchedule:

    def test_empty_groups_returns_empty(self):
        assert generate_schedule([]) == []

    def test_single_group_entry_fields(self):
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
        g1 = make_group("GRP-1", "COMP101", "WED-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert entries[0].day == "MON"
        assert entries[1].day == "WED"

    def test_sorted_by_time_within_same_day(self):
        g1 = make_group("GRP-1", "COMP101", "MON-14:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert entries[0].time == "09:00"
        assert entries[1].time == "14:00"

    def test_multiple_groups_same_slot(self):
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        entries = generate_schedule([g1, g2])
        assert len(entries) == 2
        # both entries have same day/time
        assert entries[0].day == entries[1].day == "MON"
        assert entries[0].time == entries[1].time == "09:00"

    def test_member_ids_match_group_members(self):
        group = make_group("GRP-1", "COMP101", "TUE-10:00", ["X", "Y", "Z"])
        entries = generate_schedule([group])
        assert set(entries[0].member_ids) == {"X", "Y", "Z"}

    def test_day_label_property(self):
        group = make_group("GRP-1", "COMP101", "FRI-08:00", ["A"])
        entry = generate_schedule([group])[0]
        assert entry.day_label == "Friday"

    def test_display_property_contains_key_info(self):
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["A", "B"])
        entry = generate_schedule([group])[0]
        assert "GRP-1" in entry.display
        assert "COMP101" in entry.display
        assert "Monday" in entry.display
        assert "09:00" in entry.display


# ---------------------------------------------------------------------------
# format_schedule
# ---------------------------------------------------------------------------

class TestFormatSchedule:

    def test_empty_groups_message(self):
        result = format_schedule([])
        assert result == "No groups scheduled."

    def test_output_contains_header(self):
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        result = format_schedule([group])
        assert "Weekly Meeting Schedule" in result

    def test_output_contains_day_and_time(self):
        group = make_group("GRP-1", "COMP101", "WED-14:00", ["A"])
        result = format_schedule([group])
        assert "Wednesday" in result
        assert "14:00" in result

    def test_output_contains_group_id(self):
        group = make_group("GRP-42", "COMP101", "MON-09:00", ["A"])
        result = format_schedule([group])
        assert "GRP-42" in result

    def test_output_contains_member_ids(self):
        group = make_group("GRP-1", "COMP101", "MON-09:00", ["Alice", "Bob"])
        result = format_schedule([group])
        assert "Alice" in result
        assert "Bob" in result

    def test_multiple_days_sorted_in_output(self):
        g1 = make_group("GRP-1", "COMP101", "FRI-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        result = format_schedule([g1, g2])
        mon_pos = result.index("Monday")
        fri_pos = result.index("Friday")
        assert mon_pos < fri_pos

    def test_same_slot_groups_under_one_header(self):
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-09:00", ["B"])
        result = format_schedule([g1, g2])
        # Header "Monday 09:00" appears exactly once
        assert result.count("Monday 09:00") == 1

    def test_different_times_different_headers(self):
        g1 = make_group("GRP-1", "COMP101", "MON-09:00", ["A"])
        g2 = make_group("GRP-2", "COMP202", "MON-14:00", ["B"])
        result = format_schedule([g1, g2])
        assert "Monday 09:00" in result
        assert "Monday 14:00" in result
