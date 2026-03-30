"""
Black Box Tests – Smart Study Group Matching System
Techniques: Equivalence Partitioning (EP) and Boundary Value Analysis (BVA)
Reference: docs/3-black-box-testing.md

Black box testing treats the system as a "black box" — we only care about
inputs and outputs, not the internal implementation. We use two techniques:

  - Equivalence Partitioning (EP): Divide inputs into groups (partitions)
    that should behave the same way, then test one representative from each.

  - Boundary Value Analysis (BVA): Test values at the edges of valid/invalid
    ranges, since bugs tend to cluster at boundaries (e.g. exactly 2 students,
    exactly 5 students, 0 students).
"""

import pytest
from src.matcher import match_students, reset_group_counter
from src.models import Student


# ---------------------------------------------------------------------------
# Helper – builds a minimal Student object for testing
# We keep this separate so each test stays short and readable
# ---------------------------------------------------------------------------

def make_student(id, courses, slots, assigned_groups=None):
    return Student(
        id=id,
        name=f"Student {id}",
        courses=courses,
        weak_topics=[],
        available_slots=slots,
        assigned_groups=assigned_groups or [],
    )


# autouse=True means this fixture runs automatically before every test,
# ensuring the group ID counter (GRP-1, GRP-2 ...) resets to a clean state
@pytest.fixture(autouse=True)
def reset():
    reset_group_counter()


# ---------------------------------------------------------------------------
# Feature 1 – Course Matching (EP)
# Partition A: students share the course  → group should form
# Partition B: students are on different courses → no group
# Partition C: students have no courses at all → ineligible
# ---------------------------------------------------------------------------

class TestCourseMatchingEP:

    def test_EP_C1_same_course_forms_group(self):
        """EP-C1: Two students sharing a course → group formed."""
        # Both enrolled in COMP101 and free at MON-09:00 → valid group
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1       # exactly one group formed
        assert len(result.waitlisted) == 0   # nobody left over

    def test_EP_C2_different_courses_no_match(self):
        """EP-C2: Students from different courses → no group formed."""
        # A is on COMP101, B is on MATH201 — they can't share a COMP101 group
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["MATH201"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0   # B is ineligible, not enough for a group

    def test_EP_C3_no_course_selected(self):
        """EP-C3: Student enrolled in zero courses → treated as ineligible."""
        # Empty course list means neither student qualifies for COMP101 matching
        students = [
            make_student("A", [], ["MON-09:00"]),
            make_student("B", [], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0       # no eligible students → no groups
        assert len(result.waitlisted) == 0   # ineligible students aren't waitlisted


# ---------------------------------------------------------------------------
# Feature 2 – Group Size (EP + BVA)
#
# EP partitions:
#   - Too few eligible students (below group_size) → waitlist
#   - Valid number of students                     → group(s) formed
#   - More students than one group can hold        → multiple groups + possible waitlist
#
# BVA boundaries (default group_size = 2..5):
#   0 students, 1 (just below min), 2 (at min), 3 (nominal),
#   5 (at max), 6 (just above max)
# ---------------------------------------------------------------------------

class TestGroupSizeEP:

    def test_EP_invalid_too_few(self):
        """EP: Only 1 eligible student → no group, waitlisted."""
        # 1 student can't fill a group of 2, so they go to the waitlist
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 1

    def test_EP_valid_group_formed(self):
        """EP: 3 eligible students → group formed."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        assert len(result.groups) == 1

    def test_EP_too_many_students_split(self):
        """EP: 7 eligible students with group_size=3 → multiple groups + possible waitlist."""
        # 7 students split into groups of 3: [3, 3] with 1 waitlisted
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(7)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        # Every student must end up either in a group or on the waitlist
        total_assigned = sum(len(g.members) for g in result.groups)
        assert total_assigned + len(result.waitlisted) == 7


class TestGroupSizeBVA:

    def test_BVA_G1_zero_students(self):
        """BVA-G1: 0 eligible students → no group."""
        # Boundary: absolute minimum input — empty list
        result = match_students([], "COMP101", "MON-09:00")
        assert len(result.groups) == 0

    def test_BVA_G2_one_student_below_minimum(self):
        """BVA-G2: 1 student → no group, waitlisted (just below minimum boundary)."""
        # 1 is one below the minimum of 2 — the edge case most likely to fail
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 1

    def test_BVA_G3_two_students_at_minimum(self):
        """BVA-G3: 2 students → group formed (at minimum boundary)."""
        # Exactly 2 is the smallest valid group — must succeed
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.groups[0].members) == 2

    def test_BVA_G4_three_students_nominal(self):
        """BVA-G4: 3 students → group formed (nominal valid value)."""
        # Mid-range value — sanity check that the happy path works
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        assert len(result.groups) == 1

    def test_BVA_G5_five_students_at_maximum(self):
        """BVA-G5: 5 students → group of 5 formed (at maximum boundary)."""
        # 5 is the largest allowed group size — all 5 must fit in one group
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=5)
        assert len(result.groups) == 1
        assert len(result.groups[0].members) == 5

    def test_BVA_G6_six_students_above_maximum(self):
        """BVA-G6: 6 students with group_size=5 → 1 group of 5, 1 waitlisted."""
        # One beyond the max — the leftover student must be waitlisted, not lost
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(6)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=5)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 1


# ---------------------------------------------------------------------------
# Feature 3 – Time Conflict Detection (EP + BVA)
#
# A student can only join a group if they:
#   (a) are available at the proposed slot, AND
#   (b) are not already assigned to a group at that same slot
#
# EP partitions:
#   - Student is free at the slot     → eligible
#   - Student has a conflict          → excluded from group
#   - Student has no slots at all     → excluded
#
# BVA boundaries:
#   - 0 available slots (below minimum)
#   - Exact same slot as existing group (conflict)
#   - Adjacent slot to existing group (no conflict)
# ---------------------------------------------------------------------------

class TestTimeConflictEP:

    def test_EP_T1_no_conflict_assignment_succeeds(self):
        """EP-T1: Student free at proposed slot → assigned successfully."""
        # A has two slots; B only has MON-09:00. Both are free at MON-09:00.
        students = [
            make_student("A", ["COMP101"], ["MON-09:00", "TUE-14:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1

    def test_EP_T2_conflict_student_excluded(self):
        """EP-T2: Student already in a group at MON-09:00 → excluded from new group."""
        student_a = make_student("A", ["COMP101"], ["MON-09:00"])
        student_b = make_student("B", ["COMP101"], ["MON-09:00"])
        student_c = make_student("C", ["COMP101"], ["MON-09:00"])

        # Manually assign A to an existing group at the same slot to create a conflict
        from src.models import Group
        existing_group = Group(id="GRP-0", course="COMP101", members=[student_a], time_slot="MON-09:00")
        student_a.assigned_groups.append(existing_group)

        result = match_students([student_a, student_b, student_c], "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids   # A is blocked due to conflict
        assert len(result.groups) == 1  # B and C form a group

    def test_EP_T3_no_slots_selected_excluded(self):
        """EP: Student with no available slots cannot be matched."""
        # A has an empty availability list — they can't attend any slot
        students = [
            make_student("A", ["COMP101"], []),  # no slots
            make_student("B", ["COMP101"], ["MON-09:00"]),
            make_student("C", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids   # A should be excluded silently


class TestTimeConflictBVA:

    def test_BVA_T1_zero_slots_excluded(self):
        """BVA-T1: 0 slots selected → student ineligible (below minimum availability)."""
        # Both students have zero slots — neither can be placed, so no group forms
        students = [make_student("A", ["COMP101"], []),
                    make_student("B", ["COMP101"], [])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0

    def test_BVA_T3_exact_same_slot_conflict(self):
        """BVA-T3: Student already assigned at exact proposed slot → conflict detected."""
        # The proposed slot is identical to the student's existing group slot
        from src.models import Group
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)

        from src.matcher import has_time_conflict
        assert has_time_conflict(student, "MON-09:00") is True   # exact match → conflict

    def test_BVA_T4_adjacent_slot_no_conflict(self):
        """BVA-T4: Student assigned at MON-09:00; proposed MON-10:00 → no conflict."""
        # One hour later is a different slot — should NOT count as a conflict
        from src.models import Group
        from src.matcher import has_time_conflict
        student = make_student("A", ["COMP101"], ["MON-09:00", "MON-10:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)

        assert has_time_conflict(student, "MON-10:00") is False  # different time → no conflict


# ---------------------------------------------------------------------------
# Feature 4 – Odd Student Handling (BVA)
#
# When the number of eligible students doesn't divide evenly by group_size,
# the leftover students go to the waitlist. These boundary cases check that
# the system handles the "odd one out" correctly at each edge.
# ---------------------------------------------------------------------------

class TestOddStudentHandling:

    def test_BVA_O1_one_student_waitlisted(self):
        """BVA-O1: 1 eligible student → waitlisted, no group."""
        # Can't form a group of 1 — student must land on the waitlist
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 1

    def test_BVA_O2_two_students_form_group(self):
        """BVA-O2: 2 eligible students → 1 group of 2 (minimum)."""
        # Exactly fills one group — no remainder
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 0

    def test_BVA_O3_three_students_one_waitlisted(self):
        """BVA-O3: 3 students with group_size=2 → 1 group of 2, 1 waitlisted."""
        # 3 ÷ 2 = 1 group with 1 left over on the waitlist
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 1

    def test_BVA_O4_five_students_split(self):
        """BVA-O4: 5 students with group_size=2 → 2 groups of 2, 1 waitlisted."""
        # 5 ÷ 2 = 2 full groups with 1 remainder — tests that splitting works correctly
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 2
        assert len(result.waitlisted) == 1
