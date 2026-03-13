"""
SankalpRoom - Direct Messages Module
Peer-to-peer chat between any two SankalpRoom users.
"""

import streamlit as st
from database.db import fetchone, fetchall, execute


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
        WHERE (dm.sender_id=? AND dm.receiver_id=?)
           OR (dm.sender_id=? AND dm.receiver_id=?)
        ORDER BY dm.created_at ASC
        LIMIT ?
    """, (user_a, user_b, user_b, user_a, limit))


def mark_read(sender_id: int, receiver_id: int):
    execute(
        "UPDATE direct_messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0",
        (sender_id, receiver_id),
    )


def get_unread_count(receiver_id: int, sender_id: int) -> int:
    row = fetchone(
        "SELECT COUNT(*) as cnt FROM direct_messages WHERE sender_id=? AND receiver_id=? AND is_read=0",
        (sender_id, receiver_id),
    )
    return row["cnt"] if row else 0


def get_inbox(user_id: int):
    """
    Returns one row per conversation partner — most recent message first.
    Includes unread count and last message preview.
    """
    return fetchall("""
        SELECT
            u.id        AS partner_id,
            u.name      AS partner_name,
            u.avatar_color AS partner_color,
            dm.content  AS last_message,
            dm.created_at AS last_at,
            dm.sender_id,
            SUM(CASE WHEN dm2.is_read=0 AND dm2.receiver_id=? THEN 1 ELSE 0 END) AS unread
        FROM users u
        JOIN direct_messages dm ON (
            (dm.sender_id=u.id   AND dm.receiver_id=?) OR
            (dm.receiver_id=u.id AND dm.sender_id=?)
        )
        LEFT JOIN direct_messages dm2 ON (
            dm2.sender_id=u.id AND dm2.receiver_id=?
        )
        WHERE u.id != ?
          AND dm.id = (
            SELECT id FROM direct_messages
            WHERE (sender_id=u.id AND receiver_id=?)
               OR (sender_id=? AND receiver_id=u.id)
            ORDER BY created_at DESC LIMIT 1
          )
        GROUP BY u.id
        ORDER BY dm.created_at DESC
    """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id))


def search_users(query: str, exclude_id: int):
    q = f"%{query}%"
    return fetchall(
        "SELECT id, name, avatar_color FROM users WHERE id != ? AND (name LIKE ? OR email LIKE ?) LIMIT 10",
        (exclude_id, q, q),
    )


def get_user(user_id: int):
    return fetchone("SELECT id, name, avatar_color FROM users WHERE id=?", (user_id,))


# ══════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════

def render_dm_page(current_user_id: int):
    """Full DM page — inbox on left, conversation on right."""

    # ── Layout ──────────────────────────────────────────────────
    left, right = st.columns([1, 2.5])

    with left:
        _render_inbox_panel(current_user_id)

    with right:
        partner_id = st.session_state.get("dm_partner_id")
        if partner_id:
            _render_conversation(current_user_id, partner_id)
        else:
            _render_empty_dm()


def _render_inbox_panel(user_id: int):
    # Header + new DM button
    st.markdown("""
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;
        font-weight:700;color:#F1F5F9;margin-bottom:0.75rem;
        letter-spacing:-0.01em;">Messages</div>
    """, unsafe_allow_html=True)

    # Search / start new DM
    # Use a counter as part of the key so we can "reset" by incrementing it
    search_key = f"dm_search_{st.session_state.get('dm_search_reset', 0)}"
    search_q = st.text_input("", placeholder="🔍  Find a person…", key=search_key,
                              label_visibility="collapsed")

    if search_q and len(search_q) >= 1:
        results = search_users(search_q, user_id)
        if results:
            for u in results:
                ini = "".join(w[0].upper() for w in u["name"].split()[:2])
                col_av, col_name = st.columns([1, 4])
                with col_av:
                    st.markdown(f"""
                    <div style="width:32px;height:32px;border-radius:50%;
                        background:{u['avatar_color']};color:white;
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.65rem;font-weight:700;
                        font-family:'Space Grotesk',sans-serif;margin-top:4px;">
                        {ini}</div>
                    """, unsafe_allow_html=True)
                with col_name:
                    if st.button(u["name"], key=f"sr_{u['id']}", use_container_width=True):
                        st.session_state["dm_partner_id"]  = u["id"]
                        # increment counter → new widget key → empty input on rerun
                        st.session_state["dm_search_reset"] = st.session_state.get("dm_search_reset", 0) + 1
                        st.rerun()
        else:
            st.markdown('<div style="color:#334155;font-size:0.78rem;padding:0.5rem 0;font-family:Inter,sans-serif;">No users found</div>', unsafe_allow_html=True)
        return

    # Inbox list
    st.divider()
    inbox = get_inbox(user_id)

    if not inbox:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0.5rem;
            border:1px dashed #1C2030;border-radius:8px;margin-top:0.5rem;">
            <div style="font-size:1.5rem;opacity:0.3;margin-bottom:0.5rem;">💬</div>
            <div style="color:#334155;font-size:0.78rem;font-family:'Inter',sans-serif;">
                No conversations yet.<br>Search for someone above.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    active = st.session_state.get("dm_partner_id")
    for conv in inbox:
        pid      = conv["partner_id"]
        unread   = conv.get("unread", 0)
        ini      = "".join(w[0].upper() for w in conv["partner_name"].split()[:2])
        preview  = (conv.get("last_message") or "")[:35]
        if len(conv.get("last_message") or "") > 35:
            preview += "…"
        is_active = active == pid
        bg        = "#131720" if is_active else "transparent"
        border    = "1px solid #6366F1" if is_active else "1px solid transparent"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.625rem;
            padding:0.55rem 0.625rem;border-radius:8px;
            background:{bg};border:{border};margin-bottom:2px;cursor:pointer;">
            <div style="position:relative;flex-shrink:0;">
                <div style="width:34px;height:34px;border-radius:50%;
                    background:{conv['partner_color']};color:white;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.65rem;font-weight:700;
                    font-family:'Space Grotesk',sans-serif;">{ini}</div>
                {'<div style="position:absolute;top:-2px;right:-2px;width:10px;height:10px;border-radius:50%;background:#6366F1;border:2px solid #080A0F;"></div>' if unread else ''}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:0.82rem;
                        font-weight:{'700' if unread else '600'};
                        color:{'#F1F5F9' if unread else '#CBD5E1'};">
                        {conv['partner_name']}</span>
                    <span style="color:#334155;font-size:0.65rem;font-family:'Inter',sans-serif;">
                        {str(conv.get('last_at',''))[:10]}</span>
                </div>
                <div style="color:#475569;font-size:0.72rem;font-family:'Inter',sans-serif;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {preview}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("open", key=f"inbox_{pid}", label_visibility="collapsed"):
            st.session_state["dm_partner_id"] = pid
            st.rerun()


def _render_conversation(user_id: int, partner_id: int):
    partner = get_user(partner_id)
    if not partner:
        st.error("User not found.")
        return

    # Mark messages from partner as read
    mark_read(partner_id, user_id)

    ini = "".join(w[0].upper() for w in partner["name"].split()[:2])

    # Conversation header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.75rem;
        padding:0.75rem 0 0.875rem;
        border-bottom:1px solid #1C2030;margin-bottom:1rem;">
        <div style="width:38px;height:38px;border-radius:50%;
            background:{partner['avatar_color']};color:white;
            display:flex;align-items:center;justify-content:center;
            font-size:0.7rem;font-weight:700;
            font-family:'Space Grotesk',sans-serif;flex-shrink:0;">{ini}</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;
                font-weight:700;color:#F1F5F9;">{partner['name']}</div>
            <div style="color:#334155;font-size:0.72rem;font-family:'Inter',sans-serif;">
                Direct message</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    messages = get_conversation(user_id, partner_id)
    chat_box = st.container(height=440)

    with chat_box:
        if not messages:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem 1rem;">
                <div style="font-size:2rem;opacity:0.3;margin-bottom:0.75rem;">👋</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:0.88rem;
                    font-weight:600;color:#334155;">
                    Start a conversation with {partner['name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        prev_date = None
        for msg in messages:
            msg_date = str(msg.get("created_at", ""))[:10]
            is_mine  = msg["sender_id"] == user_id

            # Date separator
            if msg_date != prev_date:
                prev_date = msg_date
                st.markdown(f"""
                <div style="text-align:center;margin:0.75rem 0;">
                    <span style="background:#0C0E14;border:1px solid #1C2030;
                        border-radius:20px;padding:2px 12px;
                        color:#334155;font-size:0.68rem;font-family:'Inter',sans-serif;">
                        {msg_date}</span>
                </div>
                """, unsafe_allow_html=True)

            # Message bubble
            if is_mine:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:0.4rem;">
                    <div style="max-width:70%;">
                        <div style="background:#6366F1;color:white;
                            border-radius:12px 12px 2px 12px;
                            padding:0.5rem 0.875rem;
                            font-family:'Inter',sans-serif;font-size:0.85rem;
                            line-height:1.45;">
                            {msg['content']}
                        </div>
                        <div style="text-align:right;color:#334155;
                            font-size:0.65rem;margin-top:2px;font-family:'Inter',sans-serif;">
                            {str(msg.get('created_at',''))[11:16]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                sender_ini = "".join(w[0].upper() for w in msg["sender_name"].split()[:2])
                st.markdown(f"""
                <div style="display:flex;align-items:flex-end;gap:0.5rem;margin-bottom:0.4rem;">
                    <div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;
                        background:{msg['sender_color']};color:white;
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.58rem;font-weight:700;
                        font-family:'Space Grotesk',sans-serif;">{sender_ini}</div>
                    <div style="max-width:70%;">
                        <div style="background:#0C0E14;border:1px solid #1C2030;
                            color:#CBD5E1;border-radius:12px 12px 12px 2px;
                            padding:0.5rem 0.875rem;
                            font-family:'Inter',sans-serif;font-size:0.85rem;
                            line-height:1.45;">
                            {msg['content']}
                        </div>
                        <div style="color:#334155;font-size:0.65rem;
                            margin-top:2px;font-family:'Inter',sans-serif;">
                            {str(msg.get('created_at',''))[11:16]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Input
    prompt = st.chat_input(f"Message {partner['name']}…", key=f"dm_input_{partner_id}")
    if prompt and prompt.strip():
        send_dm(user_id, partner_id, prompt.strip())
        st.rerun()


def _render_empty_dm():
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
        justify-content:center;height:60vh;text-align:center;">
        <div style="font-size:2.5rem;opacity:0.2;margin-bottom:1rem;">💬</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;
            font-weight:700;color:#334155;margin-bottom:0.4rem;">
            Your messages</div>
        <div style="color:#1E293B;font-size:0.82rem;font-family:'Inter',sans-serif;">
            Select a conversation or search for someone to start chatting.
        </div>
    </div>
    """, unsafe_allow_html=True)


def open_dm_with(partner_id: int):
    """Call this from anywhere (e.g. member avatar click) to jump to a DM."""
    st.session_state["dm_partner_id"] = partner_id
    st.session_state["active_view"]   = "dm"
