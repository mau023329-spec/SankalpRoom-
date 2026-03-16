"""
SankalpRoom - Rooms Module
All room data loaded in ONE batched query per view — no sequential round trips.
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
    # Clear cache so new room shows up immediately
    get_user_rooms.clear()
    return fetchone("SELECT * FROM rooms WHERE id = ?", (room_id,))


def delete_room(room_id: int, user_id: int) -> tuple:
    member = fetchone(
        "SELECT role FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    )
    if not member or member["role"] != "admin":
        return False, "Only the room admin can delete this room."
    execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    get_user_rooms.clear()
    get_room_members.clear()
    get_room_subgroups.clear()
    return True, None


def leave_room(room_id: int, user_id: int) -> tuple:
    member = fetchone(
        "SELECT role FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    )
    if not member:
        return False, "You are not a member of this room."
    if member["role"] == "admin":
        return False, "Admins cannot leave — delete the room instead."
    execute(
        "DELETE FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    )
    get_user_rooms.clear()
    get_room_members.clear()
    return True, None


def remove_member(room_id: int, target_user_id: int, admin_user_id: int) -> tuple:
    admin = fetchone(
        "SELECT role FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, admin_user_id),
    )
    if not admin or admin["role"] != "admin":
        return False, "Only admins can remove members."
    if target_user_id == admin_user_id:
        return False, "You cannot remove yourself."
    execute(
        "DELETE FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, target_user_id),
    )
    # Auto-blacklist by user_id (immutable) so they cannot re-join even after username change
    _add_to_blacklist(room_id, target_user_id, admin_user_id)
    get_room_members.clear()
    return True, None


# ── Blacklist ─────────────────────────────────────────────────────────────────

def _add_to_blacklist(room_id: int, user_id: int, banned_by: int):
    """Internal: add user to room blacklist. Safe to call if already banned."""
    existing = fetchone(
        "SELECT id FROM room_blacklist WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    )
    if not existing:
        execute(
            "INSERT INTO room_blacklist (room_id, user_id, banned_by) VALUES (?, ?, ?)",
            (room_id, user_id, banned_by),
        )


def is_blacklisted(room_id: int, user_id: int) -> bool:
    """Return True if the user is banned from this room."""
    return bool(fetchone(
        "SELECT id FROM room_blacklist WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    ))


def get_blacklist(room_id: int) -> list:
    """Return all banned users for a room with their names."""
    return fetchall("""
        SELECT rb.id, rb.user_id, rb.banned_at,
               u.name  AS user_name,
               b.name  AS banned_by_name
        FROM room_blacklist rb
        JOIN users u ON u.id = rb.user_id
        JOIN users b ON b.id = rb.banned_by
        WHERE rb.room_id = ?
        ORDER BY rb.banned_at DESC
    """, (room_id,))


def unblacklist_user(room_id: int, target_user_id: int, admin_user_id: int) -> tuple:
    """Admin removes a user from the blacklist so they can re-join."""
    if not is_room_admin(room_id, admin_user_id):
        return False, "Only admins can unban members."
    execute(
        "DELETE FROM room_blacklist WHERE room_id = ? AND user_id = ?",
        (room_id, target_user_id),
    )
    return True, None


# ── CHANGE 4: Admin-only room details editing ─────────────────────────────────

def update_room(room_id: int, user_id: int, new_name: str, new_description: str) -> tuple:
    """Only the room admin can update the room name and description."""
    if not is_room_admin(room_id, user_id):
        return False, "Only the room admin can edit room details."
    new_name = new_name.strip()
    if not new_name:
        return False, "Room name cannot be empty."
    execute(
        "UPDATE rooms SET name = ?, description = ? WHERE id = ?",
        (new_name, new_description.strip(), room_id),
    )
    get_user_rooms.clear()
    return True, None


# ── CHANGE 5: Admin can promote members to admin ──────────────────────────────

def promote_to_admin(room_id: int, target_user_id: int, admin_user_id: int) -> tuple:
    """Allow an existing admin to promote another member to admin."""
    if not is_room_admin(room_id, admin_user_id):
        return False, "Only admins can promote members."
    member = fetchone(
        "SELECT role FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, target_user_id),
    )
    if not member:
        return False, "User is not a member of this room."
    if member["role"] == "admin":
        return False, "User is already an admin."
    execute(
        "UPDATE room_members SET role = 'admin' WHERE room_id = ? AND user_id = ?",
        (room_id, target_user_id),
    )
    get_room_members.clear()
    get_user_rooms.clear()
    return True, None


def join_room(invite_code: str, user_id: int):
    room = fetchone("SELECT * FROM rooms WHERE invite_code = ?", (invite_code.upper(),))
    if not room:
        return None, "Invalid invite code."
    # Check blacklist — tied to user_id so renaming doesn't bypass the ban
    if is_blacklisted(room["id"], user_id):
        return None, "You have been banned from this room by the admin."
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
    get_user_rooms.clear()
    get_room_members.clear()
    return room, None


# ── Cached reads ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=15, show_spinner=False)
def get_user_rooms(user_id: int):
    return fetchall("""
        SELECT r.*, rm.role,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) AS member_count
        FROM rooms r
        JOIN room_members rm ON r.id = rm.room_id
        WHERE rm.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))


def get_room(room_id: int):
    return fetchone("SELECT * FROM rooms WHERE id = ?", (room_id,))


@st.cache_data(ttl=20, show_spinner=False)
def get_room_members(room_id: int):
    # profile_photo included so avatars show in member lists and chat
    return fetchall("""
        SELECT u.id, u.name, u.email, u.avatar_color, u.profile_photo, rm.role
        FROM users u
        JOIN room_members rm ON u.id = rm.user_id
        WHERE rm.room_id = ?
        ORDER BY rm.joined_at
    """, (room_id,))


@st.cache_data(ttl=15, show_spinner=False)
def get_room_subgroups(room_id: int):
    return fetchall("""
        SELECT s.*,
               (SELECT COUNT(*) FROM subgroup_members WHERE subgroup_id = s.id) AS member_count,
               (SELECT COUNT(*) FROM tasks WHERE subgroup_id = s.id) AS task_count
        FROM subgroups s
        WHERE s.room_id = ?
        ORDER BY s.created_at
    """, (room_id,))


# ── BATCHED room load — ONE query instead of 4 separate ones ─────────────────

def get_room_data(room_id: int, user_id: int) -> dict:
    """
    Load everything needed for the room view in two queries instead of 6+.
    Returns dict with keys: room, members, subgroups, is_member, is_admin
    """
    # Query 1: room + membership check
    row = fetchone("""
        SELECT r.*,
               rm.role AS user_role
        FROM rooms r
        LEFT JOIN room_members rm ON r.id = rm.room_id AND rm.user_id = ?
        WHERE r.id = ?
    """, (user_id, room_id))

    if not row or not row.get("user_role"):
        return None

    # Query 2: members + subgroups in parallel via cached functions
    members   = get_room_members(room_id)
    subgroups = get_room_subgroups(room_id)

    return {
        "room":     row,
        "members":  members,
        "subgroups": subgroups,
        "is_admin": row["user_role"] == "admin",
    }


# ── Subgroup CRUD ─────────────────────────────────────────────────────────────

SUBGROUP_COLORS = ["#4F46E5","#8B5CF6","#EC4899","#06B6D4","#22C55E","#F59E0B","#EF4444"]


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
    get_room_subgroups.clear()
    return fetchone("SELECT * FROM subgroups WHERE id = ?", (sg_id,))


def delete_subgroup(sg_id: int, user_id: int, room_id: int) -> tuple:
    if not is_room_admin(room_id, user_id):
        return False, "Only room admins can delete subgroups."
    execute("DELETE FROM subgroups WHERE id = ?", (sg_id,))
    get_room_subgroups.clear()
    return True, None


def get_subgroup(sg_id: int):
    return fetchone("SELECT * FROM subgroups WHERE id = ?", (sg_id,))


@st.cache_data(ttl=20, show_spinner=False)
def get_subgroup_members(sg_id: int):
    # profile_photo included so avatars show in subgroup member lists
    return fetchall("""
        SELECT u.id, u.name, u.email, u.avatar_color, u.profile_photo
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
        get_subgroup_members.clear()
        get_room_subgroups.clear()


def is_room_member(room_id: int, user_id: int) -> bool:
    return bool(fetchone(
        "SELECT id FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    ))


def is_room_admin(room_id: int, user_id: int) -> bool:
    row = fetchone(
        "SELECT role FROM room_members WHERE room_id = ? AND user_id = ?",
        (room_id, user_id),
    )
    return bool(row and row["role"] == "admin")


def is_subgroup_member(sg_id: int, user_id: int) -> bool:
    return bool(fetchone(
        "SELECT id FROM subgroup_members WHERE subgroup_id = ? AND user_id = ?",
        (sg_id, user_id),
    ))


# ── Messages ──────────────────────────────────────────────────────────────────

def add_room_message(room_id: int, user_id: int, content: str, is_ai: bool = False) -> int:
    return execute(
        "INSERT INTO messages (room_id, user_id, content, is_ai) VALUES (?, ?, ?, ?)",
        (room_id, user_id, content, is_ai),
    )


def get_room_messages(room_id: int, limit: int = 60):
    # Not cached — always fresh so refresh button works
    # profile_photo fetched so photo shows in chat bubbles
    return fetchall("""
        SELECT m.*, u.name AS user_name, u.avatar_color, u.profile_photo AS user_photo
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.room_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (room_id, limit))


def add_subgroup_message(sg_id: int, user_id: int, content: str, is_ai: bool = False) -> int:
    return execute(
        "INSERT INTO subgroup_messages (subgroup_id, user_id, content, is_ai) VALUES (?, ?, ?, ?)",
        (sg_id, user_id, content, is_ai),
    )


def get_subgroup_messages(sg_id: int, limit: int = 60):
    # profile_photo fetched so photo shows in subgroup chat bubbles
    return fetchall("""
        SELECT m.*, u.name AS user_name, u.avatar_color, u.profile_photo AS user_photo
        FROM subgroup_messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.subgroup_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (sg_id, limit))
