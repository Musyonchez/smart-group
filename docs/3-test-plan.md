# 3. Test Plan

> Aligned with Chapter 2: Integrating Quality Activities in the Project Life Cycle

---

## 1. Test Objectives

- Verify that students are matched only with others in the same unit
- Confirm no student is double-booked across two groups
- Validate correct handling of edge cases (odd numbers, no shared slots)
- Ensure system performance is acceptable under load (≤ 3s for 500 students)

---

## 2. Scope

| In Scope | Out of Scope |
|----------|-------------|
| Matching algorithm logic | UI/frontend rendering |
| Conflict detection | Email notifications |
| Schedule suggestion | Authentication/login |
| Edge case handling | Database migrations |

---

## 3. Test Levels

### 3.1 Unit Testing
Tests individual functions in isolation.

| Component | Function | What to Test |
|-----------|----------|-------------|
| Matcher | `find_overlap(s1, s2)` | Returns correct shared time slots |
| Matcher | `form_groups(students)` | Groups are size 2–4 |
| Matcher | `has_conflict(student, slot)` | Detects double-booking |
| Matcher | `balance_groups(groups)` | Strength/weakness pairing |
| DataStore | `save_student(student)` | Data persists correctly |
| DataStore | `get_students_by_unit(unit)` | Returns correct filtered list |

**Tools:** pytest
**Coverage Target:** 80% line coverage on `matcher.py`

---

### 3.2 Integration Testing
Tests interaction between components.

| Test | Components | Expected |
|------|-----------|----------|
| Profile saved then matched | DataStore + Matcher | Group formed with correct members |
| Match then conflict check | Matcher + ConflictChecker | No double-booked student |
| Full match flow per unit | API + Matcher + DataStore | Groups returned via API response |

---

### 3.3 System Testing
End-to-end tests against the running application.

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| 4 students, same unit, shared slot | 4 profiles | 1 group of 4 |
| 6 students, same unit, shared slot | 6 profiles | 2 groups of 3 |
| 5 students, same unit, shared slot | 5 profiles | Groups of 3+2 |
| Students with no shared slot | 3 profiles | All marked unmatched |
| Student in 2 units | 1 profile, 2 units | Appears in groups for each unit, no time conflict |

---

### 3.4 Acceptance Testing
Validates the system meets requirements from the student's perspective.

| Requirement | Acceptance Criterion |
|-------------|---------------------|
| FR1 | Student with no units selected cannot be matched |
| FR3 | No group contains students from different units |
| FR4 | Every group has at least one common time slot |
| FR5 | No student appears in two groups scheduled at the same time |
| FR6 | All groups have 2–4 members |
| NFR1 | Matching 500 students completes in < 3 seconds |

---

## 4. Test Environment

| Item | Detail |
|------|--------|
| Language | Python 3.11 |
| Test Framework | pytest |
| Test Data | JSON fixtures in `tests/fixtures/` |
| CI | Run tests on every commit (GitHub Actions) |

---

## 5. Entry and Exit Criteria

**Entry Criteria:**
- Matching algorithm implementation is complete
- Unit tests can be run without errors

**Exit Criteria:**
- All test cases executed
- No critical (P1) defects open
- Code coverage ≥ 80%

---

## 6. Defect Severity Levels

| Level | Description | Example |
|-------|-------------|---------|
| P1 – Critical | System cannot function | Matching crashes on any input |
| P2 – High | Core requirement violated | Student double-booked |
| P3 – Medium | Partial functionality broken | Odd-number edge case wrong |
| P4 – Low | Minor issue | Suboptimal group balance |
