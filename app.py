"""
SankalpRoom — AI-Powered Team Collaboration
Mobile-first. Fast. Clean.
"""

import html as _h
import streamlit as st
import streamlit.components.v1 as components

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
# AVATAR HELPER — photo if available, else colour + initials
# ══════════════════════════════════════════════════════════════════

def _avatar_html(name: str, color: str, avatar_url: str = None,
                 size: int = 32, font_size: str = "0.65rem") -> str:
    """Returns an <img> tag if photo exists, otherwise a coloured initials circle."""
    ini = _h.escape("".join(w[0].upper() for w in name.split()[:2]))
    base = (f'style="width:{size}px;height:{size}px;border-radius:50%;'
            f'object-fit:cover;flex-shrink:0;"')
    if avatar_url:
        return (f'<img src="{avatar_url}" {base} alt="{ini}"/>')
    else:
        return (
            f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'background:{color};color:white;display:inline-flex;'
            f'align-items:center;justify-content:center;'
            f'font-size:{font_size};font-weight:700;flex-shrink:0;">{ini}</div>'
        )

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
# BRAND BANNER
# ══════════════════════════════════════════════════════════════════

def render_brand_banner():
    """
    Slim gradient banner at the very top — visible on all pages.
    Non-intrusive: 36px tall, just the logo + tagline.
    Dismissible via X button.
    """
    if st.session_state.get("banner_dismissed"):
        return
    st.markdown(
        '''<div id="sr-banner" style="
            background: linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);
            padding: 0 1rem; height: 36px;
            display: flex; align-items: center; justify-content: space-between;
            margin: -1rem -1rem 0.75rem -1rem;
            position: sticky; top: 0; z-index: 999;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <span style="font-size:0.9rem;">⚡</span>
                <span style="font-family:Space Grotesk,sans-serif;font-size:0.78rem;
                    font-weight:700;color:white;letter-spacing:0.02em;">SankalpRoom</span>
                <span style="color:rgba(255,255,255,0.55);font-size:0.7rem;
                    font-family:Inter,sans-serif;">· Where ideas become action</span>
            </div>
            <span id="banner-close" style="color:rgba(255,255,255,0.6);font-size:0.75rem;
                cursor:pointer;padding:0.2rem 0.4rem;border-radius:4px;
                font-family:Inter,sans-serif;"
                onclick="this.parentElement.style.display='none'">✕</span>
        </div>''',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# BROWSER NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════

def inject_notification_js(user_id: int):
    """
    Injects JS that:
    1. Requests browser notification permission on first visit
    2. Watches the page title for unread count and fires a notification
       when the tab is in the background.
    """
    js = """
(function() {
    if (Notification && Notification.permission === "default") {
        Notification.requestPermission();
    }

    window.srNotify = function(title, body) {
        if (Notification && Notification.permission === "granted") {
            new Notification(title, {
                body: body,
                icon: "https://cdn.jsdelivr.net/npm/twemoji@14/2/svg/26a1.svg",
                tag: "sankalproom-msg",
                renotify: true
            });
        }
    };

    var prevUnread = parseInt(sessionStorage.getItem("sr_unread") || "0");
    var re = /[(]([0-9]+)[)]/;

    var observer = new MutationObserver(function() {
        var t = document.title || "";
        var m = t.match(re);
        var cur = m ? parseInt(m[1]) : 0;
        if (cur > prevUnread && document.hidden) {
            window.srNotify(
                "SankalpRoom — " + cur + " new message" + (cur > 1 ? "s" : ""),
                "Tap to open SankalpRoom"
            );
        }
        prevUnread = cur;
        sessionStorage.setItem("sr_unread", cur);
    });

    observer.observe(document.querySelector("title") || document.head, {
        subtree: true, childList: true, characterData: true
    });
})();
"""
    components.html(f"<script>{js}</script>", height=0)


def trigger_notification(title: str, body: str):
    """Call from Python to fire a browser notification immediately."""
    import json
    components.html(
        f'''<script>
        if (window.srNotify) {{
            window.srNotify({json.dumps(title)}, {json.dumps(body)});
        }}
        </script>''',
        height=0,
    )


# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════

def mini_header(user_name):
    initials  = "".join(w[0].upper() for w in user_name.split()[:2])
    av_url    = st.session_state.get("user_avatar_url") or None
    av_color  = st.session_state.get("user_color", "#6366F1")
    av_html   = _avatar_html(user_name, av_color, av_url, size=34, font_size="0.68rem")
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.5rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        + av_html +
        f'</div>',
        unsafe_allow_html=True,
    )


def room_header(room, user_name):
    av_url   = st.session_state.get("user_avatar_url") or None
    av_color = st.session_state.get("user_color", "#6366F1")
    av_html  = _avatar_html(user_name, av_color, av_url, size=32, font_size="0.65rem")
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.625rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        + av_html +
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
    color    = sg.get("color","#6366F1")
    av_url   = st.session_state.get("user_avatar_url") or None
    av_color = st.session_state.get("user_color", "#6366F1")
    av_html  = _avatar_html(user_name, av_color, av_url, size=32, font_size="0.65rem")
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:0.625rem 0 0.625rem;border-bottom:1px solid #1C2030;margin-bottom:0.875rem;">'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;font-weight:700;'
        f'background:linear-gradient(90deg,#6366F1,#8B5CF6,#EC4899);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">⚡ SankalpRoom</span>'
        + av_html +
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
    """Shows invite code + WhatsApp share button with the auto-join link."""
    # Build the invite URL using current page URL
    base_url = "https://sankalproom.streamlit.app"
    invite_url = f"{base_url}/?invite={code}"
    wa_text = f"Join my SankalpRoom! Click to join instantly: {invite_url}"
    import urllib.parse
    wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem;">'
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;'
        f'background:#0C0E14;border:1px solid #1C2030;border-radius:8px;'
        f'padding:0.4rem 0.75rem;">'
        f'<span style="color:#334155;font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-family:Inter,sans-serif;">Invite code</span>'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.9rem;'
        f'font-weight:700;color:#6366F1;letter-spacing:0.1em;">{code}</span></div>'
        f'<a href="{wa_link}" target="_blank" rel="noopener" style="'
        f'display:inline-flex;align-items:center;gap:0.375rem;'
        f'background:#25D366;border-radius:8px;padding:0.4rem 0.75rem;'
        f'text-decoration:none;font-family:Inter,sans-serif;font-size:0.75rem;'
        f'font-weight:600;color:white;">'
        f'<svg width="14" height="14" viewBox="0 0 24 24" fill="white">'
        f'<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15'
        f'-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475'
        f'-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52'
        f'.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207'
        f'-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372'
        f'-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2'
        f'5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719'
        f'2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>'
        f'<path d="M12 0C5.373 0 0 5.373 0 12c0 2.117.554 4.103 1.523 5.824L.057 23.882'
        f'a.5.5 0 00.556.611l6.188-1.438A11.945 11.945 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0z'
        f'M12 22c-1.885 0-3.652-.518-5.165-1.42l-.372-.22-3.853.895.966-3.738-.243-.386'
        f'A9.956 9.956 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>'
        f'</svg>'
        f'Share on WhatsApp</a>'
        f'</div>',
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
        url = m.get("avatar_url") or None
        av  = _avatar_html(m["name"], c, url, size=30, font_size="0.6rem")
        html += f'<div title="{_h.escape(m["name"])}" style="margin-right:-6px;display:inline-block;">{av}</div>'
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
                murl = m.get("avatar_url") or None
                mav  = _avatar_html(m["name"], m.get("avatar_color","#6366F1"), murl, size=22, font_size="0.55rem")
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

    stat_cards([
        {"label":"Rooms",   "value":str(len(rooms)),                                          "color":"#6366F1"},
        {"label":"Admin",   "value":str(sum(1 for r in rooms if r["role"]=="admin")),         "color":"#8B5CF6"},
        {"label":"Members", "value":str(sum(r["member_count"] for r in rooms)),               "color":"#22C55E"},
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
    from database.db import fetchone as _fetchone, execute as _execute
    from auth.auth import hash_password

    AVATAR_COLORS = [
        "#6366F1","#8B5CF6","#EC4899","#EF4444",
        "#F59E0B","#22C55E","#06B6D4","#E8A838",
    ]
    COLOR_NAMES = [
        "Indigo","Purple","Pink","Red",
        "Amber","Green","Cyan","Gold",
    ]

    user = _fetchone("SELECT * FROM users WHERE id=?", (user_id,))
    if not user:
        st.error("User not found."); return

    initials = "".join(w[0].upper() for w in user["name"].split()[:2])
    av_color = user.get("avatar_color","#6366F1")

    avatar_url = user.get("avatar_url") or ""

    # Profile card — shows photo if set
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;'
        f'background:#0C0E14;border:1px solid #1C2030;border-radius:12px;'
        f'padding:1.25rem;margin-bottom:1.25rem;">'
        + _avatar_html(user["name"], av_color, avatar_url or None, size=56, font_size="1.1rem") +
        f'<div>'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:700;'
        f'color:#F1F5F9;">{_h.escape(user["name"])}</div>'
        f'<div style="color:#64748B;font-size:0.78rem;font-family:Inter,sans-serif;">'
        f'{_h.escape(user.get("email",""))}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Photo upload ─────────────────────────────────────────────
    section_hdr("Profile Photo")
    uploaded = st.file_uploader(
        "Upload photo",
        type=["jpg","jpeg","png","webp"],
        label_visibility="collapsed",
        key="avatar_uploader",
    )
    if uploaded:
        import base64
        raw   = uploaded.read()
        if len(raw) > 500_000:          # 500 KB limit
            st.error("Photo must be under 500 KB. Please compress it first.")
        else:
            mime    = uploaded.type or "image/jpeg"
            b64     = base64.b64encode(raw).decode()
            data_url = f"data:{mime};base64,{b64}"

            # Preview
            st.markdown(
                f'<img src="{data_url}" style="width:72px;height:72px;'
                f'border-radius:50%;object-fit:cover;border:2px solid #6366F1;'
                f'margin-bottom:0.5rem;">',
                unsafe_allow_html=True,
            )
            if st.button("✅ Save photo", type="primary", use_container_width=True, key="save_photo"):
                _execute("UPDATE users SET avatar_url=? WHERE id=?", (data_url, user_id))
                st.session_state["user_avatar_url"] = data_url
                st.success("Photo saved!")
                st.rerun()

    if avatar_url:
        if st.button("🗑 Remove photo", use_container_width=True, key="remove_photo"):
            _execute("UPDATE users SET avatar_url=NULL WHERE id=?", (user_id,))
            st.session_state["user_avatar_url"] = None
            st.rerun()

    st.divider()
    # Edit name
    section_hdr("Edit Name & Colour")
    with st.form("edit_profile_form", border=True):
        new_name = st.text_input("Display name", value=user["name"])
        st.markdown(
            '<div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.06em;color:#64748B;margin-bottom:0.4rem;">Avatar colour</div>',
            unsafe_allow_html=True,
        )
        color_cols = st.columns(len(AVATAR_COLORS))
        selected_color = av_color
        for ci, (col, clr, cname) in enumerate(zip(color_cols, AVATAR_COLORS, COLOR_NAMES)):
            with col:
                ini2 = "".join(w[0].upper() for w in (new_name or user["name"]).split()[:2])
                border = "3px solid white" if clr == av_color else "3px solid transparent"
                st.markdown(
                    f'<div title="{cname}" style="width:32px;height:32px;border-radius:50%;'
                    f'background:{clr};display:flex;align-items:center;justify-content:center;'
                    f'font-size:0.65rem;font-weight:700;color:white;border:{border};'
                    f'cursor:pointer;">{ini2}</div>',
                    unsafe_allow_html=True,
                )
        # Color picker via selectbox
        selected_color = st.selectbox(
            "Pick colour",
            options=AVATAR_COLORS,
            index=AVATAR_COLORS.index(av_color) if av_color in AVATAR_COLORS else 0,
            format_func=lambda c: COLOR_NAMES[AVATAR_COLORS.index(c)],
            label_visibility="collapsed",
        )
        if st.form_submit_button("Save profile", type="primary", use_container_width=True):
            if new_name.strip():
                _execute(
                    "UPDATE users SET name=?, avatar_color=? WHERE id=?",
                    (new_name.strip(), selected_color, user_id),
                )
                st.session_state["user_name"] = new_name.strip()
                st.session_state["user_color"] = selected_color
                st.success("Profile updated!")
                st.rerun()
            else:
                st.error("Name cannot be empty.")

    # Change password
    st.divider()
    section_hdr("Change Password")
    with st.form("change_pw_form", border=True):
        old_pw  = st.text_input("Current password", type="password")
        new_pw  = st.text_input("New password", type="password", placeholder="Min 6 characters")
        new_pw2 = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password", type="primary", use_container_width=True):
            if not old_pw or not new_pw or not new_pw2:
                st.error("Fill in all fields.")
            elif new_pw != new_pw2:
                st.error("New passwords don't match.")
            elif len(new_pw) < 6:
                st.error("Min 6 characters.")
            else:
                check = _fetchone(
                    "SELECT id FROM users WHERE id=? AND password_hash=?",
                    (user_id, hash_password(old_pw)),
                )
                if not check:
                    st.error("Current password is wrong.")
                else:
                    _execute(
                        "UPDATE users SET password_hash=? WHERE id=?",
                        (hash_password(new_pw), user_id),
                    )
                    st.success("Password updated!")

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
            is_ai   = bool(msg.get("is_ai"))
            who     = "SankalpAI" if is_ai else msg["user_name"]
            color   = "#818CF8" if is_ai else msg.get("avatar_color","#6366F1")
            url     = None if is_ai else (msg.get("avatar_url") or None)
            av      = _avatar_html(who, color, url, size=28, font_size="0.6rem")
            time_s  = str(msg.get("created_at",""))[11:16]
            content_escaped = _h.escape(msg["content"])
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.625rem;">'
                f'{av}'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="margin-bottom:0.15rem;">'
                f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                f'font-size:0.8rem;color:{"#818CF8" if is_ai else "#CBD5E1"};">{_h.escape(who)}</span>'
                f'<span style="color:#334155;font-size:0.65rem;margin-left:0.4rem;">{time_s}</span>'
                f'</div>'
                f'<div style="background:#0F1218;border:1px solid #1C2030;border-radius:0 8px 8px 8px;'
                f'padding:0.5rem 0.75rem;font-size:0.85rem;color:#CBD5E1;'
                f'font-family:Inter,sans-serif;line-height:1.45;">'
                f'{content_escaped}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    prompt = st.chat_input("Message the team…", key="room_chat_input")
    if prompt:
        add_room_message(room_id, user_id, prompt)
        if prompt.lower().startswith("/ai "):
            with st.spinner("Thinking…"):
                reply = chat_with_ai(prompt[4:].strip())
            add_room_message(room_id, user_id, f"**SankalpAI:** {reply}", is_ai=True)
        st.rerun()


def render_room_settings(room_id, user_id, members):
    from database.db import execute as _execute, fetchone as _fetchone

    s_room, s_members, s_danger = st.tabs(["✏️ Edit Room", "👥 Members", "🗑 Danger"])

    # ── Tab 1: Edit room name + description ──────────────────────
    with s_room:
        section_hdr("Edit Room")
        room = _fetchone("SELECT * FROM rooms WHERE id=?", (room_id,))
        if room:
            with st.form("edit_room_form", border=True):
                new_name = st.text_input("Room name", value=room["name"])
                new_desc = st.text_area("Description", value=room.get("description","") or "", height=80)
                if st.form_submit_button("Save", type="primary", use_container_width=True):
                    if new_name.strip():
                        _execute(
                            "UPDATE rooms SET name=?, description=? WHERE id=?",
                            (new_name.strip(), new_desc.strip(), room_id),
                        )
                        get_user_rooms.clear()
                        st.success("Room updated!"); st.rerun()
                    else:
                        st.error("Room name cannot be empty.")

    # ── Tab 2: Members — remove + promote ────────────────────────
    with s_members:
        section_hdr("Members", "Promote to admin or remove")
        for m in members:
            is_self  = m["id"] == user_id
            is_admin = m.get("role") == "admin"
            ini      = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))

            col_av, col_name, col_act = st.columns([1, 4, 3])
            with col_av:
                murl = m.get("avatar_url") or None
                st.markdown(
                    _avatar_html(m["name"], m["avatar_color"], murl, size=32, font_size="0.62rem"),
                    unsafe_allow_html=True,
                )
            with col_name:
                role_badge = (
                    '<span style="background:#6366F118;color:#6366F1;border-radius:4px;'
                    'padding:1px 6px;font-size:0.62rem;margin-left:0.35rem;">admin</span>'
                    if is_admin else ""
                )
                st.markdown(
                    f'<div style="font-family:Inter,sans-serif;font-size:0.85rem;color:#CBD5E1;'
                    f'padding:0.5rem 0;">{_h.escape(m["name"])}{role_badge}</div>',
                    unsafe_allow_html=True,
                )
            with col_act:
                if not is_self:
                    if is_admin:
                        # Can demote admin → member (only if not the only admin)
                        if st.button("Demote", key=f"demote_{m['id']}", use_container_width=True):
                            admins = [x for x in members if x.get("role") == "admin"]
                            if len(admins) <= 1:
                                st.error("Cannot demote the only admin.")
                            else:
                                _execute(
                                    "UPDATE room_members SET role='member' WHERE room_id=? AND user_id=?",
                                    (room_id, m["id"]),
                                )
                                get_room_members.clear()
                                st.rerun()
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Admin", key=f"promote_{m['id']}", use_container_width=True):
                                _execute(
                                    "UPDATE room_members SET role='admin' WHERE room_id=? AND user_id=?",
                                    (room_id, m["id"]),
                                )
                                get_room_members.clear()
                                st.rerun()
                        with c2:
                            if st.button("Remove", key=f"rm_{m['id']}", use_container_width=True):
                                ok, err = remove_member(room_id, m["id"], user_id)
                                if ok: st.rerun()
                                else:  st.error(err)

    # ── Tab 3: Danger zone ───────────────────────────────────────
    with s_danger:
        section_hdr("Danger Zone")
        st.markdown(
            '<div style="color:#64748B;font-size:0.78rem;font-family:Inter,sans-serif;margin-bottom:0.75rem;">'
            'Deleting a room permanently removes all messages, ideas, subgroups and tasks.</div>',
            unsafe_allow_html=True,
        )
        ck = f"confirm_delete_{room_id}"
        if not st.session_state.get(ck):
            if st.button("🗑 Delete this room", key=f"del_room_{room_id}", use_container_width=True):
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

    # Admins get a Settings tab in subgroups too
    is_sg_creator = sg.get("created_by") == user_id
    is_room_adm   = is_room_admin(room_id or 0, user_id) if room_id else False
    can_manage_sg = is_sg_creator or is_room_adm

    if can_manage_sg:
        t_kanban, t_chat, t_sg_settings = st.tabs(["🗂 Kanban", "💬 Chat", "⚙ Settings"])
    else:
        t_kanban, t_chat = st.tabs(["🗂 Kanban", "💬 Chat"])

    with t_kanban: render_kanban(sg_id, user_id, members)
    with t_chat:   render_sg_chat(sg_id, user_id, messages)

    if can_manage_sg:
        with t_sg_settings:
            render_subgroup_settings(sg_id, sg, members, user_id, room_id)


def render_subgroup_settings(sg_id, sg, members, user_id, room_id):
    from database.db import execute as _execute, fetchone as _fetchone

    s_edit, s_members = st.tabs(["✏️ Edit", "👥 Members"])

    with s_edit:
        section_hdr("Edit Subgroup")
        with st.form("edit_sg_form", border=True):
            new_name = st.text_input("Subgroup name", value=sg.get("name",""))
            new_desc = st.text_area("Description", value=sg.get("description","") or "", height=72)
            if st.form_submit_button("Save", type="primary", use_container_width=True):
                if new_name.strip():
                    _execute(
                        "UPDATE subgroups SET name=?, description=? WHERE id=?",
                        (new_name.strip(), new_desc.strip(), sg_id),
                    )
                    get_room_subgroups.clear()
                    st.success("Subgroup updated!"); st.rerun()
                else:
                    st.error("Name cannot be empty.")

        st.divider()
        ck = f"del_sg_{sg_id}"
        if not st.session_state.get(ck):
            if st.button("🗑 Delete subgroup", key=f"del_sg_btn_{sg_id}", use_container_width=True):
                st.session_state[ck] = True; st.rerun()
        else:
            st.warning("Delete this subgroup and all its tasks?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete", key=f"del_sg_yes_{sg_id}", type="primary", use_container_width=True):
                    _execute("DELETE FROM subgroups WHERE id=?", (sg_id,))
                    get_room_subgroups.clear()
                    st.session_state.pop("current_subgroup", None)
                    st.session_state.pop(ck, None)
                    st.rerun()
            with c2:
                if st.button("Cancel", key=f"del_sg_no_{sg_id}", use_container_width=True):
                    st.session_state.pop(ck, None); st.rerun()

    with s_members:
        section_hdr("Subgroup Members")
        for m in members:
            is_self = m["id"] == user_id
            ini     = _h.escape("".join(w[0].upper() for w in m["name"].split()[:2]))
            col_av, col_name, col_btn = st.columns([1, 5, 2])
            with col_av:
                st.markdown(
                    f'<div style="width:30px;height:30px;border-radius:50%;background:{m["avatar_color"]};'
                    f'color:white;display:flex;align-items:center;justify-content:center;'
                    f'font-size:0.6rem;font-weight:700;margin-top:6px;">{ini}</div>',
                    unsafe_allow_html=True,
                )
            with col_name:
                st.markdown(
                    f'<div style="color:#CBD5E1;font-size:0.85rem;font-family:Inter,sans-serif;'
                    f'padding:0.5rem 0;">{_h.escape(m["name"])}</div>',
                    unsafe_allow_html=True,
                )
            with col_btn:
                if not is_self:
                    if st.button("Remove", key=f"sg_rm_{sg_id}_{m['id']}", use_container_width=True):
                        _execute(
                            "DELETE FROM subgroup_members WHERE subgroup_id=? AND user_id=?",
                            (sg_id, m["id"]),
                        )
                        get_subgroup_members.clear()
                        get_room_subgroups.clear()
                        st.rerun()


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
            is_ai   = bool(msg.get("is_ai"))
            who     = "SankalpAI" if is_ai else msg["user_name"]
            color   = "#818CF8" if is_ai else msg.get("avatar_color","#6366F1")
            url     = None if is_ai else (msg.get("avatar_url") or None)
            av      = _avatar_html(who, color, url, size=28, font_size="0.6rem")
            time_s  = str(msg.get("created_at",""))[11:16]
            content_escaped = _h.escape(msg["content"])
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.625rem;">'
                f'{av}'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="margin-bottom:0.15rem;">'
                f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;'
                f'font-size:0.8rem;color:{"#818CF8" if is_ai else "#CBD5E1"};">{_h.escape(who)}</span>'
                f'<span style="color:#334155;font-size:0.65rem;margin-left:0.4rem;">{time_s}</span>'
                f'</div>'
                f'<div style="background:#0F1218;border:1px solid #1C2030;border-radius:0 8px 8px 8px;'
                f'padding:0.5rem 0.75rem;font-size:0.85rem;color:#CBD5E1;'
                f'font-family:Inter,sans-serif;line-height:1.45;">'
                f'{content_escaped}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

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

    # ── Render brand banner (non-intrusive, dismissible) ──────────
    render_brand_banner()

    # ── Inject notification JS (runs once, zero height) ───────────
    inject_notification_js(user_id)

    # ── Auto-join room from invite link ───────────────────────────
    # Check BOTH session_state (set before login) AND query_params
    # (in case user opened the link while already logged in)
    pending_invite = (
        st.session_state.pop("pending_invite", None)
        or st.query_params.get("invite", "")
    )
    if pending_invite:
        pending_invite = pending_invite.strip().upper()
        room, err = join_room(pending_invite, user_id)
        # Clear URL param regardless of outcome
        try:
            st.query_params.clear()
        except Exception:
            pass

        if err == "already_member":
            # Already a member — just navigate into the room silently
            st.session_state["current_room"] = room["id"]
            st.session_state.pop("current_subgroup", None)
            st.rerun()
        elif room and not err:
            # Successfully joined
            st.session_state["current_room"] = room["id"]
            st.session_state.pop("current_subgroup", None)
            st.session_state["_just_joined"] = room["name"]
            st.rerun()
        elif err:
            st.warning(f"Could not join room: {err}")

    # Show welcome toast after joining (survives the rerun above)
    just_joined = st.session_state.pop("_just_joined", None)
    if just_joined:
        st.success(f"You joined **{just_joined}**! Welcome 🎉")

    # ── Update page title with unread count (triggers JS notif) ───
    inbox        = get_inbox(user_id)
    total_unread = sum(c.get("unread", 0) for c in inbox)
    if total_unread:
        st.markdown(
            f'<script>document.title = "({total_unread}) SankalpRoom";</script>',
            unsafe_allow_html=True,
        )

    build_sidebar(user_id)

    cur_room    = st.session_state.get("current_room")
    cur_sg      = st.session_state.get("current_subgroup")
    active_view = st.session_state.get("active_view")

    if cur_sg:
        render_subgroup_view(cur_sg, cur_room, user_id, user_name)
    elif cur_room:
        render_room_view(cur_room, user_id, user_name)
    elif active_view == "dm":
        mini_header(user_name)
        if st.button("← Back to Home", key="dm_back_home", use_container_width=False):
            st.session_state.pop("active_view", None)
            st.session_state.pop("dm_partner_id", None)
            st.rerun()
        render_dm_page(user_id)
    else:
        render_main_nav(user_id, user_name)


if __name__ == "__main__":
    main()
