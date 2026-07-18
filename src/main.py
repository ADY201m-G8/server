import os
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import Client, create_client

load_dotenv()


origins = [
    "http://localhost:3000",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL", default=""),
    os.environ.get("SUPABASE_KEY", default=""),
)


class Student(BaseModel):
    id: str
    name: str


class Lesson(BaseModel):
    subject_id: str
    room_id: str
    date: str
    slot: int


class Attendance(BaseModel):
    lesson_id: int
    student_id: str
    present: bool = False


class ScanAttendance(BaseModel):
    student_id: str
    room_id: str
    timestamp: int  # unix timestamp
    present: bool = True


SLOT_RANGES = {
    1: (time(7, 30), time(9, 50)),
    2: (time(10, 10), time(12, 20)),
    3: (time(12, 50), time(15, 10)),
    4: (time(15, 20), time(17, 40)),
}


@app.get("/")
def read_root():
    return FileResponse("src/index.html")


@app.get("/students")
def get_students():
    result = supabase.table("students").select("*").execute()
    return result.data


@app.get("/subjects")
def get_subjects():
    result = supabase.table("subjects").select("*").execute()
    return result.data


@app.get("/rooms")
def get_rooms():
    result = supabase.table("rooms").select("*").execute()
    return result.data


@app.get("/enrollments")
def get_enrollments(
    student_id: str | None = Query(default=None),
    subject_id: str | None = Query(default=None),
):
    query = supabase.table("enrollments").select("*")
    if student_id:
        query = query.eq("student_id", student_id)
    if subject_id:
        query = query.eq("subject_id", subject_id)
    result = query.execute()
    return result.data


@app.get("/lessons")
def get_lessons(
    subject_id: str | None = Query(default=None),
    date: str | None = Query(default=None),
):
    query = supabase.table("lessons").select("*")
    if subject_id:
        query = query.eq("subject_id", subject_id)
    if date:
        query = query.eq("date", date)
    result = query.execute()
    return result.data


@app.post("/lessons")
def createLesson(lesson: Lesson):
    result = supabase.table("lessons").insert(lesson.model_dump()).execute()
    return result.data[0]


@app.post("/students")
def create_student(student: Student):
    result = supabase.table("students").insert(student.model_dump()).execute()
    return result.data[0]


@app.get("/attendances")
def get_attendances(
    lesson_id: int = Query(...), student_id: str | None = Query(default=None)
):
    query = supabase.table("attendances").select("*").eq("lesson_id", lesson_id)
    if student_id:
        query = query.eq("student_id", student_id)
    result = query.execute()
    return result.data


@app.post("/attendances")
def create_attendance(attendance: Attendance):
    result = supabase.table("attendances").upsert(attendance.model_dump()).execute()
    return result.data[0]


@app.post("/attendances/scan")
def scan_attendance(scan: ScanAttendance):
    dt = datetime.fromtimestamp(scan.timestamp, tz=ZoneInfo("Asia/Ho_Chi_Minh"))
    current_time = dt.time()
    current_date = dt.strftime("%Y-%m-%d")

    matched_slot = None
    for slot, (start, end) in SLOT_RANGES.items():
        if start <= current_time <= end:
            matched_slot = slot
            break

    print(f"Time: {current_time} | Matched slot: {matched_slot}")

    if matched_slot is None:
        raise HTTPException(
            status_code=404, detail="No active lesson slot for this time"
        )

    lessons = (
        supabase.table("lessons")
        .select("*")
        .eq("room_id", scan.room_id)
        .eq("date", current_date)
        .eq("slot", matched_slot)
        .execute()
        .data
    )

    if not lessons:
        raise HTTPException(
            status_code=404, detail="No lesson found for this room at this time"
        )

    lesson = lessons[0]
    result = (
        supabase.table("attendances")
        .upsert(
            {
                "lesson_id": lesson["id"],
                "student_id": scan.student_id,
                "present": scan.present,
            }
        )
        .execute()
    )
    return result.data[0]
