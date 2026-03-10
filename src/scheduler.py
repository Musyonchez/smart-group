"""
Schedule Suggester for the Smart Study Group Matching System.

Responsibilities:
  - Parse a time slot string (e.g. "MON-09:00") into day and time.
  - Build a human-readable weekly meeting schedule from a list of groups.
  - Return structured ScheduleEntry objects for programmatic use.
"""

from dataclasses import dataclass
from src.models import Group

DAY_LABELS = {
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}

DAY_ORDER = list(DAY_LABELS.keys())


@dataclass
class ScheduleEntry:
    group_id: str
    course: str
    day: str          # e.g. "MON"
    time: str         # e.g. "09:00"
    member_ids: list[str]

    @property
    def day_label(self) -> str:
        return DAY_LABELS.get(self.day, self.day)

    @property
    def display(self) -> str:
        members = ", ".join(self.member_ids)
        return (
            f"[{self.group_id}] {self.course} — "
            f"{self.day_label} {self.time} | Members: {members}"
        )


def parse_slot(time_slot: str) -> tuple[str, str]:
    """
    Parse a slot string like 'MON-09:00' into ('MON', '09:00').

    Raises ValueError for unrecognised formats.
    """
    parts = time_slot.split("-", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid time slot format: {time_slot!r}")
    day, time = parts
    if day not in DAY_LABELS:
        raise ValueError(f"Unknown day code: {day!r}")
    return day, time


def generate_schedule(groups: list[Group]) -> list[ScheduleEntry]:
    """
    Build a list of ScheduleEntry objects from a list of groups,
    sorted by day-of-week then time.

    Args:
        groups: Groups returned by match_students (or any Group list).

    Returns:
        List of ScheduleEntry sorted by (day_order, time, group_id).
    """
    entries: list[ScheduleEntry] = []
    for group in groups:
        day, time = parse_slot(group.time_slot)
        entries.append(
            ScheduleEntry(
                group_id=group.id,
                course=group.course,
                day=day,
                time=time,
                member_ids=[m.id for m in group.members],
            )
        )

    entries.sort(key=lambda e: (DAY_ORDER.index(e.day), e.time, e.group_id))
    return entries


def format_schedule(groups: list[Group]) -> str:
    """
    Return a plain-text weekly meeting schedule.

    Example output:
        === Weekly Meeting Schedule ===
        Monday 09:00
          [GRP-1] COMP101 — Members: A, B, C
        Wednesday 14:00
          [GRP-2] COMP202 — Members: D, E
    """
    entries = generate_schedule(groups)
    if not entries:
        return "No groups scheduled."

    lines = ["=== Weekly Meeting Schedule ==="]
    current_header = None
    for e in entries:
        header = f"{e.day_label} {e.time}"
        if header != current_header:
            lines.append(header)
            current_header = header
        members = ", ".join(e.member_ids)
        lines.append(f"  [{e.group_id}] {e.course} — Members: {members}")

    return "\n".join(lines)
