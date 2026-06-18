import sqlite3
from pathlib import Path

from src import SQL_DB_PATH


class DB:
    _conn: sqlite3.Connection

    def __init__(self, file_path: Path = SQL_DB_PATH) -> None:
        self._conn = sqlite3.connect(file_path, check_same_thread=False)

    def init(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                [id] TEXT PRIMARY KEY,
                [present] INTEGER
            )
            """
        )

    def get_attendance(self, id: str):
        self._conn.row_factory = sqlite3.Row

        cur = self._conn.cursor()

        cur.execute(
            """
            SELECT * FROM student
            LEFT JOIN attendance ON student.id = attendance.id
            WHERE student.id = ?;
            """,
            (id,),
        )

        rows = cur.fetchall()

        return dict(rows[0])

    def get_attendance_report(self):
        self._conn.row_factory = sqlite3.Row

        cur = self._conn.cursor()

        cur.execute(
            """
            SELECT * FROM student
            LEFT JOIN attendance ON student.id = attendance.id
            """
        )

        rows = cur.fetchall()
        lst = [dict(row) for row in rows]

        return lst

    def set_attendance(self, id: str, present: bool):
        cur = self._conn.cursor()

        cur.execute(
            """
            INSERT INTO attendance (id, present)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET present = excluded.present;
            """,
            (id, present),
        )
        self._conn.commit()
