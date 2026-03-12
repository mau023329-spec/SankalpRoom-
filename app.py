"""
SankalpRoom — AI-Powered Team Collaboration Platform
Main Streamlit Application Entry Point

Run:  streamlit run app.py
"""

import streamlit as st

# ── Page config (MUST be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="SankalpRoom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ──────────────────────────────────────────────────────────
from database.database import init_db
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
    render_member_avatars, render_empty_state,
)

# ── Init ───────────────────────────────────────────────────────────────────
init_db()
inject_global_styles()


def main():
    # ── Auth gate ──────────────────────────────────────────────────────────
    if not is_logged_in():
        render_auth_page()
        return

    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0 0.5rem; text-align:center;">
            <div style="
                font-family:'Syne',sans-serif;
                font-size:1.5rem;
                font-weight:800;
                background:linear-gradient(135deg,#4F46E5,#8B5CF6);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
            ">⚡ SankalpRoom</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        render_room_selector(user_id)
        st.divider()

        # Room actions
        with st.expander("➕ Create Room"):
            with st.form("create_room_form"):
                r_name = st.text_input("Room name", placeholder="e.g. Product Team Q2")
                r_desc = st.text_area("Description", placeholder="What is this room for?", height=80)
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if r_name:
                        create_room(r_name, r_desc, user_id)
                        st.success("Room created!")
                        st.rerun()

        with st.expander("🔗 Join Room"):
            with st.form("join_room_form"):
                invite = st.text_input("Invite code", placeholder="XXXXXXXX")
                if st.form_submit_button("Join", type="primary", use_container_width=True):
                    if invite:
                        room, err = join_room(invite, user_id)
                        if err == "already_member":
                            st.info("You're already in this room!")
                        elif err:
                            st.error(err)
                        else:
                            st.session_state["current_room"] = room["id"]
                            st.success(f"Joined {room['name']}!")
                            st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    # ── Main content area ──────────────────────────────────────────────────
    current_room_id = st.session_state.get("current_room")
    current_sg_id = st.session_state.get("current_subgroup")

    if not current_room_id:
        render_dashboard(user_id, user_name)
    elif current_sg_id:
        render_subgroup_view(current_sg_id, current_room_id, user_id, user_name)
    else:
        render_room_view(current_room_id, user_id, user_name)


# ── Dashboard (no room selected) ───────────────────────────────────────────

def render_dashboard(user_id: int, user_name: str):
    render_topbar(user_name)

    st.markdown(f"""
    <div style="text-align:center; padding:2rem 0 1rem;">
        <div style="
            font-family:'Syne',sans-serif;
            font-size:2.5rem;
            font-weight:800;
            background:linear-gradient(135deg,#4F46E5,#8B5CF6,#EC4899);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            background-clip:text;
            margin-bottom:0.5rem;
        ">Welcome back, {user_name}! 👋</div>
        <div style="color:#6B7280; font-size:1rem;">
            Your collaboration hub for turning ideas into action.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rooms = get_user_rooms(user_id)

    if not rooms:
        render_empty_state(
            "🚀",
            "No rooms yet",
            "Create a new room or join one with an invite code from the sidebar.",
        )
        return

    # Stats
    total_rooms = len(rooms)
    render_stat_cards([
        {"label": "Rooms Joined", "value": str(total_rooms), "icon": "🏠", "color": "#4F46E5"},
        {"label": "Admin Roles", "value": str(sum(1 for r in rooms if r["role"] == "admin")), "icon": "👑", "color": "#8B5CF6"},
        {"label": "Total Members", "value": str(sum(r["member_count"] for r in rooms)), "icon": "👥", "color": "#22C55E"},
    ])

    st.markdown("### 🏠 Your Rooms")
    cols = st.columns(min(len(rooms), 3))
    for i, room in enumerate(rooms):
        with cols[i % 3]:
            role_badge = "👑 Admin" if room["role"] == "admin" else "👤 Member"
            st.markdown(f"""
            <div style="
                background: #1A1D27;
                border: 1px solid #2D3148;
                border-top: 3px solid #4F46E5;
                border-radius: 12px;
                padding: 1.25rem;
                margin-bottom: 0.75rem;
            ">
                <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem; color:#E2E8F0; margin-bottom:0.4rem;">
                    {room['name']}
                </div>
                <div style="color:#9CA3AF; font-size:0.82rem; margin-bottom:0.75rem;">
                    {room.get('description','') or 'No description'}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6B7280;">
                    <span>👥 {room['member_count']} members</span>
                    <span style="color:#4F46E5;">{role_badge}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open Room →", key=f"open_{room['id']}", use_container_width=True):
                st.session_state["current_room"] = room["id"]
                st.rerun()


# ── Room View ──────────────────────────────────────────────────────────────

def render_room_view(room_id: int, user_id: int, user_name: str):
    room = get_room(room_id)
    if not room or not is_room_member(room_id, user_id):
        st.error("Room not found or access denied.")
        st.session_state.pop("current_room", None)
        st.rerun()
        return

    members = get_room_members(room_id)
    subgroups = get_room_subgroups(room_id)
    ideas = get_room_ideas(room_id)
    messages = get_room_messages(room_id)

    render_topbar(user_name, room["name"])

    # Room header
    col_info, col_invite = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom:1rem;">
            <h2 style="margin:0; font-family:'Syne',sans-serif;">{room['name']}</h2>
            <p style="color:#9CA3AF; margin:0.3rem 0 0;">{room.get('description','')}</p>
        </div>
        """, unsafe_allow_html=True)
        render_member_avatars(members)

    with col_invite:
        st.markdown(f"""
        <div style="
            background:#1A1D27; border:1px solid #2D3148; border-radius:10px;
            padding:0.75rem; text-align:center; margin-top:0.5rem;
        ">
            <div style="color:#6B7280; font-size:0.72rem; margin-bottom:0.3rem;">INVITE CODE</div>
            <div style="
                font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
                color:#4F46E5; letter-spacing:2px;
            ">{room['invite_code']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Stats
    render_stat_cards([
        {"label": "Members", "value": str(len(members)), "icon": "👥", "color": "#4F46E5"},
        {"label": "Ideas", "value": str(len(ideas)), "icon": "💡", "color": "#8B5CF6"},
        {"label": "Selected", "value": str(len([i for i in ideas if i["status"] == "Selected"])), "icon": "✅", "color": "#22C55E"},
        {"label": "Subgroups", "value": str(len(subgroups)), "icon": "🔬", "color": "#F59E0B"},
    ])

    st.divider()

    # Main tabs
    tab_chat, tab_ideas, tab_subgroups, tab_ai = st.tabs(
        ["💬 Discussion", "💡 Ideas Board", "🔬 Subgroups", "🤖 SankalpAI"]
    )

    # ── Chat tab ──
    with tab_chat:
        render_room_chat(room_id, user_id, user_name, messages)

    # ── Ideas tab ──
    with tab_ideas:
        render_ideas_panel(room_id, user_id)

    # ── Subgroups tab ──
    with tab_subgroups:
        render_subgroups_panel(room_id, user_id, subgroups)

    # ── AI tab ──
    with tab_ai:
        render_ai_panel(room_id, ideas, messages, subgroups)


def render_room_chat(room_id: int, user_id: int, user_name: str, messages: list):
    st.markdown("### 💬 Team Discussion")

    # Display messages (reverse for display)
    display_messages = list(reversed(messages[:50]))

    chat_container = st.container(height=420)
    with chat_container:
        if not display_messages:
            render_empty_state("💬", "No messages yet", "Start the conversation!")
        for msg in display_messages:
            is_ai = bool(msg.get("is_ai"))
            role = "assistant" if is_ai else "user"
            name = "🤖 SankalpAI" if is_ai else msg.get("user_name", "Unknown")
            with st.chat_message(role):
                st.markdown(f"**{name}** · *{msg.get('created_at','')[:16]}*")
                st.markdown(msg["content"])

    # Chat input
    col_input, col_ai = st.columns([4, 1])
    with col_input:
        prompt = st.chat_input("Message the team... (use @mention or 💡 for ideas)", key="room_chat_input")
    with col_ai:
        ai_help = st.button("🤖 Ask AI", use_container_width=True, key="ai_quick")

    if prompt:
        add_room_message(room_id, user_id, prompt)
        # Check if it's an AI request
        if prompt.startswith("/ai ") or "@ai" in prompt.lower():
            query = prompt.replace("/ai ", "").replace("@ai", "").strip()
            with st.spinner("SankalpAI is responding..."):
                ai_response = chat_with_ai(query)
            # AI bot user_id = 0 (system)
            ai_user_id = user_id  # store as current user but flagged
            add_room_message(room_id, user_id, f"🤖 **SankalpAI:** {ai_response}", is_ai=True)
        st.rerun()

    if ai_help:
        st.session_state["ai_quick_open"] = True

    if st.session_state.get("ai_quick_open"):
        with st.form("quick_ai_form"):
            ai_q = st.text_input("Ask SankalpAI anything...", placeholder="e.g. What are 3 ways to prioritize these ideas?")
            cs, cc = st.columns(2)
            with cs:
                if st.form_submit_button("Ask", type="primary", use_container_width=True):
                    if ai_q:
                        with st.spinner("Thinking..."):
                            response = chat_with_ai(ai_q)
                        add_room_message(room_id, user_id, f"🤖 **SankalpAI:** {response}", is_ai=True)
                        st.session_state["ai_quick_open"] = False
                        st.rerun()
            with cc:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["ai_quick_open"] = False
                    st.rerun()


def render_subgroups_panel(room_id: int, user_id: int, subgroups: list):
    col_h, col_btn = st.columns([3, 1])
    with col_h:
        st.markdown("### 🔬 Subgroups")
    with col_btn:
        if st.button("➕ New Subgroup", type="primary", use_container_width=True, key="new_sg_btn"):
            st.session_state["show_sg_form"] = True

    if st.session_state.get("show_sg_form"):
        with st.form("create_sg_form"):
            sg_name = st.text_input("Subgroup name", placeholder="e.g. Design Squad")
            sg_desc = st.text_area("Purpose", placeholder="What will this subgroup execute?", height=80)
            cs, cc = st.columns(2)
            with cs:
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if sg_name:
                        create_subgroup(room_id, sg_name, sg_desc, user_id)
                        st.session_state["show_sg_form"] = False
                        st.rerun()
            with cc:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_sg_form"] = False
                    st.rerun()

    if not subgroups:
        render_empty_state("🔬", "No subgroups yet", "Create subgroups to assign execution tasks.")
        return

    cols = st.columns(min(len(subgroups), 3))
    for i, sg in enumerate(subgroups):
        with cols[i % 3]:
            color = sg.get("color", "#4F46E5")
            is_member = is_subgroup_member(sg["id"], user_id)
            st.markdown(f"""
            <div style="
                background:#1A1D27; border:1px solid #2D3148;
                border-top: 3px solid {color};
                border-radius:12px; padding:1.25rem; margin-bottom:0.75rem;
            ">
                <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:0.95rem; color:#E2E8F0;">
                    {sg['name']}
                </div>
                <div style="color:#9CA3AF; font-size:0.8rem; margin:0.4rem 0;">
                    {sg.get('description','') or 'Execution subgroup'}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6B7280;">
                    <span>👥 {sg['member_count']}</span>
                    <span>📋 {sg['task_count']} tasks</span>
                    {'<span style="color:#22C55E;">✓ Member</span>' if is_member else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_cols = st.columns(2 if not is_member else 1)
            with btn_cols[0]:
                if st.button("Open →", key=f"open_sg_{sg['id']}", use_container_width=True):
                    if not is_member:
                        join_subgroup(sg["id"], user_id)
                    st.session_state["current_subgroup"] = sg["id"]
                    st.rerun()
            if not is_member:
                with btn_cols[1]:
                    if st.button("Join", key=f"join_sg_{sg['id']}", use_container_width=True):
                        join_subgroup(sg["id"], user_id)
                        st.rerun()


# ── Subgroup View ──────────────────────────────────────────────────────────

def render_subgroup_view(sg_id: int, room_id: int, user_id: int, user_name: str):
    sg = get_subgroup(sg_id)
    room = get_room(room_id)

    if not sg:
        st.error("Subgroup not found.")
        st.session_state.pop("current_subgroup", None)
        st.rerun()
        return

    members = get_subgroup_members(sg_id)
    tasks = get_subgroup_tasks(sg_id)
    messages = get_subgroup_messages(sg_id)

    render_topbar(user_name, room["name"] if room else "Room", sg["name"])

    # Back button
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Room", key="back_btn"):
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_title:
        color = sg.get("color", "#4F46E5")
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span style="
                font-family:'Syne',sans-serif;
                font-size:1.4rem; font-weight:700;
                color: {color};
            ">🔬 {sg['name']}</span>
            <span style="color:#9CA3AF; font-size:0.85rem; margin-left:0.75rem;">
                {sg.get('description','')}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Stats
    done_tasks = [t for t in tasks if t["status"] == "done"]
    doing_tasks = [t for t in tasks if t["status"] == "doing"]
    render_stat_cards([
        {"label": "Members", "value": str(len(members)), "icon": "👥", "color": color},
        {"label": "Total Tasks", "value": str(len(tasks)), "icon": "📋", "color": "#4F46E5"},
        {"label": "In Progress", "value": str(len(doing_tasks)), "icon": "⚙️", "color": "#F59E0B"},
        {"label": "Completed", "value": str(len(done_tasks)), "icon": "✅", "color": "#22C55E"},
    ])

    st.divider()

    tab_kanban, tab_chat = st.tabs(["🗂️ Kanban Board", "💬 Subgroup Chat"])

    with tab_kanban:
        render_kanban(sg_id, user_id, members)

    with tab_chat:
        render_sg_chat(sg_id, user_id, user_name, messages)


def render_sg_chat(sg_id: int, user_id: int, user_name: str, messages: list):
    st.markdown("### 💬 Subgroup Chat")

    display_messages = list(reversed(messages[:50]))

    chat_container = st.container(height=380)
    with chat_container:
        if not display_messages:
            render_empty_state("💬", "No messages yet", "Start coordinating with your subgroup!")
        for msg in display_messages:
            is_ai = bool(msg.get("is_ai"))
            role = "assistant" if is_ai else "user"
            name = "🤖 SankalpAI" if is_ai else msg.get("user_name", "Unknown")
            with st.chat_message(role):
                st.markdown(f"**{name}** · *{msg.get('created_at','')[:16]}*")
                st.markdown(msg["content"])

    prompt = st.chat_input("Chat with your subgroup...", key="sg_chat_input")
    if prompt:
        add_subgroup_message(sg_id, user_id, prompt)
        if prompt.startswith("/ai ") or "@ai" in prompt.lower():
            query = prompt.replace("/ai ", "").replace("@ai", "").strip()
            with st.spinner("SankalpAI is responding..."):
                ai_response = chat_with_ai(query)
            add_subgroup_message(sg_id, user_id, f"🤖 **SankalpAI:** {ai_response}", is_ai=True)
        st.rerun()


if __name__ == "__main__":
    main()
