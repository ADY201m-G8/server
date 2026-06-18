import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.db import DB
from src.utils import compress_chroma_db


class AttendanceReportItem(BaseModel):
    id: str
    fullname: str
    present: bool


app = FastAPI()
db = DB()
db.init()


@app.get("/")
def read_root():
    return {"message": "API port for ADY201m project."}


@app.get("/chromadb")
def get_chroma_db_archive():
    file_path = compress_chroma_db()

    return FileResponse(
        path=file_path,
        media_type="application/x-xz",
        filename=os.path.basename(file_path),
    )


@app.get("/attendance")
async def get_attendance_report():
    rows = db.get_attendance_report()
    return JSONResponse(rows)


@app.get("/attendance/{id}")
async def get_attendance(id: str):
    id = id.upper()
    row = db.get_attendance(id)
    return JSONResponse(row)


@app.post("/attendance/{id}")
def set_attendance(id: str, present: bool):
    id = id.upper()
    db.set_attendance(id, present)
