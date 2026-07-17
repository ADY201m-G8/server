import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
def read_root():
    return {"message": "API port for ADY201m project."}


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
def get_attendances(lesson_id: int = Query(...)):
    result = supabase.table("attendances").select("*").eq("lesson_id", lesson_id).execute()
    return result.data


@app.post("/attendances")
def create_attendance(attendance: Attendance):
    result = supabase.table("attendances").insert(attendance.model_dump()).execute()
    return result.data[0]
