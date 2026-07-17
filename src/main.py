import os

from dotenv import load_dotenv
from fastapi import FastAPI
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


@app.get("/")
def read_root():
    return {"message": "API port for ADY201m project."}
