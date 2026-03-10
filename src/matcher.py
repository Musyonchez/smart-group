"""
Core matching engine for the Smart Study Group Matching System.

Pseudocode (as modelled in white-box CFG docs/4-white-box-testing.md):

    function match_students(students, course, proposed_slot):
        eligible = []
        for student in students:                      # Loop A
            if student.course == course:              # Decision 1
                if not has_time_conflict(student):    # Decision 2
                    eligible.append(student)

        if len(eligible) < GROUP_SIZE_MIN:            # Decision 3
            return MatchResult(groups=[], waitlisted=eligible)

        groups = []
        i = 0
        while i < len(eligible):                      # Loop B
            chunk = eligible[i : i + group_size]
            if len(chunk) >= GROUP_SIZE_MIN:
                groups.append(Group(...))
            else:
                waitlisted.extend(chunk)
            i += group_size

        return MatchResult(groups, waitlisted)
"""

from src.models import Group, MatchResult, Student

GROUP_SIZE_MIN = 2
GROUP_SIZE_MAX = 5
DEFAULT_GROUP_SIZE = 3

_group_counter = 0


def _next_group_id() -> str:
    global _group_counter
    _group_counter += 1
    return f"GRP-{_group_counter}"


def reset_group_counter() -> None:
    """Reset ID counter — call between test runs for predictable IDs."""
    global _group_counter
    _group_counter = 0


def has_time_conflict(student: Student, proposed_slot: str) -> bool:
    """
    Returns True if the student cannot join a group at proposed_slot.
    Two cases trigger a conflict:
      - The student did not select proposed_slot as available.
      - The student is already assigned to another group at proposed_slot.

    Contains Decision 4 and Loop C (see docs/4-white-box-testing.md).
    """
    if proposed_slot not in student.available_slots:
        return True

    for group in student.assigned_groups:      # Loop C
        if group.time_slot == proposed_slot:   # Decision 4
            return True

    return False


def match_students(
    students: list[Student],
    course: str,
    proposed_slot: str,
    group_size: int = DEFAULT_GROUP_SIZE,
) -> MatchResult:
    """
    Match students into study groups for a given course and time slot.

    Args:
        students:      All registered students.
        course:        The course to match on.
        proposed_slot: The time slot for the new groups (e.g. 'MON-09:00').
        group_size:    Target group size (clamped to GROUP_SIZE_MIN–MAX).

    Returns:
        MatchResult with formed groups and waitlisted students.
    """
    group_size = max(GROUP_SIZE_MIN, min(GROUP_SIZE_MAX, group_size))

    # --- Build eligible list (Loop A) ---
    eligible: list[Student] = []
    for student in students:                              # Loop A
        if course in student.courses:                    # Decision 1
            if not has_time_conflict(student, proposed_slot):  # Decision 2
                eligible.append(student)

    # --- Guard: need at least two students (Decision 3) ---
    if len(eligible) < GROUP_SIZE_MIN:                   # Decision 3
        return MatchResult(groups=[], waitlisted=list(eligible))

    # --- Form groups (Loop B) ---
    groups: list[Group] = []
    waitlisted: list[Student] = []
    i = 0

    while i < len(eligible):                             # Loop B
        chunk = eligible[i : i + group_size]

        if len(chunk) >= GROUP_SIZE_MIN:
            group = Group(
                id=_next_group_id(),
                course=course,
                members=list(chunk),
                time_slot=proposed_slot,
            )
            for member in chunk:
                member.assigned_groups.append(group)
            groups.append(group)
        else:
            # Last chunk too small to form a group → waitlist
            waitlisted.extend(chunk)

        i += group_size

    return MatchResult(groups=groups, waitlisted=waitlisted)
