# 5. White-Box Testing

> Aligned with Chapter 5: White-Box Testing Techniques
> Tests are derived from the internal structure and logic of the code.

---

## 5.1 Code Under Test

The primary function under white-box analysis is `form_groups()` in `matcher.py`.

```python
def form_groups(students: list[Student]) -> list[StudyGroup]:
    groups = []
    unassigned = list(students)

    while unassigned:                                    # Node 1
        student = unassigned.pop(0)                     # Node 2
        compatible = find_compatible(student, unassigned)  # Node 3

        if len(compatible) == 0:                        # Node 4
            student.status = "unmatched"                # Node 5
            continue                                    # back to Node 1

        group_members = pick_group(student, compatible) # Node 6

        slot = find_common_slot(group_members)          # Node 7

        if slot is None:                                # Node 8
            student.status = "unmatched"                # Node 9
            continue                                    # back to Node 1

        if has_conflict(group_members, slot):           # Node 10
            student.status = "unmatched"                # Node 11
            continue                                    # back to Node 1

        groups.append(StudyGroup(group_members, slot))  # Node 12
        for m in group_members:                         # Node 13
            unassigned.remove(m)                        # Node 14

    return groups                                       # Node 15
```

---

## 5.2 Control Flow Testing

### Control Flow Graph (CFG)

```
        [1] while unassigned
           |
          [2] pop student
           |
          [3] find_compatible
           |
          [4] compatible == 0?
         /        \
       Yes         No
      [5]          [6] pick_group
   unmatched        |
      |            [7] find_common_slot
    (→1)            |
                   [8] slot is None?
                  /        \
                Yes         No
               [9]          [10] has_conflict?
            unmatched       /         \
               |          Yes          No
             (→1)        [11]         [12] append group
                       unmatched       |
                          |           [13] loop members
                        (→1)          [14] remove from unassigned
                                       |
                                      (→1)
                                        |
                                       [15] return groups
```

### Coverage Targets

#### Statement Coverage

All 15 nodes must be executed at least once.

| Node | Description | Covered By |
|------|-------------|-----------|
| 1–3 | Main loop, pop, compatible search | Any input with students |
| 4→5 | No compatible peers | WB-03 |
| 6–7 | Pick group, find slot | WB-01 |
| 8→9 | No common slot | WB-04 |
| 10→11 | Conflict detected | WB-05 |
| 10→12–14 | Happy path | WB-01, WB-02 |
| 15 | Return | All tests |

#### Branch Coverage

Every decision (if/while) must be exercised in both True and False directions.

| Decision | True Branch | False Branch |
|----------|------------|-------------|
| `while unassigned` | WB-01 (has students) | WB-06 (empty list) |
| `compatible == 0` | WB-03 | WB-01 |
| `slot is None` | WB-04 | WB-01 |
| `has_conflict` | WB-05 | WB-01 |
| `for m in group_members` | WB-01 | n/a (always entered) |

#### Path Coverage (basis paths)

Using cyclomatic complexity: V(G) = 4 decisions + 1 = **5 basis paths**

| Path | Description |
|------|-------------|
| P1 | Empty input → return immediately |
| P2 | Student → compatible found → slot found → no conflict → group formed |
| P3 | Student → no compatible peers → unmatched |
| P4 | Student → compatible found → no common slot → unmatched |
| P5 | Student → compatible found → slot found → conflict → unmatched |

---

## 5.3 Data Flow Testing

Tracks variables from definition (def) to use (use) to find def-use anomalies.

### Variable: `unassigned`

| Event | Location | Type |
|-------|----------|------|
| def | Entry — `unassigned = list(students)` | definition |
| use | Node 1 — `while unassigned` | predicate use |
| use | Node 2 — `unassigned.pop(0)` | computation use |
| use | Node 14 — `unassigned.remove(m)` | computation use |

**Def-Use pairs to test:**
- Entry → Node 1 (list populated, loop runs)
- Entry → Node 1 with empty list (loop skipped)
- Node 2 → Node 14 (item removed after group formed)

### Variable: `slot`

| Event | Location | Type |
|-------|----------|------|
| def | Node 7 — `slot = find_common_slot(...)` | definition |
| use | Node 8 — `if slot is None` | predicate use |
| use | Node 10 — `has_conflict(..., slot)` | computation use |
| use | Node 12 — `StudyGroup(..., slot)` | computation use |

**Def-Use pairs to test:**
- Node 7 → Node 8: slot = None (no common slot path)
- Node 7 → Node 10: slot valid, check conflict
- Node 7 → Node 12: slot valid, no conflict, used in group creation

---

## 5.4 White-Box Test Cases

| Test ID | Target | Coverage Type | Input | Expected |
|---------|--------|--------------|-------|----------|
| WB-01 | `form_groups` | Statement + Branch (happy path) | 3 students, shared slot, no conflict | 1 group of 3 |
| WB-02 | `form_groups` | Statement (multi-group) | 6 students, 2 compatible clusters | 2 groups |
| WB-03 | `form_groups` | Branch: compatible==0 | 1 student, no peers in unit | Student unmatched |
| WB-04 | `form_groups` | Branch: slot is None | 2 students, compatible but disjoint slots | Both unmatched |
| WB-05 | `form_groups` | Branch: has_conflict | 3 students, valid slot but one already booked | Conflict student unmatched |
| WB-06 | `form_groups` | Branch: while=False | Empty student list | Empty group list |
| WB-07 | `find_overlap` | Statement | Two matching slots | Returns shared slot |
| WB-08 | `find_overlap` | Branch | No matching slots | Returns empty list |
| WB-09 | `has_conflict` | Statement | Student has existing group at same slot | Returns True |
| WB-10 | `has_conflict` | Branch | Student free at slot | Returns False |

---

## 5.5 Code Coverage Summary

| Metric | Target | Rationale |
|--------|--------|-----------|
| Statement coverage | 100% | All paths should be reachable |
| Branch coverage | 100% | 4 decisions — manageable |
| Path coverage | 5 basis paths | Matches cyclomatic complexity |

Tools: `pytest --cov=matcher --cov-report=term-missing`
