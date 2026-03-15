"""
SankalpRoom — AI-Powered Team Collaboration
Mobile-first. Fast. Clean.
"""

import html as _h
import streamlit as st

st.set_page_config(
    page_title="SankalpRoom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from database.db import init_db
from auth.auth import is_logged_in, render_auth_page, logout
from rooms.rooms import (
    get_user_rooms, get_room, get_room_members,
    get_room_subgroups, get_subgroup, get_subgroup_members,
    get_room_data,
    create_room, join_room, create_subgroup, join_subgroup,
    delete_room, leave_room, remove_member,
    is_room_member, is_subgroup_member, is_room_admin,
    add_room_message, get_room_messages,
    add_subgroup_message, get_subgroup_messages,
)
from ideas.ideas import get_room_ideas, render_ideas_panel
from tasks.tasks import render_kanban, get_subgroup_tasks
from ai.ai_assistant import render_ai_panel, chat_with_ai
from dm.dm import render_dm_page, open_dm_with, get_inbox

init_db()

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Pastel creative theme ── */
/* Background: warm off-white cream, not cold black */
.stApp { background: #FAF8F5 !important; color: #2D2A26; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Open sidebar"],
button[aria-label="Close sidebar"] { display: none !important; }

.block-container {
    padding-top: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── warm white */
[data-testid="stSidebar"] {
    background: #FFF8F0 !important;
    border-right: 1px solid #EDE8E0 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    color: #7C6F5E !important; text-align: left !important;
    border-radius: 8px !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 0.625rem 0.875rem !important;
    width: 100% !important; min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F5EFE6 !important; color: #2D2A26 !important;
}

/* ── Main nav pills — pastel lavender ── */
.main-nav .stTabs [data-baseweb="tab-list"] {
    background: #F0EBF8 !important;
    border: 1px solid #DDD5EE !important;
    border-radius: 14px !important; padding: 4px !important; gap: 3px !important;
    overflow-x: auto !important; flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important; scrollbar-width: none !important;
    margin-bottom: 1.25rem !important;
}
.main-nav .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.main-nav .stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #9B8EC4 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 0.5rem 1rem !important;
    min-height: 38px !important; border-bottom: none !important;
    border-radius: 10px !important; white-space: nowrap !important; flex: 1 !important;
}
.main-nav .stTabs [aria-selected="true"] {
    background: #7C5CCC !important; color: #fff !important;
    font-weight: 600 !important; border-bottom: none !important;
    box-shadow: 0 2px 10px rgba(124,92,204,0.3) !important;
}

/* ── Inner room tabs — warm underline ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #EDE8E0 !important;
    gap: 0 !important; overflow-x: auto !important; flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important; scrollbar-width: none !important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #A89880 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 0.7rem 1rem !important;
    min-height: 44px !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; margin-bottom: -1px !important; white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: #7C5CCC !important;
    border-bottom: 2px solid #7C5CCC !important; font-weight: 600 !important;
}

/* ── Inputs — warm white ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFBF7 !important; border: 1.5px solid #E8E0D4 !important;
    color: #2D2A26 !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-size: 16px !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7C5CCC !important;
    box-shadow: 0 0 0 3px rgba(124,92,204,0.12) !important;
}
.stTextInput > label, .stTextArea > label,
.stSelectbox > label, .stMultiSelect > label {
    color: #A89880 !important; font-size: 0.7rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}
.stSelectbox > div > div {
    background: #FFFBF7 !important; border: 1.5px solid #E8E0D4 !important;
    border-radius: 10px !important; color: #2D2A26 !important;
}

/* ── Buttons — warm pastel ── */
.stButton > button {
    background: #FFFBF7 !important; border: 1.5px solid #E8E0D4 !important;
    color: #6B5E4E !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 0.6rem 1rem !important;
    min-height: 44px !important; transition: all 0.1s ease !important;
}
.stButton > button:hover {
    background: #F5EFE6 !important; border-color: #D4C9B8 !important;
    color: #2D2A26 !important;
}
.stButton > button[kind="primary"] {
    background: #7C5CCC !important; border-color: #7C5CCC !important;
    color: #fff !important; font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(124,92,204,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #6A4DB8 !important;
    box-shadow: 0 4px 16px rgba(124,92,204,0.35) !important;
}

/* ── Chat ── warm card ── */
[data-testid="stChatMessage"] {
    background: #FFFBF7 !important; border: 1px solid #EDE8E0 !important;
    border-radius: 12px !important; padding: 0.75rem 1rem !important; margin-bottom: 0.4rem !important;
}
[data-testid="stChatInput"] > div {
    background: #FFFBF7 !important; border: 1.5px solid #E8E0D4 !important; border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: #2D2A26 !important; font-size: 16px !important;
}

/* ── Forms / Expanders ── */
[data-testid="stForm"] {
    background: #FFFBF7 !important; border: 1.5px solid #EDE8E0 !important;
    border-radius: 12px !important; padding: 1.1rem !important;
}
[data-testid="stExpander"] {
    background: #FFFBF7 !important; border: 1.5px solid #EDE8E0 !important; border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #7C6F5E !important; font-size: 0.875rem !important; min-height: 44px !important;
}
.stAlert { border-radius: 10px !important; }
hr { border: none !important; border-top: 1px solid #EDE8E0 !important; margin: 0.75rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #DDD5EE; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7C5CCC; }

/* ══════════════════════════════════════
   MOBILE ≤ 768px
   ══════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
    [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 0.35rem !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }
    .stButton > button { min-height: 48px !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════

def mini_header(user_name):
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    col_brand, col_user = st.columns([5, 1])
    with col_brand:
        st.markdown(
            '<div style="padding:0.75rem 0 0.5rem;">'
            '<span style="font-family:Space Grotesk,sans-serif;font-size:1rem;'
            'font-weight:700;color:#7C5CCC;">⚡ SankalpRoom</span></div>',
            unsafe_allow_html=True,
        )
    with col_user:
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end;padding:0.6rem 0;">'
            f'<div style="width:34px;height:34px;border-radius:50%;'
            f'background:linear-gradient(135deg,#7C5CCC,#C084A0);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.68rem;font-weight:700;color:white;">{initials}</div></div>',
            unsafe_allow_html=True,
        )


def room_header(room, user_name):
    mini_header(user_name)
    col_back, col_name = st.columns([1, 5])
    with col_back:
        if st.button("←", key="rh_back", use_container_width=True):
            st.session_state.pop("current_room", None)
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_name:
        st.markdown(
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.05rem;'
            f'font-weight:700;color:#1A1714;padding:0.5rem 0;">{_h.escape(room["name"])}</div>',
            unsafe_allow_html=True,
        )


def sg_header(sg, room, user_name):
    mini_header(user_name)
    col_back, col_name = st.columns([1, 5])
    with col_back:
        if st.button("←", key="sgh_back", use_container_width=True):
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_name:
        color = sg.get("color", "#7C5CCC")
        st.markdown(
            f'<div style="padding:0.1rem 0 0;">'
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.75rem;color:#7C6F5E;">'
            f'{_h.escape(room["name"] if room else "")}</div>'
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:1rem;'
            f'font-weight:700;color:{color};">{_h.escape(sg["name"])}</div></div>',
            unsafe_allow_html=True,
        )


def stat_cards(stats):
    cols = st.columns(len(stats))
    for i, s in enumerate(stats):
        with cols[i]:
            c = s.get("color", "#7C5CCC")
            st.markdown(
                f'<div style="background:#FFFBF7;border:1px solid #EDE8E0;border-radius:8px;'
                f'padding:0.75rem 0.875rem;margin-bottom:0.75rem;position:relative;overflow:hidden;">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:2px;background:{c};"></div>'
                f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.4rem;font-weight:700;'
                f'color:{c};line-height:1;margin-bottom:0.2rem;">{s["value"]}</div>'
                f'<div style="color:#7C6F5E;font-size:0.65rem;font-weight:600;text-transform:uppercase;'
                f'letter-spacing:0.06em;font-family:Inter,sans-serif;">{s["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def empty_state(icon, title, sub):
    st.markdown(
        f'<div style="text-align:center;padding:3rem 1rem;border:1px dashed #EDE8E0;'
        f'border-radius:10px;margin:0.75rem 0;">'
        f'<div style="font-size:2rem;margin-bottom:0.75rem;opacity:0.35;">{icon}</div>'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:600;'
        f'color:#B8A898;margin-bottom:0.3rem;">{title}</div>'
        f'<div style="color:#C8B8A8;font-size:0.78rem;font-family:Inter,sans-serif;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_hdr(title, subtitle=""):
    sub_html = (f'<div style="color:#7C6F5E;font-size:0.76rem;margin-top:0.15rem;'
                f'font-family:Inter,sans-serif;">{subtitle}</div>') if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:0.875rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;font-weight:700;'
        f'color:#1A1714;letter-spacing:-0.01em;">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def invite_pill(code):
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;'
        f'background:#FFFBF7;border:1px solid #EDE8E0;border-radius:8px;'
        f'padding:0.4rem 0.75rem;margin-bottom:0.5rem;">'
        f'<span style="color:#B8A898;font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-family:Inter,sans-serif;">Invite</span>'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;'
        f'font-weight:700;color:#7C5CCC;letter-spacing:0.1em;">{code}</span></div>',
        unsafe_allow_html=True,
    )


def room_card_ui(room):
    is_admin = room["role"] == "admin"
    rc = "#7C5CCC" if is_admin else "#B8A898"
    rt = "admin" if is_admin else "member"
    st.markdown(
        f'<div style="background:#FFFBF7;border:1px solid #EDE8E0;border-radius:10px;'
        f'padding:1rem;margin-bottom:0.4rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.35rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'color:#2D2A26;flex:1;margin-right:0.5rem;">{_h.escape(room["name"])}</div>'
        f'<span style="background:{rc}18;color:{rc};border:1px solid {rc}25;border-radius:4px;'
        f'padding:1px 7px;font-size:0.62rem;font-weight:600;font-family:Inter,sans-serif;'
        f'text-transform:uppercase;white-space:nowrap;">{rt}</span>'
        f'</div>'
        f'<div style="color:#B8A898;font-size:0.76rem;font-family:Inter,sans-serif;margin-bottom:0.4rem;">'
        f'{_h.escape(room.get("description","") or "—")}</div>'
        f'<div style="color:#C8B8A8;font-size:0.7rem;font-family:Inter,sans-serif;">'
        f'{room["member_count"]} member{"s" if room["member_count"]!=1 else ""}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def sg_card_ui(sg, is_member):
    color  = sg.get("color","#7C5CCC")
    joined = '<span style="color:#4CA86A;font-weight:600;font-size:0.7rem;">✓ joined</span>' if is_member else ""
    st.markdown(
        f'<div style="background:#FFFBF7;border:1px solid #EDE8E0;border-left:3px solid {color};'
        f'border-radius:10px;padding:1rem;margin-bottom:0.4rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.88rem;font-weight:700;'
        f'color:#2D2A26;margin-bottom:0.25rem;">{_h.escape(sg["name"])}</div>'
        f'<div style="color:#B8A898;font-size:0.75rem;font-family:Inter,sans-serif;margin-bottom:0.4rem;">'
        f'{_h.escape(sg.get("description","") or "Execution subgroup")}</div>'
        f'<div style="display:flex;gap:0.75rem;font-size:0.68rem;color:#C8B8A8;'
        f'font-family:Inter,sans-serif;align-items:center;">'
        f'<span>{sg["member_count"]} members</span><span>{sg["task_count"]} tasks</span>{joined}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def member_avatars(members, user_id=None, clickable=False):
    html = ""
    for m in members[:6]:
        c   = m.get("avatar_color","#7C5CCC")
        ini = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))
        html += (f'<div title="{_h.escape(m["name"])}" style="width:30px;height:30px;border-radius:50%;'
                 f'background:{c};color:white;display:inline-flex;align-items:center;'
                 f'justify-content:center;font-size:0.6rem;font-weight:700;'
                 f'border:2px solid #FAF8F5;margin-right:-6px;">{ini}</div>')
    if len(members) > 6:
        html += (f'<div style="width:30px;height:30px;border-radius:50%;background:#EDE8E0;'
                 f'color:#A89880;display:inline-flex;align-items:center;justify-content:center;'
                 f'font-size:0.6rem;border:2px solid #FAF8F5;margin-right:-6px;">+{len(members)-6}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:0.625rem;">{html}</div>',
                unsafe_allow_html=True)
    if clickable and user_id:
        others = [m for m in members if m["id"] != user_id][:4]
        if others:
            st.markdown(
                '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.06em;color:#A89880;font-family:Inter,sans-serif;'
                'margin-bottom:0.35rem;">Message a teammate</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(len(others))
            for i, m in enumerate(others):
                first_name = m["name"].split()[0]   # first name only — fits better
                with cols[i]:
                    if st.button(
                        f"💬 {first_name}",
                        key=f"dm_av_{m['id']}",
                        use_container_width=True,
                        help=f"Message {m['name']}",
                    ):
                        # Navigate to Messages tab and open conversation
                        st.session_state["dm_partner_id"] = m["id"]
                        # Clear room so main nav shows
                        st.session_state.pop("current_room", None)
                        st.session_state.pop("current_subgroup", None)
                        st.rerun()


def chat_refresh_btn(key: str):
    """Small 🔄 refresh button for chat panels."""
    col_sp, col_btn = st.columns([6, 1])
    with col_btn:
        if st.button("🔄", key=f"refresh_{key}", help="Refresh messages", use_container_width=True):
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

def build_sidebar(user_id):
    with st.sidebar:
        st.markdown(
            '<div style="padding:1rem 0.5rem 0.75rem;border-bottom:1px solid #EDE8E0;margin-bottom:0.5rem;">'
            '<span style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
            'color:#7C5CCC;">⚡ SankalpRoom</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("⌂  Home", key="sb_home", use_container_width=True):
            for k in ["current_room","current_subgroup","active_view"]: st.session_state.pop(k,None)
            st.rerun()

        inbox        = get_inbox(user_id)
        total_unread = sum(c.get("unread",0) for c in inbox)
        dm_label     = f"💬  Messages  ·  {total_unread}" if total_unread else "💬  Messages"
        if st.button(dm_label, key="sb_dm", use_container_width=True):
            st.session_state["active_view"] = "dm"
            for k in ["current_room","current_subgroup"]: st.session_state.pop(k,None)
            st.rerun()

        st.divider()
        st.caption("ROOMS")
        rooms = get_user_rooms(user_id)
        if not rooms: st.caption("No rooms yet")
        for r in rooms:
            prefix = "◆ " if r["role"] == "admin" else "◇ "
            if st.button(f"{prefix}{r['name']}", key=f"sb_r_{r['id']}", use_container_width=True):
                st.session_state["current_room"] = r["id"]
                for k in ["current_subgroup","active_view"]: st.session_state.pop(k,None)
                st.rerun()

        cur_room = st.session_state.get("current_room")
        if cur_room:
            sgs = get_room_subgroups(cur_room)
            if sgs:
                st.caption("SUBGROUPS")
                for sg in sgs:
                    dot = "• " if is_subgroup_member(sg["id"],user_id) else "  "
                    if st.button(f"{dot}{sg['name']}", key=f"sb_sg_{sg['id']}", use_container_width=True):
                        st.session_state["current_subgroup"] = sg["id"]
                        st.session_state.pop("active_view",None)
                        st.rerun()

        st.divider()
        with st.expander("＋ New room"):
            with st.form("crf", border=False):
                rn = st.text_input("Name", placeholder="e.g. Q2 Launch")
                rd = st.text_area("Purpose", height=72)
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if rn: create_room(rn, rd, user_id); st.rerun()

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
            logout(); st.rerun()


# ══════════════════════════════════════════════════════════════════
# MAIN NAV
# ══════════════════════════════════════════════════════════════════

def render_main_nav(user_id, user_name):
    inbox        = get_inbox(user_id)
    total_unread = sum(c.get("unread",0) for c in inbox)
    msg_label    = f"💬 Messages {total_unread}" if total_unread else "💬 Messages"

    mini_header(user_name)

    # If coming from a Quick DM click, default to Messages tab
    default_tab = 2 if st.session_state.get("dm_partner_id") else 0

    st.markdown('<div class="main-nav">', unsafe_allow_html=True)
    tabs = st.tabs(["⌂ Home", "🏠 Rooms", msg_label, "⚙ Account"])
    st.markdown('</div>', unsafe_allow_html=True)

    with tabs[0]: render_home_tab(user_id, user_name)
    with tabs[1]: render_rooms_tab(user_id)
    with tabs[2]: render_dm_page(user_id)
    with tabs[3]: render_account_tab(user_id, user_name)


def render_home_tab(user_id, user_name):
    first = user_name.split()[0]
    st.markdown(
        f'<div style="padding:0.5rem 0 1rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.4rem;font-weight:700;'
        f'color:#1A1714;letter-spacing:-0.03em;margin-bottom:0.2rem;">Hey, {_h.escape(first)} 👋</div>'
        f'<div style="color:#B8A898;font-size:0.85rem;font-family:Inter,sans-serif;">'
        f'Pick a room to continue.</div></div>',
        unsafe_allow_html=True,
    )
    rooms = get_user_rooms(user_id)
    if not rooms:
        empty_state("⚡", "No rooms yet", "Go to Rooms → create or join one.")
        return

    stat_cards([
        {"label":"Rooms",   "value":str(len(rooms)),                                          "color":"#7C5CCC"},
        {"label":"Admin",   "value":str(sum(1 for r in rooms if r["role"]=="admin")),         "color":"#C084A0"},
        {"label":"Members", "value":str(sum(r["member_count"] for r in rooms)),               "color":"#4CA86A"},
    ])
    section_hdr("Your rooms")
    for room in rooms:
        room_card_ui(room)
        if st.button("Open →", key=f"h_open_{room['id']}", use_container_width=True):
            st.session_state["current_room"] = room["id"]
            st.rerun()


def render_rooms_tab(user_id):
    section_hdr("Rooms", "Create a room or join one with an invite code.")
    rooms = get_user_rooms(user_id)
    if rooms:
        for room in rooms:
            room_card_ui(room)
            if st.button("Open →", key=f"r_open_{room['id']}", use_container_width=True):
                st.session_state["current_room"] = room["id"]
                st.rerun()
        st.divider()

    with st.expander("＋ Create new room"):
        with st.form("crf_tab", border=False):
            rn = st.text_input("Room name", placeholder="e.g. Q2 Launch")
            rd = st.text_area("Purpose", height=64)
            if st.form_submit_button("Create room", type="primary", use_container_width=True):
                if rn: create_room(rn, rd, user_id); st.rerun()

    with st.expander("→ Join with invite code"):
        with st.form("jrf_tab", border=False):
            ic = st.text_input("Invite code", placeholder="e.g. ABC12345")
            if st.form_submit_button("Join room", type="primary", use_container_width=True):
                if ic:
                    r, err = join_room(ic, user_id)
                    if err == "already_member": st.info("Already a member!")
                    elif err: st.error(err)
                    else:
                        st.session_state["current_room"] = r["id"]
                        st.rerun()


def render_account_tab(user_id, user_name):
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;'
        f'background:#FFFBF7;border:1px solid #EDE8E0;border-radius:12px;'
        f'padding:1.25rem;margin-bottom:1rem;">'
        f'<div style="width:52px;height:52px;border-radius:50%;flex-shrink:0;'
        f'background:linear-gradient(135deg,#7C5CCC,#C084A0);'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:1.1rem;font-weight:700;color:white;">{initials}</div>'
        f'<div>'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
        f'color:#1A1714;">{_h.escape(user_name)}</div>'
        f'<div style="color:#7C6F5E;font-size:0.78rem;font-family:Inter,sans-serif;">SankalpRoom member</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("Sign out", use_container_width=True):
        logout(); st.rerun()


# ══════════════════════════════════════════════════════════════════
# ROOM VIEW  — uses get_room_data() for batched loading
# ══════════════════════════════════════════════════════════════════

def render_room_view(room_id, user_id, user_name):
    # ONE batched call instead of 6+ separate queries
    data = get_room_data(room_id, user_id)
    if not data:
        st.error("Room not found or access denied.")
        st.session_state.pop("current_room", None)
        st.rerun()
        return

    room      = data["room"]
    members   = data["members"]
    subgroups = data["subgroups"]
    is_admin  = data["is_admin"]

    # Messages are never cached — always fresh
    ideas    = get_room_ideas(room_id)
    messages = get_room_messages(room_id)

    room_header(room, user_name)

    st.markdown(
        f'<div style="color:#B8A898;font-size:0.8rem;font-family:Inter,sans-serif;'
        f'margin-bottom:0.5rem;">{_h.escape(room.get("description","") or "")}</div>',
        unsafe_allow_html=True,
    )
    member_avatars(members, user_id=user_id, clickable=True)
    invite_pill(room["invite_code"])

    stat_cards([
        {"label":"Members",  "value":str(len(members)),                                          "color":"#7C5CCC"},
        {"label":"Ideas",    "value":str(len(ideas)),                                            "color":"#C084A0"},
        {"label":"Selected", "value":str(len([i for i in ideas if i["status"]=="Selected"])),    "color":"#4CA86A"},
        {"label":"Groups",   "value":str(len(subgroups)),                                        "color":"#D4873A"},
    ])

    tab_labels = ["💬 Chat", "💡 Ideas", "🔬 Groups", "🤖 AI", "⚙ Settings" if is_admin else "🚪 Leave"]
    tabs = st.tabs(tab_labels)
    with tabs[0]: render_room_chat(room_id, user_id, messages)
    with tabs[1]: render_ideas_panel(room_id, user_id)
    with tabs[2]: render_subgroups_panel(room_id, user_id, subgroups)
    with tabs[3]: render_ai_panel(room_id, ideas, messages, subgroups)
    with tabs[4]:
        if is_admin: render_room_settings(room_id, user_id, members)
        else:        render_leave_room(room_id, user_id)


def render_room_chat(room_id, user_id, messages):
    # Header row: title + refresh button
    c_hdr, c_btn = st.columns([6, 1])
    with c_hdr:
        section_hdr("Chat", "Tap 🔄 to check for new messages")
    with c_btn:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("🔄", key="rc_refresh", help="Refresh", use_container_width=True):
            st.rerun()

    box = st.container(height=360)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬", "No messages yet", "Start the conversation.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#9B7FE8" if is_ai else "#2D2A26"
                st.markdown(
                    f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                    f'font-size:0.82rem;color:{nc};">{_h.escape(who)}</span> '
                    f'<span style="color:#C8B8A8;font-size:0.7rem;">'
                    f'{str(msg.get("created_at",""))[:16]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(msg["content"])

    prompt = st.chat_input("Message the team…", key="room_chat_input")
    if prompt:
        add_room_message(room_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            with st.spinner("Thinking…"):
                reply = chat_with_ai(prompt[4:].strip())
            add_room_message(room_id, user_id, f"**SankalpAI:** {reply}", is_ai=True)
        st.rerun()


def render_room_settings(room_id, user_id, members):
    section_hdr("Room Settings", "Manage members and room options")

    st.markdown(
        '<div style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;font-weight:600;'
        'color:#1A1714;margin-bottom:0.5rem;">Members</div>',
        unsafe_allow_html=True,
    )
    for m in members:
        is_self  = m["id"] == user_id
        is_admin = m.get("role") == "admin"
        ini      = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))
        col_av, col_name, col_btn = st.columns([1, 5, 2])
        with col_av:
            st.markdown(
                f'<div style="width:32px;height:32px;border-radius:50%;background:{m["avatar_color"]};'
                f'color:white;display:flex;align-items:center;justify-content:center;'
                f'font-size:0.62rem;font-weight:700;margin-top:4px;">{ini}</div>',
                unsafe_allow_html=True,
            )
        with col_name:
            role_badge = (
                '<span style="background:#7C5CCC18;color:#7C5CCC;border-radius:4px;'
                'padding:1px 6px;font-size:0.62rem;margin-left:0.4rem;">admin</span>'
                if is_admin else ""
            )
            st.markdown(
                f'<div style="font-family:Inter,sans-serif;font-size:0.85rem;color:#2D2A26;'
                f'padding:0.5rem 0;">{_h.escape(m["name"])}{role_badge}</div>',
                unsafe_allow_html=True,
            )
        with col_btn:
            if not is_self and not is_admin:
                if st.button("Remove", key=f"rm_{m['id']}", use_container_width=True):
                    ok, err = remove_member(room_id, m["id"], user_id)
                    if ok: st.success(f"Removed {m['name']}"); st.rerun()
                    else:  st.error(err)

    st.divider()
    st.markdown(
        '<div style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;font-weight:600;'
        'color:#D45050;margin-bottom:0.5rem;">Danger Zone</div>'
        '<div style="color:#7C6F5E;font-size:0.78rem;font-family:Inter,sans-serif;margin-bottom:0.75rem;">'
        'Deleting a room permanently removes all messages, ideas, subgroups and tasks.</div>',
        unsafe_allow_html=True,
    )
    ck = f"confirm_delete_{room_id}"
    if not st.session_state.get(ck):
        if st.button("Delete this room", key=f"del_room_{room_id}", use_container_width=True):
            st.session_state[ck] = True; st.rerun()
    else:
        st.warning("Are you sure? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete", key=f"del_yes_{room_id}", type="primary", use_container_width=True):
                ok, err = delete_room(room_id, user_id)
                if ok:
                    for k in ["current_room","current_subgroup",ck]: st.session_state.pop(k,None)
                    st.rerun()
                else: st.error(err)
        with c2:
            if st.button("Cancel", key=f"del_no_{room_id}", use_container_width=True):
                st.session_state.pop(ck,None); st.rerun()


def render_leave_room(room_id, user_id):
    section_hdr("Leave Room")
    st.markdown(
        '<div style="color:#7C6F5E;font-size:0.82rem;font-family:Inter,sans-serif;margin-bottom:1rem;">'
        'You will lose access to this room once you leave.</div>',
        unsafe_allow_html=True,
    )
    ck = f"confirm_leave_{room_id}"
    if not st.session_state.get(ck):
        if st.button("Leave this room", key=f"leave_{room_id}", use_container_width=True):
            st.session_state[ck] = True; st.rerun()
    else:
        st.warning("Are you sure?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, leave", key=f"leave_yes_{room_id}", type="primary", use_container_width=True):
                ok, err = leave_room(room_id, user_id)
                if ok:
                    for k in ["current_room","current_subgroup",ck]: st.session_state.pop(k,None)
                    st.rerun()
                else: st.error(err)
        with c2:
            if st.button("Cancel", key=f"leave_no_{room_id}", use_container_width=True):
                st.session_state.pop(ck,None); st.rerun()


def render_subgroups_panel(room_id, user_id, subgroups):
    col_h, col_btn = st.columns([3, 1])
    with col_h: section_hdr("Subgroups")
    with col_btn:
        if st.button("＋ New", type="primary", use_container_width=True, key="new_sg"):
            st.session_state["show_sg_form"] = not st.session_state.get("show_sg_form",False)

    if st.session_state.get("show_sg_form"):
        with st.form("sgf", border=True):
            sg_name = st.text_input("Name", placeholder="e.g. Design Squad")
            sg_desc = st.text_area("Purpose", height=64)
            c1, c2  = st.columns(2)
            with c1:
                if st.form_submit_button("Create", type="primary", use_container_width=True):
                    if sg_name:
                        create_subgroup(room_id, sg_name, sg_desc, user_id)
                        st.session_state["show_sg_form"] = False
                        st.rerun()
            with c2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_sg_form"] = False; st.rerun()

    if not subgroups:
        empty_state("🔬", "No subgroups yet", "Create one to start executing.")
        return

    for sg in subgroups:
        is_member = is_subgroup_member(sg["id"], user_id)
        sg_card_ui(sg, is_member)
        btn_cols = st.columns(2) if not is_member else st.columns(1)
        with btn_cols[0]:
            if st.button("Open", key=f"osg_{sg['id']}", use_container_width=True):
                if not is_member: join_subgroup(sg["id"], user_id)
                st.session_state["current_subgroup"] = sg["id"]
                st.rerun()
        if not is_member:
            with btn_cols[1]:
                if st.button("Join", key=f"jsg_{sg['id']}", use_container_width=True):
                    join_subgroup(sg["id"], user_id); st.rerun()


# ══════════════════════════════════════════════════════════════════
# SUBGROUP VIEW
# ══════════════════════════════════════════════════════════════════

def render_subgroup_view(sg_id, room_id, user_id, user_name):
    sg   = get_subgroup(sg_id)
    room = get_room(room_id)
    if not sg:
        st.session_state.pop("current_subgroup",None); st.rerun(); return

    members  = get_subgroup_members(sg_id)
    tasks    = get_subgroup_tasks(sg_id)
    messages = get_subgroup_messages(sg_id)
    color    = sg.get("color","#7C5CCC")

    sg_header(sg, room, user_name)

    st.markdown(
        f'<div style="color:#B8A898;font-size:0.78rem;font-family:Inter,sans-serif;'
        f'margin-bottom:0.75rem;">{_h.escape(sg.get("description",""))}</div>',
        unsafe_allow_html=True,
    )

    done  = [t for t in tasks if t["status"]=="done"]
    doing = [t for t in tasks if t["status"]=="doing"]
    stat_cards([
        {"label":"Members",    "value":str(len(members)),"color":color},
        {"label":"Tasks",      "value":str(len(tasks)),  "color":"#7C5CCC"},
        {"label":"In progress","value":str(len(doing)),  "color":"#D4873A"},
        {"label":"Done",       "value":str(len(done)),   "color":"#4CA86A"},
    ])

    t_kanban, t_chat = st.tabs(["🗂 Kanban", "💬 Chat"])
    with t_kanban: render_kanban(sg_id, user_id, members)
    with t_chat:   render_sg_chat(sg_id, user_id, messages)


def render_sg_chat(sg_id, user_id, messages):
    c_hdr, c_btn = st.columns([6, 1])
    with c_hdr:
        section_hdr("Chat", "Tap 🔄 to check for new messages")
    with c_btn:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("🔄", key="sg_refresh", help="Refresh", use_container_width=True):
            st.rerun()

    box = st.container(height=340)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬","No messages yet","Coordinate with your subgroup.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#9B7FE8" if is_ai else "#2D2A26"
                st.markdown(
                    f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                    f'font-size:0.82rem;color:{nc};">{_h.escape(who)}</span> '
                    f'<span style="color:#C8B8A8;font-size:0.7rem;">'
                    f'{str(msg.get("created_at",""))[:16]}</span>',
                    unsafe_allow_html=True,
                )
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

    cur_room = st.session_state.get("current_room")
    cur_sg   = st.session_state.get("current_subgroup")

    if cur_sg:
        render_subgroup_view(cur_sg, cur_room, user_id, user_name)
    elif cur_room:
        render_room_view(cur_room, user_id, user_name)
    else:
        render_main_nav(user_id, user_name)


if __name__ == "__main__":
    main()
