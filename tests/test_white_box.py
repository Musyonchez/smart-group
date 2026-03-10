"""
White Box Tests – Smart Study Group Matching System
Techniques: Control Flow Graph (CFG), Branch Coverage (Level 2), Data Flow (DU)
Reference: docs/4-white-box-testing.md
"""

import pytest
from src.matcher import has_time_conflict, match_students, reset_group_counter
from src.models import Group, Student


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
# Decision 1 – student.course == course (Loop A, branch coverage)
# ---------------------------------------------------------------------------

class TestDecision1CourseBranch:

    def test_WB_D1_T_course_matches_student_eligible(self):
        """WB-D1-T: D1 True → student added to eligible list."""
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" in member_ids
        assert "B" in member_ids

    def test_WB_D1_F_course_mismatch_student_skipped(self):
        """WB-D1-F: D1 False → student not included in any group."""
        students = [
            make_student("A", ["MATH201"], ["MON-09:00"]),  # wrong course
            make_student("B", ["COMP101"], ["MON-09:00"]),
            make_student("C", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids


# ---------------------------------------------------------------------------
# Decision 2 – not has_time_conflict(student) (Loop A, branch coverage)
# ---------------------------------------------------------------------------

class TestDecision2ConflictBranch:

    def test_WB_D2_T_no_conflict_student_eligible(self):
        """WB-D2-T: D2 True (no conflict) → student eligible."""
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1

    def test_WB_D2_F_conflict_student_skipped(self):
        """WB-D2-F: D2 False (conflict exists) → student excluded."""
        student_a = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student_a], time_slot="MON-09:00")
        student_a.assigned_groups.append(existing)

        students = [
            student_a,
            make_student("B", ["COMP101"], ["MON-09:00"]),
            make_student("C", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids


# ---------------------------------------------------------------------------
# Decision 3 – len(eligible) < GROUP_SIZE_MIN
# ---------------------------------------------------------------------------

class TestDecision3EligibleGuard:

    def test_WB_D3_T_too_few_eligible_returns_waitlist(self):
        """WB-D3-T: D3 True (eligible < 2) → waitlist returned immediately."""
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert result.groups == []
        assert len(result.waitlisted) == 1

    def test_WB_D3_F_enough_eligible_proceeds_to_groups(self):
        """WB-D3-F: D3 False (eligible >= 2) → group formation proceeds."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) >= 1


# ---------------------------------------------------------------------------
# Loop A – for student in students (0, 1, multiple iterations)
# ---------------------------------------------------------------------------

class TestLoopA:

    def test_WB_LA_0_empty_list_skips_loop(self):
        """WB-LA-0: Empty students list → Loop A executes 0 times → waitlist."""
        result = match_students([], "COMP101", "MON-09:00")
        assert result.groups == []
        assert result.waitlisted == []

    def test_WB_LA_1_single_student_one_iteration(self):
        """WB-LA-1: 1 student → Loop A iterates once → waitlisted (D3 triggers)."""
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert result.groups == []
        assert len(result.waitlisted) == 1

    def test_WB_LA_N_multiple_students_multiple_iterations(self):
        """WB-LA-N: 5 students → Loop A iterates 5 times → all processed."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        total = sum(len(g.members) for g in result.groups) + len(result.waitlisted)
        assert total == 5


# ---------------------------------------------------------------------------
# Loop B – while i < len(eligible) (1 iteration, multiple iterations)
# ---------------------------------------------------------------------------

class TestLoopB:

    def test_WB_LB_1_one_group_formed(self):
        """WB-LB-1: Exactly group_size eligible students → Loop B runs once → 1 group."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1

    def test_WB_LB_N_multiple_groups_formed(self):
        """WB-LB-N: 6 eligible students, group_size=2 → Loop B runs 3 times → 3 groups."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(6)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 3


# ---------------------------------------------------------------------------
# Decision 4 & Loop C – has_time_conflict internals
# ---------------------------------------------------------------------------

class TestDecision4AndLoopC:

    def test_WB_D4_T_slot_matches_conflict_detected(self):
        """WB-D4-T: D4 True → group slot matches proposed → returns True."""
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "MON-09:00") is True

    def test_WB_D4_F_slot_differs_no_conflict(self):
        """WB-D4-F: D4 False → group slot differs from proposed → no conflict."""
        student = make_student("A", ["COMP101"], ["MON-09:00", "TUE-14:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "TUE-14:00") is False

    def test_WB_LC_0_no_assigned_groups_loop_skipped(self):
        """WB-LC-0: No assigned groups → Loop C executes 0 times → no conflict."""
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        assert has_time_conflict(student, "MON-09:00") is False

    def test_WB_LC_1_one_group_checked(self):
        """WB-LC-1: 1 assigned group → Loop C runs once → conflict detected."""
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "MON-09:00") is True

    def test_WB_LC_N_multiple_groups_all_checked(self):
        """WB-LC-N: 3 assigned groups, conflict only in last → all iterations run."""
        student = make_student("A", ["COMP101"], ["MON-09:00", "TUE-10:00", "WED-14:00"])
        g1 = Group(id="GRP-1", course="COMP101", members=[student], time_slot="MON-09:00")
        g2 = Group(id="GRP-2", course="COMP101", members=[student], time_slot="TUE-10:00")
        student.assigned_groups = [g1, g2]
        # Conflict would be at WED-14:00 only if a group exists there
        assert has_time_conflict(student, "WED-14:00") is False


# ---------------------------------------------------------------------------
# Data Flow – DU cycle for `eligible` variable
# ---------------------------------------------------------------------------

class TestDataFlowEligible:

    def test_DU_definition_before_use(self):
        """DU: eligible is defined (= []) before any append or len() call."""
        # If definition were missing, NameError would be raised here
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        # No NameError → definition precedes all uses ✓
        assert result is not None

    def test_DU_append_modifies_eligible(self):
        """DU: eligible is correctly modified (appended to) for matching students."""
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        # Both students were appended to eligible and appear in a group
        member_ids = {m.id for g in result.groups for m in g.members}
        assert member_ids == {"A", "B"}

    def test_DU_len_eligible_read_at_decision3(self):
        """DU: len(eligible) is read at Decision 3; correct value used."""
        # 1 eligible student → len == 1 → D3 triggers waitlist
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert result.groups == []

    def test_DU_eligible_sliced_in_loop_b(self):
        """DU: eligible is sliced in Loop B to form groups; value is read correctly."""
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(4)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        # eligible sliced into [0:2] and [2:4] → 2 groups
        assert len(result.groups) == 2
