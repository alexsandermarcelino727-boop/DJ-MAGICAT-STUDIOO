from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DB_DIR / "magicat_studio.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "data" / "schema.sql"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_DIR.mkdir(exist_ok=True)
    if not DB_PATH.exists():
        conn = _connect()
        with SCHEMA_PATH.open("r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
    else:
        conn = _connect()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tracks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, bpm INTEGER NOT NULL, genre TEXT DEFAULT 'Electronic', magic_effect TEXT DEFAULT 'laser_smoke');"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS studio_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, description TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP);"
        )
        if conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO tracks (title, bpm, genre, magic_effect) VALUES (?, ?, ?, ?)",
                [
                    ("Cyber Purr", 128, "Synthwave", "laser_smoke"),
                    ("Neon Illusion", 132, "Electro House", "hat_trick_scratch"),
                    ("Mystic Beats", 124, "Deep House", "meow_echo"),
                ],
            )
            conn.commit()
        conn.close()


def get_tracks() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM tracks ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_events(limit: int = 10) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT event_type, description, timestamp FROM studio_events ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def trigger_effect(effect_name: str) -> dict:
    effect = (effect_name or "laser_smoke").strip()
    effects = {
        "laser_smoke": "Laser Smoke",
        "hat_trick_scratch": "Hat Trick Scratch",
        "meow_echo": "Meow Echo",
        "neon_flip": "Neon Flip",
    }
    label = effects.get(effect, effect.replace("_", " ").title())

    conn = _connect()
    conn.execute(
        "INSERT INTO studio_events (event_type, description) VALUES (?, ?)",
        ("EFFECT_TRIGGERED", f"Efeito '{label}' processado pelo motor do estúdio."),
    )
    conn.commit()
    conn.close()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "success",
        "effect": effect,
        "label": label,
        "message": f"{label} ativado com sucesso. Mangueira de som sincronizada.",
        "timestamp": timestamp,
    }
