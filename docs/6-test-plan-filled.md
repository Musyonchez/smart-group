# Test Plan — Smart Study Group Matching System

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Project Overview](#12-project-overview)
2. [Scope](#2-scope)
   - 2.1 [In-Scope](#21-in-scope)
   - 2.2 [Out-of-Scope](#22-out-of-scope)
3. [Testing Strategy](#3-testing-strategy)
   - 3.1 [Test Objectives](#31-test-objectives)
   - 3.2 [Test Assumptions](#32-test-assumptions)
   - 3.3 [Data Approach](#33-data-approach)
   - 3.4 [Level of Testing](#34-level-of-testing)
   - 3.5 [Unit Testing](#35-unit-testing)
   - 3.6 [Functional Testing](#36-functional-testing)
   - 3.7 [User Acceptance Testing](#37-user-acceptance-testing)
   - 3.8 [Regression Testing](#38-regression-testing)
4. [Execution Strategy](#4-execution-strategy)
   - 4.1 [Entry Criteria](#41-entry-criteria)
   - 4.2 [Exit Criteria](#42-exit-criteria)
   - 4.3 [Validation and Defect Management](#43-validation-and-defect-management)
5. [Environment Requirements](#5-environment-requirements)
   - 5.1 [Test Environments](#51-test-environments)
6. [Significantly Impacted Division/College/Department](#6-significantly-impacted-divisioncollegedepartment)
7. [Dependencies](#7-dependencies)

---

## 1 Introduction

### 1.1 PURPOSE

This test plan defines the test strategy, approach, execution strategy, and test management activities for the Smart Study Group Matching System. It provides a structured framework to ensure the matching algorithm, conflict detection, and edge-case handling are verified against the specified requirements before the system is considered complete.

### 1.2 PROJECT OVERVIEW

The Smart Study Group Matching System is a Python-based application that automatically forms balanced study groups from student profiles. Students provide their enrolled units, topics they are strong or weak in, and their available time slots. The system runs a matching algorithm (`src/matcher.py`) that groups students per unit, balances strengths against weaknesses, detects scheduling conflicts, and suggests a shared meeting time for each group.

---

## 2 Scope

### 2.1 IN-SCOPE

The following features and interfaces are included in testing:

| Feature | File / Function |
|---------|----------------|
| Time slot overlap detection | `find_overlap()`, `find_common_slot()` |
| Compatible peer filtering | `find_compatible()` |
| Group member selection with balance | `pick_group()` |
| Full group formation per unit | `form_groups()` |
| Cross-unit conflict detection | `has_conflict()`, `match_all_units()` |
| Edge cases: 0, 1, odd-number students | `form_groups()` |
| Edge cases: no shared availability | `form_groups()` |
| Performance: 500 students < 3 seconds | `form_groups()` |

### 2.2 OUT-OF-SCOPE

| Feature | Reason Excluded |
|---------|----------------|
| User interface / frontend (HTML forms) | Not part of this release; no UI implemented |
| Email and notification delivery | Dependent on external service; out of scope |
| User authentication and login | Not implemented in this release |
| Database migrations | Flat-file / in-memory storage used; no DB schema |
| Load testing beyond 500 students | Out of NFR scope for this assignment |

---

## 3 Testing Strategy

### 3.1 TEST OBJECTIVES

1. Verify students are only grouped with peers enrolled in the same unit (FR3).
2. Confirm no student is assigned to two groups with an overlapping time slot (FR5).
3. Validate all formed groups contain between 2 and 4 members (FR6).
4. Ensure students with no compatible peers or no shared availability are flagged as "unmatched" (FR7).
5. Confirm the matching algorithm completes in under 3 seconds for 500 students (NFR1).
6. Confirm strength/weakness balancing is applied when selecting group members.

### 3.2 TEST ASSUMPTIONS

- Python 3.11 or higher is available in the test environment.
- `pytest` and `pytest-cov` are installed (`pip install pytest pytest-cov`).
- Time slots are discrete and non-overlapping within a single student's profile.
- Students are registered and have a complete profile before matching is triggered.
- Matching is triggered per unit; units are processed independently unless cross-unit conflict checking is active.
- No UI testing is required; all testing is performed at the code/function level.

### 3.3 DATA APPROACH

All test data is defined inline within `tests/test_matcher.py` using a `make_student()` helper function and a set of predefined `TimeSlot` constants (e.g., `MON_9_11`, `TUE_14_16`). This ensures:

- Tests are fully self-contained and require no external files or database connections.
- Test data is deterministic and reproducible across environments.
- Each test constructs only the data it needs, preventing inter-test contamination.

For acceptance testing, representative data scenarios (0 students, 1 student, 5 students, cross-unit student) are used to simulate real student profiles.

### 3.4 LEVEL OF TESTING

| Test Type | Description | Responsible Parties |
|-----------|-------------|---------------------|
| Unit Testing | Individual functions in `matcher.py` tested in isolation with controlled inputs | Developer |
| Functional Testing | `form_groups()` and `match_all_units()` tested end-to-end for a unit | Developer |
| User Acceptance Testing | Full matching scenario validated against acceptance criteria | Developer / Tester |
| Regression Testing | Full test suite re-run after any change to `matcher.py` or `models.py` | Developer (automated) |

### 3.5 UNIT TESTING

**Features to be tested:**
- `find_overlap(s1, s2)` — returns correct list of shared time slots between two students
- `find_common_slot(students)` — returns the first slot common to all students, or None
- `has_conflict(student, slot, groups)` — correctly identifies double-booking
- `find_compatible(student, others)` — filters students by availability overlap
- `pick_group(student, compatible)` — selects correct group size and prefers strength/weakness balance

**Participants:**

| Tester's Name | Department / Area | Role |
|--------------|-------------------|------|
| [Your Name] | Software Engineering | Test Manager |
| [Your Name] | Software Engineering | Test Lead |
| [Your Name] | Software Engineering | Test Analyst |

### 3.6 FUNCTIONAL TESTING

**Features to be tested:**
- `form_groups()` for a single unit with all edge cases: 0 students, 1 student, 2–4 students (single group), 5 students (split), 6 students (two groups of 3), students with no shared slot
- `match_all_units()` for a student enrolled in multiple units — verifying cross-unit conflict detection and correct group assignment per unit

**Participants:**

| Tester's Name | Department / Area | Role |
|--------------|-------------------|------|
| [Your Name] | Software Engineering | Test Manager |
| [Your Name] | Software Engineering | Test Lead |
| [Your Name] | Software Engineering | Test Analyst |

### 3.7 USER ACCEPTANCE TESTING

**Features to be tested:**
- A student who selects at least one unit and available time slots can be successfully matched into a group for that unit
- A student enrolled in two units is placed into a group for each unit without a scheduling conflict
- A student with no compatible peers (no shared availability) receives "unmatched" status
- All groups produced by the system contain students from the same unit only
- Meeting slots assigned to groups are valid and shared by all group members

**Participants:**

| Tester's Name | Department / Area | Role |
|--------------|-------------------|------|
| [Your Name] | Software Engineering | Test Manager |
| [Your Name] | Software Engineering | Test Lead |
| [Your Name] | Software Engineering | Test Analyst |

### 3.8 REGRESSION TESTING

**Features to be tested:**
- Full test suite (`tests/test_matcher.py`, 29 test cases) re-executed after any modification to `src/matcher.py` or `src/models.py`
- Covers all previously verified behaviours: overlap detection, group formation, conflict detection, edge cases, and performance

**Participants:**

| Tester's Name | Department / Area | Role |
|--------------|-------------------|------|
| [Your Name] | Software Engineering | Test Manager |
| [Your Name] | Software Engineering | Test Lead |
| [Your Name] | Software Engineering | Test Analyst |

---

## 4 Execution Strategy

### 4.1 ENTRY CRITERIA

- The entry criteria refer to the desirable conditions in order to start test execution.
- Entry criteria are flexible benchmarks. If they are not met, the test team will assess the risk, identify mitigation actions, and provide a recommendation.

| Entry Criteria | Test Team | Technical Team | Notes |
|---------------|-----------|----------------|-------|
| Test environment(s) is available | ✓ | | Python 3.12 + pytest installed |
| Test data is available | ✓ | | Inline fixtures in `tests/test_matcher.py` |
| Code has been merged successfully | | ✓ | `src/matcher.py` and `src/models.py` complete |
| Development has completed unit testing | | ✓ | All 5 core functions implemented |
| Test scripts are completed, reviewed and approved by the Project Team | ✓ | | `tests/test_matcher.py` — 29 test cases |

### 4.2 EXIT CRITERIA

- The exit criteria are the desirable conditions that need to be met in order to proceed with implementation.
- Exit criteria are flexible benchmarks. If they are not met, the test team will assess the risk, identify mitigation actions, and provide a recommendation.

| Exit Criteria | Test Team | Technical Team | Notes |
|--------------|-----------|----------------|-------|
| 100% Test Scripts executed | ✓ | | Run: `python -m pytest tests/ -v` |
| 90% pass rate of Test Scripts | ✓ | | Target: 29/29 (100%) passing |
| No open Critical and High severity defects | ✓ | ✓ | All P1/P2 defects resolved before release |
| All remaining defects are either cancelled or documented as Change Requests for a future release | ✓ | | P3/P4 issues logged as GitHub Issues |
| All expected and actual results are captured and documented with the test script | ✓ | | pytest `-v` output captured as test report |
| All test metrics collected based on reports from daily and Weekly Status reports | ✓ | | Coverage via `pytest --cov=src --cov-report=term-missing` |
| All defects logged in Defect Tracker/Spreadsheet | ✓ | | Tracked via GitHub Issues |
| Test environment cleanup completed and a new back up of the environment | ✓ | | No persistent state; each test run is clean |

### 4.3 VALIDATION AND DEFECT MANAGEMENT

**Validation:** Each test case validates behaviour by asserting the actual output of a function against the expected output using pytest's `assert` statements. Tests are independent with no shared mutable state. Test cases reference specific requirements (e.g., FR3, FR5, NFR1) in their docstrings.

**Defect Management:**
- Testers are expected to execute all test scripts in each cycle.
- Defects are tracked through GitHub Issues.
- It is the responsibility of the tester to open defects, retest after fix, and close when the associated test passes.

Defects found during testing are categorised as follows:

| Severity | Impact |
|----------|--------|
| 1 (Critical) | Functionality is blocked and no testing can proceed. Application/feature is unusable. Example: `form_groups()` raises an unhandled exception on any input. |
| 2 (High) | Functionality is not usable and there is no workaround, but other tests can proceed. Example: a student is double-booked in two groups at the same time slot. |
| 3 (Medium) | Functionality issues but there is a workaround for achieving the desired functionality. Example: odd-number edge case produces an incorrect group size. |
| 4 (Low) | Unclear error message or cosmetic error which has minimum impact on product use. Example: group balance is suboptimal but no requirement is violated. |

---

## 5 Environment Requirements

### 5.1 TEST ENVIRONMENTS

| Item | Detail |
|------|--------|
| Operating System | Windows 11 / Linux (CI) |
| Language | Python 3.12 |
| Test Framework | pytest 9.x |
| Coverage Tool | pytest-cov 7.x |
| Source under test | `src/matcher.py`, `src/models.py` |
| Test file | `tests/test_matcher.py` |
| Run command | `python -m pytest tests/ -v --cov=src --cov-report=term-missing` |
| External services required | None |
| Security requirements | No student data leaves the local environment; tests use synthetic data only |

---

## 6 Significantly Impacted Division/College/Department

| Business Area | Business Manager | Tester(s) |
|--------------|-----------------|-----------|
| Computer Science Department | [Lecturer / Unit Coordinator] | [Your Name] |
| | | |
| | | |

---

## 7 Dependencies

| Dependency | Owner | Risk if Unavailable |
|-----------|-------|---------------------|
| Python 3.11+ runtime | Developer environment | Tests cannot be executed |
| pytest and pytest-cov packages | Developer | Install via `pip install pytest pytest-cov` |
| `src/models.py` (Student, TimeSlot, StudyGroup) | Developer | All tests fail at import |
| `src/matcher.py` (matching algorithm) | Developer | All functional tests fail |
| Test fixtures (inline in test file) | Developer | Self-contained — no external dependency |
