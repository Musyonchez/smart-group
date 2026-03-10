# SQA Plan – Smart Study Group Matching System

## Quality Objectives

The SQA Plan for the Smart Study Group Matching System aims to:

1. Assure the system correctly matches students into balanced study groups based on shared courses, difficulty topics, and time availability.
2. Prevent students from being assigned to two groups at the same time (no scheduling conflicts).
3. Ensure the system handles edge cases (odd student counts, no available matches, high user load) without failure.
4. Maintain correctness, reliability, usability, and testability as primary quality factors (McCall's model).

---

## 1. Coding Standards

- Language: Python (backend logic), with clear module separation (matching engine, scheduler, participation tracker).
- Functions must be single-responsibility; maximum function length: 30 lines.
- Naming convention: `snake_case` for variables and functions, `PascalCase` for classes.
- All functions that implement matching or conflict-detection logic must have inline comments explaining the decision logic.
- No hardcoded values — configuration (group size limits, time slot formats) must use constants or config files.
- Version control: all changes committed via Git with descriptive commit messages.

---

## 2. Database Design Standards

- Student profile table must store: student ID, enrolled courses (list), weak topics (list), available time slots (list).
- Group table must store: group ID, course, member IDs, assigned time slot, status.
- No student ID may appear in two group records with the same time slot (enforced at DB level via constraint).
- All tables must have primary keys and appropriate foreign key relationships.
- Time slots stored in standardized format: `DAY-HH:MM` (e.g., `MON-09:00`).
- Data must be normalized to at least 3NF to avoid redundancy.

---

## 3. GUI Design Standards

- Student registration form must display all available courses from a predefined list (dropdown/checkbox) — no free-text course entry.
- Weak topics must be selectable only from topics relevant to the chosen courses.
- Available time slots presented as a weekly grid (days × time blocks); student selects multiple slots.
- After matching, the system displays the assigned group clearly: group members, shared course, scheduled time.
- Error messages must be meaningful (e.g., "No students available for COMP101 on Monday 9:00 — try adding more time slots").
- UI must be consistent in layout, fonts, and color scheme across all screens.

---

## 4. Testing & Test Case Design Standards

- All test cases must follow the format: **Test ID | Input | Expected Output | Actual Output | Pass/Fail**.
- Black box testing must use **Equivalence Partitioning (EP)** and **Boundary Value Analysis (BVA)** — see `3-black-box-testing.md`.
- White box testing must use **Control Flow Graph (CFG)** and achieve **Branch Coverage (Level 2)** — see `4-white-box-testing.md`.
- Every `if` statement in the matching and conflict-detection modules must have at least one test case where the condition is `True` and one where it is `False`.
- Every loop must be tested with: 0 iterations (skip), 1 iteration, multiple iterations.
- Test cases must be traceable to requirements (each test references the feature it validates).
- Defects found during testing must be logged with: severity, description, steps to reproduce, and resolution status.

---

## 5. Review Standards

- **Peer Review**: Each module (matching engine, scheduler, tracker) reviewed by at least one other team member before integration. Reviewer must check logic correctness, adherence to coding standards, and edge case handling.
- **Walkthrough**: Before each testing phase, the team walks through the test plan together to confirm completeness and coverage.
- **Formal Review Checklist** items:
  - [ ] All requirements are covered by at least one test case.
  - [ ] No student can appear in two simultaneously-scheduled groups.
  - [ ] Odd-number student edge case is handled.
  - [ ] Boundary conditions (min/max group size) are tested.
  - [ ] Code meets naming and length standards.
- Reviews are logged with date, participants, findings, and action items.

---

## 6. Organizational Process Reference

- This SQA plan aligns with the **IEEE definition of SQA**: a systematic, planned set of actions to provide confidence that the software development process conforms to established functional and technical requirements.
- Development follows a phased approach: Requirements → Design → Implementation → Testing → Review.
- SQA activities are scheduled alongside development milestones — not treated as optional add-ons.
- Quality factors applied (McCall's model):
  - **Correctness**: matching output verified against defined rules.
  - **Reliability**: system must not crash on odd student counts or empty inputs.
  - **Usability**: students can complete registration and view group assignment without confusion.
  - **Testability**: modules are structured to allow independent unit testing.
  - **Maintainability**: code is modular and documented for future changes.
