# Black Box Testing – Smart Study Group Matching System

Black box testing treats the system as a closed box: we supply inputs and verify outputs without knowledge of internal code. The two techniques used are **Equivalence Partitioning (EP)** and **Boundary Value Analysis (BVA)**.

---

## Feature 1: Student Course Matching

**Rule**: Students are matched only if they share the same enrolled course.

### Equivalence Partitioning (EP)

| Partition | Description | Representative Input | Expected Output |
|-----------|-------------|----------------------|-----------------|
| Valid – same course | Two or more students share a course | Student A: COMP101, Student B: COMP101 | Matched into a group |
| Invalid – different courses | Students have no shared course | Student A: COMP101, Student B: MATH201 | No match formed |
| Invalid – student has no course | Student enrolled in zero courses | Student A: (none) | Error: "Please select at least one course" |

**Justification**: These three partitions cover all logical categories of course overlap. Any input within a partition should behave identically — we only need one representative per partition.

---

## Feature 2: Group Size

**Rule**: A valid group requires between 2 and 5 students (inclusive).

### Equivalence Partitioning (EP)

| Partition | Range | Representative Value | Expected Output |
|-----------|-------|----------------------|-----------------|
| Too few (invalid) | 0–1 students eligible | 1 student | No group formed; student placed on waitlist |
| Valid | 2–5 students | 3 students | Group formed successfully |
| Too many (invalid) | > 5 students | 7 students | Split into sub-groups or place extras on waitlist |

### Boundary Value Analysis (BVA)

BVA tests the edges of valid ranges — where off-by-one errors most commonly occur.

| Test ID | Input (eligible students) | Expected Output | Rationale |
|---------|--------------------------|-----------------|-----------|
| BVA-G1 | 0 students | No group | Below minimum |
| BVA-G2 | 1 student | No group (waitlist) | Just below minimum boundary |
| BVA-G3 | 2 students | Group formed | At minimum boundary |
| BVA-G4 | 3 students | Group formed | Nominal valid value |
| BVA-G5 | 5 students | Group formed | At maximum boundary |
| BVA-G6 | 6 students | Overflow handled (split or waitlist) | Just above maximum boundary |

---

## Feature 3: Time Conflict Detection

**Rule**: No student may be assigned to two groups sharing the same time slot.

### Equivalence Partitioning (EP)

| Partition | Description | Input | Expected Output |
|-----------|-------------|-------|-----------------|
| Valid – no conflict | Student's selected slot is free | Student A assigned MON-09:00; new group is TUE-14:00 | Assignment succeeds |
| Invalid – conflict | Student already assigned at the same time | Student A already in MON-09:00 group; second group also MON-09:00 | System rejects assignment; reports conflict |
| Edge – student has no slots | Student selected zero availability slots | No slots selected | Error: "Please select at least one available time slot" |

### Boundary Value Analysis (BVA)

| Test ID | Input | Expected Output | Rationale |
|---------|-------|-----------------|-----------|
| BVA-T1 | 0 time slots selected | Error message | Below minimum (no availability) |
| BVA-T2 | 1 time slot selected | Matching attempted with single slot | Minimum availability |
| BVA-T3 | Student in 1 group at MON-09:00; new group at MON-09:00 | Conflict detected | Exact conflict at boundary |
| BVA-T4 | Student in 1 group at MON-09:00; new group at MON-10:00 | No conflict; assigned | Adjacent slot, no overlap |

---

## Feature 4: Handling Odd Number of Students

**Rule**: When an odd number of students qualifies for matching, the system must not leave exactly one student permanently unmatched without notification.

### Equivalence Partitioning (EP)

| Partition | Description | Input | Expected Output |
|-----------|-------------|-------|-----------------|
| Even count | Even number of eligible students | 4 students for COMP101 | 2 groups of 2, or 1 group of 4 |
| Odd count | Odd number of eligible students | 5 students for COMP101 | Groups formed; 1 leftover placed on waitlist with notification |
| Single student | Only 1 eligible student | 1 student | Waitlist; no group formed |

### Boundary Value Analysis (BVA)

| Test ID | Input | Expected Output | Rationale |
|---------|-------|-----------------|-----------|
| BVA-O1 | 1 eligible student | Waitlisted | Just below minimum for a group |
| BVA-O2 | 2 eligible students | 1 group of 2 | Minimum group formed |
| BVA-O3 | 3 eligible students | 1 group of 2, 1 waitlisted | Odd number — boundary behavior |
| BVA-O4 | 5 eligible students | 2 groups (e.g., 3+2), 0 waitlisted | Odd number split successfully |

---

## Feature 5: System Performance (Load)

**Rule**: System must handle a high number of concurrent users without failure.

### Equivalence Partitioning (EP)

| Partition | Range | Representative Input | Expected Output |
|-----------|-------|----------------------|-----------------|
| Low load (valid) | 1–50 users | 20 simultaneous registrations | All processed correctly |
| Normal load (valid) | 51–500 users | 200 simultaneous registrations | All processed correctly |
| High load (stress) | > 500 users | 1000 simultaneous registrations | System handles gracefully or queues overflow |

### Boundary Value Analysis (BVA)

| Test ID | Input (concurrent users) | Expected Output | Rationale |
|---------|--------------------------|-----------------|-----------|
| BVA-P1 | 1 user | Processed correctly | Minimum load |
| BVA-P2 | 499 users | All processed | Just below upper threshold |
| BVA-P3 | 500 users | All processed | At threshold |
| BVA-P4 | 501 users | Graceful handling (queue or error message) | Just above threshold |

---

## Summary: EP and BVA Test Cases

| Test ID | Feature | Technique | Input | Expected Output | Pass/Fail |
|---------|---------|-----------|-------|-----------------|-----------|
| EP-C1 | Course matching | EP | Same course (COMP101 × 2) | Match formed | |
| EP-C2 | Course matching | EP | Different courses | No match | |
| EP-C3 | Course matching | EP | No course selected | Validation error | |
| BVA-G2 | Group size | BVA | 1 student | No group | |
| BVA-G3 | Group size | BVA | 2 students | Group formed | |
| BVA-G5 | Group size | BVA | 5 students | Group formed | |
| BVA-G6 | Group size | BVA | 6 students | Overflow handled | |
| EP-T1 | Time conflict | EP | No slot conflict | Assigned | |
| EP-T2 | Time conflict | EP | Same slot conflict | Rejected | |
| BVA-T3 | Time conflict | BVA | Exact same slot | Conflict detected | |
| BVA-O2 | Odd numbers | BVA | 2 students | Group of 2 formed | |
| BVA-O3 | Odd numbers | BVA | 3 students | Group + 1 waitlisted | |
