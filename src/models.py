from dataclasses import dataclass, field


@dataclass
class TimeSlot:
    day: str    # e.g. "Mon", "Tue"
    start: int  # 24h hour, e.g. 9
    end: int    # 24h hour, e.g. 11

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.day == other.day and self.start < other.end and other.start < self.end

    def __eq__(self, other):
        return isinstance(other, TimeSlot) and self.day == other.day and self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.day, self.start, self.end))


@dataclass
class Student:
    id: str
    name: str
    units: list
    strong: list
    weak: list
    availability: list
    status: str = "unmatched"


@dataclass
class StudyGroup:
    id: str
    unit: str
    members: list       # list of Student.id
    meeting_slot: TimeSlot
