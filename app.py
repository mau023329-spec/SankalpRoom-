"""
SankalpRoom — AI-Powered Team Collaboration Platform
Run: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="SankalpRoom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",   # collapsed by default → mobile friendly
)

from database.db import init_db
from auth.auth import is_logged_in, render_auth_page, logout
from rooms.rooms import (
    get_user_rooms, get_room, get_room_members,
    get_room_subgroups, get_subgroup, get_subgroup_members,
    create_room, join_room, create_subgroup, join_subgroup,
    is_room_member, is_subgroup_member,
    add_room_message, get_room_messages,
    add_subgroup_message, get_subgroup_messages,
)
from ideas.ideas import get_room_ideas, render_ideas_panel
from tasks.tasks import render_kanban, get_subgroup_tasks
from ai.ai_assistant import render_ai_panel, chat_with_ai
from dm.dm import render_dm_page, open_dm_with, get_inbox

init_db()

# ══════════════════════════════════════════════════════════════════
# GLOBAL CSS  — desktop + mobile responsive
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 14px; }
.stApp { background: #080A0F !important; color: #CBD5E1; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0C0E14 !important;
    border-right: 1px solid #1C2030 !important;
    min-width: 240px !important;
    max-width: 280px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    color: #64748B !important; text-align: left !important;
    border-radius: 8px !important; font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.875rem !important;   /* bigger tap target */
    width: 100% !important; transition: all 0.1s !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 40px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #131720 !important; color: #E2E8F0 !important;
    border-left: 2px solid #6366F1 !important;
}

/* ── Typography ── */
h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; color:#F1F5F9 !important; letter-spacing:-0.02em !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0F1218 !important; border: 1px solid #1E2533 !important;
    color: #E2E8F0 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;       /* 16px prevents iOS zoom */
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366F1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stTextInput > label, .stTextArea > label,
.stSelectbox > label, .stMultiSelect > label {
    color: #64748B !important; font-size: 0.72rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div { background:#0F1218 !important; border:1px solid #1E2533 !important; border-radius:8px !important; color:#E2E8F0 !important; }
.stMultiSelect > div > div { background:#0F1218 !important; border:1px solid #1E2533 !important; border-radius:8px !important; }

/* ── Buttons — bigger tap targets on all screens ── */
.stButton > button {
    background: #0F1218 !important; border: 1px solid #1E2533 !important;
    color: #94A3B8 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.1rem !important;
    min-height: 40px !important;        /* 40px min tap target */
    transition: all 0.12s ease !important;
}
.stButton > button:hover { background:#131720 !important; border-color:#2D3650 !important; color:#E2E8F0 !important; }
.stButton > button[kind="primary"] {
    background: #6366F1 !important; border-color: #6366F1 !important;
    color: #fff !important; font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.25) !important;
}
.stButton > button[kind="primary"]:hover { background:#4F52D9 !important; box-shadow:0 4px 20px rgba(99,102,241,0.4) !important; }

/* ── Tabs — scrollable on mobile ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1C2030 !important;
    gap: 0 !important;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #475569 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.7rem 1.1rem !important;
    min-height: 42px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; margin-bottom: -1px !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] { background:transparent !important; color:#6366F1 !important; border-bottom:2px solid #6366F1 !important; font-weight:600 !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] { background:#0C0E14 !important; border:1px solid #1C2030 !important; border-radius:10px !important; padding:0.875rem 1rem !important; margin-bottom:0.5rem !important; }
[data-testid="stChatInput"] > div { background:#0C0E14 !important; border:1px solid #1C2030 !important; border-radius:10px !important; }
[data-testid="stChatInput"] textarea { background:transparent !important; color:#E2E8F0 !important; font-family:'Inter',sans-serif !important; font-size:1rem !important; }

/* ── Forms ── */
[data-testid="stForm"] { background:#0C0E14 !important; border:1px solid #1C2030 !important; border-radius:10px !important; padding:1.25rem !important; }
[data-testid="stExpander"] { background:#0C0E14 !important; border:1px solid #1C2030 !important; border-radius:8px !important; }
[data-testid="stExpander"] summary { color:#64748B !important; font-size:0.85rem !important; min-height:44px !important; display:flex !important; align-items:center !important; }

.stAlert { border-radius:8px !important; font-family:'Inter',sans-serif !important; font-size:0.875rem !important; }
hr { border:none !important; border-top:1px solid #1C2030 !important; margin:0.75rem 0 !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#1C2030; border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:#6366F1; }

/* ════════════════════════════════════════════════
   MOBILE  ≤ 768px
   Stack every st.columns grid to single column
   ════════════════════════════════════════════════ */
@media (max-width: 768px) {

    /* Block container padding */
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    /* Stack ALL column grids vertically */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* Bigger touch targets */
    .stButton > button {
        min-height: 48px !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
        width: 100% !important;
    }

    /* Inputs — 16px stops iOS zoom */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
    }

    /* Topbar — hide username text, keep avatar */
    .tb-username { display: none !important; }
    .tb-crumb    { display: none !important; }

    /* Stat card numbers smaller on mobile */
    .sc-value { font-size: 1.3rem !important; }

    /* Chat containers — shorter on mobile */
    [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
    }

    /* Kanban — full width columns */
    .kanban-col { min-width: 100% !important; }

    /* DM page — hide inbox panel, show full conversation */
    .dm-inbox { display: none; }
    .dm-conv  { width: 100% !important; }
}

@media (max-width: 480px) {
    html, body, [class*="css"] { font-size: 13px; }
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════

def topbar(user_name, room_name=None, sg_name=None):
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    crumb = ""
    if room_name:
        crumb += f'<span class="tb-crumb" style="color:#2D3650;margin:0 0.3rem;">/</span><span class="tb-crumb" style="color:#64748B;font-size:0.8rem;font-family:Inter,sans-serif;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:inline-block;vertical-align:middle;">{room_name}</span>'
    if sg_name:
        crumb += f'<span class="tb-crumb" style="color:#2D3650;margin:0 0.3rem;">/</span><span class="tb-crumb" style="color:#818CF8;font-size:0.8rem;font-family:Inter,sans-serif;max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:inline-block;vertical-align:middle;">{sg_name}</span>'
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
        padding:0 1rem;height:52px;background:#080A0F;
        border-bottom:1px solid #1C2030;margin-bottom:1.25rem;">
        <div style="display:flex;align-items:center;min-width:0;overflow:hidden;">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:1rem;
                font-weight:700;color:#6366F1;letter-spacing:-0.02em;
                margin-right:0.25rem;white-space:nowrap;">⚡ SankalpRoom</span>
            {crumb}
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;flex-shrink:0;">
            <div style="width:32px;height:32px;border-radius:50%;
                background:linear-gradient(135deg,#6366F1,#8B5CF6);
                display:flex;align-items:center;justify-content:center;
                font-size:0.68rem;font-weight:700;color:white;
                font-family:'Space Grotesk',sans-serif;flex-shrink:0;">{initials}</div>
            <span class="tb-username" style="color:#475569;font-size:0.8rem;font-family:'Inter',sans-serif;white-space:nowrap;">{user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def stat_cards(stats):
    # On mobile these stack via CSS; on desktop show as columns
    cols = st.columns(len(stats))
    for i, s in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="background:#0C0E14;border:1px solid #1C2030;border-radius:8px;
                padding:0.875rem 1rem;margin-bottom:0.75rem;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{s.get('color','#6366F1')};"></div>
                <div class="sc-value" style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;
                    font-weight:700;color:{s.get('color','#6366F1')};line-height:1;margin-bottom:0.25rem;">{s['value']}</div>
                <div style="color:#475569;font-size:0.68rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.06em;font-family:'Inter',sans-serif;">{s['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def member_avatars(members, user_id=None, clickable=False):
    html = ""
    for m in members[:6]:
        c   = m.get("avatar_color", "#6366F1")
        ini = "".join(w[0].upper() for w in m["name"].split()[:2])
        html += f'<div title="{m["name"]}" style="width:30px;height:30px;border-radius:50%;background:{c};color:white;display:inline-flex;align-items:center;justify-content:center;font-size:0.62rem;font-weight:700;border:2px solid #080A0F;margin-right:-6px;font-family:Space Grotesk,sans-serif;">{ini}</div>'
    if len(members) > 6:
        html += f'<div style="width:30px;height:30px;border-radius:50%;background:#1C2030;color:#64748B;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;border:2px solid #080A0F;margin-right:-6px;">+{len(members)-6}</div>'
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:0.5rem;">{html}</div>', unsafe_allow_html=True)

    if clickable and user_id:
        others = [m for m in members if m["id"] != user_id]
        if others:
            st.markdown('<div style="color:#334155;font-size:0.7rem;font-family:Inter,sans-serif;margin:0.4rem 0 0.25rem;">Message a member:</div>', unsafe_allow_html=True)
            # Max 3 per row on mobile
            n = min(len(others), 3)
            cols = st.columns(n)
            for i, m in enumerate(others[:n]):
                with cols[i]:
                    ini = "".join(w[0].upper() for w in m["name"].split()[:2])
                    if st.button(f"💬 {ini}", key=f"dm_av_{m['id']}", use_container_width=True, help=f"DM {m['name']}"):
                        open_dm_with(m["id"])
                        st.rerun()


def empty_state(icon, title, sub):
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;border:1px dashed #1C2030;border-radius:10px;margin:1rem 0;">
        <div style="font-size:2rem;margin-bottom:0.75rem;opacity:0.4;">{icon}</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:600;color:#334155;margin-bottom:0.35rem;">{title}</div>
        <div style="color:#1E293B;font-size:0.8rem;font-family:'Inter',sans-serif;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def section_hdr(title, subtitle=""):
    sub_html = f'<div style="color:#475569;font-size:0.78rem;margin-top:0.2rem;font-family:Inter,sans-serif;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:0.875rem;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#F1F5F9;letter-spacing:-0.01em;">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def invite_pill(code):
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:0.5rem;
        background:#0C0E14;border:1px solid #1C2030;border-radius:8px;
        padding:0.5rem 0.875rem;margin-bottom:0.5rem;">
        <span style="color:#334155;font-size:0.68rem;font-weight:600;text-transform:uppercase;
            letter-spacing:0.08em;font-family:'Inter',sans-serif;">Invite</span>
        <span style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;
            font-weight:700;color:#6366F1;letter-spacing:0.1em;">{code}</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

def build_sidebar(user_id):
    with st.sidebar:
        st.markdown("""
        <div style="padding:1rem 1rem 0.875rem;border-bottom:1px solid #1C2030;margin-bottom:0.75rem;">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;
                font-weight:700;color:#6366F1;letter-spacing:-0.02em;">⚡ SankalpRoom</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⌂  Home", key="sb_home", use_container_width=True):
            st.session_state.pop("current_room", None)
            st.session_state.pop("current_subgroup", None)
            st.session_state.pop("active_view", None)
            st.rerun()

        inbox        = get_inbox(user_id)
        total_unread = sum(c.get("unread", 0) for c in inbox)
        dm_label     = f"💬  Messages  ·  {total_unread}" if total_unread else "💬  Messages"
        if st.button(dm_label, key="sb_dm", use_container_width=True):
            st.session_state["active_view"] = "dm"
            st.session_state.pop("current_room", None)
            st.session_state.pop("current_subgroup", None)
            st.rerun()

        st.divider()
        st.markdown('<div style="color:#334155;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;padding:0.25rem 0.25rem 0.4rem;font-family:Inter,sans-serif;">Rooms</div>', unsafe_allow_html=True)

        rooms = get_user_rooms(user_id)
        if not rooms:
            st.markdown('<div style="color:#1E293B;font-size:0.8rem;padding:0.25rem 0.75rem;font-family:Inter,sans-serif;">No rooms yet</div>', unsafe_allow_html=True)
        for r in rooms:
            prefix = "◆ " if r["role"] == "admin" else "◇ "
            if st.button(f"{prefix}{r['name']}", key=f"sb_r_{r['id']}", use_container_width=True):
                st.session_state["current_room"] = r["id"]
                st.session_state.pop("current_subgroup", None)
                st.session_state.pop("active_view", None)
                st.rerun()

        cur_room = st.session_state.get("current_room")
        if cur_room:
            sgs = get_room_subgroups(cur_room)
            if sgs:
                st.markdown('<div style="color:#334155;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;padding:0.75rem 0.25rem 0.35rem;font-family:Inter,sans-serif;">Subgroups</div>', unsafe_allow_html=True)
                for sg in sgs:
                    dot = "• " if is_subgroup_member(sg["id"], user_id) else "  "
                    if st.button(f"{dot}{sg['name']}", key=f"sb_sg_{sg['id']}", use_container_width=True):
                        st.session_state["current_subgroup"] = sg["id"]
                        st.session_state.pop("active_view", None)
                        st.rerun()

        st.divider()

        with st.expander("＋ New room"):
            with st.form("crf", border=False):
                rn = st.text_input("Name", placeholder="e.g. Q2 Launch")
                rd = st.text_area("Purpose", placeholder="What's this room for?", height=80)
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if rn:
                        create_room(rn, rd, user_id)
                        st.rerun()

        with st.expander("→ Join room"):
            with st.form("jrf", border=False):
                ic = st.text_input("Invite code", placeholder="ABC12345")
                if st.form_submit_button("Join", type="primary", use_container_width=True):
                    if ic:
                        r, err = join_room(ic, user_id)
                        if err == "already_member": st.info("Already a member!")
                        elif err: st.error(err)
                        else:
                            st.session_state["current_room"] = r["id"]
                            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

def render_dashboard(user_id, user_name):
    topbar(user_name)
    first = user_name.split()[0]
    st.markdown(f"""
    <div style="padding:0.5rem 0 1.25rem;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;
            font-weight:700;color:#F1F5F9;letter-spacing:-0.03em;margin-bottom:0.3rem;">
            Good to see you, {first}.</div>
        <div style="color:#334155;font-size:0.85rem;font-family:'Inter',sans-serif;">
            Pick a room to continue, or create a new one.</div>
    </div>
    """, unsafe_allow_html=True)

    rooms = get_user_rooms(user_id)
    if not rooms:
        empty_state("⚡", "No rooms yet", "Create a room or join one with an invite code.")
        return

    stat_cards([
        {"label": "Rooms",         "value": str(len(rooms)),                                           "color": "#6366F1"},
        {"label": "As admin",      "value": str(sum(1 for r in rooms if r["role"] == "admin")),        "color": "#8B5CF6"},
        {"label": "Total members", "value": str(sum(r["member_count"] for r in rooms)),                "color": "#22C55E"},
    ])

    section_hdr("Your Rooms")

    # 1 col on mobile, 2 on tablet, 3 on desktop — we use 2 cols as safe middle ground
    cols = st.columns(2)
    for i, room in enumerate(rooms):
        with cols[i % 2]:
            is_admin   = room["role"] == "admin"
            role_color = "#6366F1" if is_admin else "#334155"
            role_text  = "admin"   if is_admin else "member"
            st.markdown(f"""
            <div style="background:#0C0E14;border:1px solid #1C2030;border-radius:10px;
                padding:1rem 1.1rem 0.875rem;margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;
                        font-weight:700;color:#E2E8F0;flex:1;margin-right:0.5rem;">{room['name']}</div>
                    <span style="background:{role_color}18;color:{role_color};border:1px solid {role_color}25;
                        border-radius:4px;padding:1px 7px;font-size:0.62rem;font-weight:600;
                        font-family:'Inter',sans-serif;text-transform:uppercase;
                        letter-spacing:0.06em;white-space:nowrap;">{role_text}</span>
                </div>
                <div style="color:#334155;font-size:0.78rem;font-family:'Inter',sans-serif;
                    margin-bottom:0.625rem;min-height:1rem;">{room.get('description','') or '—'}</div>
                <div style="color:#1E293B;font-size:0.7rem;font-family:'Inter',sans-serif;">
                    {room['member_count']} member{'s' if room['member_count'] != 1 else ''}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open →", key=f"d_open_{room['id']}", use_container_width=True):
                st.session_state["current_room"] = room["id"]
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# ROOM VIEW
# ══════════════════════════════════════════════════════════════════

def render_room_view(room_id, user_id, user_name):
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

    topbar(user_name, room["name"])

    # Room header — stacks on mobile via CSS
    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.markdown(f"""
        <div style="margin-bottom:0.75rem;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;
                color:#F1F5F9;letter-spacing:-0.02em;margin-bottom:0.2rem;">{room['name']}</div>
            <div style="color:#334155;font-size:0.8rem;font-family:'Inter',sans-serif;">
                {room.get('description','') or ''}</div>
        </div>
        """, unsafe_allow_html=True)
        member_avatars(members, user_id=user_id, clickable=True)
    with col_r:
        invite_pill(room["invite_code"])

    stat_cards([
        {"label": "Members",   "value": str(len(members)),                                             "color": "#6366F1"},
        {"label": "Ideas",     "value": str(len(ideas)),                                               "color": "#8B5CF6"},
        {"label": "Selected",  "value": str(len([i for i in ideas if i["status"] == "Selected"])),     "color": "#22C55E"},
        {"label": "Subgroups", "value": str(len(subgroups)),                                           "color": "#F59E0B"},
    ])

    t_chat, t_ideas, t_sgs, t_ai = st.tabs(["💬 Chat", "💡 Ideas", "🔬 Subgroups", "🤖 AI"])
    with t_chat:  render_room_chat(room_id, user_id, messages)
    with t_ideas: render_ideas_panel(room_id, user_id)
    with t_sgs:   render_subgroups_panel(room_id, user_id, subgroups)
    with t_ai:    render_ai_panel(room_id, ideas, messages, subgroups)


def render_room_chat(room_id, user_id, messages):
    section_hdr("Discussion", "Type /ai <question> for an inline AI response")
    box = st.container(height=380)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬", "No messages yet", "Start the conversation.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#818CF8" if is_ai else "#CBD5E1"
                st.markdown(f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;font-size:0.82rem;color:{nc};">{who}</span> <span style="color:#1E293B;font-size:0.7rem;">{str(msg.get("created_at",""))[:16]}</span>', unsafe_allow_html=True)
                st.markdown(msg["content"])
    prompt = st.chat_input("Message the team…", key="room_chat_input")
    if prompt:
        add_room_message(room_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            with st.spinner("Thinking…"):
                reply = chat_with_ai(prompt[4:].strip())
            add_room_message(room_id, user_id, f"**SankalpAI:** {reply}", is_ai=True)
        st.rerun()


def render_subgroups_panel(room_id, user_id, subgroups):
    col_h, col_btn = st.columns([3, 1])
    with col_h:
        section_hdr("Subgroups", "Execution spaces for selected ideas")
    with col_btn:
        if st.button("＋ New", type="primary", use_container_width=True, key="new_sg"):
            st.session_state["show_sg_form"] = not st.session_state.get("show_sg_form", False)

    if st.session_state.get("show_sg_form"):
        with st.form("sgf", border=True):
            sg_name = st.text_input("Subgroup name", placeholder="e.g. Design Squad")
            sg_desc = st.text_area("Purpose", height=72)
            c1, c2  = st.columns(2)
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
        empty_state("🔬", "No subgroups yet", "Create one to start executing ideas.")
        return

    # 1 col on mobile (CSS stacks), 2 cols here
    cols = st.columns(2)
    for i, sg in enumerate(subgroups):
        with cols[i % 2]:
            color     = sg.get("color", "#6366F1")
            is_member = is_subgroup_member(sg["id"], user_id)
            st.markdown(f"""
            <div style="background:#0C0E14;border:1px solid #1C2030;border-left:3px solid {color};
                border-radius:10px;padding:1rem 1rem 0.875rem;margin-bottom:0.5rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:700;
                    color:#E2E8F0;margin-bottom:0.3rem;">{sg['name']}</div>
                <div style="color:#334155;font-size:0.76rem;font-family:'Inter',sans-serif;
                    margin-bottom:0.625rem;">{sg.get('description','') or 'Execution subgroup'}</div>
                <div style="display:flex;gap:0.875rem;font-size:0.7rem;color:#1E293B;font-family:'Inter',sans-serif;flex-wrap:wrap;">
                    <span>{sg['member_count']} members</span>
                    <span>{sg['task_count']} tasks</span>
                    {'<span style="color:#22C55E;font-weight:600;">✓ joined</span>' if is_member else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            btn_cols = st.columns(2) if not is_member else st.columns(1)
            with btn_cols[0]:
                if st.button("Open", key=f"osg_{sg['id']}", use_container_width=True):
                    if not is_member: join_subgroup(sg["id"], user_id)
                    st.session_state["current_subgroup"] = sg["id"]
                    st.rerun()
            if not is_member:
                with btn_cols[1]:
                    if st.button("Join", key=f"jsg_{sg['id']}", use_container_width=True):
                        join_subgroup(sg["id"], user_id)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════
# SUBGROUP VIEW
# ══════════════════════════════════════════════════════════════════

def render_subgroup_view(sg_id, room_id, user_id, user_name):
    sg   = get_subgroup(sg_id)
    room = get_room(room_id)
    if not sg:
        st.session_state.pop("current_subgroup", None)
        st.rerun()
        return

    members  = get_subgroup_members(sg_id)
    tasks    = get_subgroup_tasks(sg_id)
    messages = get_subgroup_messages(sg_id)
    color    = sg.get("color", "#6366F1")

    topbar(user_name, room["name"] if room else "Room", sg["name"])

    col_back, col_info = st.columns([1, 4])
    with col_back:
        if st.button("← Back", key="sg_back"):
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;
                font-weight:700;color:{color};">{sg['name']}</span>
            <span style="color:#334155;font-size:0.78rem;font-family:'Inter',sans-serif;
                margin-left:0.625rem;">{sg.get('description','')}</span>
        </div>
        """, unsafe_allow_html=True)

    done  = [t for t in tasks if t["status"] == "done"]
    doing = [t for t in tasks if t["status"] == "doing"]
    stat_cards([
        {"label": "Members",    "value": str(len(members)), "color": color},
        {"label": "Tasks",      "value": str(len(tasks)),   "color": "#6366F1"},
        {"label": "In progress","value": str(len(doing)),   "color": "#F59E0B"},
        {"label": "Done",       "value": str(len(done)),    "color": "#22C55E"},
    ])

    t_kanban, t_chat = st.tabs(["🗂 Kanban", "💬 Chat"])
    with t_kanban: render_kanban(sg_id, user_id, members)
    with t_chat:   render_sg_chat(sg_id, user_id, messages)


def render_sg_chat(sg_id, user_id, messages):
    section_hdr("Subgroup Chat", "Type /ai <question> for AI help")
    box = st.container(height=360)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬", "No messages yet", "Coordinate with your subgroup.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#818CF8" if is_ai else "#CBD5E1"
                st.markdown(f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;font-size:0.82rem;color:{nc};">{who}</span> <span style="color:#1E293B;font-size:0.7rem;">{str(msg.get("created_at",""))[:16]}</span>', unsafe_allow_html=True)
                st.markdown(msg["content"])
    prompt = st.chat_input("Message your subgroup…", key="sg_chat_input")
    if prompt:
        add_subgroup_message(sg_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            with st.spinner("Thinking…"):
                reply = chat_with_ai(prompt[4:].strip())
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

    active_view = st.session_state.get("active_view")
    cur_room    = st.session_state.get("current_room")
    cur_sg      = st.session_state.get("current_subgroup")

    if active_view == "dm":
        topbar(user_name)
        render_dm_page(user_id)
    elif not cur_room:
        render_dashboard(user_id, user_name)
    elif cur_sg:
        render_subgroup_view(cur_sg, cur_room, user_id, user_name)
    else:
        render_room_view(cur_room, user_id, user_name)


if __name__ == "__main__":
    main()
