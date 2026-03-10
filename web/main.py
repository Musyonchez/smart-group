"""
Smart Study Group Matching System – Web UI
Run: uvicorn web.main:app --reload
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys, os

# Make sure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Group, Student, Session
from src.matcher import match_students, reset_group_counter
from src.tracker import record_session, get_group_report, reset_session_counter
from src.scheduler import generate_schedule

app = FastAPI(title="Smart Study Group Matching System")

BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

# ── In-memory store ──────────────────────────────────────────────────────────
_students: list[Student] = []
_groups:   list[Group]   = []
_sessions: list[Session] = []


def _reset_all():
    global _students, _groups, _sessions
    _students, _groups, _sessions = [], [], []
    reset_group_counter()
    reset_session_counter()


def _seed():
    """Pre-load demo data so the presenter isn't typing during demo."""
    _reset_all()
    data = [
        ("S1", "Alice",   ["COMP101", "MATH201"], ["Recursion"],        ["MON-09:00", "WED-14:00"]),
        ("S2", "Bob",     ["COMP101"],             ["Sorting"],          ["MON-09:00", "FRI-10:00"]),
        ("S3", "Carol",   ["COMP101", "MATH201"],  ["Graphs"],           ["MON-09:00"]),
        ("S4", "Dan",     ["COMP101"],             ["Recursion","Trees"],["WED-14:00", "FRI-10:00"]),
        ("S5", "Eve",     ["MATH201"],              ["Integration"],      ["MON-09:00", "WED-14:00"]),
        ("S6", "Frank",   ["COMP101"],             [],                   ["MON-09:00"]),
        ("S7", "Grace",   ["COMP101", "MATH201"],  ["Sorting"],          ["FRI-10:00"]),
        ("S8", "Hank",    ["MATH201"],              ["Derivatives"],      ["WED-14:00"]),
    ]
    for sid, name, courses, weak, slots in data:
        _students.append(Student(id=sid, name=name, courses=courses,
                                 weak_topics=weak, available_slots=slots))


_seed()  # seed on startup


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, msg: str = ""):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "students": _students,
        "groups": _groups,
        "sessions": _sessions,
        "schedule": generate_schedule(_groups),
        "msg": msg,
    })


# -- Students -----------------------------------------------------------------

@app.post("/students/add")
async def add_student(
    sid:    str = Form(...),
    name:   str = Form(...),
    courses: str = Form(...),   # comma-separated
    weak:   str = Form(""),
    slots:  str = Form(...),    # comma-separated
):
    if any(s.id == sid for s in _students):
        return RedirectResponse(f"/?msg=ID+{sid}+already+exists", status_code=303)
    _students.append(Student(
        id=sid, name=name,
        courses=[c.strip() for c in courses.split(",") if c.strip()],
        weak_topics=[w.strip() for w in weak.split(",") if w.strip()],
        available_slots=[s.strip() for s in slots.split(",") if s.strip()],
    ))
    return RedirectResponse(f"/?msg=Student+{name}+added", status_code=303)


@app.post("/students/delete")
async def delete_student(sid: str = Form(...)):
    global _students
    _students = [s for s in _students if s.id != sid]
    return RedirectResponse("/?msg=Student+removed", status_code=303)


# -- Matching -----------------------------------------------------------------

@app.post("/match")
async def match(
    course:    str = Form(...),
    slot:      str = Form(...),
    groupsize: int = Form(3),
):
    result = match_students(_students, course, slot, groupsize)
    _groups.extend(result.groups)
    waitlisted = ", ".join(s.name for s in result.waitlisted) or "none"
    msg = f"{len(result.groups)}+group(s)+formed.+Waitlisted:+{waitlisted}"
    return RedirectResponse(f"/?msg={msg}", status_code=303)


@app.post("/match/reset")
async def reset_match():
    global _groups, _sessions
    _groups, _sessions = [], []
    reset_group_counter()
    reset_session_counter()
    # clear assigned_groups on students
    for s in _students:
        s.assigned_groups = []
    return RedirectResponse("/?msg=Groups+and+sessions+cleared", status_code=303)


# -- Sessions -----------------------------------------------------------------

@app.post("/sessions/record")
async def record(
    group_id:    str = Form(...),
    date:        str = Form(...),
    attendee_ids: str = Form(""),   # comma-separated
):
    group = next((g for g in _groups if g.id == group_id), None)
    if not group:
        return RedirectResponse("/?msg=Group+not+found", status_code=303)
    ids = [i.strip() for i in attendee_ids.split(",") if i.strip()]
    session = record_session(group, date, ids)
    _sessions.append(session)
    return RedirectResponse(f"/?msg=Session+{session.id}+recorded", status_code=303)


# -- Reports ------------------------------------------------------------------

@app.get("/report/group/{group_id}", response_class=HTMLResponse)
async def group_report(request: Request, group_id: str):
    group = next((g for g in _groups if g.id == group_id), None)
    if not group:
        return RedirectResponse("/?msg=Group+not+found")
    report = get_group_report(group, _sessions)
    return templates.TemplateResponse("report.html", {
        "request": request,
        "group": group,
        "report": report,
    })


# -- Demo reset ---------------------------------------------------------------

@app.post("/demo/reset")
async def demo_reset():
    _seed()
    return RedirectResponse("/?msg=Demo+data+reloaded", status_code=303)
