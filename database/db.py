"""
SankalpRoom - Database Layer (Supabase / Postgres)
Keeps identical fetchone / fetchall / execute API so no other file needs changing.
"""

import os
import re
import streamlit as st
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse


# ── Connection ────────────────────────────────────────────────────────────────

def _get_conn_params() -> dict:
    """Build psycopg2 connection kwargs from Supabase secrets."""
    url = (getattr(st.secrets, "get", lambda k, d=None: d)("SUPABASE_URL")
           or os.environ.get("SUPABASE_URL", "")).strip()
    pwd = (getattr(st.secrets, "get", lambda k, d=None: d)("SUPABASE_DB_PASSWORD")
           or os.environ.get("SUPABASE_DB_PASSWORD", "")).strip()

    if not url:
        raise RuntimeError("SUPABASE_URL not set in secrets or environment.")

    parsed = urlparse(url)
    ref    = parsed.hostname.split(".")[0]   # e.g. pwnfxajwyinamvqegcms

    return dict(
        host     = f"db.{ref}.supabase.co",
        port     = 5432,
        dbname   = "postgres",
        user     = "postgres",
        password = pwd,
        sslmode  = "require",
    )


def get_connection():
    params = _get_conn_params()
    conn   = psycopg2.connect(**params, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


# ── No-op init (tables already created in Supabase SQL editor) ────────────────

def init_db():
    """Tables live in Supabase — nothing to create locally."""
    pass


# ── SQLite → Postgres translation ─────────────────────────────────────────────

def _to_pg(query: str) -> str:
    """Convert SQLite syntax to Postgres."""
    # ? → %s
    result = []
    for ch in query:
        result.append("%s" if ch == "?" else ch)
    query = "".join(result)
    # datetime('now') → NOW()
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
    """
    Run INSERT / UPDATE / DELETE.
    Returns inserted row id for INSERTs, None otherwise.
    """
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
