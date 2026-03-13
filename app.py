"""
SankalpRoom — AI-Powered Team Collaboration Platform
Run: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="sankalproom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import init_db
from auth.auth import is_logged_in, render_auth_page, logout
from rooms.rooms import (
    render_room_selector, get_user_rooms, get_room, get_room_members,
    get_room_subgroups, get_subgroup, get_subgroup_members,
    create_room, join_room, create_subgroup, join_subgroup,
    is_room_member, is_subgroup_member,
    add_room_message, get_room_messages,
    add_subgroup_message, get_subgroup_messages,
)
from ideas.ideas import get_room_ideas, render_ideas_panel
from tasks.tasks import render_kanban, get_subgroup_tasks
from ai.ai_assistant import render_ai_panel, chat_with_ai
from ui.components import (
    inject_global_styles, render_topbar, render_stat_cards,
    render_member_avatars, render_empty_state, render_invite_pill,
    section_header,
)

init_db()
inject_global_styles()


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

def build_sidebar(user_id: int):
    with st.sidebar:
        # Logo mark
        st.markdown("""
        <div style="
            padding: 1.1rem 1rem 0.875rem;
            border-bottom: 1px solid #1A1A1A;
            margin-bottom: 0.875rem;
        ">
            <span style="
                font-family:'Clash Display','Outfit',sans-serif;
                font-size:0.95rem; font-weight:700;
                color:#E8A838; letter-spacing:-0.02em;
            ">sankalproom</span>
        </div>
        """, unsafe_allow_html=True)

        # Rooms section
        st.markdown('<div style="color:#2A2A2A;font-size:0.67rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;padding:0 0.75rem 0.375rem;font-family:Outfit,sans-serif;">Rooms</div>', unsafe_allow_html=True)

        rooms = get_user_rooms(user_id)
        if not rooms:
            st.markdown('<div style="color:#2A2A2A;font-size:0.78rem;padding:0.375rem 0.75rem;font-family:Outfit,sans-serif;">No rooms yet</div>', unsafe_allow_html=True)
        for r in rooms:
            is_cur = st.session_state.get("current_room") == r["id"]
            dot = "◆ " if r["role"] == "admin" else "◇ "
            btn_style = "color: #E8A838 !important; background: #1A1400 !important;" if is_cur else ""
            if st.button(f"{dot}{r['name']}", key=f"nav_r_{r['id']}", use_container_width=True):
                st.session_state["current_room"] = r["id"]
                st.session_state.pop("current_subgroup", None)
                st.rerun()

        # Subgroups section
        cur_room = st.session_state.get("current_room")
        if cur_room:
            sgs = get_room_subgroups(cur_room)
            if sgs:
                st.markdown('<div style="color:#2A2A2A;font-size:0.67rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;padding:0.875rem 0.75rem 0.375rem;font-family:Outfit,sans-serif;">Subgroups</div>', unsafe_allow_html=True)
                for sg in sgs:
                    is_mem = is_subgroup_member(sg["id"], user_id)
                    prefix = "  ● " if is_mem else "  ○ "
                    if st.button(f"{prefix}{sg['name']}", key=f"nav_sg_{sg['id']}", use_container_width=True):
                        st.session_state["current_subgroup"] = sg["id"]
                        st.rerun()

        # Spacer + actions
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        with st.expander("＋  New room"):
            with st.form("crf", border=False):
                rn = st.text_input("Name", placeholder="e.g. Q2 Launch")
                rd = st.text_area("Purpose", placeholder="What's this room for?", height=64)
                if st.form_submit_button("Create room", type="primary", use_container_width=True):
                    if rn:
                        create_room(rn, rd, user_id)
                        st.rerun()

        with st.expander("→  Join room"):
            with st.form("jrf", border=False):
                ic = st.text_input("Invite code", placeholder="ABC12345")
                if st.form_submit_button("Join", type="primary", use_container_width=True):
                    if ic:
                        r, err = join_room(ic, user_id)
                        if err == "already_member":
                            st.info("You're already in this room.")
                        elif err:
                            st.error(err)
                        else:
                            st.session_state["current_room"] = r["id"]
                            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

def render_dashboard(user_id: int, user_name: str):
    render_topbar(user_name)

    # Hero
    first = user_name.split()[0]
    st.markdown(f"""
    <div style="padding: 0.5rem 0 2rem;">
        <div style="
            font-family:'Clash Display','Outfit',sans-serif;
            font-size:2rem; font-weight:700;
            color:#EEEADF; letter-spacing:-0.035em; line-height:1.1;
            margin-bottom:0.5rem;
        ">Good to see you, {first}.</div>
        <div style="color:#3A3A3A; font-size:0.87rem; font-family:'Outfit',sans-serif;">
            Pick a room to continue, or start a new one.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rooms = get_user_rooms(user_id)
    if not rooms:
        render_empty_state("⚡", "No rooms yet", "Create a room from the sidebar or join one with an invite code.")
        return

    render_stat_cards([
        {"label": "Rooms",        "value": str(len(rooms)),                                           "color": "#E8A838"},
        {"label": "Admin",        "value": str(sum(1 for r in rooms if r["role"] == "admin")),        "color": "#E86F3A"},
        {"label": "Total members","value": str(sum(r["member_count"] for r in rooms)),                "color": "#22C55E"},
    ])

    section_header("Your rooms")

    cols = st.columns(3)
    for i, room in enumerate(rooms):
        with cols[i % 3]:
            is_admin   = room["role"] == "admin"
            role_color = "#E8A838" if is_admin else "#2A2A2A"
            role_text  = "admin"   if is_admin else "member"
            st.markdown(f"""
            <div style="
                background:#181818; border:1px solid #1E1E1E;
                border-radius:10px; padding:1.25rem 1.25rem 1rem;
                margin-bottom:0.5rem;
            ">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.625rem;">
                    <div style="
                        font-family:'Clash Display','Outfit',sans-serif;
                        font-size:0.95rem; font-weight:700;
                        color:#EEEADF; letter-spacing:-0.015em;
                    ">{room['name']}</div>
                    <span style="
                        background:{role_color}20; color:{role_color};
                        border:1px solid {role_color}30; border-radius:4px;
                        padding:2px 8px; font-size:0.65rem; font-weight:600;
                        font-family:'Outfit',sans-serif; text-transform:uppercase; letter-spacing:0.06em;
                    ">{role_text}</span>
                </div>
                <div style="color:#2A2A2A;font-size:0.78rem;font-family:'Outfit',sans-serif;margin-bottom:0.875rem;min-height:1rem;">
                    {room.get('description','') or '—'}
                </div>
                <div style="color:#2A2A2A;font-size:0.72rem;font-family:'Outfit',sans-serif;">
                    {room['member_count']} member{'s' if room['member_count']!=1 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open room →", key=f"open_r_{room['id']}", use_container_width=True):
                st.session_state["current_room"] = room["id"]
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# ROOM VIEW
# ══════════════════════════════════════════════════════════════════

def render_room_view(room_id: int, user_id: int, user_name: str):
    room = get_room(room_id)
    if not room or not is_room_member(room_id, user_id):
        st.error("Room not found or access denied.")
        st.session_state.pop("current_room", None)
        st.rerun()
        return

    members   = get_room_members(room_id)
    subgroups = get_room_subgroups(room_id)
    ideas     = get_room_ideas(room_id)
    messages  = get_room_messages(room_id)

    render_topbar(user_name, room["name"])

    # Room header
    col_info, col_code = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <div style="
                font-family:'Clash Display','Outfit',sans-serif;
                font-size:1.5rem; font-weight:700;
                color:#EEEADF; letter-spacing:-0.03em; margin-bottom:0.25rem;
            ">{room['name']}</div>
            <div style="color:#333;font-size:0.82rem;font-family:'Outfit',sans-serif;">
                {room.get('description','') or ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_member_avatars(members)

    with col_code:
        st.markdown("<div style='height:0.375rem'></div>", unsafe_allow_html=True)
        render_invite_pill(room["invite_code"])

    # Stats row
    render_stat_cards([
        {"label": "Members",      "value": str(len(members)),                                                    "color": "#E8A838"},
        {"label": "Ideas",        "value": str(len(ideas)),                                                       "color": "#6366F1"},
        {"label": "Selected",     "value": str(len([i for i in ideas if i["status"] == "Selected"])),            "color": "#22C55E"},
        {"label": "Subgroups",    "value": str(len(subgroups)),                                                   "color": "#E86F3A"},
    ])

    st.divider()

    t_chat, t_ideas, t_sgs, t_ai = st.tabs([
        "Discussion", "Ideas board", "Subgroups", "SankalpAI"
    ])

    with t_chat:  render_room_chat(room_id, user_id, messages)
    with t_ideas: render_ideas_panel(room_id, user_id)
    with t_sgs:   render_subgroups_panel(room_id, user_id, subgroups)
    with t_ai:    render_ai_panel(room_id, ideas, messages, subgroups)


# ── Room chat ──────────────────────────────────────────────────────

def render_room_chat(room_id: int, user_id: int, messages: list):
    section_header("Team discussion", "Type /ai <question> to get an AI response inline")

    box = st.container(height=420)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            render_empty_state("💬", "No messages yet", "Start the conversation.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                name_color = "#E8A838" if is_ai else "#EEEADF"
                who = "SankalpAI" if is_ai else msg["user_name"]
                st.markdown(
                    f'<span style="font-family:\'Outfit\',sans-serif;font-weight:600;font-size:0.82rem;color:{name_color};">{who}</span>'
                    f' <span style="color:#2A2A2A;font-size:0.72rem;">{str(msg.get("created_at",""))[:16]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(msg["content"])

    prompt = st.chat_input("Message the team…", key="room_chat_input")
    if prompt:
        add_room_message(room_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            q = prompt[4:].strip()
            with st.spinner("Thinking…"):
                reply = chat_with_ai(q)
            add_room_message(room_id, user_id, f"**SankalpAI:** {reply}", is_ai=True)
        st.rerun()


# ── Subgroups panel ────────────────────────────────────────────────

def render_subgroups_panel(room_id: int, user_id: int, subgroups: list):
    col_h, col_btn = st.columns([4, 1])
    with col_h:
        section_header("Subgroups", "Focused execution spaces for selected ideas")
    with col_btn:
        st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)
        if st.button("＋ New", type="primary", use_container_width=True, key="new_sg"):
            st.session_state["show_sg_form"] = not st.session_state.get("show_sg_form", False)

    if st.session_state.get("show_sg_form"):
        with st.form("sgf", border=True):
            sg_name = st.text_input("Subgroup name", placeholder="e.g. Design Squad")
            sg_desc = st.text_area("Purpose", height=64)
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if sg_name:
                        create_subgroup(room_id, sg_name, sg_desc, user_id)
                        st.session_state["show_sg_form"] = False
                        st.rerun()
            with c2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_sg_form"] = False
                    st.rerun()

    if not subgroups:
        render_empty_state("🔬", "No subgroups yet", "Create one to start executing selected ideas.")
        return

    cols = st.columns(3)
    for i, sg in enumerate(subgroups):
        with cols[i % 3]:
            color     = sg.get("color", "#E8A838")
            is_member = is_subgroup_member(sg["id"], user_id)
            st.markdown(f"""
            <div style="
                background:#181818; border:1px solid #1E1E1E;
                border-top: 2px solid {color};
                border-radius:10px; padding:1.1rem 1.25rem 0.875rem;
                margin-bottom:0.5rem;
            ">
                <div style="
                    font-family:'Clash Display','Outfit',sans-serif;
                    font-size:0.88rem; font-weight:700;
                    color:#EEEADF; margin-bottom:0.3rem; letter-spacing:-0.01em;
                ">{sg['name']}</div>
                <div style="color:#2A2A2A;font-size:0.76rem;font-family:'Outfit',sans-serif;margin-bottom:0.75rem;min-height:1rem;">
                    {sg.get('description','') or 'Execution subgroup'}
                </div>
                <div style="display:flex;gap:1.25rem;font-size:0.7rem;color:#2A2A2A;font-family:'Outfit',sans-serif;align-items:center;">
                    <span>{sg['member_count']} members</span>
                    <span>{sg['task_count']} tasks</span>
                    {'<span style="color:#22C55E;font-weight:600;font-size:0.68rem;">✓ joined</span>' if is_member else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            btns = st.columns(2) if not is_member else [st.columns(1)[0]]
            with btns[0]:
                if st.button("Open →", key=f"osg_{sg['id']}", use_container_width=True):
                    if not is_member:
                        join_subgroup(sg["id"], user_id)
                    st.session_state["current_subgroup"] = sg["id"]
                    st.rerun()
            if not is_member:
                with btns[1]:
                    if st.button("Join", key=f"jsg_{sg['id']}", use_container_width=True):
                        join_subgroup(sg["id"], user_id)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════
# SUBGROUP VIEW
# ══════════════════════════════════════════════════════════════════

def render_subgroup_view(sg_id: int, room_id: int, user_id: int, user_name: str):
    sg   = get_subgroup(sg_id)
    room = get_room(room_id)
    if not sg:
        st.session_state.pop("current_subgroup", None)
        st.rerun()
        return

    members  = get_subgroup_members(sg_id)
    tasks    = get_subgroup_tasks(sg_id)
    messages = get_subgroup_messages(sg_id)
    color    = sg.get("color", "#E8A838")

    render_topbar(user_name, room["name"] if room else "Room", sg["name"])

    # Back + header
    col_back, col_info = st.columns([1, 6])
    with col_back:
        if st.button("← Back", key="sg_back"):
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom:0.375rem;">
            <span style="
                font-family:'Clash Display','Outfit',sans-serif;
                font-size:1.1rem; font-weight:700;
                color:{color}; letter-spacing:-0.015em;
            ">{sg['name']}</span>
            {'<span style="color:#2A2A2A;font-size:0.78rem;font-family:Outfit,sans-serif;margin-left:0.75rem;">'+sg.get("description","")+"</span>" if sg.get("description") else ""}
        </div>
        """, unsafe_allow_html=True)

    done  = [t for t in tasks if t["status"] == "done"]
    doing = [t for t in tasks if t["status"] == "doing"]
    render_stat_cards([
        {"label": "Members",     "value": str(len(members)), "color": color},
        {"label": "Total tasks", "value": str(len(tasks)),   "color": "#6366F1"},
        {"label": "In progress", "value": str(len(doing)),   "color": "#E86F3A"},
        {"label": "Done",        "value": str(len(done)),    "color": "#22C55E"},
    ])

    t_kanban, t_chat = st.tabs(["Kanban board", "Chat"])
    with t_kanban: render_kanban(sg_id, user_id, members)
    with t_chat:   render_sg_chat(sg_id, user_id, messages)


def render_sg_chat(sg_id: int, user_id: int, messages: list):
    section_header("Subgroup chat", "Type /ai <question> for AI help")

    box = st.container(height=380)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            render_empty_state("💬", "No messages yet", "Coordinate with your subgroup.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                name_color = "#E8A838" if is_ai else "#EEEADF"
                who = "SankalpAI" if is_ai else msg["user_name"]
                st.markdown(
                    f'<span style="font-family:\'Outfit\',sans-serif;font-weight:600;font-size:0.82rem;color:{name_color};">{who}</span>'
                    f' <span style="color:#2A2A2A;font-size:0.72rem;">{str(msg.get("created_at",""))[:16]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(msg["content"])

    prompt = st.chat_input("Message your subgroup…", key="sg_chat_input")
    if prompt:
        add_subgroup_message(sg_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            q = prompt[4:].strip()
            with st.spinner("Thinking…"):
                reply = chat_with_ai(q)
            add_subgroup_message(sg_id, user_id, f"**SankalpAI:** {reply}", is_ai=True)
        st.rerun()


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    if not is_logged_in():
        render_auth_page()
        return

    user_id   = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    build_sidebar(user_id)

    cur_room = st.session_state.get("current_room")
    cur_sg   = st.session_state.get("current_subgroup")

    if not cur_room:
        render_dashboard(user_id, user_name)
    elif cur_sg:
        render_subgroup_view(cur_sg, cur_room, user_id, user_name)
    else:
        render_room_view(cur_room, user_id, user_name)


if __name__ == "__main__":
    main()
