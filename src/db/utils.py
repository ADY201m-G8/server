import sqlite3
from typing import Any, Dict


def table_to_dict_by_id(
    conn: sqlite3.Connection, table_name: str
) -> Dict[Any, Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    dictionary = {}
    for row in rows:
        row_dict = dict(row)

        if "id" in row_dict:
            row_id = row_dict.pop("id")
            dictionary[row_id] = row_dict
        else:
            raise KeyError(f"The table '{table_name}' does not contain an 'id' column.")

    return dictionary
