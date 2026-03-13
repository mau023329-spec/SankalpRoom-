"""
SankalpRoom - Tasks Module
Mobile-friendly Kanban: tabs on mobile, 3-col on desktop.
"""

import streamlit as st
from database.db import fetchone, fetchall, execute

STATUSES   = ["todo", "doing", "done"]
COL_LABEL  = {"todo": "To Do", "doing": "In Progress", "done": "Done"}
COL_COLOR  = {"todo": "#6366F1", "doing": "#F59E0B", "done": "#22C55E"}
PRIO_COLOR = {"low": "#334155", "medium": "#F59E0B", "high": "#EF4444", "critical": "#EC4899"}
PRIO_LABEL = {"low": "low", "medium": "med", "high": "high", "critical": "crit"}


def create_task(sg_id, uid, title, desc="", priority="medium", assigned=None, deadline=None):
    return execute(
        "INSERT INTO tasks(subgroup_id,title,description,priority,assigned_to,deadline,created_by) VALUES(?,?,?,?,?,?,?)",
        (sg_id, title, desc, priority, assigned, deadline, uid),
    )

def get_subgroup_tasks(sg_id):
    return fetchall("""
        SELECT t.*, ua.name as assigned_name
        FROM tasks t LEFT JOIN users ua ON t.assigned_to=ua.id
        WHERE t.subgroup_id=? ORDER BY t.created_at DESC
    """, (sg_id,))

def move_task(tid, status): execute("UPDATE tasks SET status=? WHERE id=?", (status, tid))
def delete_task(tid):       execute("DELETE FROM tasks WHERE id=?", (tid,))


def render_kanban(sg_id: int, user_id: int, members: list):
    from ui.components import render_empty_state, section_header

    col_h, col_btn = st.columns([3, 1])
    with col_h:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;
            color:#F1F5F9;margin-bottom:0.875rem;">Kanban Board</div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("＋ Add task", type="primary", use_container_width=True, key="add_task_btn"):
            st.session_state["show_task_form"] = not st.session_state.get("show_task_form", False)

    if st.session_state.get("show_task_form"):
        mmap = {m["id"]: m["name"] for m in members}
        with st.form("ntf", border=True):
            tt = st.text_input("Task title", placeholder="What needs to be done?")
            td = st.text_area("Description", height=64, placeholder="Optional details…")
            c1, c2 = st.columns(2)
            with c1:
                tp = st.selectbox("Priority", ["low", "medium", "high", "critical"], index=1)
            with c2:
                opts    = ["Unassigned"] + list(mmap.values())
                ta_name = st.selectbox("Assign to", opts)
                ta      = next((k for k, v in mmap.items() if v == ta_name), None)
            tdl = st.date_input("Deadline (optional)", value=None)
            cs, cc = st.columns(2)
            with cs:
                if st.form_submit_button("Create task", type="primary", use_container_width=True):
                    if tt:
                        create_task(sg_id, user_id, tt, td, tp, ta, str(tdl) if tdl else None)
                        st.session_state["show_task_form"] = False
                        st.rerun()
            with cc:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_task_form"] = False
                    st.rerun()

    tasks = get_subgroup_tasks(sg_id)
    if not tasks:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;border:1px dashed #1C2030;border-radius:10px;margin:1rem 0;">
            <div style="font-size:2rem;opacity:0.4;margin-bottom:0.75rem;">📋</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:600;color:#334155;">No tasks yet</div>
            <div style="color:#1E293B;font-size:0.8rem;font-family:'Inter',sans-serif;margin-top:0.3rem;">Add tasks to start tracking work.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Mobile: use tabs per column; Desktop: CSS handles 3-col ──
    # We use st.tabs so on narrow screens each column is a tab swipe
    tab_todo, tab_doing, tab_done = st.tabs([
        f"To Do  {len([t for t in tasks if t['status']=='todo'])}",
        f"In Progress  {len([t for t in tasks if t['status']=='doing'])}",
        f"Done  {len([t for t in tasks if t['status']=='done'])}",
    ])

    with tab_todo:
        _render_column(tasks, "todo", user_id)
    with tab_doing:
        _render_column(tasks, "doing", user_id)
    with tab_done:
        _render_column(tasks, "done", user_id)


def _render_column(tasks, status, user_id):
    color      = COL_COLOR[status]
    col_tasks  = [t for t in tasks if t["status"] == status]

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
        padding:0.5rem 0.75rem;background:#0C0E14;
        border:1px solid #1C2030;border-top:2px solid {color};
        border-radius:8px 8px 0 0;margin-bottom:0;">
        <span style="font-family:'Space Grotesk',sans-serif;font-size:0.8rem;
            font-weight:600;color:{color};">{COL_LABEL[status]}</span>
        <span style="background:{color}18;color:{color};border-radius:10px;
            padding:1px 8px;font-size:0.7rem;font-weight:700;
            font-family:'Space Grotesk',sans-serif;">{len(col_tasks)}</span>
    </div>
    <div style="border:1px solid #1C2030;border-top:none;border-radius:0 0 8px 8px;
        padding:0.5rem;min-height:3rem;background:#080A0F;margin-bottom:0.75rem;"></div>
    """, unsafe_allow_html=True)

    if not col_tasks:
        st.markdown('<div style="color:#1E293B;font-size:0.78rem;font-family:Inter,sans-serif;text-align:center;padding:1rem 0;">Empty</div>', unsafe_allow_html=True)
        return

    for task in col_tasks:
        _render_task_card(task, status)


def _render_task_card(task: dict, status: str):
    pc = PRIO_COLOR.get(task.get("priority", "medium"), "#334155")
    pl = PRIO_LABEL.get(task.get("priority", "medium"), "med")
    assign = task.get("assigned_name") or "—"
    dl     = task.get("deadline", "") or ""

    st.markdown(f"""
    <div style="background:#0C0E14;border:1px solid #1C2030;border-radius:8px;
        padding:0.75rem 0.875rem 0.625rem;margin-bottom:0.4rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.3rem;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.82rem;font-weight:600;
                color:#CBD5E1;flex:1;margin-right:0.5rem;line-height:1.35;">{task['title']}</div>
            <span style="color:{pc};background:{pc}15;border:1px solid {pc}25;border-radius:4px;
                padding:1px 6px;font-size:0.62rem;font-weight:700;font-family:'Inter',sans-serif;
                text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;">{pl}</span>
        </div>
        {'<div style="color:#334155;font-size:0.73rem;font-family:Inter,sans-serif;margin-bottom:0.3rem;line-height:1.4;">'+task.get("description","")+"</div>" if task.get("description") else ""}
        <div style="display:flex;justify-content:space-between;font-size:0.68rem;color:#1E293B;font-family:'Inter',sans-serif;">
            <span>{assign}</span>
            {'<span>'+dl+'</span>' if dl else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    other = [s for s in STATUSES if s != status]
    short = {"todo": "To Do", "doing": "Doing", "done": "Done"}

    # Move buttons + delete — all full-width stacked on mobile
    for ns in other:
        if st.button(f"→ {short[ns]}", key=f"mv_{task['id']}_{ns}", use_container_width=True):
            move_task(task["id"], ns)
            st.rerun()
    if st.button(f"✕ Delete", key=f"del_{task['id']}", use_container_width=True):
        delete_task(task["id"])
        st.rerun()
