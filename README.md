# Smart Study Group Matching System

> SWE3020 Software Quality Assurance — Progress Presentation Project

A Python system that automatically forms balanced study groups based on students' courses, weak topics, and available time slots. Built to demonstrate SQA principles: requirements-driven design, black-box and white-box testing, and a formal SQA plan.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Running the Web UI](#running-the-web-ui)
- [Running the Tests](#running-the-tests)
- [Architecture](#architecture)
- [SQA Documentation](#sqa-documentation)
- [API Reference](#api-reference)
- [Branch Strategy](#branch-strategy)

---

## Project Overview

The system accepts a list of students (each with courses, weak topics, and available time slots) and matches them into study groups of 2–5 members. It enforces:

- Students only grouped with others on the **same course**
- No student assigned to **two groups at the same time** (conflict detection)
- **Odd students** who cannot form a full group are waitlisted
- **Session attendance** tracked per group with participation reports
- **Weekly schedule** auto-generated from formed groups

---

## Features

| Feature | Module | Description |
|---|---|---|
| Group Matching | `src/matcher.py` | Matches students into balanced groups with conflict detection |
| Participation Tracking | `src/tracker.py` | Records sessions and calculates per-student attendance rates |
| Schedule Suggestion | `src/scheduler.py` | Generates a sorted weekly meeting schedule from groups |
| Web UI | `web/` | 5-tab FastAPI interface for live demo |

---

## Project Structure

```
smart-group/
│
├── src/                        # Core business logic
│   ├── models.py               # Dataclasses: Student, Group, Session, etc.
│   ├── matcher.py              # Matching engine + conflict detection
│   ├── tracker.py              # Participation tracker
│   └── scheduler.py           # Schedule generator
│
├── tests/                      # pytest test suite (80 tests)
│   ├── test_black_box.py       # EP and BVA tests (22 tests)
│   ├── test_white_box.py       # CFG, branch coverage, DU tests (20 tests)
│   ├── test_tracker.py         # Participation tracker tests (16 tests)
│   └── test_scheduler.py      # Scheduler tests (22 tests)
│
├── web/                        # Web UI (FastAPI)
│   ├── main.py                 # FastAPI app, routes, in-memory state
│   └── templates/
│       ├── index.html          # Main 5-tab UI (Tailwind CSS)
│       └── report.html         # Group attendance report page
│
├── docs/                       # SQA documentation
│   ├── 1-project-description.md
│   ├── 2-sqa-plan.md           # SQA Plan (McCall's quality model)
│   ├── 3-black-box-testing.md  # EP + BVA test case tables
│   ├── 4-white-box-testing.md  # CFG, branch coverage, DU cycles
│   ├── 5-test-plan.md          # Formal test plan (IEEE template)
│   ├── 6-presentation-guide.md # Rubric-mapped presentation guide
│   └── 7-powerpoint-guide.md  # 13-slide PowerPoint outline with speaker notes
│
├── notes/                      # Course materials (reference only)
│   ├── test-plan-template.docx
│   ├── SWE3020 Progress Presentations Grading Rubric.pdf
│   └── Chapter 1–7.pdf, SQA Plan.pdf, Group work.pdf
│
├── pyproject.toml              # pytest configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run all tests

```bash
python -m pytest tests/ -v
```

Expected output: **80 passed**

---

## Running the Web UI

Install web dependencies (one-time):

```bash
pip install fastapi jinja2 uvicorn python-multipart
```

Start the server:

```bash
uvicorn web.main:app --reload
```

Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Web UI Tabs

| Tab | What it does |
|---|---|
| **Students** | View all students, add new ones, remove existing ones. Pre-loaded with 8 demo students on startup. |
| **Match** | Enter a course code, time slot, and group size — instantly forms groups and shows member cards. |
| **Sessions** | Select a group, pick a date, enter attendee IDs — records the session. |
| **Schedule** | Auto-generated weekly timetable sorted by day and time. |
| **Reports** | Click any group to see a per-student attendance table with colour-coded progress bars. |

> Click **Reset Demo Data** in the header to reload the 8 pre-seeded students at any time.

---

## Running the Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_black_box.py -v
python -m pytest tests/test_white_box.py -v
python -m pytest tests/test_tracker.py -v
python -m pytest tests/test_scheduler.py -v

# With coverage summary
python -m pytest tests/ -v --tb=short
```

### Test Suite Breakdown

| File | Tests | What is covered |
|---|---|---|
| `test_black_box.py` | 22 | Equivalence Partitioning and Boundary Value Analysis |
| `test_white_box.py` | 20 | CFG decisions D1–D4, loops A/B/C, DU cycles for `eligible` |
| `test_tracker.py` | 16 | `record_session`, `get_student_report`, `get_group_report` |
| `test_scheduler.py` | 22 | `parse_slot`, `generate_schedule`, `format_schedule` |
| **Total** | **80** | |

---

## Architecture

### Data Models (`src/models.py`)

```
Student         — id, name, courses, weak_topics, available_slots, assigned_groups
Group           — id, course, members, time_slot
MatchResult     — groups, waitlisted
Session         — id, group, date, attendee_ids
ParticipationReport — student_id, sessions_expected, sessions_attended,
                      attendance_rate, missed_session_ids
```

### Matching Algorithm (`src/matcher.py`)

```
match_students(students, course, slot, group_size):
  Loop A: for each student
    D1: if course matches → candidate
    D2: if no time conflict → eligible
  D3: if len(eligible) < 2 → return all as waitlisted
  Loop B: chunk eligible into groups of group_size
    if chunk >= 2 → form Group, assign to members
    else → waitlist remainder

has_time_conflict(student, slot):
  if slot not in student.available_slots → True
  Loop C: for each assigned group
    D4: if group.time_slot == slot → True (double-booking)
  return False
```

This structure maps directly to the Control Flow Graph in [docs/4-white-box-testing.md](docs/4-white-box-testing.md).

### Time Slot Format

Slots follow the pattern `DAY-HH:MM`:

```
MON-09:00   TUE-14:30   WED-10:00
THU-16:00   FRI-08:30   SAT-11:00   SUN-15:00
```

---

## SQA Documentation

| Document | Content |
|---|---|
| [docs/2-sqa-plan.md](docs/2-sqa-plan.md) | SQA Plan using McCall's 11 quality factors; 6 standards areas (coding, DB, GUI, testing, review, process) |
| [docs/3-black-box-testing.md](docs/3-black-box-testing.md) | EP partitions and BVA edge cases for 5 features with pass/fail criteria |
| [docs/4-white-box-testing.md](docs/4-white-box-testing.md) | Full CFG of `match_students()`, branch coverage table, DU cycle analysis |
| [docs/5-test-plan.md](docs/5-test-plan.md) | IEEE-format test plan: scope, approach, environment, responsibilities, all 80 test cases |
| [docs/6-presentation-guide.md](docs/6-presentation-guide.md) | Rubric-mapped Q&A guide and presentation structure |
| [docs/7-powerpoint-guide.md](docs/7-powerpoint-guide.md) | 13-slide PowerPoint outline with full speaker notes |

---

## API Reference

### `src/matcher.py`

```python
match_students(students, course, slot, group_size=3) -> MatchResult
# Forms groups from eligible students. Clamps group_size to 2–5.

has_time_conflict(student, slot) -> bool
# Returns True if student is unavailable or already in a group at that slot.

reset_group_counter()
# Resets the GRP-N counter. Used in tests for isolation.
```

### `src/tracker.py`

```python
record_session(group, date, attendee_ids) -> Session
# Records a session. Non-member IDs are silently excluded.

get_student_report(student, sessions) -> ParticipationReport
# Calculates attendance rate across all sessions the student was expected at.

get_group_report(group, sessions) -> dict[str, ParticipationReport]
# Returns a report for every member of the group.

reset_session_counter()
# Resets the SES-N counter. Used in tests for isolation.
```

### `src/scheduler.py`

```python
parse_slot(time_slot) -> tuple[str, str]
# Parses "MON-09:00" into ("MON", "09:00"). Raises ValueError on bad input.

generate_schedule(groups) -> list[ScheduleEntry]
# Returns ScheduleEntry list sorted by (day-of-week, time, group_id).

format_schedule(groups) -> str
# Returns a plain-text weekly schedule string.
```

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable — all features, all docs, web UI |
| `dev` | Feature development (merged into main) |
| `presentation` | PowerPoint guide snapshot (merged into main) |
