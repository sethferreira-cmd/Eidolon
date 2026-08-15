"""
EIDOLON database layer.

Uses plain sqlite3 (no ORM) so the project has zero extra runtime
dependencies and the schema is easy to audit. The DB file lives at
backend/eidolon.db and is created automatically on first import.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "eidolon.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'ollama',
    detected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompts (
    id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    category TEXT NOT NULL,
    template TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    baseline TEXT NOT NULL,
    variant TEXT NOT NULL,
    condition TEXT NOT NULL,
    transformation_percentage INTEGER NOT NULL,
    model TEXT NOT NULL,
    blind_condition INTEGER NOT NULL DEFAULT 0,
    trial_count INTEGER NOT NULL,
    random_seed INTEGER,
    prompt_version TEXT,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    trial_index INTEGER NOT NULL,
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    perspective TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);

CREATE TABLE IF NOT EXISTS responses (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    raw_response TEXT,
    parsed_json TEXT,
    parse_failed INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS scores (
    id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    run_id TEXT,
    same_entity INTEGER,
    identity_score REAL,
    confidence REAL,
    primary_identity_property TEXT,
    reason TEXT,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id),
    FOREIGN KEY (run_id) REFERENCES runs(id)
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


def dumps(obj) -> str:
    return json.dumps(obj, default=str)
