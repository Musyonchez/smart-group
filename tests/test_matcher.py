"""
Test suite for the Smart Study Group Matching System.
Covers black-box (EP, BVA, Decision Table, State Transition)
and white-box (statement, branch, path coverage) test cases.
"""
import pytest
from src.models import Student, TimeSlot, StudyGroup
from src.matcher import (
    find_overlap,
    find_common_slot,
    has_conflict,
    find_compatible,
    form_groups,
    match_all_units,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MON_9_11 = TimeSlot("Mon", 9, 11)
MON_11_13 = TimeSlot("Mon", 11, 13)
TUE_14_16 = TimeSlot("Tue", 14, 16)
WED_10_12 = TimeSlot("Wed", 10, 12)


def make_student(sid, units, availability, strong=None, weak=None):
    return Student(
        id=sid,
        name=f"Student {sid}",
        units=units,
        strong=strong or [],
        weak=weak or [],
        availability=availability,
    )


# ---------------------------------------------------------------------------
# Unit Tests — find_overlap
# ---------------------------------------------------------------------------

class TestFindOverlap:
    def test_identical_slots_overlap(self):
        """WB-07 / BVA2-1: same slot returns it as overlap."""
        s1 = make_student("A", ["CS101"], [MON_9_11])
        s2 = make_student("B", ["CS101"], [MON_9_11])
        assert find_overlap(s1, s2) == [MON_9_11]

    def test_adjacent_slots_do_not_overlap(self):
        """BVA2-2: Mon 9-11 and Mon 11-13 are adjacent, not overlapping."""
        s1 = make_student("A", ["CS101"], [MON_9_11])
        s2 = make_student("B", ["CS101"], [MON_11_13])
        assert find_overlap(s1, s2) == []

    def test_different_days_no_overlap(self):
        s1 = make_student("A", ["CS101"], [MON_9_11])
        s2 = make_student("B", ["CS101"], [TUE_14_16])
        assert find_overlap(s1, s2) == []

    def test_one_student_no_slots(self):
        """BVA2-4: student with no availability has no overlap."""
        s1 = make_student("A", ["CS101"], [])
        s2 = make_student("B", ["CS101"], [MON_9_11])
        assert find_overlap(s1, s2) == []

    def test_multiple_slots_partial_overlap(self):
        """BVA2-3: shared slot found among multiple."""
        s1 = make_student("A", ["CS101"], [MON_9_11, TUE_14_16])
        s2 = make_student("B", ["CS101"], [TUE_14_16])
        assert TUE_14_16 in find_overlap(s1, s2)


# ---------------------------------------------------------------------------
# Unit Tests — find_common_slot
# ---------------------------------------------------------------------------

class TestFindCommonSlot:
    def test_all_share_same_slot(self):
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["CS101"], [MON_9_11]),
        ]
        assert find_common_slot(students) == MON_9_11

    def test_no_common_slot_returns_none(self):
        """WB-08: disjoint availability — no common slot."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [TUE_14_16]),
        ]
        assert find_common_slot(students) is None

    def test_empty_list_returns_none(self):
        assert find_common_slot([]) is None

    def test_single_student_returns_their_slot(self):
        s = make_student("A", ["CS101"], [MON_9_11])
        assert find_common_slot([s]) == MON_9_11


# ---------------------------------------------------------------------------
# Unit Tests — has_conflict
# ---------------------------------------------------------------------------

class TestHasConflict:
    def test_conflict_detected_same_slot(self):
        """WB-09: student already in a group at Mon 9-11."""
        student = make_student("A", ["CS101"], [MON_9_11])
        existing = [StudyGroup("g1", "CS101", ["A", "B"], MON_9_11)]
        assert has_conflict(student, MON_9_11, existing) is True

    def test_no_conflict_different_slot(self):
        """WB-10: student's group is at a different slot."""
        student = make_student("A", ["CS101"], [MON_9_11])
        existing = [StudyGroup("g1", "CS101", ["A", "B"], TUE_14_16)]
        assert has_conflict(student, MON_9_11, existing) is False

    def test_no_conflict_student_not_in_group(self):
        student = make_student("A", ["CS101"], [MON_9_11])
        existing = [StudyGroup("g1", "CS101", ["B", "C"], MON_9_11)]
        assert has_conflict(student, MON_9_11, existing) is False

    def test_no_conflict_no_existing_groups(self):
        student = make_student("A", ["CS101"], [MON_9_11])
        assert has_conflict(student, MON_9_11, []) is False


# ---------------------------------------------------------------------------
# Integration Tests — form_groups
# ---------------------------------------------------------------------------

class TestFormGroups:
    # --- Happy path ---

    def test_three_students_same_unit_shared_slot(self):
        """WB-01 / BB-03: standard happy path — 1 group of 3."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["CS101"], [MON_9_11]),
        ]
        groups = form_groups(students, "CS101")
        assert len(groups) == 1
        assert len(groups[0].members) == 3
        assert groups[0].meeting_slot == MON_9_11

    def test_two_students_form_group(self):
        """BVA1-2: minimum group size of 2."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
        ]
        groups = form_groups(students, "CS101")
        assert len(groups) == 1
        assert len(groups[0].members) == 2

    def test_four_students_form_single_group(self):
        """BVA1-4: maximum group size of 4."""
        students = [make_student(str(i), ["CS101"], [MON_9_11]) for i in range(4)]
        groups = form_groups(students, "CS101")
        total_members = sum(len(g.members) for g in groups)
        assert total_members == 4

    def test_five_students_split_into_two_groups(self):
        """BVA1-5 / BB-05: 5 students → groups of 3 + 2."""
        students = [make_student(str(i), ["CS101"], [MON_9_11]) for i in range(5)]
        groups = form_groups(students, "CS101")
        assert len(groups) == 2
        sizes = sorted(len(g.members) for g in groups)
        assert sizes == [2, 3]

    def test_six_students_split_into_two_groups(self):
        """EP1-V4: 6 students → 2 groups of 3."""
        students = [make_student(str(i), ["CS101"], [MON_9_11]) for i in range(6)]
        groups = form_groups(students, "CS101")
        assert len(groups) == 2
        assert all(len(g.members) == 3 for g in groups)

    # --- Edge cases ---

    def test_empty_student_list(self):
        """WB-06 / BB-01 / EP1-V1: no students → empty result."""
        assert form_groups([], "CS101") == []

    def test_single_student_unmatched(self):
        """BB-02 / EP1-V2: lone student stays unmatched."""
        students = [make_student("A", ["CS101"], [MON_9_11])]
        groups = form_groups(students, "CS101")
        assert groups == []
        assert students[0].status == "unmatched"

    def test_no_shared_slot_all_unmatched(self):
        """BB-08 / WB-04: students share unit but have no overlapping slots."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [TUE_14_16]),
            make_student("C", ["CS101"], [WED_10_12]),
        ]
        groups = form_groups(students, "CS101")
        assert groups == []
        assert all(s.status == "unmatched" for s in students)

    def test_different_units_not_grouped_together(self):
        """BB-07 / Decision Table R4: different units → separate groups."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["MATH201"], [MON_9_11]),
        ]
        cs_groups = form_groups(students, "CS101")
        math_groups = form_groups(students, "MATH201")
        # Each unit produces its own (unmatched) group — students not cross-matched
        assert all("B" not in g.members for g in cs_groups)
        assert all("A" not in g.members for g in math_groups)

    def test_student_not_enrolled_in_unit_excluded(self):
        """FR3: student not in unit must not appear in that unit's groups."""
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["MATH201"], [MON_9_11]),  # different unit
        ]
        groups = form_groups(students, "CS101")
        member_ids = [mid for g in groups for mid in g.members]
        assert "C" not in member_ids

    # --- Conflict detection ---

    def test_conflict_prevents_double_booking(self):
        """WB-05 / BB-10 / FR5: student cannot be in two groups at same time."""
        # s_A and s_B share Mon 9-11; s_A and s_C also share Mon 9-11.
        # After A+B form a group at Mon 9-11, A should not be added to another group at same slot.
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["CS101"], [MON_9_11]),
            make_student("D", ["CS101"], [MON_9_11]),
        ]
        groups = form_groups(students, "CS101")
        # Collect all (student_id, slot) pairs
        bookings = [(mid, g.meeting_slot) for g in groups for mid in g.members]
        # No student should appear twice at the same slot
        from collections import Counter
        counts = Counter(bookings)
        assert all(v == 1 for v in counts.values()), "Double-booking detected"

    # --- Strength / weakness balancing ---

    def test_strength_weakness_balance(self):
        """Groups prefer pairing weak students with strong ones."""
        students = [
            make_student("A", ["CS101"], [MON_9_11], weak=["recursion"]),
            make_student("B", ["CS101"], [MON_9_11], strong=["recursion"]),
            make_student("C", ["CS101"], [MON_9_11]),
        ]
        groups = form_groups(students, "CS101")
        assert len(groups) == 1
        assert "A" in groups[0].members
        assert "B" in groups[0].members


# ---------------------------------------------------------------------------
# System Tests — match_all_units
# ---------------------------------------------------------------------------

class TestMatchAllUnits:
    def test_student_in_two_units_gets_two_groups(self):
        """FR2: student enrolled in 2 units appears in groups for each."""
        students = [
            make_student("A", ["CS101", "MATH201"], [MON_9_11, TUE_14_16]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["MATH201"], [TUE_14_16]),
        ]
        result = match_all_units(students)
        cs_members = [mid for g in result.get("CS101", []) for mid in g.members]
        math_members = [mid for g in result.get("MATH201", []) for mid in g.members]
        assert "A" in cs_members
        assert "A" in math_members

    def test_no_time_conflict_across_units(self):
        """FR5: student in two units must not be double-booked."""
        # A is in CS101 (Mon 9-11) and MATH201 (Mon 9-11) — same slot
        # The second group should not be formed if it would conflict
        students = [
            make_student("A", ["CS101", "MATH201"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
            make_student("C", ["MATH201"], [MON_9_11]),
        ]
        result = match_all_units(students)
        # Collect all bookings for student A
        bookings = []
        for unit_groups in result.values():
            for g in unit_groups:
                if "A" in g.members:
                    bookings.append(g.meeting_slot)
        # If A ended up in two groups, their slots must not overlap
        for i, slot_a in enumerate(bookings):
            for slot_b in bookings[i + 1:]:
                assert not slot_a.overlaps(slot_b), "A is double-booked across units"

    def test_returns_dict_keyed_by_unit(self):
        students = [
            make_student("A", ["CS101"], [MON_9_11]),
            make_student("B", ["CS101"], [MON_9_11]),
        ]
        result = match_all_units(students)
        assert "CS101" in result
        assert isinstance(result["CS101"], list)


# ---------------------------------------------------------------------------
# Performance Test
# ---------------------------------------------------------------------------

class TestPerformance:
    def test_500_students_under_3_seconds(self):
        """NFR1: matching 500 students must complete within 3 seconds."""
        import time
        students = [
            make_student(str(i), ["CS101"], [MON_9_11])
            for i in range(500)
        ]
        start = time.time()
        form_groups(students, "CS101")
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Matching took {elapsed:.2f}s — too slow"
