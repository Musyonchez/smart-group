# 2. System Design

## Data Models

### Student
```
Student {
  id:           string
  name:         string
  email:        string
  units:        list[string]         # e.g., ["CS101", "MATH201"]
  strong:       list[string]         # topics student is confident in
  weak:         list[string]         # topics student needs help with
  availability: list[TimeSlot]
}
```

### TimeSlot
```
TimeSlot {
  day:   string   # "Mon", "Tue", ...
  start: int      # 24h hour, e.g., 9
  end:   int      # 24h hour, e.g., 11
}
```

### StudyGroup
```
StudyGroup {
  id:           string
  unit:         string
  members:      list[Student.id]
  meeting_slot: TimeSlot
}
```

---

## Matching Algorithm

The algorithm runs per unit independently.

```
function match_unit(unit, students):

  1. Filter students enrolled in `unit`
  2. Build availability overlap graph:
       - Two students are "compatible" if they share >= 1 time slot
  3. Greedy grouping:
       a. Sort students by number of compatible peers (ascending — harder to place first)
       b. For each unassigned student:
          - Find compatible unassigned students
          - Form group of size 2–4
          - Pick the time slot shared by all members
  4. Balance strength/weakness:
       - Prefer groups where at least one member is strong in a topic
         another member is weak in
  5. Conflict check:
       - After assigning a meeting_slot, verify no member already has
         a group scheduled at that slot
  6. Return list[StudyGroup]
```

---

## Key Constraints Enforced

| Constraint | Where Enforced |
|------------|---------------|
| Same unit | Step 1 filter |
| Time overlap | Steps 2 & 3 |
| Group size 2–4 | Step 3b |
| No time conflict across groups | Step 5 |
| Odd student handling | Step 3b — last lone student joins smallest compatible group if size < 4 |

---

## Component Overview

```
┌─────────────────────────────────────┐
│            Flask API                │
│  POST /register                     │
│  POST /profile                      │
│  GET  /match/{unit}                 │
│  GET  /groups/{student_id}          │
└──────────────┬──────────────────────┘
               │
       ┌───────▼───────┐
       │  Matcher      │  core matching logic
       └───────┬───────┘
               │
       ┌───────▼───────┐
       │  Data Store   │  students.json / groups.json
       └───────────────┘
```

---

## Edge Cases

| Scenario | Handling |
|----------|---------|
| 0 students in unit | Return empty group list |
| 1 student in unit | Mark as "unmatched — waiting" |
| No shared time slot between any students | Mark all as unmatched |
| All students same availability, same strengths | Form groups by size only |
