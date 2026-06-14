import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

from src.utils import compress_chroma_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/chromadb")
def get_chroma_db_archive():
    file_path = compress_chroma_db()

    return FileResponse(
        path=file_path,
        media_type="application/x-xz",
        filename=os.path.basename(file_path),
    )
