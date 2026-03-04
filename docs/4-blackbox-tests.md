# 4. Black-Box Testing

> Aligned with Chapter 4: Black-Box Testing Techniques
> Tests are derived from requirements and specifications — no knowledge of internal code required.

---

## 4.1 Equivalence Partitioning (EP)

Divide inputs into classes where the system behaves identically for all values within a class.

### EP1 — Number of Students per Unit

| Class | Range | Type | Example |
|-------|-------|------|---------|
| EP1-V1 | 0 students | Invalid | 0 |
| EP1-V2 | 1 student | Invalid (unmatched) | 1 |
| EP1-V3 | 2–4 students | Valid | 3 |
| EP1-V4 | 5–8 students | Valid (multi-group) | 6 |
| EP1-V5 | > 500 students | Valid (stress) | 501 |

### EP2 — Available Time Slots per Student

| Class | Range | Type | Example |
|-------|-------|------|---------|
| EP2-V1 | 0 slots | Invalid | [] |
| EP2-V2 | 1–3 slots | Valid | ["Mon 9-11"] |
| EP2-V3 | 4–7 slots | Valid | 5 slots |

### EP3 — Units Selected per Student

| Class | Range | Type |
|-------|-------|------|
| EP3-V1 | 0 units | Invalid |
| EP3-V2 | 1 unit | Valid |
| EP3-V3 | 2–5 units | Valid |

---

## 4.2 Boundary Value Analysis (BVA)

Test values at the boundaries of equivalence classes.

### BVA1 — Group Size (valid: 2–4)

| Test ID | Input (# students with shared slot) | Expected Group Size | Result |
|---------|-------------------------------------|---------------------|--------|
| BVA1-1 | 1 | Unmatched | — |
| BVA1-2 | 2 | Group of 2 | Pass |
| BVA1-3 | 3 | Group of 3 | Pass |
| BVA1-4 | 4 | Group of 4 | Pass |
| BVA1-5 | 5 | Groups of 3+2 | Pass |

### BVA2 — Time Slot Overlap

| Test ID | Slots Student A | Slots Student B | Overlap? |
|---------|----------------|----------------|----------|
| BVA2-1 | Mon 9-11 | Mon 9-11 | Yes |
| BVA2-2 | Mon 9-11 | Mon 11-13 | No |
| BVA2-3 | Mon 9-11, Tue 14-16 | Tue 14-16 | Yes |
| BVA2-4 | (none) | Mon 9-11 | No |

---

## 4.3 Decision Table

Tests combinations of matching conditions.

### Decision Table — Group Formation

| Rule | Same Unit | Shared Slot | Group Size OK | Expected Outcome |
|------|-----------|-------------|---------------|-----------------|
| R1 | Yes | Yes | Yes (2–4) | Group formed |
| R2 | Yes | Yes | No (>4) | Split into smaller groups |
| R3 | Yes | No | — | All unmatched |
| R4 | No | Yes | — | Not grouped together |
| R5 | No | No | — | Not grouped together |

### Decision Table — Conflict Detection

| Rule | Student in Group A | Same Slot as Group B | Action |
|------|-------------------|----------------------|--------|
| R1 | Yes | Yes | Block assignment to B |
| R2 | Yes | No | Allow assignment to B |
| R3 | No | — | Allow assignment to B |

---

## 4.4 State Transition Testing

Models the lifecycle of a student profile in the system.

### States
- **Unregistered** → **Registered** → **Profile Complete** → **Matched** / **Unmatched**

### State Transition Table

| Current State | Event | Next State | Action |
|--------------|-------|------------|--------|
| Unregistered | Submit registration | Registered | Create student record |
| Registered | Complete profile (units + slots) | Profile Complete | Enable matching |
| Registered | Submit incomplete profile | Registered | Error: missing required fields |
| Profile Complete | Matching run | Matched | Assign to group, set meeting slot |
| Profile Complete | Matching run, no compatible peers | Unmatched | Flag student, notify |
| Matched | Another student joins, slot conflict | Unmatched | Remove from group, re-run |
| Unmatched | New compatible student registers | Matched | Re-run matching |

### State Transition Test Cases

| Test ID | Start State | Event | Expected End State |
|---------|------------|-------|-------------------|
| ST-1 | Unregistered | Valid registration | Registered |
| ST-2 | Registered | Full profile submitted | Profile Complete |
| ST-3 | Registered | Empty units submitted | Registered (error) |
| ST-4 | Profile Complete | Matching with 2 compatible peers | Matched |
| ST-5 | Profile Complete | No peers share any slot | Unmatched |
| ST-6 | Matched | Conflict detected post-assignment | Re-evaluated |

---

## 4.5 Test Case Summary Table

| Test ID | Technique | Input | Expected Output | Priority |
|---------|-----------|-------|----------------|----------|
| BB-01 | EP | 0 students in unit | Empty group list | P2 |
| BB-02 | EP | 1 student in unit | "Unmatched — waiting" | P3 |
| BB-03 | EP | 3 students, shared slot | 1 group of 3 | P1 |
| BB-04 | BVA | 2 students, shared slot | 1 group of 2 | P1 |
| BB-05 | BVA | 5 students, shared slot | Groups of 3 + 2 | P2 |
| BB-06 | BVA | Students with adjacent (non-overlapping) slots | Unmatched | P1 |
| BB-07 | Decision Table | Different units, shared slot | Not grouped | P1 |
| BB-08 | Decision Table | Same unit, no shared slot | All unmatched | P1 |
| BB-09 | State Transition | Student submits empty unit list | Error state | P2 |
| BB-10 | State Transition | Matched student gets conflict | Re-evaluated | P2 |
