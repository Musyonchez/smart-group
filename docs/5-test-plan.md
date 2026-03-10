# Test Plan – Smart Study Group Matching System

This document fulfills the test plan template structure. It consolidates test design from `3-black-box-testing.md` and `4-white-box-testing.md` into a single formal plan.

---

## 1. Test Plan Identifier

**Document ID**: TP-SSGMS-v1.0
**Project**: Smart Study Group Matching System
**Date**: 2026-03-10
**Prepared by**: [Group Name]
**Course**: SWE3020 – Software Quality Assurance

---

## 2. Introduction / Scope

The Smart Study Group Matching System automatically forms study groups based on:
- Shared enrolled courses
- Topics students find difficult
- Available study times

This test plan covers functional testing of the matching logic, conflict detection, edge-case handling (odd student counts), and basic performance testing. It does not cover third-party API integrations (none planned) or production infrastructure.

---

## 3. Test Items (Features Under Test)

| Feature | Description |
|---------|-------------|
| F1 – Course Matching | Students matched only if they share the same enrolled course |
| F2 – Group Size Control | Groups formed with 2–5 members; excess students waitlisted |
| F3 – Time Conflict Detection | No student assigned to two simultaneous groups |
| F4 – Odd Student Handling | Graceful handling when eligible count is odd |
| F5 – Meeting Schedule Suggestion | System proposes a meeting time based on shared availability |
| F6 – Participation Tracking | System records which students attended each session |
| F7 – Performance Under Load | System handles high concurrent user counts |

---

## 4. Features to Be Tested

- F1, F2, F3, F4 (core matching logic — highest priority)
- F5, F6 (schedule and tracking — medium priority)
- F7 (performance — tested after functional correctness confirmed)

## 5. Features Not to Be Tested

- Authentication/login (out of scope for current phase)
- Email notification system (not yet implemented)
- Mobile UI responsiveness (phase 2)

---

## 6. Testing Approach

### Black Box Testing (External behavior)
- **Equivalence Partitioning (EP)**: Divide inputs into valid/invalid classes. Test one representative per class.
- **Boundary Value Analysis (BVA)**: Test at and just beyond the boundaries of valid input ranges (group size: 1, 2, 5, 6; time slots: 0, 1, many).
- Reference: `3-black-box-testing.md` for full test case tables.

### White Box Testing (Internal structure)
- **Control Flow Graph (CFG)**: Model the `match_students()` and `has_time_conflict()` functions as graphs.
- **Branch Coverage (Level 2)**: Every `if`/`else` branch tested with True and False conditions. Every loop tested at 0, 1, and multiple iterations.
- **Data Flow (DU Analysis)**: Track lifecycle of critical variable `eligible` — definition, use, scope end.
- Reference: `4-white-box-testing.md` for full coverage matrix.

---

## 7. Test Pass/Fail Criteria

**Pass**: Actual output matches expected output exactly for all test cases in a feature.
**Fail**: Any deviation from expected output, including crashes, wrong group assignments, undetected conflicts, or missing error messages.

A feature is considered **ready for release** only when all its test cases pass.

---

## 8. Suspension and Resumption Criteria

- **Suspend**: If a critical defect (severity 1) is found in the matching engine, halt all dependent tests (F3, F4, F5) until the defect is resolved.
- **Resume**: After defect fix is verified by re-running the failed test cases plus regression on previously passing cases.

---

## 9. Test Deliverables

| Deliverable | Description |
|-------------|-------------|
| Test Plan (this document) | Scope, approach, test cases |
| Black Box Test Cases | `3-black-box-testing.md` |
| White Box Test Cases | `4-white-box-testing.md` |
| SQA Plan | `2-sqa-plan.md` |
| Test Execution Log | Completed table of Test ID | Result | Date | Tester |
| Defect Report | Log of all failures with severity, description, resolution |

---

## 10. Test Environment

- **Language**: Python 3.x
- **Testing Framework**: `pytest` (unit tests for matching logic)
- **Database**: SQLite (local testing); PostgreSQL (integration testing)
- **Test Data**: Simulated student profiles with varied course/topic/slot combinations
- **Load Testing Tool**: `locust` or manual script for F7 (performance)

---

## 11. Full Test Case Summary

### Black Box (from `3-black-box-testing.md`)

| Test ID | Feature | Technique | Input | Expected Output |
|---------|---------|-----------|-------|-----------------|
| EP-C1 | F1 | EP | 2 students, same course | Group formed |
| EP-C2 | F1 | EP | 2 students, different courses | No match |
| EP-C3 | F1 | EP | Student with no course | Validation error |
| BVA-G2 | F2 | BVA | 1 eligible student | No group; waitlisted |
| BVA-G3 | F2 | BVA | 2 eligible students | Group of 2 formed |
| BVA-G5 | F2 | BVA | 5 eligible students | Group of 5 formed |
| BVA-G6 | F2 | BVA | 6 eligible students | Split / waitlist |
| EP-T1 | F3 | EP | No slot conflict | Assignment succeeds |
| EP-T2 | F3 | EP | Same slot conflict | Rejected with error |
| BVA-T1 | F3 | BVA | 0 slots selected | Validation error |
| BVA-T3 | F3 | BVA | Exact same slot | Conflict detected |
| BVA-T4 | F3 | BVA | Adjacent slot (no overlap) | No conflict |
| BVA-O2 | F4 | BVA | 2 eligible students | Group of 2 |
| BVA-O3 | F4 | BVA | 3 eligible students | Group + 1 waitlisted |

### White Box (from `4-white-box-testing.md`)

| Test ID | Decision/Loop | Condition | Expected |
|---------|---------------|-----------|----------|
| WB-D1-T | D1 course match | True | Student eligible |
| WB-D1-F | D1 course match | False | Student skipped |
| WB-D2-T | D2 no conflict | True | Student eligible |
| WB-D2-F | D2 no conflict | False | Student skipped |
| WB-D3-T | D3 eligible < 2 | True | Waitlist |
| WB-D3-F | D3 eligible < 2 | False | Groups returned |
| WB-LA-0 | Loop A | 0 iterations | Waitlist (empty eligible) |
| WB-LA-1 | Loop A | 1 iteration | Single student processed |
| WB-LA-N | Loop A | Multiple | All students processed |
| WB-LB-1 | Loop B | 1 iteration | 1 group formed |
| WB-LB-N | Loop B | Multiple | Multiple groups formed |
| WB-D4-T | D4 slot conflict | True | Conflict detected |
| WB-D4-F | D4 slot conflict | False | No conflict |
| WB-LC-0 | Loop C | 0 iterations | No conflict |

---

## 12. Responsibilities

| Role | Responsibility |
|------|----------------|
| Test Designer | Writes and reviews test cases (black + white box) |
| Developer | Implements fixes for defects found during testing |
| SQA Reviewer | Verifies test coverage, signs off on test plan |
| All Members | Participate in peer reviews and walkthroughs |

---

## 13. Staffing and Training

- All team members must be familiar with EP and BVA techniques (Chapter 5/6 course material).
- White box testers must understand how to read and construct a CFG.
- `pytest` usage: basic tutorial required before test execution phase begins.
