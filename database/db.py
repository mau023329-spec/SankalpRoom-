"""
SankalpRoom - Database Layer (Supabase / Postgres)
ThreadedConnectionPool — reuses connections instead of opening a new TCP
handshake on every query. Cuts per-page latency significantly.
"""

import os
import re
import atexit
import streamlit as st
import psycopg2
import psycopg2.extras
import psycopg2.pool


_pool: "psycopg2.pool.ThreadedConnectionPool | None" = None


def _secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")


def _build_db_url() -> str:
    db_url = _secret("DATABASE_URL").strip()
    if db_url:
        return db_url
    url = _secret("SUPABASE_URL").strip().rstrip("/")
    pwd = _secret("SUPABASE_DB_PASSWORD").strip()
    ref = url.replace("https://", "").split(".")[0]
    return (
        f"postgresql://postgres.{ref}:{pwd}"
        f"@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    )


def _get_pool() -> "psycopg2.pool.ThreadedConnectionPool":
    global _pool
    if _pool is None or _pool.closed:
        db_url = _build_db_url()
        _pool  = psycopg2.pool.ThreadedConnectionPool(
            minconn = 2,
            maxconn = 10,
            dsn     = db_url,
            cursor_factory = psycopg2.extras.RealDictCursor,
        )
        atexit.register(_pool.closeall)
    return _pool


def get_connection():
    return _get_pool().getconn()


def _return(conn, bad=False):
    try:
        _get_pool().putconn(conn, close=bad)
    except Exception:
        pass


def init_db():
    """Warm up the pool on startup so the first request is instant."""
    try:
        conn = get_connection()
        _return(conn)
    except Exception:
        pass


# ── SQLite → Postgres ─────────────────────────────────────────────────────────

def _to_pg(query: str) -> str:
    result = ["%" + "s" if ch == "?" else ch for ch in query]
    # simpler: just replace ? with %s
    q = query.replace("?", "%s")
    q = re.sub(r"datetime\('now'\)", "NOW()", q, flags=re.IGNORECASE)
    return q


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetchall(query: str, params=()):
    q    = _to_pg(query)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(q, params)
            rows = cur.fetchall()
        _return(conn)
        return [dict(r) for r in rows]
    except Exception:
        _return(conn, bad=True)
        raise


def fetchone(query: str, params=()):
    q    = _to_pg(query)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(q, params)
            row = cur.fetchone()
        _return(conn)
        return dict(row) if row else None
    except Exception:
        _return(conn, bad=True)
        raise


def execute(query: str, params=()):
    q         = _to_pg(query)
    q_upper   = q.strip().upper()
    is_insert = q_upper.startswith("INSERT")

    if is_insert and "RETURNING" not in q_upper:
        q = q.rstrip("; ") + " RETURNING id"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(q, params)
            last_id = None
            if is_insert:
                row     = cur.fetchone()
                last_id = row["id"] if row else None
        conn.commit()
        _return(conn)
        return last_id
    except Exception:
        conn.rollback()
        _return(conn, bad=True)
        raise
