import uuid
from .models import Student, StudyGroup, TimeSlot


def find_overlap(s1: Student, s2: Student) -> list:
    """Return time slots shared by both students."""
    return [slot for slot in s1.availability for other in s2.availability if slot.overlaps(other)]


def find_common_slot(students: list) -> TimeSlot | None:
    """Return a slot common to ALL students, or None."""
    if not students:
        return None
    shared = list(students[0].availability)
    for student in students[1:]:
        shared = [s for s in shared for o in student.availability if s.overlaps(o)]
    return shared[0] if shared else None


def has_conflict(student: Student, slot: TimeSlot, existing_groups: list) -> bool:
    """Check if student already belongs to a group scheduled at the given slot."""
    for group in existing_groups:
        if student.id in group.members and group.meeting_slot.overlaps(slot):
            return True
    return False


def find_compatible(student: Student, others: list) -> list:
    """Return students who share at least one time slot with the given student."""
    return [s for s in others if find_overlap(student, s)]


def pick_group(student: Student, compatible: list) -> list:
    """
    Select group members from compatible students.
    Prefers students whose strengths cover the student's weak topics.
    Target size: 3; min: 2, max: 4.
    Expands to 4 if exactly 1 student would otherwise be left without a partner.
    """
    def score(candidate):
        return len(set(candidate.strong) & set(student.weak))

    ranked = sorted(compatible, key=score, reverse=True)
    size = min(3, len(ranked) + 1)  # +1 for the student themselves
    # If exactly 1 leftover would result, expand to avoid an unmatched singleton
    leftover = len(ranked) - (size - 1)
    if leftover == 1 and size < 4:
        size = 4
    return [student] + ranked[:size - 1]


def form_groups(students: list, unit: str, existing_groups: list = None) -> list:
    """
    Form study groups for a given unit.
    existing_groups: groups already formed in other units (for cross-unit conflict detection).
    Returns a list of StudyGroup objects.
    """
    if existing_groups is None:
        existing_groups = []

    groups = []
    unit_students = [s for s in students if unit in s.units]

    if not unit_students:
        return groups

    assigned_ids = set()

    # Sort ascending by number of compatible peers — harder-to-place students first
    def compatibility_count(s):
        others = [x for x in unit_students if x.id != s.id]
        return len(find_compatible(s, others))

    sorted_students = sorted(unit_students, key=compatibility_count)

    for student in sorted_students:
        if student.id in assigned_ids:
            continue

        remaining = [s for s in unit_students if s.id not in assigned_ids and s.id != student.id]
        compatible = find_compatible(student, remaining)

        if not compatible:
            student.status = "unmatched"
            continue

        members = pick_group(student, compatible)
        slot = find_common_slot(members)

        if slot is None:
            student.status = "unmatched"
            continue

        all_known_groups = groups + existing_groups
        if any(has_conflict(m, slot, all_known_groups) for m in members):
            student.status = "unmatched"
            continue

        group = StudyGroup(
            id=str(uuid.uuid4()),
            unit=unit,
            members=[m.id for m in members],
            meeting_slot=slot,
        )
        groups.append(group)

        for m in members:
            m.status = "matched"
            assigned_ids.add(m.id)

    return groups


def match_all_units(students: list) -> dict:
    """Run matching for every unit, sharing conflict state across units."""
    units = {unit for s in students for unit in s.units}
    all_groups: list = []
    result = {}
    for unit in sorted(units):  # sorted for determinism
        unit_groups = form_groups(students, unit, existing_groups=all_groups)
        all_groups.extend(unit_groups)
        result[unit] = unit_groups
    return result
