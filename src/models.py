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
