"""
SankalpRoom - Database Layer
SQLite database initialization and helper functions.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sankalproom.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_color TEXT DEFAULT '#4F46E5',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Rooms
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            invite_code TEXT UNIQUE NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Room members
    c.execute("""
        CREATE TABLE IF NOT EXISTS room_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TEXT DEFAULT (datetime('now')),
            UNIQUE(room_id, user_id),
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Subgroups
    c.execute("""
        CREATE TABLE IF NOT EXISTS subgroups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#4F46E5',
            created_by INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Subgroup members
    c.execute("""
        CREATE TABLE IF NOT EXISTS subgroup_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subgroup_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TEXT DEFAULT (datetime('now')),
            UNIQUE(subgroup_id, user_id),
            FOREIGN KEY (subgroup_id) REFERENCES subgroups(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Messages (room chat)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_ai BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Subgroup messages
    c.execute("""
        CREATE TABLE IF NOT EXISTS subgroup_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subgroup_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_ai BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (subgroup_id) REFERENCES subgroups(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Ideas
    c.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open',
            ai_analysis TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Votes
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(idea_id, user_id),
            FOREIGN KEY (idea_id) REFERENCES ideas(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Reactions
    c.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            emoji TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(message_id, user_id, emoji),
            FOREIGN KEY (message_id) REFERENCES messages(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tasks
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subgroup_id INTEGER NOT NULL,
            idea_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            assigned_to INTEGER,
            deadline TEXT,
            created_by INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (subgroup_id) REFERENCES subgroups(id),
            FOREIGN KEY (idea_id) REFERENCES ideas(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Direct messages
    c.execute("""
        CREATE TABLE IF NOT EXISTS direct_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_dm_pair ON direct_messages(sender_id, receiver_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dm_receiver ON direct_messages(receiver_id, is_read)")

    conn.commit()
    conn.close()


# ── Generic helpers ──────────────────────────────────────────────────────────

def fetchall(query: str, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetchone(query: str, params=()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None


def execute(query: str, params=()):
    conn = get_connection()
    cursor = conn.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id
