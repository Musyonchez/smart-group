# PowerPoint Presentation Guide
## SWE3020 – Smart Study Group Matching System

**Rubric:** SQA Planning & Factors (4) + Test Design Black & White Box (11) + Individual Presentation (5) = **20 marks**

---

## Slide Structure Overview

| Slide | Title | Rubric Criterion |
|-------|-------|-----------------|
| 1 | Title Slide | — |
| 2 | Project Overview | Context |
| 3 | Quality Objectives | SQA Planning (4 marks) |
| 4 | SQA Plan – Standards | SQA Planning (4 marks) |
| 5 | SQA Lifecycle Integration | SQA Planning (4 marks) |
| 6 | Testing Strategy | Test Design intro |
| 7 | Equivalence Partitioning | Test Design (11 marks) |
| 8 | Boundary Value Analysis | Test Design (11 marks) |
| 9 | Control Flow Graph | Test Design (11 marks) |
| 10 | Branch Coverage Results | Test Design (11 marks) |
| 11 | Data Flow – DU Cycle | Test Design (11 marks) |
| 12 | Live Test Demo | Test Design (11 marks) |
| 13 | Summary & Conclusion | All |

---

## Slide 1 – Title Slide

**Title:** Smart Study Group Matching System
**Subtitle:** Software Quality Assurance – SWE3020 Progress Presentation
**Group name / Student names**
**Date**

> Design tip: Keep it clean. Dark background, white text, or university template.

---

## Slide 2 – Project Overview

**Title:** What We Built

**Bullet points:**
- Automatically matches students into study groups
- Matching criteria: shared course + topic difficulty + available time slots
- Key constraints: no student in two groups at the same time, handles odd student counts
- Built in Python; 42 automated tests written and passing

**Visual:** simple 3-box flow diagram:
```
[Student Registers] → [Matching Engine] → [Group Assigned]
```

> Keep this slide to 30 seconds. It's just context — don't linger.

---

## Slide 3 – Quality Objectives

**Title:** SQA Quality Objectives (McCall's Model)

**Content:**
> "Our quality objectives are grounded in McCall's 11-factor model. For this project we prioritised:"

| Quality Factor | What it means for our system |
|---------------|------------------------------|
| **Correctness** | Matching output must follow defined rules exactly |
| **Reliability** | System must not crash on odd counts or empty inputs |
| **Usability** | Students complete registration without confusion |
| **Testability** | Modules structured for independent unit testing |
| **Maintainability** | Code is modular and documented for future changes |

**Say:** *"SQA is not just about testing — it starts with defining what quality means for the product. We used McCall's model to make quality measurable from day one."*

> This slide directly targets the 4-mark SQA Planning criterion.

---

## Slide 4 – SQA Plan: Standards

**Title:** SQA Plan – Six Standards Areas

**Content (two columns):**

**Left column:**
- **Coding Standards** — snake_case naming, max 30 lines per function, no hardcoded values
- **Database Design Standards** — 3NF normalisation, unique constraint: no student in two groups at same time slot
- **GUI Design Standards** — course selection via dropdown, meaningful error messages

**Right column:**
- **Testing Standards** — EP, BVA, CFG; every branch covered; test IDs trace to requirements
- **Review Standards** — peer review checklist, walkthrough before each test phase
- **Org. Process Reference** — aligned to IEEE SQA definition

**Say:** *"Each standard directly prevents one or more of the nine causes of software error — faulty requirements, coding errors, shortcomings of testing — as defined in our course material."*

---

## Slide 5 – SQA Lifecycle Integration

**Title:** SQA Integrated Into the Project Lifecycle

**Visual:** horizontal lifecycle bar with SQA activities pinned beneath each phase:

```
Requirements → Design → Implementation → Testing → Review
     |              |           |              |         |
  Req Review   Design      Code Review    Test Plan  Defect
  Checklist   Walkthrough  + Standards    Execution   Log
```

**Say:** *"SQA activities are not done at the end — they are scheduled as part of every phase. This is the IEEE definition in practice: a systematic, planned set of actions throughout the development process."*

---

## Slide 6 – Testing Strategy

**Title:** Two-Track Testing Approach

**Content:**

| | Black Box | White Box |
|-|-----------|-----------|
| **View** | External behaviour | Internal structure |
| **Techniques** | EP + BVA | CFG + Branch Coverage + DU Analysis |
| **What it finds** | Wrong outputs, missing validations | Untested branches, variable lifecycle bugs |
| **Applied to** | Course matching, group size, conflicts, odd counts | `match_students()` and `has_time_conflict()` |

**Say:** *"Black box and white box are complementary — black box catches 'does it do the right thing?' and white box catches 'does every path of code get exercised?'"*

---

## Slide 7 – Equivalence Partitioning (EP)

**Title:** Black Box – Equivalence Partitioning

**Say:** *"EP divides the input space into partitions where all values behave identically. We only need one test per partition — testing more adds no confidence."*

**Example — Course Matching:**

| Partition | Input | Expected Output |
|-----------|-------|-----------------|
| Valid – same course | Student A + B: COMP101 | Group formed ✓ |
| Invalid – different course | A: COMP101, B: MATH201 | No match ✓ |
| Invalid – no course | A: (none) | Validation error ✓ |

**Example — Group Size:**

| Partition | Range | Representative | Expected |
|-----------|-------|----------------|----------|
| Too few | 0–1 | 1 student | Waitlisted |
| Valid | 2–5 | 3 students | Group formed |
| Too many | > 5 | 7 students | Split / waitlist |

**Justification:** *"Each partition exercises a distinct code path. Inputs within a partition are logically equivalent — choosing one is sufficient."*

---

## Slide 8 – Boundary Value Analysis (BVA)

**Title:** Black Box – Boundary Value Analysis

**Say:** *"BVA targets the edges of valid ranges — where off-by-one errors cluster. It complements EP: EP finds the classes, BVA tests the edges between them."*

**Group Size Boundaries (GROUP_SIZE_MIN = 2, MAX = 5):**

| Test ID | Input | Boundary Position | Expected |
|---------|-------|-------------------|----------|
| BVA-G2 | 1 student | Just below min | Waitlisted |
| BVA-G3 | **2 students** | **At minimum** | Group formed |
| BVA-G5 | **5 students** | **At maximum** | Group formed |
| BVA-G6 | 6 students | Just above max | Split/waitlist |

**Odd Student Boundaries:**

| Test ID | Input | Expected |
|---------|-------|----------|
| BVA-O2 | 2 students | 1 group of 2 |
| BVA-O3 | 3 students | 1 group + 1 waitlisted |
| BVA-O4 | 5 students | 2 groups, 0 waitlisted |

---

## Slide 9 – Control Flow Graph (CFG)

**Title:** White Box – Control Flow Graph

**Say:** *"We modelled the `match_students()` function as a CFG — every decision point and loop becomes a node. Branch Coverage Level 2 requires every True and False branch to be tested."*

**Visual (draw this on the slide):**

```
        START
          │
          ▼
    ┌─ Loop A: for each student ─────────────────┐
    │         │                                   │ (done)
    │    ┌────▼────┐                              │
    │    │   D1    │ course matches?              │
    │    └────┬────┘                              │
    │    T    │    F                              │
    │    ▼    ▼                                   │
    │  ┌─D2─┐ skip ──────────────────────────────┤
    │  │    │ no conflict?                        │
    │  └─┬──┘                                     │
    │  T │  F → skip ─────────────────────────────┤
    │    ▼                                         │
    │  [add to eligible] ─────────────────────────┘
          │
          ▼
        ┌─D3─┐  eligible < 2?
        └─┬──┘
        T │  F
        ▼    ▼
    WAITLIST  Loop B: while i < len(eligible)
                │
              [form group, i += size]
                │
              RETURN groups
```

**4 decisions × 2 branches = 8 branch tests**
**3 loops × {0, 1, many} = 9 loop tests**

---

## Slide 10 – Branch Coverage Results

**Title:** White Box – Branch Coverage (Level 2)

**Content:**

| Decision | True Branch Test | False Branch Test |
|----------|-----------------|-------------------|
| D1: course match | A enrolled in COMP101 ✓ | A enrolled in MATH201 ✓ |
| D2: no conflict | A free at MON-09:00 ✓ | A already in MON-09:00 group ✓ |
| D3: eligible < 2 | Only 1 eligible student ✓ | 3 eligible students ✓ |
| D4: slot match | Group slot = proposed ✓ | Group slot ≠ proposed ✓ |

| Loop | 0 iterations | 1 iteration | Multiple |
|------|-------------|-------------|----------|
| Loop A (students) | Empty list ✓ | 1 student ✓ | 5 students ✓ |
| Loop B (group formation) | Caught by D3 | 2 students → 1 group ✓ | 6 students → 3 groups ✓ |
| Loop C (conflict check) | No assigned groups ✓ | 1 group ✓ | 3 groups ✓ |

**Say:** *"Every branch is exercised. No path through this code is untested."*

---

## Slide 11 – Data Flow: DU Cycle

**Title:** White Box – Data Flow Analysis (`eligible` variable)

**Say:** *"Data flow analysis tracks a variable from its definition to every use, checking for abnormal pairs — using a variable before defining it, or overwriting it before it's ever read."*

**DU Cycle for `eligible`:**

```
Definition:   eligible = []              ← line 1 of function
    │
    ▼
Use (modify): eligible.append(student)  ← inside Loop A (D1+D2 both True)
    │
    ▼
Use (read):   len(eligible) < 2         ← Decision 3
    │
    ▼
Use (read):   eligible[i : i+group_size]← inside Loop B
    │
    ▼
Out of scope: function returns          ← local variable freed
```

**Abnormal pairs checked:**

| Abnormal Pair | Found? |
|---------------|--------|
| Use before definition | No ✗ |
| Overwrite before use | No ✗ |
| Use after deletion | No ✗ |
| Defined but never used | No ✗ |

**Conclusion:** Clean DU cycle — no data flow defects.

---

## Slide 12 – Live Test Demo

**Title:** 42 Tests – All Passing

**What to show:**
Run this command live during the presentation:
```bash
pytest --tb=short -v
```

**Expected output (show on screen):**
```
tests/test_black_box.py::TestCourseMatchingEP::test_EP_C1 PASSED
tests/test_black_box.py::TestGroupSizeBVA::test_BVA_G3_two_students_at_minimum PASSED
tests/test_white_box.py::TestDecision1CourseBranch::test_WB_D1_T PASSED
...
42 passed in 0.09s
```

**Point out:**
- Test IDs in the output (`EP-C1`, `BVA-G3`, `WB-D1-T`) match directly to the tables on the previous slides.
- 22 black box tests (EP + BVA) + 20 white box tests (CFG + DU) = 42 total.
- 0.09s runtime — the matching engine is efficient.

**Say:** *"This is SQA in practice — not just a plan on paper, but executable, traceable test cases that verify every branch of the matching algorithm."*

---

## Slide 13 – Summary & Conclusion

**Title:** Summary

**Three columns matching the rubric:**

**SQA Planning (4 marks)**
- Quality objectives defined using McCall's model
- 6-area SQA plan covering coding, DB, GUI, testing, review, and org. process
- SQA activities integrated into every lifecycle phase

**Test Design (11 marks)**
- EP: 3 partitions per feature, justified by equivalence principle
- BVA: boundary tests at min (2), max (5), and ±1
- CFG: 4 decisions × 2 branches + 3 loops × 3 scenarios
- DU: clean lifecycle for `eligible`, no abnormal pairs

**Delivery (5 marks)**
- All 42 tests passing, live-demonstrable
- Test IDs traceable from code → docs → slides
- Code available at: github.com/Musyonchez/smart-group

---

## Design Tips for the Slides

- **Font**: Use a clean sans-serif (Calibri, Inter, or Arial). Body text no smaller than 18pt.
- **Color scheme**: Pick two colors — one for headers, one accent (match university branding if required).
- **Tables**: Use them — the rubric is heavy on technical criteria and tables communicate coverage clearly.
- **CFG diagram**: Draw it in PowerPoint using shapes + arrows, or paste a screenshot of the text version from the docs.
- **Live demo slide**: Have the terminal open and ready before the presentation starts. Don't type the command during — just run it.
- **One idea per slide**: Don't overcrowd. If a slide has more than 6 bullet points, split it.
- **Presenter notes**: Copy the "Say:" text from each slide above into PowerPoint's notes pane.
