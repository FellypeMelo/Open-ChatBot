#!/usr/bin/env python3
"""Clears all runtime data — SQLite rows + ChromaDB vector stores.

Usage: python scripts/reset_data.py
Run from the project root directory.
"""

import sqlite3
import shutil
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "chatbot.db"
CHROMA_PATHS = ["chroma_db", "chroma_db_old"]

TABLES_IN_ORDER = [
    "messages",
    "agent_states",
    "character_tags",
    "characters",
    "users",
    "tags",
]


def reset_sqlite(db_path: Path) -> None:
    if not db_path.exists():
        print(f"  SQLite database not found at {db_path}, skipping.")
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    for table in TABLES_IN_ORDER:
        cur.execute(f"DELETE FROM {table}")
        count = cur.rowcount
        print(f"  Cleared {count} row(s) from '{table}'")
    conn.commit()
    conn.close()
    print(f"  All tables cleared in {db_path}")


def reset_chroma(paths: list[str]) -> None:
    for name in paths:
        p = PROJECT_ROOT / name
        if p.exists():
            shutil.rmtree(p)
            print(f"  Removed {name}/")
        else:
            print(f"  {name}/ not found, skipping.")


def main() -> None:
    print("Open-ChatBot Data Reset")
    print("=" * 40)
    reset_sqlite(DB_PATH)
    reset_chroma(CHROMA_PATHS)
    print("=" * 40)
    print("Done. Data will be recreated on next server startup.")


if __name__ == "__main__":
    main()
