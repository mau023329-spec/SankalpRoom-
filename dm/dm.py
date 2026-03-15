"""
SankalpRoom - Direct Messages
Supabase Realtime: new messages appear within ~1 second without manual refresh.
"""

import html as _html
import os
import streamlit as st
from database.db import fetchone, fetchall, execute


def _e(text) -> str:
    return _html.escape(str(text or ""), quote=True)


# ══════════════════════════════════════════════════════════════════
# DB HELPERS
# ══════════════════════════════════════════════════════════════════

def send_dm(sender_id: int, receiver_id: int, content: str):
    return execute(
        "INSERT INTO direct_messages(sender_id, receiver_id, content) VALUES (?,?,?)",
        (sender_id, receiver_id, content),
    )


def get_conversation(user_a: int, user_b: int, limit: int = 100):
    return fetchall("""
        SELECT dm.*, u.name as sender_name, u.avatar_color as sender_color
        FROM direct_messages dm
        JOIN users u ON dm.sender_id = u.id
        WHERE (dm.sender_id=%s AND dm.receiver_id=%s)
           OR (dm.sender_id=%s AND dm.receiver_id=%s)
        ORDER BY dm.created_at ASC
        LIMIT %s
    """.replace("%s", "?"), (user_a, user_b, user_b, user_a, limit))


def mark_read(sender_id: int, receiver_id: int):
    execute(
        "UPDATE direct_messages SET is_read=TRUE WHERE sender_id=? AND receiver_id=? AND is_read=FALSE",
        (sender_id, receiver_id),
    )


def get_unread_count(receiver_id: int, sender_id: int) -> int:
    row = fetchone(
        "SELECT COUNT(*) as cnt FROM direct_messages WHERE sender_id=? AND receiver_id=? AND is_read=FALSE",
        (sender_id, receiver_id),
    )
    return row["cnt"] if row else 0


def get_inbox(user_id: int):
    return fetchall("""
        WITH last_msgs AS (
            SELECT DISTINCT ON (
                LEAST(sender_id, receiver_id),
                GREATEST(sender_id, receiver_id)
            )
            id, sender_id, receiver_id, content, created_at
            FROM direct_messages
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY
                LEAST(sender_id, receiver_id),
                GREATEST(sender_id, receiver_id),
                created_at DESC
        ),
        unread_counts AS (
            SELECT sender_id, COUNT(*) AS unread
            FROM direct_messages
            WHERE receiver_id = %s AND is_read = FALSE
            GROUP BY sender_id
        )
        SELECT
            u.id           AS partner_id,
            u.name         AS partner_name,
            u.avatar_color AS partner_color,
            lm.content     AS last_message,
            lm.created_at  AS last_at,
            lm.sender_id,
            COALESCE(uc.unread, 0) AS unread
        FROM last_msgs lm
        JOIN users u ON (
            u.id = CASE
                WHEN lm.sender_id = %s THEN lm.receiver_id
                ELSE lm.sender_id
            END
        )
        LEFT JOIN unread_counts uc ON uc.sender_id = u.id
        ORDER BY lm.created_at DESC
    """.replace("%s", "?"), (user_id, user_id, user_id, user_id))


def search_users(query: str, exclude_id: int):
    q = f"%{query}%"
    return fetchall(
        "SELECT id, name, avatar_color FROM users WHERE id != ? AND (name LIKE ? OR email LIKE ?) LIMIT 10",
        (exclude_id, q, q),
    )


def get_user(user_id: int):
    return fetchone("SELECT id, name, avatar_color FROM users WHERE id=?", (user_id,))


def open_dm_with(partner_id: int):
    st.session_state["dm_partner_id"]  = partner_id
    st.session_state["active_view"]    = "dm"
    st.session_state["dm_mobile_view"] = "conversation"




# ══════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════

def render_dm_page(current_user_id: int):

    partner_id = st.session_state.get("dm_partner_id")

    tab_inbox, tab_conv = st.tabs([
        "📥  Inbox",
        f"💬  Chat{' ·' if partner_id else ''}",
    ])

    with tab_inbox:
        _render_inbox_panel(current_user_id)

    with tab_conv:
        if partner_id:
            _render_conversation(current_user_id, partner_id)
        else:
            _render_empty_dm()


# ── Inbox ─────────────────────────────────────────────────────────

def _render_inbox_panel(user_id: int):
    st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] [data-testid="stButton"] button[kind="secondary"] {
        margin-top: -8px !important;
        border-top: none !important;
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        font-size: 0.72rem !important;
        color: #475569 !important;
        min-height: 30px !important;
        padding: 0.2rem 0.75rem !important;
        background: #0C0E14 !important;
        border-color: #1C2030 !important;
    }
    [data-testid="stVerticalBlock"] [data-testid="stButton"] button[kind="secondary"]:hover {
        color: #6366F1 !important; background: #131720 !important;
    }
    </style>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;
        font-weight:700;color:#F1F5F9;margin-bottom:0.75rem;">Messages</div>
    """, unsafe_allow_html=True)

    search_key = f"dm_search_{st.session_state.get('dm_search_reset', 0)}"
    search_q   = st.text_input("", placeholder="🔍  Search people…", key=search_key,
                                label_visibility="collapsed")

    if search_q:
        results = search_users(search_q, user_id)
        if results:
            for u in results:
                ini      = _e("".join(w[0].upper() for w in u["name"].split()[:2]))
                av_col, name_col = st.columns([1, 5])
                with av_col:
                    st.markdown(
                        f'<div style="width:36px;height:36px;border-radius:50%;'
                        f'background:{u["avatar_color"]};color:white;'
                        f'display:flex;align-items:center;justify-content:center;'
                        f'font-size:0.65rem;font-weight:700;'
                        f'font-family:Space Grotesk,sans-serif;margin-top:6px;">{ini}</div>',
                        unsafe_allow_html=True,
                    )
                with name_col:
                    if st.button(u["name"], key=f"sr_{u['id']}", use_container_width=True):
                        st.session_state["dm_partner_id"]   = u["id"]
                        st.session_state["dm_search_reset"] = st.session_state.get("dm_search_reset", 0) + 1
                        st.rerun()
        else:
            st.markdown('<div style="color:#334155;font-size:0.82rem;padding:0.5rem 0;">No users found</div>',
                        unsafe_allow_html=True)
        return

    st.divider()
    inbox = get_inbox(user_id)

    if not inbox:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 1rem;border:1px dashed #1C2030;
            border-radius:10px;margin-top:0.5rem;">
            <div style="font-size:1.75rem;opacity:0.3;margin-bottom:0.5rem;">💬</div>
            <div style="color:#334155;font-size:0.82rem;font-family:Inter,sans-serif;">
                No conversations yet.<br>Search for someone above.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    active = st.session_state.get("dm_partner_id")
    for conv in inbox:
        pid       = conv["partner_id"]
        unread    = conv.get("unread", 0)
        ini       = _e("".join(w[0].upper() for w in conv["partner_name"].split()[:2]))
        raw_msg   = conv.get("last_message") or ""
        short     = _e(raw_msg[:38] + ("…" if len(raw_msg) > 38 else ""))
        date      = str(conv.get("last_at", ""))[:10]
        is_active = active == pid
        bg        = "#131720" if is_active else "#0C0E14"
        border    = "1px solid #6366F1" if is_active else "1px solid #1C2030"
        dot       = '<div style="position:absolute;top:-2px;right:-2px;width:10px;height:10px;border-radius:50%;background:#6366F1;border:2px solid #080A0F;"></div>' if unread else ""

        st.markdown(
            f'<div style="background:{bg};border:{border};border-radius:10px;'
            f'padding:0.6rem 0.75rem;margin-bottom:2px;pointer-events:none;">'
            f'<div style="display:flex;align-items:center;gap:0.625rem;">'
            f'<div style="position:relative;flex-shrink:0;">'
            f'<div style="width:36px;height:36px;border-radius:50%;'
            f'background:{conv["partner_color"]};color:white;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.65rem;font-weight:700;font-family:Space Grotesk,sans-serif;">{ini}</div>'
            f'{dot}</div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;'
            f'font-weight:{"700" if unread else "600"};'
            f'color:{"#F1F5F9" if unread else "#CBD5E1"};">{_e(conv["partner_name"])}</span>'
            f'<span style="color:#334155;font-size:0.65rem;font-family:Inter,sans-serif;">{date}</span>'
            f'</div>'
            f'<div style="color:#475569;font-size:0.73rem;font-family:Inter,sans-serif;'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{short}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Open chat with {_e(conv['partner_name'])}", key=f"inbox_{pid}",
                     use_container_width=True):
            st.session_state["dm_partner_id"] = pid
            st.rerun()


# ── Conversation ──────────────────────────────────────────────────

def _render_conversation(user_id: int, partner_id: int):
    partner = get_user(partner_id)
    if not partner:
        st.error("User not found.")
        return

    mark_read(partner_id, user_id)

    ini = _e("".join(w[0].upper() for w in partner["name"].split()[:2]))

    c_back, c_info = st.columns([1, 5])
    with c_back:
        if st.button("← Back", key="dm_back_btn"):
            st.session_state.pop("dm_partner_id", None)
            st.rerun()
    with c_info:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.625rem;padding:0.2rem 0 0.75rem;">'
            f'<div style="width:36px;height:36px;border-radius:50%;flex-shrink:0;'
            f'background:{partner["avatar_color"]};color:white;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.65rem;font-weight:700;font-family:Space Grotesk,sans-serif;">{ini}</div>'
            f'<div>'
            f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.92rem;'
            f'font-weight:700;color:#F1F5F9;">{_e(partner["name"])}</div>'
            f'<div style="color:#334155;font-size:0.7rem;font-family:Inter,sans-serif;">'
            f'Direct message · updates every 2s</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    messages  = get_conversation(user_id, partner_id)
    chat_box  = st.container(height=420)

    with chat_box:
        if not messages:
            st.markdown(
                f'<div style="text-align:center;padding:3rem 1rem;">'
                f'<div style="font-size:2rem;opacity:0.3;margin-bottom:0.75rem;">👋</div>'
                f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.88rem;'
                f'font-weight:600;color:#334155;">'
                f'Start a conversation with {_e(partner["name"])}</div></div>',
                unsafe_allow_html=True,
            )

        prev_date = None
        for msg in messages:
            msg_date = str(msg.get("created_at", ""))[:10]
            is_mine  = msg["sender_id"] == user_id

            if msg_date != prev_date:
                prev_date = msg_date
                st.markdown(
                    f'<div style="text-align:center;margin:0.75rem 0;">'
                    f'<span style="background:#0C0E14;border:1px solid #1C2030;'
                    f'border-radius:20px;padding:2px 12px;color:#334155;'
                    f'font-size:0.68rem;font-family:Inter,sans-serif;">{_e(msg_date)}</span></div>',
                    unsafe_allow_html=True,
                )

            time_str = str(msg.get("created_at", ""))[11:16]

            if is_mine:
                st.markdown(
                    f'<div style="display:flex;justify-content:flex-end;margin-bottom:0.4rem;">'
                    f'<div style="max-width:80%;">'
                    f'<div style="background:#6366F1;color:white;'
                    f'border-radius:14px 14px 2px 14px;padding:0.55rem 0.9rem;'
                    f'font-family:Inter,sans-serif;font-size:0.875rem;line-height:1.45;">'
                    f'{_e(msg["content"])}</div>'
                    f'<div style="text-align:right;color:#334155;font-size:0.65rem;'
                    f'margin-top:2px;font-family:Inter,sans-serif;">{time_str}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                s_ini = _e("".join(w[0].upper() for w in msg["sender_name"].split()[:2]))
                st.markdown(
                    f'<div style="display:flex;align-items:flex-end;gap:0.5rem;margin-bottom:0.4rem;">'
                    f'<div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;'
                    f'background:{msg["sender_color"]};color:white;'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:0.58rem;font-weight:700;font-family:Space Grotesk,sans-serif;">{s_ini}</div>'
                    f'<div style="max-width:80%;">'
                    f'<div style="background:#0C0E14;border:1px solid #1C2030;color:#CBD5E1;'
                    f'border-radius:14px 14px 14px 2px;padding:0.55rem 0.9rem;'
                    f'font-family:Inter,sans-serif;font-size:0.875rem;line-height:1.45;">'
                    f'{_e(msg["content"])}</div>'
                    f'<div style="color:#334155;font-size:0.65rem;margin-top:2px;'
                    f'font-family:Inter,sans-serif;">{time_str}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    prompt = st.chat_input(f"Message {partner['name']}…", key=f"dm_input_{partner_id}")
    if prompt and prompt.strip():
        send_dm(user_id, partner_id, prompt.strip())
        st.rerun()


def _render_empty_dm():
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
        justify-content:center;padding:4rem 1rem;text-align:center;">
        <div style="font-size:2.5rem;opacity:0.2;margin-bottom:1rem;">💬</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;
            font-weight:700;color:#334155;margin-bottom:0.4rem;">Your messages</div>
        <div style="color:#1E293B;font-size:0.82rem;font-family:'Inter',sans-serif;">
            Select a conversation from the Inbox tab.</div>
    </div>
    """, unsafe_allow_html=True)
