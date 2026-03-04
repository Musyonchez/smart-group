# 1. Project Overview

## Smart Study Group Matching System

A web-based system that automatically forms balanced study groups based on students' enrolled courses, self-reported strengths/weaknesses, and available time slots.

---

## Problem Statement

Students struggle to find suitable study partners who share the same subjects, can cover topics they are weak in, and are available at the same times. Manual coordination is inefficient and often results in unbalanced groups.

---

## Core Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Student Registration | Students register with their name and email |
| 2 | Profile Setup | Select units, strong topics, weak topics, and available time slots |
| 3 | Group Matching | System matches students into groups of 2–4 based on shared units and complementary strengths |
| 4 | Schedule Suggestion | System suggests a meeting time based on overlapping availability |
| 5 | Conflict Detection | Prevents a student from being assigned to two groups with overlapping times |
| 6 | Participation Tracking | Records attendance/participation per session |

---

## Actors

- **Student** — registers, sets up profile, views assigned group and schedule
- **System** — runs matching algorithm, detects conflicts, suggests schedules

---

## Functional Requirements

- FR1: A student must select at least one unit to be eligible for matching
- FR2: A student can only belong to one group per unit
- FR3: Groups must contain students enrolled in the same unit
- FR4: Groups must have at least one overlapping available time slot
- FR5: No two groups assigned to the same student may share a time slot
- FR6: Groups are sized between 2 and 4 students
- FR7: Odd-numbered student pools must still be handled (no student left unassigned if avoidable)

## Non-Functional Requirements

- NFR1: Matching must complete within 3 seconds for up to 500 students
- NFR2: System must handle concurrent profile submissions without data corruption
- NFR3: Student data must not be exposed to other students

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python (Flask) |
| Data Storage | JSON flat files (or SQLite) |
| Testing | pytest |
| Frontend | Simple HTML form (out of scope for testing) |

---

## Constraints & Assumptions

- A student may enrol in multiple units but is matched per unit independently
- Time slots are discrete (e.g., Mon 9–11am, Tue 2–4pm)
- Group size preference: 3 students; min 2, max 4
- A student with no overlapping availability with anyone else in their unit is flagged as "unmatched"
