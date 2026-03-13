"""
SankalpRoom - Ideas Module
Idea creation, voting, and status management.
"""

import streamlit as st
from database.db import fetchone, fetchall, execute

VOTE_TYPES = {"👍": "like", "🔥": "high_priority", "⏳": "do_later"}
VOTE_LABELS = {"like": "👍 Like", "high_priority": "🔥 High Priority", "do_later": "⏳ Do Later"}
STATUSES = ["Open", "Selected", "In Progress", "Dropped"]
STATUS_COLORS = {
    "Open": "#4F46E5",
    "Selected": "#22C55E",
    "In Progress": "#F59E0B",
    "Dropped": "#6B7280",
}
STATUS_ICONS = {"Open": "💡", "Selected": "✅", "In Progress": "⚙️", "Dropped": "🗑️"}


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_idea(room_id: int, user_id: int, title: str, description: str = "") -> int:
    return execute(
        "INSERT INTO ideas (room_id, user_id, title, description) VALUES (?, ?, ?, ?)",
        (room_id, user_id, title, description),
    )


def get_room_ideas(room_id: int):
    ideas = fetchall("""
        SELECT i.*, u.name as author_name, u.avatar_color as author_color
        FROM ideas i
        JOIN users u ON i.user_id = u.id
        WHERE i.room_id = ?
        ORDER BY i.created_at DESC
    """, (room_id,))

    for idea in ideas:
        idea["votes"] = get_idea_votes(idea["id"])
        idea["vote_count"] = sum(idea["votes"].values())

    return ideas


def get_idea(idea_id: int):
    idea = fetchone("""
        SELECT i.*, u.name as author_name
        FROM ideas i JOIN users u ON i.user_id = u.id
        WHERE i.id = ?
    """, (idea_id,))
    if idea:
        idea["votes"] = get_idea_votes(idea_id)
    return idea


def update_idea_status(idea_id: int, status: str):
    execute(
        "UPDATE ideas SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, idea_id),
    )


def update_idea_analysis(idea_id: int, analysis: str):
    execute(
        "UPDATE ideas SET ai_analysis = ?, updated_at = datetime('now') WHERE id = ?",
        (analysis, idea_id),
    )


def delete_idea(idea_id: int):
    execute("DELETE FROM votes WHERE idea_id = ?", (idea_id,))
    execute("DELETE FROM ideas WHERE id = ?", (idea_id,))


# ── Voting ────────────────────────────────────────────────────────────────────

def cast_vote(idea_id: int, user_id: int, vote_type: str):
    existing = fetchone(
        "SELECT id, vote_type FROM votes WHERE idea_id = ? AND user_id = ?",
        (idea_id, user_id),
    )
    if existing:
        if existing["vote_type"] == vote_type:
            # Toggle off
            execute("DELETE FROM votes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id))
        else:
            execute(
                "UPDATE votes SET vote_type = ?, created_at = datetime('now') WHERE idea_id = ? AND user_id = ?",
                (vote_type, idea_id, user_id),
            )
    else:
        execute(
            "INSERT INTO votes (idea_id, user_id, vote_type) VALUES (?, ?, ?)",
            (idea_id, user_id, vote_type),
        )


def get_idea_votes(idea_id: int) -> dict:
    rows = fetchall("SELECT vote_type, COUNT(*) as cnt FROM votes WHERE idea_id = ? GROUP BY vote_type", (idea_id,))
    result = {v: 0 for v in VOTE_TYPES.values()}
    for row in rows:
        result[row["vote_type"]] = row["cnt"]
    return result


def get_user_vote(idea_id: int, user_id: int) -> str | None:
    row = fetchone("SELECT vote_type FROM votes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id))
    return row["vote_type"] if row else None


# ── Render ────────────────────────────────────────────────────────────────────

def render_idea_card(idea: dict, user_id: int, show_actions: bool = True):
    status = idea.get("status", "Open")
    color = STATUS_COLORS.get(status, "#4F46E5")
    icon = STATUS_ICONS.get(status, "💡")
    user_vote = get_user_vote(idea["id"], user_id)

    with st.container():
        st.markdown(f"""
        <div style="
            background: #1A1D27;
            border: 1px solid #2D3148;
            border-left: 4px solid {color};
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.75rem;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                <span style="font-weight:600; color:#E2E8F0; font-size:0.95rem;">{idea['title']}</span>
                <span style="
                    background: {color}22;
                    color: {color};
                    border: 1px solid {color}44;
                    border-radius: 20px;
                    padding: 2px 10px;
                    font-size: 0.7rem;
                    font-weight: 600;
                ">{icon} {status}</span>
            </div>
            <div style="color:#9CA3AF; font-size:0.82rem; margin-bottom:0.6rem;">{idea.get('description','')}</div>
            <div style="color:#6B7280; font-size:0.75rem;">by {idea.get('author_name','?')} · {idea.get('created_at','')[:10]}</div>
        </div>
        """, unsafe_allow_html=True)

        if show_actions:
            votes = idea.get("votes", {})
            cols = st.columns([1, 1, 1, 1, 2])

            for i, (emoji, vtype) in enumerate(VOTE_TYPES.items()):
                count = votes.get(vtype, 0)
                active = user_vote == vtype
                label = f"{emoji} {count}{' ✓' if active else ''}"
                with cols[i]:
                    if st.button(label, key=f"vote_{idea['id']}_{vtype}", use_container_width=True):
                        cast_vote(idea["id"], user_id, vtype)
                        st.rerun()

            with cols[3]:
                new_status = st.selectbox(
                    "Status",
                    STATUSES,
                    index=STATUSES.index(status),
                    key=f"status_{idea['id']}",
                    label_visibility="collapsed",
                )
                if new_status != status:
                    update_idea_status(idea["id"], new_status)
                    st.rerun()


def render_ideas_panel(room_id: int, user_id: int):
    ideas = get_room_ideas(room_id)

    col_header, col_new = st.columns([3, 1])
    with col_header:
        st.markdown("### 💡 Ideas Board")
    with col_new:
        if st.button("➕ Add Idea", use_container_width=True, type="primary"):
            st.session_state["show_idea_form"] = True

    if st.session_state.get("show_idea_form"):
        with st.form("new_idea_form"):
            title = st.text_input("Idea title", placeholder="What's your idea?")
            description = st.text_area("Description (optional)", placeholder="Elaborate a bit...")
            col_s, col_c = st.columns(2)
            with col_s:
                submitted = st.form_submit_button("Submit Idea", type="primary", use_container_width=True)
            with col_c:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)
            if submitted and title:
                create_idea(room_id, user_id, title, description)
                st.session_state["show_idea_form"] = False
                st.rerun()
            if cancelled:
                st.session_state["show_idea_form"] = False
                st.rerun()

    # Filter bar
    filter_col, sort_col = st.columns([2, 1])
    with filter_col:
        status_filter = st.multiselect(
            "Filter by status",
            STATUSES,
            default=["Open", "Selected", "In Progress"],
            label_visibility="collapsed",
            placeholder="Filter by status...",
        )
    with sort_col:
        sort_by = st.selectbox("Sort", ["Newest", "Most Voted"], label_visibility="collapsed")

    filtered = [i for i in ideas if i["status"] in (status_filter or STATUSES)]
    if sort_by == "Most Voted":
        filtered.sort(key=lambda x: x["vote_count"], reverse=True)

    if not filtered:
        st.info("No ideas yet. Start the brainstorm! 🚀")
    else:
        for idea in filtered:
            render_idea_card(idea, user_id)
