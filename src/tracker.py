"""
Participation Tracker for the Smart Study Group Matching System.

Responsibilities:
  - Record a study session and who attended.
  - Calculate per-student attendance rate across all sessions
    for groups they belong to.
  - Calculate per-group attendance summary.
"""

from src.models import Group, ParticipationReport, Session, Student

_session_counter = 0


def _next_session_id() -> str:
    global _session_counter
    _session_counter += 1
    return f"SES-{_session_counter}"


def reset_session_counter() -> None:
    global _session_counter
    _session_counter = 0


def record_session(group: Group, date: str, attendee_ids: list[str]) -> Session:
    """
    Record a study session for a group.

    Args:
        group:        The group that held the session.
        date:         Date of the session (YYYY-MM-DD).
        attendee_ids: IDs of students who actually attended.

    Returns:
        A Session object stored in memory.
    """
    member_ids = {m.id for m in group.members}
    valid_attendees = [sid for sid in attendee_ids if sid in member_ids]

    return Session(
        id=_next_session_id(),
        group=group,
        date=date,
        attendee_ids=valid_attendees,
    )


def get_student_report(student: Student, sessions: list[Session]) -> ParticipationReport:
    """
    Calculate participation stats for a student.

    A session is 'expected' if the student is a member of the group
    that held the session.

    Args:
        student:  The student to report on.
        sessions: All recorded sessions (across any group).

    Returns:
        ParticipationReport with attendance rate and missed sessions.
    """
    expected = [s for s in sessions if any(m.id == student.id for m in s.group.members)]

    if not expected:                                    # Decision 1: no expected sessions
        return ParticipationReport(
            student_id=student.id,
            sessions_expected=0,
            sessions_attended=0,
            attendance_rate=0.0,
            missed_session_ids=[],
        )

    attended = [s for s in expected if student.id in s.attendee_ids]   # Decision 2
    missed = [s.id for s in expected if student.id not in s.attendee_ids]

    rate = len(attended) / len(expected)

    return ParticipationReport(
        student_id=student.id,
        sessions_expected=len(expected),
        sessions_attended=len(attended),
        attendance_rate=round(rate, 4),
        missed_session_ids=missed,
    )


def get_group_report(group: Group, sessions: list[Session]) -> dict:
    """
    Return a summary of attendance for every member of a group.

    Returns:
        Dict mapping student_id → ParticipationReport.
    """
    group_sessions = [s for s in sessions if s.group.id == group.id]
    return {
        member.id: get_student_report(member, group_sessions)
        for member in group.members
    }
