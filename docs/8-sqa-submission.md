# Software Quality Assurance Documentation
## Smart Study Group Matching System

---

| Field | Detail |
|---|---|
| **Course** | SWE3020 – Software Quality Assurance |
| **Project** | Smart Study Group Matching System |
| **Document Type** | SQA Plan & Evidence Report |
| **Version** | 1.0 |
| **Date** | April 2026 |
| **Repository** | https://github.com/Musyonchez/smart-group |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Quality Objectives](#2-quality-objectives)
3. [Coding Standards](#3-coding-standards)
4. [Database Design Standards](#4-database-design-standards)
5. [GUI Design Standards](#5-gui-design-standards)
6. [Testing Standards & Test Case Design](#6-testing-standards--test-case-design)
7. [Review Standards](#7-review-standards)
8. [Organizational Process & SQA Framework](#8-organizational-process--sqa-framework)
9. [Test Results Evidence](#9-test-results-evidence)

---

## 1. Introduction

### 1.1 Purpose

This document defines the Software Quality Assurance (SQA) Plan for the Smart Study Group Matching System. It describes the standards, procedures, and activities used to ensure the system meets its functional and quality requirements throughout the development lifecycle.

### 1.2 System Overview

The Smart Study Group Matching System is a web-based application that automatically groups university students into study groups based on:

- Shared course enrollment
- Identified weak topics
- Common time slot availability

The system is composed of three core modules:

| Module | Responsibility |
|---|---|
| **Matcher** (`src/matcher.py`) | Groups eligible students by course and time slot |
| **Scheduler** (`src/scheduler.py`) | Generates and formats the weekly meeting schedule |
| **Tracker** (`src/tracker.py`) | Records sessions and calculates attendance rates |

A FastAPI web interface (`web/main.py`) exposes all functionality through a browser-based dashboard.

### 1.3 Scope

This SQA Plan applies to all phases of development:

> Requirements → Design → Implementation → Testing → Review

SQA activities are scheduled alongside each development milestone, not treated as optional post-development steps.

---

## 2. Quality Objectives

The following quality objectives guide all SQA activities, aligned with **McCall's Quality Model**:

| Quality Factor | Objective for This System |
|---|---|
| **Correctness** | The matcher must produce groups that satisfy all three eligibility criteria (course, availability, no conflict). Results are verified against defined rules by automated tests. |
| **Reliability** | The system must not crash on edge-case inputs: empty student lists, odd student counts, or students with no available slots. |
| **Usability** | Students can complete registration and view their assigned group without confusion. Error messages must be specific and actionable. |
| **Testability** | All three core modules are independently unit-testable with no external dependencies at test time. |
| **Maintainability** | Code is modular, consistently named, and documented so that future changes can be made without breaking existing behaviour. |

---

## 3. Coding Standards

All source code in this project adheres to the following standards.

### 3.1 Language & Structure

- **Language**: Python 3.12 for all backend logic.
- **Module separation**: Each concern is isolated in its own module (`matcher`, `scheduler`, `tracker`, `models`). No module imports from the web layer.
- **Function length**: Maximum 30 lines per function. Functions exceeding this are split by responsibility.
- **Single responsibility**: Each function does one thing. Matching, conflict detection, and group construction are separate functions.

### 3.2 Naming Conventions

| Construct | Convention | Example |
|---|---|---|
| Variables & functions | `snake_case` | `match_students`, `has_time_conflict` |
| Classes | `PascalCase` | `Student`, `Group`, `ScheduleEntry` |
| Constants | `UPPER_SNAKE_CASE` | `GROUP_SIZE_MIN`, `DAY_ORDER` |
| Test files | `test_<module>.py` | `test_black_box.py` |

### 3.3 Comments & Documentation

- All functions implementing matching or conflict-detection logic include inline comments explaining the decision logic.
- Test files include module-level docstrings explaining the testing technique used and which features are covered.
- Each individual test has a docstring describing what input condition it represents.

### 3.4 Configuration

- No hardcoded values in business logic. Group size limits and time slot format are defined as constants.
- Time slots use a standardised format enforced throughout: `DAY-HH:MM` (e.g., `MON-09:00`).

### 3.5 Version Control

- All changes committed via Git with descriptive commit messages.
- Repository hosted at: `https://github.com/Musyonchez/smart-group`
- Main branch is protected; development follows a commit-per-feature approach.

---

## 4. Database Design Standards

The system uses in-memory data structures (Python dataclasses) with the following schema constraints, designed to mirror a normalised relational database.

### 4.1 Student Profile

| Field | Type | Constraint |
|---|---|---|
| `id` | `str` | Primary key, unique |
| `name` | `str` | Required |
| `courses` | `list[str]` | At least one entry required for matching |
| `weak_topics` | `list[str]` | Optional |
| `available_slots` | `list[str]` | Format: `DAY-HH:MM` |
| `assigned_groups` | `list[Group]` | Populated by matcher at runtime |

### 4.2 Group Record

| Field | Type | Constraint |
|---|---|---|
| `id` | `str` | Primary key, auto-assigned (e.g., `GRP-1`) |
| `course` | `str` | Must match an enrolled course of all members |
| `members` | `list[Student]` | Min 2, Max 5 |
| `time_slot` | `str` | Format: `DAY-HH:MM` |

### 4.3 Integrity Rules

- **No scheduling conflict**: A student ID may not appear in two groups that share the same `time_slot`. This is enforced programmatically in `has_time_conflict()` before any group assignment.
- **Normalisation**: Data is structured to 3NF — no repeated groups, no transitive dependencies between fields.
- **Referential integrity**: A `Group` always holds references to valid `Student` objects, not just IDs.

---

## 5. GUI Design Standards

The web interface (`web/templates/`) adheres to the following standards.

### 5.1 Input Design

- Course selection uses predefined options — no free-text course entry to prevent invalid data.
- Available time slots follow the `DAY-HH:MM` format, documented inline in every input field placeholder.
- The student registration form validates all required fields before submission.

### 5.2 Output & Feedback

- After matching, the assigned group is displayed with: group ID, course, time slot, and member names.
- Flash messages confirm every successful action (student added, session recorded, etc.).
- Error states display specific, actionable messages rather than generic failures.

### 5.3 Visual Consistency

- Styling is implemented with **Tailwind CSS** (CDN) applied consistently across all pages.
- Color scheme: indigo primary, slate background, emerald/yellow/red for attendance status.
- All pages share the same header component and navigation structure.
- The attendance report page uses colour-coded progress bars:
  - **Green** ≥ 75% — Good
  - **Yellow** ≥ 50% — Fair
  - **Red** < 50% — At Risk

---

## 6. Testing Standards & Test Case Design

### 6.1 Test Suite Overview

The project contains **80 automated tests** across 4 files, all executed with **pytest**:

| File | Technique | Tests | Coverage Area |
|---|---|---|---|
| `test_black_box.py` | EP + BVA | 22 | Matcher — inputs and outputs only |
| `test_white_box.py` | CFG + Branch + Data Flow | 19 | Matcher internals — every branch and loop |
| `test_scheduler.py` | Functional | 15 | `parse_slot`, `generate_schedule`, `format_schedule` |
| `test_tracker.py` | Functional | 18 | Session recording, attendance calculation |

### 6.2 Black Box Testing — Equivalence Partitioning & BVA

**Equivalence Partitioning (EP)** divides inputs into classes that should behave identically, reducing the number of tests needed without sacrificing coverage.

| Partition Class | Representative Input | Expected Behaviour |
|---|---|---|
| Students share the course | Both enrolled in `COMP101` | Group formed |
| Students on different courses | A: `COMP101`, B: `MATH201` | No group formed |
| Student has no courses | `courses = []` | Student ineligible |
| Student has no time slots | `available_slots = []` | Student excluded |
| Student has a scheduling conflict | Already in a group at `MON-09:00` | Excluded from new group at same slot |

**Boundary Value Analysis (BVA)** tests values at the edges of valid ranges, where defects are most likely:

| Boundary | Value | Expected Behaviour |
|---|---|---|
| Below minimum group size | 0 students | No group, empty result |
| Below minimum group size | 1 student | No group, student waitlisted |
| At minimum group size | 2 students | 1 group formed |
| Nominal | 3 students | 1 group formed |
| At maximum group size | 5 students | 1 group of 5 formed |
| Above maximum group size | 6 students (size=5) | 1 group of 5, 1 waitlisted |

### 6.3 White Box Testing — CFG & Branch Coverage

White box tests are derived from the Control Flow Graph (CFG) of `match_students()`. Every decision point (D) and loop (L) is exercised in both directions.

**Decisions tested:**

| ID | Condition | True Branch Test | False Branch Test |
|---|---|---|---|
| D1 | `student.course == course` | Student with matching course → eligible | Student with wrong course → skipped |
| D2 | `not has_time_conflict(student, slot)` | No prior group at slot → eligible | Existing group at slot → excluded |
| D3 | `len(eligible) < GROUP_SIZE_MIN` | 1 eligible student → waitlist returned | 3 eligible students → group formation proceeds |
| D4 | `group.time_slot == proposed_slot` | Exact slot match → conflict returned | Different slot → no conflict |

**Loops tested (0 / 1 / N iterations):**

| Loop | 0 iterations | 1 iteration | N iterations |
|---|---|---|---|
| Loop A — student filtering | Empty input list | 1 student processed | 5 students all processed |
| Loop B — group slicing | N/A (guarded by D3) | 2 students → 1 group | 6 students → 3 groups |
| Loop C — conflict checking | No assigned groups | 1 assigned group | 3 assigned groups, conflict in last |

**Data Flow (DU chain for `eligible`):**

| Stage | Operation |
|---|---|
| Definition | `eligible = []` — before Loop A |
| Use 1 | `eligible.append(student)` — inside Loop A |
| Use 2 | `len(eligible) < GROUP_SIZE_MIN` — at Decision 3 |
| Use 3 | `eligible[i : i + group_size]` — inside Loop B |

### 6.4 Test Format & Traceability

All test cases follow a consistent structure:

- **Test ID** embedded in the function name (e.g., `test_EP_C1_same_course_forms_group`, `test_BVA_G3_two_students_at_minimum`)
- **Docstring** describing the input condition and expected behaviour
- **Assertions** directly verifying the expected output
- Each test references the feature it validates through its class grouping (`TestCourseMatchingEP`, `TestGroupSizeBVA`, etc.)

### 6.5 Defect Logging Standard

Any defect found during testing is logged with:

| Field | Description |
|---|---|
| Severity | Critical / Major / Minor |
| Description | What failed and under what condition |
| Steps to reproduce | Exact input that triggers the defect |
| Resolution | Fix applied and commit reference |

---

## 7. Review Standards

### 7.1 Peer Review

Each module (matcher, scheduler, tracker) is reviewed before integration. The reviewer checks:

- Logic correctness against requirements
- Adherence to coding standards (naming, length, comments)
- Edge case handling (empty input, odd counts, no matches)

### 7.2 Walkthrough

Before each testing phase, the team walks through the test plan to confirm:

- All requirements have corresponding test cases
- Test inputs cover all EP classes and BVA boundaries
- No test cases are duplicated or contradictory

### 7.3 Formal Review Checklist

| Item | Status |
|---|---|
| All requirements covered by at least one test case | ✅ |
| No student can appear in two simultaneously-scheduled groups | ✅ |
| Odd-number student edge case is handled (waitlist) | ✅ |
| Boundary conditions (min/max group size) are tested | ✅ |
| Code meets naming and length standards | ✅ |
| Inline comments present on all decision logic | ✅ |

Reviews are recorded with date, participants, findings, and action items.

---

## 8. Organizational Process & SQA Framework

### 8.1 IEEE SQA Alignment

This plan aligns with the **IEEE definition of SQA**:

> *"A systematic, planned set of actions necessary to provide adequate confidence that the software development process conforms to established functional and technical requirements."*

SQA is not a phase — it runs throughout the entire development lifecycle.

### 8.2 Development Phases & SQA Activities

| Phase | SQA Activity |
|---|---|
| Requirements | Quality objectives defined; McCall's factors mapped to system features |
| Design | Database and GUI standards established; module boundaries agreed |
| Implementation | Coding standards enforced; peer review before each merge |
| Testing | Black box (EP/BVA) and white box (CFG/branch) tests executed; defects logged |
| Review | Formal checklist completed; walkthrough conducted before submission |

---

## 9. Test Results Evidence

### 9.1 Final Test Run

All 80 tests pass. Command used:

```
python -m pytest tests/ -v
```

### 9.2 Results Summary

```
tests/test_black_box.py     22 passed
tests/test_white_box.py     19 passed
tests/test_scheduler.py     15 passed
tests/test_tracker.py       18 passed

========================= 80 passed in 0.21s =========================
```

### 9.3 Running the Tests

| Command | Purpose |
|---|---|
| `python -m pytest` | Run all 80 tests |
| `python -m pytest -v` | Run all tests with individual test names |
| `python -m pytest tests/test_black_box.py -v` | Run black box tests only |
| `python -m pytest tests/test_white_box.py -v` | Run white box tests only |
| `python -m pytest tests/test_scheduler.py -v` | Run scheduler tests only |
| `python -m pytest tests/test_tracker.py -v` | Run tracker tests only |

### 9.4 Running the Web Application

```bash
# Install dependencies (once)
pip install fastapi uvicorn jinja2 python-multipart

# Start the server
uvicorn web.main:app --reload

# Open in browser
http://localhost:8000
```

---

*End of SQA Documentation — Smart Study Group Matching System*
