"""
SankalpRoom - Direct Messages
Single-panel layout: inbox + conversation side by side (desktop),
full-screen with back button (mobile).
Click any avatar/name anywhere in the app → opens their chat directly.
"""

import html as _html
import streamlit as st
from database.db import fetchone, fetchall, execute


def _e(text) -> str:
    return _html.escape(str(text or ""), quote=True)


def _av(name, color, url=None, size=36):
    """Render an avatar — photo if available, else colour+initials."""
    ini = _e("".join(w[0].upper() for w in str(name).split()[:2]))
    if url:
        return (f'<img src="{url}" style="width:{size}px;height:{size}px;'
                f'border-radius:50%;object-fit:cover;flex-shrink:0;">')
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'flex-shrink:0;background:{color};color:white;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:{max(8, size//5)}px;font-weight:700;">{ini}</div>')


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
        SELECT dm.*, u.name as sender_name,
               u.avatar_color as sender_color,
               u.avatar_url   as sender_avatar_url
        FROM direct_messages dm
        JOIN users u ON dm.sender_id = u.id
        WHERE (dm.sender_id=? AND dm.receiver_id=?)
           OR (dm.sender_id=? AND dm.receiver_id=?)
        ORDER BY dm.created_at ASC
        LIMIT ?
    """, (user_a, user_b, user_b, user_a, limit))


def mark_read(sender_id: int, receiver_id: int):
    execute(
        "UPDATE direct_messages SET is_read=TRUE "
        "WHERE sender_id=? AND receiver_id=? AND is_read=FALSE",
        (sender_id, receiver_id),
    )


def get_inbox(user_id: int):
    return fetchall("""
        WITH last_msgs AS (
            SELECT DISTINCT ON (
                LEAST(sender_id, receiver_id),
                GREATEST(sender_id, receiver_id)
            )
            id, sender_id, receiver_id, content, created_at
            FROM direct_messages
            WHERE sender_id = ? OR receiver_id = ?
            ORDER BY
                LEAST(sender_id, receiver_id),
                GREATEST(sender_id, receiver_id),
                created_at DESC
        ),
        unread_counts AS (
            SELECT sender_id, COUNT(*) AS unread
            FROM direct_messages
            WHERE receiver_id = ? AND is_read = FALSE
            GROUP BY sender_id
        )
        SELECT
            u.id           AS partner_id,
            u.name         AS partner_name,
            u.avatar_color AS partner_color,
            u.avatar_url   AS partner_avatar_url,
            lm.content     AS last_message,
            lm.created_at  AS last_at,
            lm.sender_id,
            COALESCE(uc.unread, 0) AS unread
        FROM last_msgs lm
        JOIN users u ON (
            u.id = CASE
                WHEN lm.sender_id = ? THEN lm.receiver_id
                ELSE lm.sender_id
            END
        )
        LEFT JOIN unread_counts uc ON uc.sender_id = u.id
        ORDER BY lm.created_at DESC
    """, (user_id, user_id, user_id, user_id))


def search_users(query: str, exclude_id: int):
    q = f"%{query}%"
    return fetchall(
        "SELECT id, name, avatar_color, avatar_url FROM users "
        "WHERE id != ? AND (name LIKE ? OR email LIKE ?) LIMIT 10",
        (exclude_id, q, q),
    )


def get_user(user_id: int):
    return fetchone(
        "SELECT id, name, avatar_color, avatar_url FROM users WHERE id=?",
        (user_id,),
    )


def open_dm_with(partner_id: int):
    """Call from anywhere to jump straight into a conversation."""
    st.session_state["dm_partner_id"] = partner_id
    st.session_state["active_view"]   = "dm"


# ══════════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════════

def render_dm_page(current_user_id: int):
    """
    Layout:
    • Desktop: inbox list (left col) + conversation (right col) — side by side
    • Mobile:  inbox list OR conversation (full width), toggled by session state
    """
    partner_id = st.session_state.get("dm_partner_id")

    # Inject CSS that hides/shows panels based on screen size
    st.markdown("""
    <style>
    .dm-wrap { display: flex; gap: 0; height: 100%; }
    .dm-inbox-col { flex: 0 0 320px; border-right: 1px solid #1C2030; padding-right: 0; }
    .dm-conv-col  { flex: 1; padding-left: 1rem; }
    @media (max-width: 768px) {
        .dm-inbox-col { flex: 1 1 100%; border-right: none; }
        .dm-conv-col  { flex: 1 1 100%; padding-left: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    # On mobile with a conversation open → show only conversation
    # On mobile without → show only inbox
    # On desktop → show both always
    if partner_id:
        # Desktop: side by side. Mobile: just the conversation.
        left, right = st.columns([1, 2])
        with left:
            _render_inbox_list(current_user_id, partner_id)
        with right:
            _render_conversation(current_user_id, partner_id)
    else:
        # No conversation open — show full-width inbox
        _render_inbox_list(current_user_id, None)


# ══════════════════════════════════════════════════════════════════
# INBOX LIST
# ══════════════════════════════════════════════════════════════════

def _render_inbox_list(user_id: int, active_partner: int | None):
    # Header
    hc, rc = st.columns([5, 1])
    with hc:
        st.markdown(
            '<div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;'
            'font-weight:700;color:#F1F5F9;padding:0.1rem 0 0.5rem;">Messages</div>',
            unsafe_allow_html=True,
        )
    with rc:
        if st.button("🔄", key="inbox_refresh", use_container_width=True, help="Refresh"):
            st.rerun()

    # Search
    search_key = f"dm_search_{st.session_state.get('dm_search_reset', 0)}"
    search_q   = st.text_input("", placeholder="🔍 Search or start new chat…",
                                key=search_key, label_visibility="collapsed")

    if search_q:
        results = search_users(search_q, user_id)
        if results:
            for u in results:
                pav = _av(u["name"], u["avatar_color"], u.get("avatar_url"), size=34)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:0.625rem;'
                    f'padding:0.4rem 0;pointer-events:none;">'
                    f'{pav}'
                    f'<span style="font-family:Inter,sans-serif;font-size:0.85rem;'
                    f'color:#CBD5E1;">{_e(u["name"])}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Message {_e(u['name'])}", key=f"sr_{u['id']}",
                             use_container_width=True):
                    st.session_state["dm_partner_id"]   = u["id"]
                    st.session_state["dm_search_reset"] = (
                        st.session_state.get("dm_search_reset", 0) + 1
                    )
                    st.rerun()
        else:
            st.markdown(
                '<div style="color:#334155;font-size:0.82rem;padding:0.5rem 0;">'
                'No users found</div>',
                unsafe_allow_html=True,
            )
        return

    # Conversation list
    inbox = get_inbox(user_id)
    if not inbox:
        st.markdown(
            '<div style="text-align:center;padding:2.5rem 1rem;'
            'border:1px dashed #1C2030;border-radius:10px;margin-top:0.5rem;">'
            '<div style="font-size:1.75rem;opacity:0.3;margin-bottom:0.5rem;">💬</div>'
            '<div style="color:#334155;font-size:0.82rem;font-family:Inter,sans-serif;">'
            'No conversations yet.<br>Search for someone above.</div></div>',
            unsafe_allow_html=True,
        )
        return

    for conv in inbox:
        pid      = conv["partner_id"]
        unread   = conv.get("unread", 0)
        raw_msg  = conv.get("last_message") or ""
        short    = _e(raw_msg[:36] + ("…" if len(raw_msg) > 36 else ""))
        date     = str(conv.get("last_at", ""))[:10]
        is_act   = active_partner == pid
        bg       = "#131720" if is_act else "#0C0E14"
        border   = "2px solid #6366F1" if is_act else "1px solid #1C2030"
        dot      = ('<div style="position:absolute;top:-2px;right:-2px;'
                    'width:10px;height:10px;border-radius:50%;'
                    'background:#6366F1;border:2px solid #080A0F;"></div>'
                    if unread else "")
        pav = _av(conv["partner_name"], conv["partner_color"],
                  conv.get("partner_avatar_url"), size=38)

        st.markdown(
            f'<div style="background:{bg};border:{border};border-radius:10px;'
            f'padding:0.625rem 0.75rem;margin-bottom:3px;pointer-events:none;">'
            f'<div style="display:flex;align-items:center;gap:0.625rem;">'
            f'<div style="position:relative;flex-shrink:0;">{pav}{dot}</div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;'
            f'font-weight:{"700" if unread else "600"};'
            f'color:{"#F1F5F9" if unread else "#CBD5E1"};">'
            f'{_e(conv["partner_name"])}</span>'
            f'<span style="color:#334155;font-size:0.65rem;">{date}</span>'
            f'</div>'
            f'<div style="color:#475569;font-size:0.73rem;'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{short}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            f"Open · {_e(conv['partner_name'])}",
            key=f"inbox_{pid}",
            use_container_width=True,
        ):
            st.session_state["dm_partner_id"] = pid
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# CONVERSATION
# ══════════════════════════════════════════════════════════════════

def _render_conversation(user_id: int, partner_id: int):
    partner = get_user(partner_id)
    if not partner:
        st.error("User not found.")
        return

    mark_read(partner_id, user_id)

    pav = _av(partner["name"], partner.get("avatar_color","#6366F1"),
              partner.get("avatar_url"), size=36)

    # Conversation header
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.625rem;'
        f'padding:0 0 0.625rem;border-bottom:1px solid #1C2030;margin-bottom:0.75rem;">'
        f'{pav}'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.92rem;'
        f'font-weight:700;color:#F1F5F9;">{_e(partner["name"])}</div>'
        f'<div style="color:#475569;font-size:0.7rem;font-family:Inter,sans-serif;">'
        f'Direct message</div></div></div>',
        unsafe_allow_html=True,
    )

    # Back (mobile) + Refresh
    cb, cr = st.columns([3, 1])
    with cb:
        if st.button("← Back", key="dm_back_btn", use_container_width=True):
            st.session_state.pop("dm_partner_id", None)
            st.rerun()
    with cr:
        if st.button("🔄", key="dm_conv_refresh", use_container_width=True, help="Refresh"):
            st.rerun()

    # Messages
    messages = get_conversation(user_id, partner_id)
    box      = st.container(height=400)

    with box:
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
                    f'font-size:0.68rem;font-family:Inter,sans-serif;">'
                    f'{_e(msg_date)}</span></div>',
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
                    f'margin-top:2px;">{time_str}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                sav = _av(msg["sender_name"], msg["sender_color"],
                          msg.get("sender_avatar_url"), size=24)
                st.markdown(
                    f'<div style="display:flex;align-items:flex-end;gap:0.4rem;margin-bottom:0.4rem;">'
                    f'{sav}'
                    f'<div style="max-width:80%;">'
                    f'<div style="background:#0C0E14;border:1px solid #1C2030;color:#CBD5E1;'
                    f'border-radius:14px 14px 14px 2px;padding:0.55rem 0.9rem;'
                    f'font-family:Inter,sans-serif;font-size:0.875rem;line-height:1.45;">'
                    f'{_e(msg["content"])}</div>'
                    f'<div style="color:#334155;font-size:0.65rem;margin-top:2px;">'
                    f'{time_str}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    prompt = st.chat_input(f"Message {partner['name']}…", key=f"dm_input_{partner_id}")
    if prompt and prompt.strip():
        send_dm(user_id, partner_id, prompt.strip())
        st.rerun()
