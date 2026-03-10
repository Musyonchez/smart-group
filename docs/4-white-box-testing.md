# White Box Testing – Smart Study Group Matching System

White box testing examines the internal structure of the code. The two techniques applied are **Control Flow Graph (CFG)** with **Branch Coverage (Level 2)**, and **Data Flow Analysis (DU cycles)**.

---

## Module: `match_students(students, course)`

This is the core matching function. Pseudocode:

```
function match_students(students, course):
    eligible = []
    for student in students:                  # Loop A
        if student.course == course:          # Decision 1
            if not has_time_conflict(student): # Decision 2
                eligible.append(student)

    if len(eligible) < 2:                     # Decision 3
        return WAITLIST(eligible)

    groups = []
    i = 0
    while i < len(eligible):                  # Loop B
        group = eligible[i:i+GROUP_SIZE]
        groups.append(group)
        i += GROUP_SIZE

    return groups
```

---

## Part 1: Control Flow Graph (CFG) & Branch Coverage

### Decision Points Identified

| Decision | Condition | True Branch | False Branch |
|----------|-----------|-------------|--------------|
| D1 | `student.course == course` | Student added to eligible list | Student skipped |
| D2 | `not has_time_conflict(student)` | Student added to eligible | Student skipped (conflict) |
| D3 | `len(eligible) < 2` | Waitlist returned | Proceed to group formation |
| Loop A | `for student in students` | Execute body | Exit loop |
| Loop B | `while i < len(eligible)` | Create next group | Exit loop |

### CFG Diagram (Textual Representation)

```
START
  │
  ▼
[Loop A: for each student]──(no more students)──► [D3]
  │
  ▼
[D1: course matches?]
  │ True                   │ False
  ▼                        ▼
[D2: no conflict?]       [skip student]
  │ True    │ False          │
  ▼         ▼               │
[add to   [skip]            │
 eligible]                  │
  └────────────────────────► (back to Loop A)

[D3: eligible < 2?]
  │ True          │ False
  ▼               ▼
[WAITLIST]    [Loop B: while i < eligible size]──(exit)──► [return groups]
                │
                ▼
              [create group, i += GROUP_SIZE]
              (back to Loop B)
```

### Branch Coverage Test Cases (Level 2)

For every `if` statement, we need one test where condition is **True** and one where it is **False**. For every loop, we test: skip, once, multiple times.

#### Decision 1: `student.course == course`

| Test ID | Input | Condition | Expected |
|---------|-------|-----------|----------|
| WB-D1-T | Student enrolled in COMP101; matching course = COMP101 | **True** | Student added to eligible list |
| WB-D1-F | Student enrolled in MATH201; matching course = COMP101 | **False** | Student skipped |

#### Decision 2: `not has_time_conflict(student)`

| Test ID | Input | Condition | Expected |
|---------|-------|-----------|----------|
| WB-D2-T | Student has free slot MON-09:00; group slot = MON-09:00 | **True** (no conflict) | Student added to eligible |
| WB-D2-F | Student already in group at MON-09:00; new group also MON-09:00 | **False** (conflict exists) | Student skipped |

#### Decision 3: `len(eligible) < 2`

| Test ID | Input | Condition | Expected |
|---------|-------|-----------|----------|
| WB-D3-T | Only 1 student eligible after filtering | **True** | Waitlist returned |
| WB-D3-F | 3 students eligible after filtering | **False** | Groups formed and returned |

#### Loop A: `for student in students`

| Test ID | Input | Iteration | Expected |
|---------|-------|-----------|----------|
| WB-LA-0 | Empty students list `[]` | 0 (skip loop) | `eligible = []`; D3 triggers waitlist |
| WB-LA-1 | List with 1 student | 1 iteration | Eligible list has 0 or 1 entry depending on D1/D2 |
| WB-LA-N | List with 5 students | Multiple iterations | All matching students added to eligible |

#### Loop B: `while i < len(eligible)`

| Test ID | Input | Iteration | Expected |
|---------|-------|-----------|----------|
| WB-LB-0 | `eligible = []` (never reached — D3 catches this) | 0 | N/A (handled by D3) |
| WB-LB-1 | 2 eligible students, GROUP_SIZE = 2 | 1 iteration | 1 group of 2 returned |
| WB-LB-N | 6 eligible students, GROUP_SIZE = 2 | 3 iterations | 3 groups of 2 returned |

---

## Part 2: Data Flow Analysis – Variable Lifecycle (`eligible`)

We track the variable `eligible` through the `match_students` function using the **Definition-Use (DU) cycle**.

### DU Cycle for `eligible`

| Stage | Code Location | Event | Notes |
|-------|---------------|-------|-------|
| **Definition** | `eligible = []` | Variable is initialized (given a value) | Occurs at function entry, before Loop A |
| **Use (modification)** | `eligible.append(student)` | Value is modified inside Loop A | Only reached when D1 and D2 are both True |
| **Use (computation)** | `len(eligible) < 2` | Value is read for comparison at D3 | Determines whether to waitlist or continue |
| **Use (computation)** | `eligible[i:i+GROUP_SIZE]` | Value is read to slice groups in Loop B | Used to build each group |
| **Out of scope** | Function returns | Variable is no longer accessible | After `return groups` or `return WAITLIST(eligible)` |

### Abnormal Pair Checks

| Abnormal Pair | Description | Check Result |
|---------------|-------------|--------------|
| Use before definition | Is `eligible` used before `eligible = []`? | **No** — definition is the first statement |
| Use after deletion | Is `eligible` accessed after the function returns? | **No** — Python garbage-collects local variables after return |
| Overwrite before use | Is `eligible` re-assigned before `append` is called? | **No** — only `append` modifies it; no re-assignment inside the loop |
| Definition with no use | Is `eligible` ever defined but never read? | **No** — it is always read at D3 (`len(eligible) < 2`) |

### Conclusion

The `eligible` variable has a clean DU cycle:
**Defined → Modified in loop → Read at D3 → Read in Loop B → Out of scope.**
No abnormal pairs detected. This confirms the variable lifecycle is correct and safe.

---

## Part 3: Additional Decision Point – `has_time_conflict(student)`

This sub-function also contains internal decision logic worth auditing.

### Pseudocode

```
function has_time_conflict(student):
    for group in student.assigned_groups:    # Loop C
        if group.time_slot == proposed_slot: # Decision 4
            return True
    return False
```

### Decision 4 Branch Coverage

| Test ID | Input | Condition | Expected |
|---------|-------|-----------|----------|
| WB-D4-T | Student has existing group at MON-09:00; proposed = MON-09:00 | **True** | Returns `True` (conflict) |
| WB-D4-F | Student has group at TUE-14:00; proposed = MON-09:00 | **False** | Loop continues; returns `False` (no conflict) |

### Loop C Coverage

| Test ID | Input | Iterations | Expected |
|---------|-------|-----------|----------|
| WB-LC-0 | Student has no assigned groups | 0 | Returns `False` immediately |
| WB-LC-1 | Student has 1 assigned group | 1 | Conflict checked once |
| WB-LC-N | Student has 3 assigned groups | Multiple | All slots checked before returning |

---

## Summary of White Box Test Cases

| Test ID | Decision/Loop | Condition | Expected Outcome |
|---------|---------------|-----------|------------------|
| WB-D1-T | D1 (course match) | True | Student eligible |
| WB-D1-F | D1 (course match) | False | Student skipped |
| WB-D2-T | D2 (no conflict) | True | Student eligible |
| WB-D2-F | D2 (no conflict) | False | Student skipped |
| WB-D3-T | D3 (eligible < 2) | True | Waitlist returned |
| WB-D3-F | D3 (eligible < 2) | False | Groups returned |
| WB-LA-0 | Loop A | 0 iterations | Empty eligible → waitlist |
| WB-LA-1 | Loop A | 1 iteration | Single student processed |
| WB-LA-N | Loop A | Multiple | All students processed |
| WB-LB-1 | Loop B | 1 iteration | 1 group formed |
| WB-LB-N | Loop B | Multiple | Multiple groups formed |
| WB-D4-T | D4 (slot match) | True | Conflict detected |
| WB-D4-F | D4 (slot match) | False | No conflict |
| WB-LC-0 | Loop C | 0 iterations | No conflict (no groups) |
