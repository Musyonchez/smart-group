# Presentation Guide – SWE3020 Progress Presentation

**Total marks: 20** | SQA Planning (4) + Test Design (11) + Individual Presentation (5)

This guide maps the rubric criteria to what each section of the presentation should cover, and suggests what to say to score full marks.

---

## Criterion 1 – SQA Planning & Factors (4 marks)

**What the marker wants**: Clear identification of quality objectives + a structured SQA plan integrated into the project lifecycle.

**What to present**:

1. State the quality objectives in SQA terminology:
   > "Our quality objectives are to ensure **correctness** of the matching algorithm, **reliability** under edge cases, and **usability** of the registration interface — using McCall's quality factor model."

2. Show the 6 standards areas from your SQA Plan (`2-sqa-plan.md`):
   - Coding Standards (naming, function length, version control)
   - Database Design Standards (schema constraints, normalization)
   - GUI Design Standards (form validation, error messages)
   - Testing & Test Case Design Standards (EP, BVA, CFG, coverage levels)
   - Review Standards (peer review checklist, walkthrough protocol)
   - Organizational Process Reference (IEEE SQA definition, phased development)

3. Show how SQA is integrated into the lifecycle:
   > "SQA activities are not done at the end — they are scheduled alongside each development phase: requirements review, design walkthrough, code review, test execution, and defect tracking."

**Key terminology to use**: SQA plan, quality objectives, quality factors, McCall's model, project lifecycle, standards.

---

## Criterion 2 – Test Design: Black & White Box (11 marks)

This is the highest-weighted criterion. Demonstrate correct application of **EP**, **BVA**, and **CFG**, and justify your test case selection.

### Black Box — EP (Equivalence Partitioning)

**How to explain it**:
> "We divide the input space into partitions where all values in a partition are expected to behave the same way. Testing one value per partition is sufficient."

**Applied to our system** (reference `3-black-box-testing.md`):
- Course matching: valid (same course), invalid (different course), invalid (no course) — 3 partitions, 3 test cases.
- Group size: too few (0–1), valid (2–5), too many (>5) — 3 partitions.
- Time slots: no conflict, conflict, no slots selected — 3 partitions.

**Justify selection**:
> "Each partition exercises a distinct behavioral class. Testing all values within a partition adds no additional confidence — only the boundary tests do, which is why we also apply BVA."

### Black Box — BVA (Boundary Value Analysis)

**How to explain it**:
> "Errors are most common at the edges of valid ranges. BVA tests the values just below, at, and just above each boundary."

**Applied to our system**:
- Group size boundary: test with 1, **2**, 5, **6** students — the bold values are the boundaries.
- Time slot: 0 slots (invalid), 1 slot (minimum valid).
- Odd student count: 2 (clean), 3 (odd boundary), 5 (odd, splittable).

### White Box — CFG & Branch Coverage (Level 2)

**How to explain it**:
> "We model the `match_students()` function as a Control Flow Graph with decision nodes. Branch Coverage Level 2 requires every True and every False branch to be exercised."

**Applied to our system** (reference `4-white-box-testing.md`):
- 4 decision points (D1–D4) × 2 branches each = 8 branch coverage test cases.
- 3 loops (A, B, C) × 3 scenarios each (0, 1, many) = 9 loop test cases.

**Show the CFG**: draw or display the textual CFG from `4-white-box-testing.md`.

### Data Flow — DU Analysis

**How to explain it**:
> "We trace the lifecycle of the `eligible` variable: where it is first defined, where its value is used, and where it goes out of scope. We check for abnormal pairs — using a variable before defining it, or overwriting it before it is ever read."

**Result**:
> "No abnormal pairs were found. The DU cycle is clean: define → append in loop → read at decision → read in group-formation loop → out of scope on return."

---

## Criterion 3 – Individual Presentation (5 marks)

**What the marker wants**: Professionalism, correct SQA terminology, clarity of delivery, ability to handle technical questions.

### Terminology to Use (memorize these)

| Term | Correct Usage |
|------|---------------|
| Equivalence Partitioning | "Divides input domain into classes where behavior is identical within each class" |
| Boundary Value Analysis | "Tests at and just beyond the edges of valid ranges where defects cluster" |
| Control Flow Graph | "A graph representation of all execution paths through a function" |
| Branch Coverage (Level 2) | "Every decision branch (True and False) is executed at least once" |
| Data Flow / DU Cycle | "Tracking a variable from its definition to each use and out of scope" |
| Software Fault | "A defect in the code that may or may not cause a failure" |
| Software Failure | "A fault that has been activated during execution" |
| SQA | "A systematic, planned set of actions to provide confidence that software conforms to requirements" |
| Quality Factor | "A non-functional attribute of software quality (correctness, reliability, usability, etc.)" |

### Anticipated Technical Questions & Suggested Answers

**Q: Why did you choose EP over testing every possible input?**
> "EP exploits the fact that all inputs within a partition trigger the same code path and produce equivalent results. Testing one representative is logically sufficient, and testing all values would be practically infeasible."

**Q: What is the difference between BVA and EP?**
> "EP identifies the classes; BVA focuses specifically on the edges between classes. An off-by-one error at a boundary would pass EP but fail BVA — they are complementary, not interchangeable."

**Q: Why do you need branch coverage and not just statement coverage?**
> "Statement coverage (Level 1) only requires that each line executes at least once. A condition that is always True would achieve full statement coverage but never test the False branch. Branch Coverage Level 2 closes that gap."

**Q: What does the DU analysis prove?**
> "It proves there are no use-before-definition errors or dead code (defined but never used). This is especially important in a loop-heavy matching algorithm where variables are modified across iterations."

**Q: How does your SQA plan integrate into the development lifecycle?**
> "SQA activities are mapped to each phase: the coding standards apply during implementation, peer review and walkthroughs occur at phase transitions, and the test plan executes after implementation. Defects found at any stage feed back into the defect log rather than being silently ignored."

---

## Presentation Structure (Suggested 10–15 min)

1. **Project Overview** (1–2 min): What the system does, key testable features.
2. **SQA Plan** (2–3 min): Quality objectives, 6 standards areas, lifecycle integration.
3. **Black Box Testing** (3–4 min): EP partitions + BVA tables for matching, group size, conflict detection.
4. **White Box Testing** (3–4 min): CFG diagram, branch coverage table, DU cycle for `eligible`.
5. **Q&A Readiness** (ongoing): Use terminology above; be specific, not vague.
