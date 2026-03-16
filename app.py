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
from auth.auth import (
    is_logged_in, render_auth_page, logout,
     update_username, update_profile_photo,   # CHANGE 2, 3
)
from rooms.rooms import (
    get_user_rooms, get_room, get_room_members,
    get_room_subgroups, get_subgroup, get_subgroup_members,
    get_room_data,
    create_room, join_room, create_subgroup, join_subgroup,
    delete_room, leave_room, remove_member,
    update_room, promote_to_admin,            # CHANGE 4, 5
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
.stApp { background: #080A0F !important; color: #CBD5E1; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Open sidebar"],
button[aria-label="Close sidebar"] { display: none !important; }

.block-container {
    padding-top: 0 !important; padding-left: 1rem !important;
    padding-right: 1rem !important; padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #0C0E14 !important; border-right: 1px solid #1C2030 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    color: #64748B !important; text-align: left !important;
    border-radius: 8px !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 0.625rem 0.875rem !important;
    width: 100% !important; min-height: 44px !important; font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #131720 !important; color: #E2E8F0 !important; }

/* ── Main nav pills ── colourful on dark ── */
.main-nav .stTabs [data-baseweb="tab-list"] {
    background: #0E0F1A !important;
    border: 1px solid #1C2030 !important;
    border-radius: 14px !important; padding: 4px !important; gap: 3px !important;
    overflow-x: auto !important; flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important; scrollbar-width: none !important;
    margin-bottom: 1.25rem !important;
}
.main-nav .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.main-nav .stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #4B5563 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 0.5rem 1rem !important;
    min-height: 38px !important; border-bottom: none !important;
    border-radius: 10px !important; white-space: nowrap !important; flex: 1 !important;
}
.main-nav .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: #fff !important; font-weight: 600 !important; border-bottom: none !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.4) !important;
}

/* ── Inner room/subgroup tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #1C2030 !important;
    gap: 0 !important; overflow-x: auto !important; flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important; scrollbar-width: none !important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #4B5563 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 0.7rem 1rem !important;
    min-height: 44px !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; margin-bottom: -1px !important; white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: #818CF8 !important;
    border-bottom: 2px solid #6366F1 !important; font-weight: 600 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0F1218 !important; border: 1px solid #1E2533 !important;
    color: #E2E8F0 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 16px !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366F1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stTextInput > label, .stTextArea > label,
.stSelectbox > label, .stMultiSelect > label {
    color: #4B5563 !important; font-size: 0.7rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}
.stSelectbox > div > div { background: #0F1218 !important; border: 1px solid #1E2533 !important; border-radius: 8px !important; color: #E2E8F0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: #0F1218 !important; border: 1px solid #1E2533 !important;
    color: #94A3B8 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 0.6rem 1rem !important;
    min-height: 44px !important; transition: all 0.1s ease !important;
}
.stButton > button:hover { background: #131720 !important; border-color: #2D3650 !important; color: #E2E8F0 !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6366F1,#8B5CF6) !important;
    border-color: #6366F1 !important; color: #fff !important; font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.35) !important;
}
.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg,#4F52D9,#7C3AED) !important; }

/* ── Stat card colour bars get a gradient glow effect via the top border ── */

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: #0C0E14 !important; border: 1px solid #1C2030 !important;
    border-radius: 10px !important; padding: 0.75rem 1rem !important; margin-bottom: 0.4rem !important;
}
[data-testid="stChatInput"] > div { background: #0C0E14 !important; border: 1px solid #1C2030 !important; border-radius: 10px !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: #E2E8F0 !important; font-size: 16px !important; }

/* ── Forms / Expanders ── */
[data-testid="stForm"] { background: #0C0E14 !important; border: 1px solid #1C2030 !important; border-radius: 10px !important; padding: 1.1rem !important; }
[data-testid="stExpander"] { background: #0C0E14 !important; border: 1px solid #1C2030 !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { color: #64748B !important; font-size: 0.875rem !important; min-height: 44px !important; }
.stAlert { border-radius: 8px !important; }
hr { border: none !important; border-top: 1px solid #1C2030 !important; margin: 0.75rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #1E2533; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #6366F1; }

/* ══════════════════════════════
   DESKTOP — richer layout
   ══════════════════════════════ */
@media (min-width: 769px) {
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 0.5rem !important;
    }
    /* Wider sidebar on desktop */
    [data-testid="stSidebar"] { min-width: 260px !important; max-width: 280px !important; }

    /* Room cards in 2-col grid on desktop */
    .desktop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
}

/* ══════════════════════════════
   MOBILE ≤ 768px
   ══════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    /* Stack MOST columns — but NOT ones with .no-stack class */
    [data-testid="stHorizontalBlock"]:not(.no-stack) {
        flex-direction: column !important;
        gap: 0.35rem !important;
    }
    [data-testid="stHorizontalBlock"]:not(.no-stack) > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .stButton > button { min-height: 48px !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════

def _avatar_html(user_name: str, size: int = 34) -> str:
    """
    CHANGE 2: Return an <img> tag if the user has a profile photo,
    otherwise fall back to the initials gradient circle.
    """
    photo = st.session_state.get("user_photo", "")
    initials = "".join(w[0].upper() for w in user_name.split()[:2])
    if photo:
        return (
            f'<img src="{photo}" style="width:{size}px;height:{size}px;'
            f'border-radius:50%;object-fit:cover;border:2px solid #1C2030;" />'
        )
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:linear-gradient(135deg,#6366F1,#8B5CF6);'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:{int(size*0.35)}px;font-weight:700;color:white;">{initials}</div>'
    )


def mini_header(user_name: str):
    # CHANGE 2: uses _avatar_html() to show photo or initials
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.5rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        f'{_avatar_html(user_name, 34)}'
        f'</div>',
        unsafe_allow_html=True,
    )


def room_header(room, user_name):
    # CHANGE 2: uses _avatar_html() for photo or initials
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.625rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        f'{_avatar_html(user_name, 32)}'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_back, col_name = st.columns([1, 6])
    with col_back:
        if st.button("←", key="rh_back", use_container_width=True):
            st.session_state.pop("current_room", None)
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_name:
        st.markdown(
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.05rem;'
            f'font-weight:700;color:#F1F5F9;padding:0.5rem 0 0.5rem 0.25rem;">'
            f'{_h.escape(room["name"])}</div>',
            unsafe_allow_html=True,
        )


def sg_header(sg, room, user_name):
    color = sg.get("color","#6366F1")
    # CHANGE 2: uses _avatar_html() for photo or initials
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.625rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        f'{_avatar_html(user_name, 32)}'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_back, col_name = st.columns([1, 6])
    with col_back:
        if st.button("←", key="sgh_back", use_container_width=True):
            st.session_state.pop("current_subgroup", None)
            st.rerun()
    with col_name:
        st.markdown(
            f'<div style="padding:0.25rem 0 0.25rem 0.25rem;">'
            f'<div style="font-size:0.72rem;color:#475569;font-family:Inter,sans-serif;">'
            f'{_h.escape(room["name"] if room else "")}</div>'
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:1rem;'
            f'font-weight:700;color:{color};">{_h.escape(sg["name"])}</div></div>',
            unsafe_allow_html=True,
        )


def stat_cards(stats):
    # Pure HTML flexbox row — NEVER stacks on mobile
    html = '<div style="display:flex;gap:0.5rem;margin-bottom:0.875rem;">'
    for s in stats:
        c = s.get("color", "#6366F1")
        html += (
            f'<div style="flex:1;min-width:0;background:#0C0E14;border:1px solid #1C2030;'
            f'border-radius:8px;padding:0.7rem 0.75rem;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;top:0;left:0;right:0;height:2px;background:{c};"></div>'
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.3rem;font-weight:700;'
            f'color:{c};line-height:1;margin-bottom:0.15rem;">{s["value"]}</div>'
            f'<div style="color:#64748B;font-size:0.6rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.05em;font-family:Inter,sans-serif;white-space:nowrap;">{s["label"]}</div>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def empty_state(icon, title, sub):
    st.markdown(
        f'<div style="text-align:center;padding:3rem 1rem;border:1px dashed #1C2030;'
        f'border-radius:10px;margin:0.75rem 0;">'
        f'<div style="font-size:2rem;margin-bottom:0.75rem;opacity:0.35;">{icon}</div>'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:600;'
        f'color:#334155;margin-bottom:0.3rem;">{title}</div>'
        f'<div style="color:#1E293B;font-size:0.78rem;font-family:Inter,sans-serif;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_hdr(title, subtitle=""):
    sub_html = (f'<div style="color:#64748B;font-size:0.76rem;margin-top:0.15rem;'
                f'font-family:Inter,sans-serif;">{subtitle}</div>') if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:0.875rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;font-weight:700;'
        f'color:#F1F5F9;letter-spacing:-0.01em;">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def invite_pill(code):
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;'
        f'background:#0C0E14;border:1px solid #1C2030;border-radius:8px;'
        f'padding:0.4rem 0.75rem;margin-bottom:0.5rem;">'
        f'<span style="color:#334155;font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-family:Inter,sans-serif;">Invite</span>'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;'
        f'font-weight:700;color:#6366F1;letter-spacing:0.1em;">{code}</span></div>',
        unsafe_allow_html=True,
    )


def room_card_ui(room):
    is_admin = room["role"] == "admin"
    rc = "#6366F1" if is_admin else "#334155"
    rt = "admin" if is_admin else "member"
    st.markdown(
        f'<div style="background:#0C0E14;border:1px solid #1C2030;border-radius:10px;'
        f'padding:1rem;margin-bottom:0.4rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.35rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'color:#CBD5E1;flex:1;margin-right:0.5rem;">{_h.escape(room["name"])}</div>'
        f'<span style="background:{rc}18;color:{rc};border:1px solid {rc}25;border-radius:4px;'
        f'padding:1px 7px;font-size:0.62rem;font-weight:600;font-family:Inter,sans-serif;'
        f'text-transform:uppercase;white-space:nowrap;">{rt}</span>'
        f'</div>'
        f'<div style="color:#334155;font-size:0.76rem;font-family:Inter,sans-serif;margin-bottom:0.4rem;">'
        f'{_h.escape(room.get("description","") or "—")}</div>'
        f'<div style="color:#1E293B;font-size:0.7rem;font-family:Inter,sans-serif;">'
        f'{room["member_count"]} member{"s" if room["member_count"]!=1 else ""}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def sg_card_ui(sg, is_member):
    color  = sg.get("color","#6366F1")
    joined = '<span style="color:#22C55E;font-weight:600;font-size:0.7rem;">✓ joined</span>' if is_member else ""
    st.markdown(
        f'<div style="background:#0C0E14;border:1px solid #1C2030;border-left:3px solid {color};'
        f'border-radius:10px;padding:1rem;margin-bottom:0.4rem;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.88rem;font-weight:700;'
        f'color:#CBD5E1;margin-bottom:0.25rem;">{_h.escape(sg["name"])}</div>'
        f'<div style="color:#334155;font-size:0.75rem;font-family:Inter,sans-serif;margin-bottom:0.4rem;">'
        f'{_h.escape(sg.get("description","") or "Execution subgroup")}</div>'
        f'<div style="display:flex;gap:0.75rem;font-size:0.68rem;color:#1E293B;'
        f'font-family:Inter,sans-serif;align-items:center;">'
        f'<span>{sg["member_count"]} members</span><span>{sg["task_count"]} tasks</span>{joined}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def member_avatars(members, user_id=None, clickable=False):
    html = ""
    for m in members[:6]:
        c   = m.get("avatar_color","#6366F1")
        ini = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))
        html += (f'<div title="{_h.escape(m["name"])}" style="width:30px;height:30px;border-radius:50%;'
                 f'background:{c};color:white;display:inline-flex;align-items:center;'
                 f'justify-content:center;font-size:0.6rem;font-weight:700;'
                 f'border:2px solid #080A0F;margin-right:-6px;">{ini}</div>')
    if len(members) > 6:
        html += (f'<div style="width:30px;height:30px;border-radius:50%;background:#1C2030;'
                 f'color:#475569;display:inline-flex;align-items:center;justify-content:center;'
                 f'font-size:0.6rem;border:2px solid #080A0F;margin-right:-6px;">+{len(members)-6}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:0.625rem;">{html}</div>',
                unsafe_allow_html=True)
    if clickable and user_id:
        others = [m for m in members if m["id"] != user_id][:4]
        if others:
            st.markdown(
                '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.06em;color:#475569;font-family:Inter,sans-serif;'
                'margin-bottom:0.35rem;">Message a teammate</div>',
                unsafe_allow_html=True,
            )
            for m in others:
                first_name = m["name"].split()[0]
                if st.button(
                    f"💬  {first_name}",
                    key=f"dm_av_{m['id']}",
                    use_container_width=True,
                    help=f"Message {m['name']}",
                ):
                    st.session_state["dm_partner_id"] = m["id"]
                    st.session_state["active_view"]   = "dm"
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
            '<div style="padding:1rem 0.5rem 0.75rem;border-bottom:1px solid #1C2030;margin-bottom:0.5rem;">'
            '<span style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
            'color:#6366F1;">⚡ SankalpRoom</span></div>',
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
        f'color:#F1F5F9;letter-spacing:-0.03em;margin-bottom:0.2rem;">Hey, {_h.escape(first)} 👋</div>'
        f'<div style="color:#334155;font-size:0.85rem;font-family:Inter,sans-serif;">'
        f'Pick a room to continue.</div></div>',
        unsafe_allow_html=True,
    )
    rooms = get_user_rooms(user_id)
    if not rooms:
        empty_state("⚡", "No rooms yet", "Go to Rooms → create or join one.")
        return

    # CHANGE 6: Removed the "Rooms | Admin | Members" stat_cards table.
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
    # CHANGE 2 + 3: Profile photo, editable username, sign out
    photo    = st.session_state.get("user_photo", "")
    initials = "".join(w[0].upper() for w in user_name.split()[:2])

    # ── Profile card ──
    if photo:
        avatar_html = (
            f'<img src="{photo}" style="width:52px;height:52px;border-radius:50%;'
            f'object-fit:cover;border:2px solid #1C2030;flex-shrink:0;" />'
        )
    else:
        avatar_html = (
            f'<div style="width:52px;height:52px;border-radius:50%;flex-shrink:0;'
            f'background:linear-gradient(135deg,#6366F1,#8B5CF6);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:1.1rem;font-weight:700;color:white;">{initials}</div>'
        )

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;'
        f'background:#0C0E14;border:1px solid #1C2030;border-radius:12px;'
        f'padding:1.25rem;margin-bottom:1rem;">'
        f'{avatar_html}'
        f'<div>'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
        f'color:#F1F5F9;">{_h.escape(user_name)}</div>'
        f'<div style="color:#64748B;font-size:0.78rem;font-family:Inter,sans-serif;">SankalpRoom member</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── CHANGE 3: Editable username ──
    with st.expander("✏️ Change username"):
        with st.form("change_name_form", border=False):
            new_name = st.text_input("New username", value=user_name, placeholder="Your display name")
            if st.form_submit_button("Save name", type="primary", use_container_width=True):
                ok, err = update_username(user_id, new_name)
                if ok:
                    st.success("Username updated!")
                    st.rerun()
                else:
                    st.error(err)

    # ── CHANGE 2: Profile photo upload ──
    with st.expander("🖼️ Upload profile photo"):
        uploaded = st.file_uploader(
            "Choose an image (JPG / PNG, max 2 MB)",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_photo_uploader",
        )
        if uploaded:
            if st.button("Save photo", type="primary", use_container_width=True, key="save_photo_btn"):
                ok, err = update_profile_photo(user_id, uploaded)
                if ok:
                    st.success("Profile photo updated!")
                    st.rerun()
                else:
                    st.error(err)

    st.divider()
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
        f'<div style="color:#334155;font-size:0.8rem;font-family:Inter,sans-serif;'
        f'margin-bottom:0.5rem;">{_h.escape(room.get("description","") or "")}</div>',
        unsafe_allow_html=True,
    )
    member_avatars(members, user_id=user_id, clickable=True)
    invite_pill(room["invite_code"])

    stat_cards([
        {"label":"Members",  "value":str(len(members)),                                          "color":"#6366F1"},
        {"label":"Ideas",    "value":str(len(ideas)),                                            "color":"#8B5CF6"},
        {"label":"Selected", "value":str(len([i for i in ideas if i["status"]=="Selected"])),    "color":"#22C55E"},
        {"label":"Groups",   "value":str(len(subgroups)),                                        "color":"#F59E0B"},
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
    # CHANGE 8: 🔄 re-fetches only messages — no full app rerun, no logout
    c_hdr, c_btn = st.columns([6, 1])
    with c_hdr:
        section_hdr("Chat", "Tap 🔄 to check for new messages")
    with c_btn:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("🔄", key="rc_refresh", help="Refresh", use_container_width=True):
            # Only re-fetch messages — preserves session_state so user stays logged in
            messages = get_room_messages(room_id)

    box = st.container(height=360)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬", "No messages yet", "Start the conversation.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#818CF8" if is_ai else "#CBD5E1"
                st.markdown(
                    f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                    f'font-size:0.82rem;color:{nc};">{_h.escape(who)}</span> '
                    f'<span style="color:#1E293B;font-size:0.7rem;">'
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

    # ── CHANGE 4: Admin-only room name & description editing ──
    room_data = get_room(room_id)
    if room_data:
        with st.expander("✏️ Edit room details", expanded=False):
            with st.form("edit_room_form", border=False):
                new_rname = st.text_input("Room name", value=room_data.get("name", ""))
                new_rdesc = st.text_area("Description", value=room_data.get("description", "") or "", height=80)
                if st.form_submit_button("Save changes", type="primary", use_container_width=True):
                    ok, err = update_room(room_id, user_id, new_rname, new_rdesc)
                    if ok:
                        st.success("Room details updated!")
                        st.rerun()
                    else:
                        st.error(err)
        st.divider()

    # ── Members list with Remove + Promote buttons ──
    st.markdown(
        '<div style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;font-weight:600;'
        'color:#F1F5F9;margin-bottom:0.5rem;">Members</div>',
        unsafe_allow_html=True,
    )
    for m in members:
        is_self   = m["id"] == user_id
        mem_admin = m.get("role") == "admin"
        ini       = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))
        col_av, col_name, col_btn1, col_btn2 = st.columns([1, 4, 2, 2])
        with col_av:
            st.markdown(
                f'<div style="width:32px;height:32px;border-radius:50%;background:{m["avatar_color"]};'
                f'color:white;display:flex;align-items:center;justify-content:center;'
                f'font-size:0.62rem;font-weight:700;margin-top:4px;">{ini}</div>',
                unsafe_allow_html=True,
            )
        with col_name:
            role_badge = (
                '<span style="background:#6366F118;color:#6366F1;border-radius:4px;'
                'padding:1px 6px;font-size:0.62rem;margin-left:0.4rem;">admin</span>'
                if mem_admin else ""
            )
            st.markdown(
                f'<div style="font-family:Inter,sans-serif;font-size:0.85rem;color:#CBD5E1;'
                f'padding:0.5rem 0;">{_h.escape(m["name"])}{role_badge}</div>',
                unsafe_allow_html=True,
            )
        with col_btn1:
            # CHANGE 5: Promote to admin button (only for non-admin, non-self members)
            if not is_self and not mem_admin:
                if st.button("⬆ Admin", key=f"promote_{m['id']}", use_container_width=True,
                             help=f"Promote {m['name']} to admin"):
                    ok, err = promote_to_admin(room_id, m["id"], user_id)
                    if ok:
                        st.success(f"{m['name']} is now an admin!")
                        st.rerun()
                    else:
                        st.error(err)
        with col_btn2:
            # CHANGE 4/5: Only show Remove for non-self, non-admin members
            if not is_self and not mem_admin:
                if st.button("Remove", key=f"rm_{m['id']}", use_container_width=True):
                    ok, err = remove_member(room_id, m["id"], user_id)
                    if ok: st.success(f"Removed {m['name']}"); st.rerun()
                    else:  st.error(err)

    st.divider()
    st.markdown(
        '<div style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;font-weight:600;'
        'color:#EF4444;margin-bottom:0.5rem;">Danger Zone</div>'
        '<div style="color:#64748B;font-size:0.78rem;font-family:Inter,sans-serif;margin-bottom:0.75rem;">'
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
        '<div style="color:#64748B;font-size:0.82rem;font-family:Inter,sans-serif;margin-bottom:1rem;">'
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
    color    = sg.get("color","#6366F1")

    sg_header(sg, room, user_name)

    st.markdown(
        f'<div style="color:#334155;font-size:0.78rem;font-family:Inter,sans-serif;'
        f'margin-bottom:0.75rem;">{_h.escape(sg.get("description",""))}</div>',
        unsafe_allow_html=True,
    )

    done  = [t for t in tasks if t["status"]=="done"]
    doing = [t for t in tasks if t["status"]=="doing"]
    stat_cards([
        {"label":"Members",    "value":str(len(members)),"color":color},
        {"label":"Tasks",      "value":str(len(tasks)),  "color":"#6366F1"},
        {"label":"In progress","value":str(len(doing)),  "color":"#F59E0B"},
        {"label":"Done",       "value":str(len(done)),   "color":"#22C55E"},
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
            # CHANGE 8: Re-fetch messages only — no full st.rerun(), user stays logged in
            messages = get_subgroup_messages(sg_id)

    box = st.container(height=340)
    with box:
        shown = list(reversed(messages[:60]))
        if not shown:
            empty_state("💬","No messages yet","Coordinate with your subgroup.")
        for msg in shown:
            is_ai = bool(msg.get("is_ai"))
            with st.chat_message("assistant" if is_ai else "user"):
                who = "SankalpAI" if is_ai else msg["user_name"]
                nc  = "#818CF8" if is_ai else "#CBD5E1"
                st.markdown(
                    f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                    f'font-size:0.82rem;color:{nc};">{_h.escape(who)}</span> '
                    f'<span style="color:#1E293B;font-size:0.7rem;">'
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

    cur_room    = st.session_state.get("current_room")
    cur_sg      = st.session_state.get("current_subgroup")
    active_view = st.session_state.get("active_view")

    if cur_sg:
        render_subgroup_view(cur_sg, cur_room, user_id, user_name)
    elif cur_room:
        render_room_view(cur_room, user_id, user_name)
    elif active_view == "dm":
        # Quick DM click lands here — show DM page directly
        mini_header(user_name)
        # Back button to return to home (not login) — only shown in this direct-jump view
        if st.button("← Home", key="dm_home_back"):
            st.session_state.pop("active_view", None)
            st.session_state.pop("dm_partner_id", None)
            st.rerun()
        render_dm_page(user_id)
    else:
        render_main_nav(user_id, user_name)


if __name__ == "__main__":
    main()
