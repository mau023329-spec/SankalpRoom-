"""
SankalpRoom - Tasks Module
Task management and Kanban board for subgroups.
"""

import streamlit as st
from database.db import fetchone, fetchall, execute

STATUSES = ["todo", "doing", "done"]
STATUS_LABELS = {"todo": "📋 To Do", "doing": "⚙️ Doing", "done": "✅ Done"}
STATUS_COLORS = {"todo": "#4F46E5", "doing": "#F59E0B", "done": "#22C55E"}
PRIORITIES = ["low", "medium", "high", "critical"]
PRIORITY_ICONS = {"low": "🔵", "medium": "🟡", "high": "🟠", "critical": "🔴"}


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_task(subgroup_id: int, user_id: int, title: str, description: str = "",
                priority: str = "medium", assigned_to: int = None,
                deadline: str = None, idea_id: int = None) -> int:
    return execute("""
        INSERT INTO tasks (subgroup_id, idea_id, title, description, priority, assigned_to, deadline, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (subgroup_id, idea_id, title, description, priority, assigned_to, deadline, user_id))


def get_subgroup_tasks(subgroup_id: int):
    return fetchall("""
        SELECT t.*,
               u_assigned.name as assigned_name,
               u_assigned.avatar_color as assigned_color,
               u_created.name as creator_name
        FROM tasks t
        LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.id
        LEFT JOIN users u_created ON t.created_by = u_created.id
        WHERE t.subgroup_id = ?
        ORDER BY t.created_at DESC
    """, (subgroup_id,))


def update_task_status(task_id: int, status: str):
    execute(
        "UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, task_id),
    )


def update_task(task_id: int, **kwargs):
    allowed = {"title", "description", "priority", "assigned_to", "deadline", "status"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    clauses = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]
    execute(f"UPDATE tasks SET {clauses}, updated_at = datetime('now') WHERE id = ?", values)


def delete_task(task_id: int):
    execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def get_task(task_id: int):
    return fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))


# ── Kanban Render ─────────────────────────────────────────────────────────────

def render_kanban(subgroup_id: int, user_id: int, members: list):
    tasks = get_subgroup_tasks(subgroup_id)
    member_map = {m["id"]: m["name"] for m in members}

    # Add task button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🗂️ Kanban Board")
    with col2:
        if st.button("➕ Add Task", key="add_task_btn", type="primary", use_container_width=True):
            st.session_state["show_task_form"] = True

    if st.session_state.get("show_task_form"):
        with st.form("new_task_form"):
            t_title = st.text_input("Task title", placeholder="What needs to be done?")
            t_desc = st.text_area("Description", placeholder="Optional details...")
            c1, c2, c3 = st.columns(3)
            with c1:
                t_priority = st.selectbox("Priority", PRIORITIES, index=1)
            with c2:
                member_names = ["(unassigned)"] + list(member_map.values())
                t_assigned_name = st.selectbox("Assign to", member_names)
                t_assigned = None
                if t_assigned_name != "(unassigned)":
                    t_assigned = next((uid for uid, n in member_map.items() if n == t_assigned_name), None)
            with c3:
                t_deadline = st.date_input("Deadline", value=None)
            cs, cc = st.columns(2)
            with cs:
                sub = st.form_submit_button("Create Task", type="primary", use_container_width=True)
            with cc:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            if sub and t_title:
                deadline_str = str(t_deadline) if t_deadline else None
                create_task(subgroup_id, user_id, t_title, t_desc, t_priority, t_assigned, deadline_str)
                st.session_state["show_task_form"] = False
                st.rerun()
            if cancel:
                st.session_state["show_task_form"] = False
                st.rerun()

    # Kanban columns
    cols = st.columns(3)
    for i, status in enumerate(STATUSES):
        col_tasks = [t for t in tasks if t["status"] == status]
        with cols[i]:
            color = STATUS_COLORS[status]
            st.markdown(f"""
            <div style="
                background: {color}15;
                border: 1px solid {color}33;
                border-radius: 10px;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                text-align: center;
                font-weight: 700;
                color: {color};
                font-size: 0.85rem;
            ">{STATUS_LABELS[status]} ({len(col_tasks)})</div>
            """, unsafe_allow_html=True)

            for task in col_tasks:
                _render_task_card(task, status, user_id)


def _render_task_card(task: dict, current_status: str, user_id: int):
    p_icon = PRIORITY_ICONS.get(task.get("priority", "medium"), "🟡")
    assigned = task.get("assigned_name") or "Unassigned"
    deadline = task.get("deadline", "")
    color = STATUS_COLORS[current_status]

    st.markdown(f"""
    <div style="
        background: #1A1D27;
        border: 1px solid #2D3148;
        border-top: 3px solid {color};
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    ">
        <div style="font-weight:600; color:#E2E8F0; font-size:0.85rem; margin-bottom:0.3rem;">
            {p_icon} {task['title']}
        </div>
        {'<div style="color:#9CA3AF; font-size:0.75rem; margin-bottom:0.3rem;">' + task.get('description','') + '</div>' if task.get('description') else ''}
        <div style="color:#6B7280; font-size:0.72rem; display:flex; justify-content:space-between;">
            <span>👤 {assigned}</span>
            {'<span>📅 ' + deadline + '</span>' if deadline else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    other_statuses = [s for s in STATUSES if s != current_status]
    move_cols = st.columns(len(other_statuses) + 1)
    for j, ns in enumerate(other_statuses):
        ns_label = STATUS_LABELS[ns].split(" ", 1)[0]
        with move_cols[j]:
            if st.button(f"→ {ns_label}", key=f"move_{task['id']}_{ns}", use_container_width=True):
                update_task_status(task["id"], ns)
                st.rerun()
    with move_cols[-1]:
        if st.button("🗑", key=f"del_{task['id']}", use_container_width=True):
            delete_task(task["id"])
            st.rerun()
