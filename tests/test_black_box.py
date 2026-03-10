"""
Black Box Tests – Smart Study Group Matching System
Techniques: Equivalence Partitioning (EP) and Boundary Value Analysis (BVA)
Reference: docs/3-black-box-testing.md
"""

import pytest
from src.matcher import match_students, reset_group_counter
from src.models import Student


def make_student(id, courses, slots, assigned_groups=None):
    return Student(
        id=id,
        name=f"Student {id}",
        courses=courses,
        weak_topics=[],
        available_slots=slots,
        assigned_groups=assigned_groups or [],
    )


@pytest.fixture(autouse=True)
def reset():
    reset_group_counter()


# ---------------------------------------------------------------------------
# Feature 1 – Course Matching (EP)
# ---------------------------------------------------------------------------

class TestCourseMatchingEP:

    def test_EP_C1_same_course_forms_group(self):
        """EP-C1: Two students sharing a course → group formed."""
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 0

    def test_EP_C2_different_courses_no_match(self):
        """EP-C2: Students from different courses → no group formed."""
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["MATH201"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0

    def test_EP_C3_no_course_selected(self):
        """EP-C3: Student enrolled in zero courses → treated as ineligible."""
        students = [
            make_student("A", [], ["MON-09:00"]),
            make_student("B", [], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 0


# ---------------------------------------------------------------------------
# Feature 2 – Group Size (EP + BVA)
# ---------------------------------------------------------------------------

class TestGroupSizeEP:

    def test_EP_invalid_too_few(self):
        """EP: Only 1 eligible student → no group, waitlisted."""
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
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(7)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        total_assigned = sum(len(g.members) for g in result.groups)
        assert total_assigned + len(result.waitlisted) == 7


class TestGroupSizeBVA:

    def test_BVA_G1_zero_students(self):
        """BVA-G1: 0 eligible students → no group."""
        result = match_students([], "COMP101", "MON-09:00")
        assert len(result.groups) == 0

    def test_BVA_G2_one_student_below_minimum(self):
        """BVA-G2: 1 student → no group, waitlisted (just below minimum boundary)."""
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 1

    def test_BVA_G3_two_students_at_minimum(self):
        """BVA-G3: 2 students → group formed (at minimum boundary)."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.groups[0].members) == 2

    def test_BVA_G4_three_students_nominal(self):
        """BVA-G4: 3 students → group formed (nominal valid value)."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        assert len(result.groups) == 1

    def test_BVA_G5_five_students_at_maximum(self):
        """BVA-G5: 5 students → group of 5 formed (at maximum boundary)."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=5)
        assert len(result.groups) == 1
        assert len(result.groups[0].members) == 5

    def test_BVA_G6_six_students_above_maximum(self):
        """BVA-G6: 6 students with group_size=5 → 1 group of 5, 1 waitlisted."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(6)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=5)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 1


# ---------------------------------------------------------------------------
# Feature 3 – Time Conflict Detection (EP + BVA)
# ---------------------------------------------------------------------------

class TestTimeConflictEP:

    def test_EP_T1_no_conflict_assignment_succeeds(self):
        """EP-T1: Student free at proposed slot → assigned successfully."""
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

        # Pre-assign A to a group at MON-09:00
        from src.models import Group
        existing_group = Group(id="GRP-0", course="COMP101", members=[student_a], time_slot="MON-09:00")
        student_a.assigned_groups.append(existing_group)

        result = match_students([student_a, student_b, student_c], "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids
        assert len(result.groups) == 1  # B and C form a group

    def test_EP_T3_no_slots_selected_excluded(self):
        """EP: Student with no available slots cannot be matched."""
        students = [
            make_student("A", ["COMP101"], []),  # no slots
            make_student("B", ["COMP101"], ["MON-09:00"]),
            make_student("C", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids


class TestTimeConflictBVA:

    def test_BVA_T1_zero_slots_excluded(self):
        """BVA-T1: 0 slots selected → student ineligible (below minimum availability)."""
        students = [make_student("A", ["COMP101"], []),
                    make_student("B", ["COMP101"], [])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0

    def test_BVA_T3_exact_same_slot_conflict(self):
        """BVA-T3: Student already assigned at exact proposed slot → conflict detected."""
        from src.models import Group
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)

        from src.matcher import has_time_conflict
        assert has_time_conflict(student, "MON-09:00") is True

    def test_BVA_T4_adjacent_slot_no_conflict(self):
        """BVA-T4: Student assigned at MON-09:00; proposed MON-10:00 → no conflict."""
        from src.models import Group
        from src.matcher import has_time_conflict
        student = make_student("A", ["COMP101"], ["MON-09:00", "MON-10:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)

        assert has_time_conflict(student, "MON-10:00") is False


# ---------------------------------------------------------------------------
# Feature 4 – Odd Student Handling (BVA)
# ---------------------------------------------------------------------------

class TestOddStudentHandling:

    def test_BVA_O1_one_student_waitlisted(self):
        """BVA-O1: 1 eligible student → waitlisted, no group."""
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 0
        assert len(result.waitlisted) == 1

    def test_BVA_O2_two_students_form_group(self):
        """BVA-O2: 2 eligible students → 1 group of 2 (minimum)."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 0

    def test_BVA_O3_three_students_one_waitlisted(self):
        """BVA-O3: 3 students with group_size=2 → 1 group of 2, 1 waitlisted."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1
        assert len(result.waitlisted) == 1

    def test_BVA_O4_five_students_split(self):
        """BVA-O4: 5 students with group_size=2 → 2 groups of 2, 1 waitlisted."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 2
        assert len(result.waitlisted) == 1
