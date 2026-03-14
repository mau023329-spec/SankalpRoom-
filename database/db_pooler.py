"""
SankalpRoom - Database Layer (Supabase / Postgres)
Reads the full DB connection string directly from secrets — most reliable approach.
"""

import os
import re
import streamlit as st
import psycopg2
import psycopg2.extras


# ── Connection ────────────────────────────────────────────────────────────────

def _secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")


def get_connection():
    """
    Connect using the full DATABASE_URL from secrets.
    Get this from: Supabase → Settings → Database → Connection string → URI
    Make sure to select "Transaction pooler" mode.
    """
    db_url = _secret("DATABASE_URL").strip()

    if not db_url:
        # Fallback: build from components
        url = _secret("SUPABASE_URL").strip().rstrip("/")
        pwd = _secret("SUPABASE_DB_PASSWORD").strip()
        ref = url.replace("https://", "").split(".")[0]
        db_url = f"postgresql://postgres.{ref}:{pwd}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

    conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    """Tables live in Supabase — nothing to create locally."""
    pass


# ── SQLite → Postgres translation ─────────────────────────────────────────────

def _to_pg(query: str) -> str:
    result = []
    for ch in query:
        result.append("%s" if ch == "?" else ch)
    query = "".join(result)
    query = re.sub(r"datetime\('now'\)", "NOW()", query, flags=re.IGNORECASE)
    return query


# ── Generic helpers ───────────────────────────────────────────────────────────

def fetchall(query: str, params=()):
    query = _to_pg(query)
    conn  = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetchone(query: str, params=()):
    query = _to_pg(query)
    conn  = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute(query: str, params=()):
    query     = _to_pg(query)
    q_upper   = query.strip().upper()
    is_insert = q_upper.startswith("INSERT")

    if is_insert and "RETURNING" not in q_upper:
        query = query.rstrip("; ") + " RETURNING id"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            last_id = None
            if is_insert:
                row     = cur.fetchone()
                last_id = row["id"] if row else None
        conn.commit()
        return last_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
