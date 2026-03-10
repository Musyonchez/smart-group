from dataclasses import dataclass, field
from typing import List


@dataclass
class Group:
    id: str
    course: str
    members: List["Student"]
    time_slot: str


@dataclass
class Student:
    id: str
    name: str
    courses: List[str]
    weak_topics: List[str]
    available_slots: List[str]
    assigned_groups: List[Group] = field(default_factory=list)


@dataclass
class MatchResult:
    groups: List[Group]
    waitlisted: List["Student"]


@dataclass
class Session:
    id: str
    group: Group
    date: str           # format: YYYY-MM-DD
    attendee_ids: List[str] = field(default_factory=list)


@dataclass
class ParticipationReport:
    student_id: str
    sessions_expected: int
    sessions_attended: int
    attendance_rate: float      # 0.0 – 1.0
    missed_session_ids: List[str]
