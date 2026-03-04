# 7. 4th March Exercise — Control Flow & Data Flow

> Applied to `src/matcher.py` — specifically `form_groups()` and supporting functions.

---

## Part 1: Control Flow Application — The Path Audit

### Decision Points Identified

Three decision points (plus two loops) were identified in `form_groups()` and `find_common_slot()`.

---

#### Decision Point 1 — `if not unit_students` (line 64)

```python
if not unit_students:
    return groups
```

**What it guards:** If no students are enrolled in the requested unit, the function returns immediately with an empty list.

| Branch | Condition | Test Case | Expected Result |
|--------|-----------|-----------|----------------|
| True | `unit_students` is empty | Call `form_groups([], "CS101")` | Returns `[]` immediately |
| False | `unit_students` has students | Call `form_groups([s1, s2], "CS101")` where both enrolled in CS101 | Continues to matching logic |

---

#### Decision Point 2 — `if not compatible` (line 83)

```python
if not compatible:
    student.status = "unmatched"
    continue
```

**What it guards:** If the current student has no peers with an overlapping time slot, they are marked unmatched and skipped.

| Branch | Condition | Test Case | Expected Result |
|--------|-----------|-----------|----------------|
| True | No compatible peers found | 1 student in unit, no others share any slot | `student.status == "unmatched"`, no group formed |
| False | At least one compatible peer exists | 2 students both available Mon 9–11 | Proceeds to `pick_group()` |

---

#### Decision Point 3 — `if slot is None` (line 90)

```python
if slot is None:
    student.status = "unmatched"
    continue
```

**What it guards:** Even if students are considered compatible (pairwise), a group of 3+ may have no single slot common to *all* members.

| Branch | Condition | Test Case | Expected Result |
|--------|-----------|-----------|----------------|
| True | No slot shared by all group members | Student A: Mon 9–11; Student B: Mon 9–11 & Tue 14–16; Student C: Tue 14–16 only — no slot shared by all three | `student.status == "unmatched"` |
| False | A common slot exists for all members | All 3 students available Mon 9–11 | `slot = MON_9_11`, continues to conflict check |

---

### Loop Tests

#### Loop 1 — `for student in sorted_students` (line 76)

This is the main processing loop — one iteration per student enrolled in the unit.

| Scenario | Input | Expected Behaviour |
|----------|-------|--------------------|
| **Skip entirely** (0 iterations) | `unit_students` is empty — caught by DP1 before this loop | Loop body never executes; empty list returned |
| **Run once** (1 iteration) | Exactly 1 student in unit | Loop runs once; student has no peers → marked unmatched |
| **Run multiple times** | 6 students in unit | Loop iterates up to 6 times; students assigned to groups or marked unmatched |

#### Loop 2 — `for m in members` (line 107)

This loop marks each group member as "matched" and records their ID in `assigned_ids`.

| Scenario | Input | Expected Behaviour |
|----------|-------|--------------------|
| **Skip entirely** | Never skipped — only reached when `members` is non-empty (min size 2) | N/A |
| **Run once** | Group of 2 members | Loop runs twice (once per member); both marked matched |
| **Run multiple times** | Group of 3 or 4 members | Loop runs 3–4 times; all members marked matched |

---

### Branch Coverage Summary

All 3 decision points require **2 test cases each** (True + False) to achieve Branch Coverage (Level 2). The loops require 3 scenarios each (skip, once, many).

| ID | Decision Point | True Branch Test | False Branch Test |
|----|---------------|-----------------|------------------|
| DP1 | `if not unit_students` | `test_empty_student_list` | `test_three_students_same_unit_shared_slot` |
| DP2 | `if not compatible` | `test_single_student_unmatched` | `test_three_students_same_unit_shared_slot` |
| DP3 | `if slot is None` | `test_no_shared_slot_all_unmatched` | `test_three_students_same_unit_shared_slot` |

All branches are covered by the existing test suite in `tests/test_matcher.py`.

---

## Part 2: Data Flow Application — The Variable Lifecycle

### Variable Chosen: `slot`

`slot` is the most important variable in `form_groups()`. It represents the shared meeting time for a group and flows through definition, multiple uses, and a conditional check before the group is created.

---

### Definition-Use (DU) Cycle

```
matcher.py — form_groups()
```

| Event | Line | Type | Description |
|-------|------|------|-------------|
| **DEF** | 88 | Definition | `slot = find_common_slot(members)` — assigned the first time slot shared by all group members, or `None` |
| **USE** | 90 | Predicate Use | `if slot is None` — slot is tested; if None, execution branches to mark student unmatched |
| **USE** | 95 | Computation Use | `has_conflict(m, slot, all_known_groups)` — slot is passed to conflict checker to see if any member is already booked at this time |
| **USE** | 103 | Computation Use | `meeting_slot=slot` — slot is embedded into the new `StudyGroup` object |
| **OUT OF SCOPE** | 111 | End of scope | `return groups` — `slot` goes out of scope at the end of the `for` loop iteration; it is re-defined in the next iteration |

---

### DU Pair Diagram

```
Line 88: slot = find_common_slot(members)       ← DEF
              │
              ▼
Line 90: if slot is None ──── True ──► student.status = "unmatched" (slot not used further)
              │
           False
              │
              ▼
Line 95: has_conflict(m, slot, ...)             ← USE (predicate)
              │
              ▼
Line 103: meeting_slot = slot                   ← USE (computation)
              │
              ▼
         (end of iteration — slot redefined next loop cycle)
```

---

### Abnormal Pair Check

| Anomaly Type | Description | Present? |
|-------------|-------------|----------|
| **Use before definition** | `slot` used before `find_common_slot()` assigns it | No — DEF at line 88 always precedes USE at lines 90, 95, 103 |
| **Overwrite before use** | `slot` reassigned without being used | No — each iteration DEFs then USEs slot before re-entering the loop |
| **Use after deletion** | `slot` accessed after going out of scope | No — `slot` is local to each loop iteration; it cannot be accessed outside the loop body |
| **Dead definition** | `slot` defined but never used | Possible only if `if slot is None` (line 90) is True — in that case slot is defined but lines 95 and 103 are skipped. This is **intentional** (the value is checked, not used further when None) and is not a defect. |

---

### Second Variable: `assigned_ids`

A second variable tracked to show the DU cycle across the full loop.

| Event | Line | Type | Description |
|-------|------|------|-------------|
| **DEF** | 67 | Definition | `assigned_ids = set()` — initialised as empty set before the loop |
| **USE** | 77 | Predicate Use | `if student.id in assigned_ids` — checked to skip already-grouped students |
| **USE** | 80 | Computation Use | `s.id not in assigned_ids` — used to filter the `remaining` list |
| **DEF** | 109 | Re-definition | `assigned_ids.add(m.id)` — updated after a group is formed |
| **USE** | 77 | Predicate Use (next iteration) | Checked again at the top of next loop iteration |
| **OUT OF SCOPE** | 111 | End of scope | `return groups` — `assigned_ids` goes out of scope |

**Abnormal pairs check:**
- No use before definition — `assigned_ids` is defined at line 67 before the loop at line 76.
- No overwrite before use — the initial DEF at line 67 is immediately available for USE at line 77.
- No use after deletion — variable is local to `form_groups()`; not accessible after return.
