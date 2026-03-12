"""
SankalpRoom - Rooms Module
Room creation, joining, and management.
"""

import secrets
import streamlit as st
from database.db import fetchone, fetchall, execute


# ── Room CRUD ─────────────────────────────────────────────────────────────────

def create_room(name: str, description: str, user_id: int) -> dict:
    invite_code = secrets.token_urlsafe(8).upper()
    room_id = execute(
        "INSERT INTO rooms (name, description, invite_code, created_by) VALUES (?, ?, ?, ?)",
        (name, description, invite_code, user_id),
    )
    execute(
        "INSERT INTO room_members (room_id, user_id, role) VALUES (?, ?, 'admin')",
        (room_id, user_id),
    )
    return fetchone("SELECT * FROM rooms WHERE id = ?", (room_id,))


def join_room(invite_code: str, user_id: int):
    room = fetchone("SELECT * FROM rooms WHERE invite_code = ?", (invite_code.upper(),))
    if not room:
        return None, "Invalid invite code."
    existing = fetchone(
        "SELECT id FROM room_members WHERE room_id = ? AND user_id = ?",
        (room["id"], user_id),
    )
    if existing:
        return room, "already_member"
    execute(
        "INSERT INTO room_members (room_id, user_id) VALUES (?, ?)",
        (room["id"], user_id),
    )
    return room, None


def get_user_rooms(user_id: int):
    return fetchall("""
        SELECT r.*, rm.role,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) as member_count
        FROM rooms r
        JOIN room_members rm ON r.id = rm.room_id
        WHERE rm.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))


def get_room(room_id: int):
    return fetchone("SELECT * FROM rooms WHERE id = ?", (room_id,))


def get_room_members(room_id: int):
    return fetchall("""
        SELECT u.id, u.name, u.email, u.avatar_color, rm.role
        FROM users u
        JOIN room_members rm ON u.id = rm.user_id
        WHERE rm.room_id = ?
        ORDER BY rm.joined_at
    """, (room_id,))


# ── Subgroup CRUD ─────────────────────────────────────────────────────────────

SUBGROUP_COLORS = ["#4F46E5", "#8B5CF6", "#EC4899", "#06B6D4", "#22C55E", "#F59E0B", "#EF4444"]


def create_subgroup(room_id: int, name: str, description: str, user_id: int) -> dict:
    color = SUBGROUP_COLORS[hash(name) % len(SUBGROUP_COLORS)]
    sg_id = execute(
        "INSERT INTO subgroups (room_id, name, description, color, created_by) VALUES (?, ?, ?, ?, ?)",
        (room_id, name, description, color, user_id),
    )
    execute(
        "INSERT INTO subgroup_members (subgroup_id, user_id) VALUES (?, ?)",
        (sg_id, user_id),
    )
    return fetchone("SELECT * FROM subgroups WHERE id = ?", (sg_id,))


def get_room_subgroups(room_id: int):
    return fetchall("""
        SELECT s.*,
               (SELECT COUNT(*) FROM subgroup_members WHERE subgroup_id = s.id) as member_count,
               (SELECT COUNT(*) FROM tasks WHERE subgroup_id = s.id) as task_count
        FROM subgroups s
        WHERE s.room_id = ?
        ORDER BY s.created_at
    """, (room_id,))


def get_subgroup(sg_id: int):
    return fetchone("SELECT * FROM subgroups WHERE id = ?", (sg_id,))


def get_subgroup_members(sg_id: int):
    return fetchall("""
        SELECT u.id, u.name, u.email, u.avatar_color
        FROM users u
        JOIN subgroup_members sm ON u.id = sm.user_id
        WHERE sm.subgroup_id = ?
    """, (sg_id,))


def join_subgroup(sg_id: int, user_id: int):
    existing = fetchone(
        "SELECT id FROM subgroup_members WHERE subgroup_id = ? AND user_id = ?",
        (sg_id, user_id),
    )
    if not existing:
        execute(
            "INSERT INTO subgroup_members (subgroup_id, user_id) VALUES (?, ?)",
            (sg_id, user_id),
        )


def is_room_member(room_id: int, user_id: int) -> bool:
    return bool(fetchone(
        "SELECT id FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    ))


def is_subgroup_member(sg_id: int, user_id: int) -> bool:
    return bool(fetchone(
        "SELECT id FROM subgroup_members WHERE subgroup_id = ? AND user_id = ?",
        (sg_id, user_id),
    ))


# ── Messages ──────────────────────────────────────────────────────────────────

def add_room_message(room_id: int, user_id: int, content: str, is_ai: bool = False) -> int:
    return execute(
        "INSERT INTO messages (room_id, user_id, content, is_ai) VALUES (?, ?, ?, ?)",
        (room_id, user_id, content, int(is_ai)),
    )


def get_room_messages(room_id: int, limit: int = 100):
    return fetchall("""
        SELECT m.*, u.name as user_name, u.avatar_color
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.room_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (room_id, limit))


def add_subgroup_message(sg_id: int, user_id: int, content: str, is_ai: bool = False) -> int:
    return execute(
        "INSERT INTO subgroup_messages (subgroup_id, user_id, content, is_ai) VALUES (?, ?, ?, ?)",
        (sg_id, user_id, content, int(is_ai)),
    )


def get_subgroup_messages(sg_id: int, limit: int = 100):
    return fetchall("""
        SELECT m.*, u.name as user_name, u.avatar_color
        FROM subgroup_messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.subgroup_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (sg_id, limit))


# ── Render helpers ────────────────────────────────────────────────────────────

def render_room_selector(user_id: int):
    """Sidebar room/subgroup selector."""
    rooms = get_user_rooms(user_id)

    st.sidebar.markdown("### 🏠 Your Rooms")

    if not rooms:
        st.sidebar.info("No rooms yet. Create or join one!")
    else:
        for room in rooms:
            label = f"{'👑 ' if room['role'] == 'admin' else ''}{room['name']}"
            if st.sidebar.button(label, key=f"room_btn_{room['id']}", use_container_width=True):
                st.session_state["current_room"] = room["id"]
                st.session_state.pop("current_subgroup", None)
                st.rerun()

    st.sidebar.divider()

    if st.session_state.get("current_room"):
        room_id = st.session_state["current_room"]
        subgroups = get_room_subgroups(room_id)
        if subgroups:
            st.sidebar.markdown("### 🔬 Subgroups")
            for sg in subgroups:
                is_member = is_subgroup_member(sg["id"], user_id)
                label = f"{'• ' if is_member else '  '}{sg['name']}"
                if st.sidebar.button(label, key=f"sg_btn_{sg['id']}", use_container_width=True):
                    st.session_state["current_subgroup"] = sg["id"]
                    st.rerun()
