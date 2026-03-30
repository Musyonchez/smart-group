"""
White Box Tests – Smart Study Group Matching System
Techniques: Control Flow Graph (CFG), Branch Coverage (Level 2), Data Flow (DU)
Reference: docs/4-white-box-testing.md

White box testing looks *inside* the implementation. We map out:

  - Every decision point (if/else) in the code → test both True and False branches
  - Every loop → test 0 iterations, 1 iteration, and many iterations
  - Data flow → confirm variables are defined before they are used

The main function under test is match_students(), which internally runs:

  Loop A  → iterates over all students, filtering eligible ones
    Decision 1 (D1): does this student take the requested course?
    Decision 2 (D2): is this student free at the requested time slot?
  Decision 3 (D3): are there enough eligible students to form even one group?
  Loop B  → slices the eligible list into groups of group_size
  Loop C  → inside has_time_conflict(), checks each of the student's existing groups
    Decision 4 (D4): does any existing group clash with the proposed slot?
"""

import pytest
from src.matcher import has_time_conflict, match_students, reset_group_counter
from src.models import Group, Student


# ---------------------------------------------------------------------------
# Helper – builds a minimal Student for testing
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


# Resets the global group ID counter before every test so IDs are predictable
@pytest.fixture(autouse=True)
def reset():
    reset_group_counter()


# ---------------------------------------------------------------------------
# Decision 1 – student.course == course
# Location: Loop A, first filter inside match_students()
# True  branch → student is added to the eligible list
# False branch → student is silently skipped
# ---------------------------------------------------------------------------

class TestDecision1CourseBranch:

    def test_WB_D1_T_course_matches_student_eligible(self):
        """WB-D1-T: D1 True → student added to eligible list."""
        # Both students have COMP101 → D1 is True for both → both land in a group
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
        # A has MATH201, not COMP101 → D1 is False for A → A is skipped entirely
        students = [
            make_student("A", ["MATH201"], ["MON-09:00"]),  # wrong course
            make_student("B", ["COMP101"], ["MON-09:00"]),
            make_student("C", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = [m.id for g in result.groups for m in g.members]
        assert "A" not in member_ids


# ---------------------------------------------------------------------------
# Decision 2 – not has_time_conflict(student, slot)
# Location: Loop A, second filter inside match_students()
# True  branch → no conflict, student remains eligible
# False branch → conflict detected, student is excluded
# ---------------------------------------------------------------------------

class TestDecision2ConflictBranch:

    def test_WB_D2_T_no_conflict_student_eligible(self):
        """WB-D2-T: D2 True (no conflict) → student eligible."""
        # Neither student has prior group assignments → no conflict → both eligible
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1

    def test_WB_D2_F_conflict_student_skipped(self):
        """WB-D2-F: D2 False (conflict exists) → student excluded."""
        # A is already in a group at MON-09:00 → conflict → D2 is False → A skipped
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
        assert "A" not in member_ids  # excluded due to conflict


# ---------------------------------------------------------------------------
# Decision 3 – len(eligible) < GROUP_SIZE_MIN
# Location: after Loop A completes, before Loop B begins
# True  branch → not enough eligible students → return waitlist immediately
# False branch → enough students → proceed to form groups in Loop B
# ---------------------------------------------------------------------------

class TestDecision3EligibleGuard:

    def test_WB_D3_T_too_few_eligible_returns_waitlist(self):
        """WB-D3-T: D3 True (eligible < 2) → waitlist returned immediately."""
        # Only 1 eligible student → len(eligible) == 1 < 2 → D3 is True → early return
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert result.groups == []
        assert len(result.waitlisted) == 1

    def test_WB_D3_F_enough_eligible_proceeds_to_groups(self):
        """WB-D3-F: D3 False (eligible >= 2) → group formation proceeds."""
        # 3 eligible students → len(eligible) == 3 >= 2 → D3 is False → Loop B runs
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(3)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) >= 1


# ---------------------------------------------------------------------------
# Loop A – for student in students
# Tests for: 0 iterations (empty list), 1 iteration, and N iterations
# This loop builds the eligible list by filtering all input students
# ---------------------------------------------------------------------------

class TestLoopA:

    def test_WB_LA_0_empty_list_skips_loop(self):
        """WB-LA-0: Empty students list → Loop A executes 0 times → waitlist."""
        # Loop body never runs → eligible stays empty → D3 triggers → empty result
        result = match_students([], "COMP101", "MON-09:00")
        assert result.groups == []
        assert result.waitlisted == []

    def test_WB_LA_1_single_student_one_iteration(self):
        """WB-LA-1: 1 student → Loop A iterates once → waitlisted (D3 triggers)."""
        # Loop runs once, adds A to eligible, but D3 catches that 1 < 2
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert result.groups == []
        assert len(result.waitlisted) == 1

    def test_WB_LA_N_multiple_students_multiple_iterations(self):
        """WB-LA-N: 5 students → Loop A iterates 5 times → all processed."""
        # Every student goes through the loop; total must be conserved
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(5)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=3)
        total = sum(len(g.members) for g in result.groups) + len(result.waitlisted)
        assert total == 5   # no student is silently dropped


# ---------------------------------------------------------------------------
# Loop B – while i < len(eligible)
# Tests for: 1 iteration (one group) and N iterations (multiple groups)
# This loop slices the eligible list into groups of group_size
# ---------------------------------------------------------------------------

class TestLoopB:

    def test_WB_LB_1_one_group_formed(self):
        """WB-LB-1: Exactly group_size eligible students → Loop B runs once → 1 group."""
        # Eligible list fills exactly one group → loop executes once → done
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(2)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 1

    def test_WB_LB_N_multiple_groups_formed(self):
        """WB-LB-N: 6 eligible students, group_size=2 → Loop B runs 3 times → 3 groups."""
        # 6 ÷ 2 = 3 full groups → loop runs 3 times
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(6)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 3


# ---------------------------------------------------------------------------
# Decision 4 & Loop C – inside has_time_conflict()
#
# Loop C  → iterates over every group the student is already assigned to
# Decision 4 → does that group's time_slot match the proposed slot?
#
# Tests for: 0 groups (loop skipped), 1 group, N groups
# ---------------------------------------------------------------------------

class TestDecision4AndLoopC:

    def test_WB_D4_T_slot_matches_conflict_detected(self):
        """WB-D4-T: D4 True → group slot matches proposed → returns True."""
        # The existing group and the proposed slot are both MON-09:00 → conflict
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "MON-09:00") is True

    def test_WB_D4_F_slot_differs_no_conflict(self):
        """WB-D4-F: D4 False → group slot differs from proposed → no conflict."""
        # Existing group is at MON-09:00 but we're proposing TUE-14:00 → no clash
        student = make_student("A", ["COMP101"], ["MON-09:00", "TUE-14:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "TUE-14:00") is False

    def test_WB_LC_0_no_assigned_groups_loop_skipped(self):
        """WB-LC-0: No assigned groups → Loop C executes 0 times → no conflict."""
        # Student has never been assigned to any group → loop body never runs
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        assert has_time_conflict(student, "MON-09:00") is False

    def test_WB_LC_1_one_group_checked(self):
        """WB-LC-1: 1 assigned group → Loop C runs once → conflict detected."""
        # Loop runs exactly once and immediately finds the conflict
        student = make_student("A", ["COMP101"], ["MON-09:00"])
        existing = Group(id="GRP-0", course="COMP101", members=[student], time_slot="MON-09:00")
        student.assigned_groups.append(existing)
        assert has_time_conflict(student, "MON-09:00") is True

    def test_WB_LC_N_multiple_groups_all_checked(self):
        """WB-LC-N: 3 assigned groups, conflict only in last → all iterations run."""
        # Student is in 2 groups (MON-09:00, TUE-10:00); proposing WED-14:00
        # Loop must check all existing groups before concluding there's no conflict
        student = make_student("A", ["COMP101"], ["MON-09:00", "TUE-10:00", "WED-14:00"])
        g1 = Group(id="GRP-1", course="COMP101", members=[student], time_slot="MON-09:00")
        g2 = Group(id="GRP-2", course="COMP101", members=[student], time_slot="TUE-10:00")
        student.assigned_groups = [g1, g2]
        # WED-14:00 is not taken → no conflict even after checking all groups
        assert has_time_conflict(student, "WED-14:00") is False


# ---------------------------------------------------------------------------
# Data Flow – DU cycle for the `eligible` variable
#
# Data flow testing tracks a variable from its Definition (D) to each Use (U):
#   D  → eligible = []                   (line where it is created)
#   U1 → eligible.append(student)        (write use inside Loop A)
#   U2 → len(eligible) < GROUP_SIZE_MIN  (read use at Decision 3)
#   U3 → eligible[i : i+group_size]      (read use inside Loop B)
#
# We verify the variable is always defined before it is read/written.
# ---------------------------------------------------------------------------

class TestDataFlowEligible:

    def test_DU_definition_before_use(self):
        """DU: eligible is defined (= []) before any append or len() call."""
        # If the definition were missing, Python would raise a NameError.
        # A clean run with no error proves the definition precedes all uses.
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert result is not None   # no NameError raised → DU path is valid

    def test_DU_append_modifies_eligible(self):
        """DU: eligible is correctly modified (appended to) for matching students."""
        # U1: both students pass D1 and D2 → both are appended to eligible
        # We verify by checking they both appear in the resulting group
        students = [
            make_student("A", ["COMP101"], ["MON-09:00"]),
            make_student("B", ["COMP101"], ["MON-09:00"]),
        ]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        member_ids = {m.id for g in result.groups for m in g.members}
        assert member_ids == {"A", "B"}

    def test_DU_len_eligible_read_at_decision3(self):
        """DU: len(eligible) is read at Decision 3; correct value used."""
        # U2: with only 1 student appended, len(eligible) == 1 → D3 fires → no groups
        students = [make_student("A", ["COMP101"], ["MON-09:00"])]
        result = match_students(students, "COMP101", "MON-09:00")
        assert result.groups == []

    def test_DU_eligible_sliced_in_loop_b(self):
        """DU: eligible is sliced in Loop B to form groups; value is read correctly."""
        # U3: 4 students → eligible == [0,1,2,3] → sliced as [0:2] and [2:4] → 2 groups
        students = [make_student(str(i), ["COMP101"], ["MON-09:00"]) for i in range(4)]
        result = match_students(students, "COMP101", "MON-09:00", group_size=2)
        assert len(result.groups) == 2
