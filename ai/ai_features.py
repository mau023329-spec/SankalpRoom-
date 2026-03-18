"""
SankalpRoom — Advanced AI Features
All 7 new AI features as clean additions to the existing ai module.

Features:
1. AI Decision Score (impact/effort/recommendation per idea)
2. Decision Locked Mode (lock + AI summary on selection)
3. Idea Evolution Tracking (version history)
4. Goal Alignment Check (before marking Selected)
5. Smart Subgroup Assignment (task → subgroup suggestions)
6. Idea Heatmap (vote-based visual indicator)
7. AI Memory Panel (past decisions + patterns)
"""

import json
import streamlit as st
from database.db import fetchone, fetchall, execute
from ai.ai_assistant import _call_groq, SYSTEM


# ══════════════════════════════════════════════════════════════════
# 1. AI DECISION SCORE
# ══════════════════════════════════════════════════════════════════

def compute_decision_score(idea_title: str, idea_desc: str) -> dict:
    """
    Returns: {impact: int, effort: int, recommendation: str, raw: str}
    Calls Groq and parses structured JSON response.
    """
    prompt = f"""You are evaluating an idea for a team. Return ONLY valid JSON, no other text.

Idea: "{idea_title}"
Description: "{idea_desc or 'No description provided.'}"

Return exactly this JSON structure:
{{
  "impact": <integer 1-10>,
  "effort": <integer 1-10>,
  "recommendation": "<Proceed or Reconsider>",
  "reason": "<one sentence>"
}}

Rules:
- impact 1=very low value, 10=transformative value
- effort 1=trivial, 10=extremely complex
- Proceed if impact >= 6 and impact > effort-2
- Reconsider otherwise"""

    raw = _call_groq(
        "You are a precise JSON-only API. Return only valid JSON, no markdown, no explanation.",
        prompt,
        max_tokens=200,
    )

    try:
        # Strip markdown code fences if model wrapped it
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data    = json.loads(cleaned)
        return {
            "impact":         int(data.get("impact", 5)),
            "effort":         int(data.get("effort", 5)),
            "recommendation": str(data.get("recommendation", "Reconsider")),
            "reason":         str(data.get("reason", "")),
        }
    except Exception:
        # Fallback — parse manually if JSON fails
        return {"impact": 5, "effort": 5, "recommendation": "Reconsider", "reason": raw[:120]}


def save_decision_score(idea_id: int, impact: int, effort: int, rec: str):
    execute(
        "UPDATE ideas SET impact_score=%s, effort_score=%s, ai_score_rec=%s WHERE id=%s",
        (impact, effort, rec, idea_id),
    )


def render_decision_score(idea: dict):
    """Inline score badges shown under each idea card."""
    impact = idea.get("impact_score")
    effort = idea.get("effort_score")
    rec    = idea.get("ai_score_rec")

    if impact is None:
        return  # Not scored yet

    rec_color = "#22C55E" if rec == "Proceed" else "#F59E0B"
    i_color   = "#6366F1" if impact >= 7 else ("#F59E0B" if impact >= 4 else "#EF4444")
    e_color   = "#22C55E" if effort <= 4 else ("#F59E0B" if effort <= 7 else "#EF4444")

    st.markdown(
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.35rem;margin-bottom:0.25rem;">'
        f'<span style="background:{i_color}18;color:{i_color};border:1px solid {i_color}30;'
        f'border-radius:6px;padding:2px 8px;font-size:0.68rem;font-weight:600;font-family:Inter,sans-serif;">'
        f'⚡ Impact {impact}/10</span>'
        f'<span style="background:{e_color}18;color:{e_color};border:1px solid {e_color}30;'
        f'border-radius:6px;padding:2px 8px;font-size:0.68rem;font-weight:600;font-family:Inter,sans-serif;">'
        f'🔧 Effort {effort}/10</span>'
        f'<span style="background:{rec_color}18;color:{rec_color};border:1px solid {rec_color}30;'
        f'border-radius:6px;padding:2px 8px;font-size:0.68rem;font-weight:600;font-family:Inter,sans-serif;">'
        f'{"✅" if rec == "Proceed" else "⚠️"} {rec}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# 2. DECISION LOCKED MODE
# ══════════════════════════════════════════════════════════════════

def lock_idea(idea_id: int, idea_title: str, idea_desc: str, room_id: int):
    """Lock an idea and generate AI final summary. Call when status → Selected."""
    prompt = f"""An idea has just been selected by the team. Generate a concise locked decision record.

Idea: "{idea_title}"
Description: "{idea_desc or 'No description.'}"

Return ONLY valid JSON:
{{
  "summary": "<2 sentence final summary>",
  "why_selected": "<1 sentence: main reason team chose this>",
  "next_steps": "<3 bullet points as a single string, each starting with • >"
}}"""

    raw = _call_groq(
        "You are a precise JSON-only API. Return only valid JSON.",
        prompt,
        max_tokens=300,
    )

    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data    = json.loads(cleaned)
        summary    = data.get("summary", "Idea selected by team.")
        why        = data.get("why_selected", "Team consensus.")
        next_steps = data.get("next_steps", "• Plan\n• Execute\n• Review")
    except Exception:
        summary, why, next_steps = "Selected idea.", "Team consensus.", "• Plan\n• Execute\n• Review"

    execute(
        "UPDATE ideas SET is_locked=TRUE, lock_summary=%s, lock_reason=%s, lock_next_steps=%s WHERE id=%s",
        (summary, why, next_steps, idea_id),
    )

    # Save to AI memory
    save_memory_event(room_id, "selected", idea_id,
                      f"Selected: '{idea_title}'. {why}")


def render_lock_badge(idea: dict):
    """Shows locked badge + expandable AI summary on selected ideas."""
    if not idea.get("is_locked"):
        return

    st.markdown(
        '<span style="background:#22C55E18;color:#22C55E;border:1px solid #22C55E30;'
        'border-radius:6px;padding:2px 8px;font-size:0.68rem;font-weight:700;'
        'font-family:Inter,sans-serif;">🔒 Decision Locked</span>',
        unsafe_allow_html=True,
    )

    with st.expander("📋 View Decision Record", expanded=False):
        if idea.get("lock_summary"):
            st.markdown(f"**Summary:** {idea['lock_summary']}")
        if idea.get("lock_reason"):
            st.markdown(f"**Why selected:** {idea['lock_reason']}")
        if idea.get("lock_next_steps"):
            st.markdown(f"**Next steps:**\n{idea['lock_next_steps']}")


# ══════════════════════════════════════════════════════════════════
# 3. IDEA EVOLUTION / VERSION HISTORY
# ══════════════════════════════════════════════════════════════════

def save_idea_version(idea_id: int, title: str, description: str, changed_by: int):
    """Call before updating an idea to preserve the old version."""
    execute(
        "INSERT INTO idea_versions(idea_id, title, description, changed_by) VALUES(%s,%s,%s,%s)",
        (idea_id, title, description or "", changed_by),
    )


def get_idea_versions(idea_id: int) -> list:
    return fetchall(
        """SELECT iv.*, u.name as editor_name
           FROM idea_versions iv
           JOIN users u ON iv.changed_by = u.id
           WHERE iv.idea_id = %s
           ORDER BY iv.changed_at DESC""",
        (idea_id,),
    )


def render_version_history(idea: dict):
    """Expandable version history panel for an idea."""
    versions = get_idea_versions(idea["id"])
    if not versions:
        return

    with st.expander(f"🕐 Version history ({len(versions)} edits)", expanded=False):
        for v in versions:
            st.markdown(
                f'<div style="border-left:2px solid #1C2030;padding:0.5rem 0.75rem;margin-bottom:0.5rem;">'
                f'<div style="font-size:0.7rem;color:#475569;font-family:Inter,sans-serif;margin-bottom:0.2rem;">'
                f'{str(v.get("changed_at",""))[:16]} · {v.get("editor_name","?")}</div>'
                f'<div style="font-size:0.82rem;color:#CBD5E1;font-family:Space Grotesk,sans-serif;font-weight:600;">'
                f'{v["title"]}</div>'
                + (f'<div style="font-size:0.75rem;color:#475569;margin-top:0.15rem;">{v["description"]}</div>'
                   if v.get("description") else "")
                + f'</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════
# 4. GOAL ALIGNMENT CHECK
# ══════════════════════════════════════════════════════════════════

def get_room_goal(room_id: int) -> str:
    row = fetchone("SELECT goal FROM rooms WHERE id=%s", (room_id,))
    return (row.get("goal") or "") if row else ""


def save_room_goal(room_id: int, goal: str):
    execute("UPDATE rooms SET goal=%s WHERE id=%s", (goal, room_id))


def check_alignment(idea_title: str, idea_desc: str, room_goal: str) -> dict:
    """Check if idea aligns with room goal. Returns {score, aligned, reason}."""
    if not room_goal:
        return {"score": 0, "aligned": None, "reason": "No room goal set."}

    prompt = f"""Evaluate how well this idea aligns with the team goal. Return ONLY valid JSON.

Team Goal: "{room_goal}"
Idea: "{idea_title}"
Description: "{idea_desc or ''}"

Return:
{{
  "score": <integer 1-10>,
  "aligned": <true or false>,
  "reason": "<one sentence>"
}}"""

    raw = _call_groq(
        "You are a precise JSON-only API. Return only valid JSON.",
        prompt,
        max_tokens=150,
    )
    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data    = json.loads(cleaned)
        return {
            "score":   int(data.get("score", 5)),
            "aligned": bool(data.get("aligned", True)),
            "reason":  str(data.get("reason", "")),
        }
    except Exception:
        return {"score": 5, "aligned": True, "reason": "Could not evaluate."}


def render_alignment_check(idea: dict, room_id: int):
    """Show alignment check UI before marking idea as Selected."""
    goal = get_room_goal(room_id)
    if not goal:
        return

    key = f"align_{idea['id']}"
    if st.button("🎯 Check Goal Alignment", key=key, use_container_width=True):
        with st.spinner("Checking alignment…"):
            result = check_alignment(idea["title"], idea.get("description",""), goal)

        score   = result["score"]
        aligned = result["aligned"]
        reason  = result["reason"]
        color   = "#22C55E" if aligned else "#EF4444"
        label   = "✅ Aligned" if aligned else "❌ Misaligned"

        st.markdown(
            f'<div style="background:{color}0F;border:1px solid {color}30;border-radius:8px;'
            f'padding:0.75rem 1rem;margin-top:0.5rem;">'
            f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;">'
            f'<span style="color:{color};font-weight:700;font-size:0.85rem;">{label}</span>'
            f'<span style="color:#475569;font-size:0.75rem;">({score}/10 alignment score)</span>'
            f'</div>'
            f'<div style="color:#CBD5E1;font-size:0.78rem;font-family:Inter,sans-serif;">{reason}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.progress(score / 10)


# ══════════════════════════════════════════════════════════════════
# 5. SMART SUBGROUP ASSIGNMENT
# ══════════════════════════════════════════════════════════════════

def suggest_subgroup_assignments(idea_title: str, idea_desc: str, subgroups: list) -> str:
    """Returns markdown with task → subgroup mapping."""
    if not subgroups:
        return "No subgroups exist yet. Create subgroups first."

    sg_list = "\n".join(f"- {sg['name']}: {sg.get('description','')}" for sg in subgroups)

    prompt = f"""An idea has been selected. Map specific tasks to the right subgroups.

Idea: "{idea_title}"
Description: "{idea_desc or ''}"

Available Subgroups:
{sg_list}

For each subgroup, suggest 2-3 specific tasks it should own.
Format as:

### 🔬 [Subgroup Name]
- **Task**: brief description · Priority: High/Med/Low

Only include subgroups that have relevant tasks. Be specific and actionable."""

    return _call_groq(SYSTEM, prompt, max_tokens=600)


# ══════════════════════════════════════════════════════════════════
# 6. IDEA HEATMAP
# ══════════════════════════════════════════════════════════════════

def compute_heatmap_score(idea: dict) -> int:
    """
    Score 0-100 based on:
    - like votes ×3, high_priority ×5, do_later ×1
    - recency bonus if updated recently
    """
    votes  = idea.get("votes", {})
    score  = (
        votes.get("like", 0) * 3 +
        votes.get("high_priority", 0) * 5 +
        votes.get("do_later", 0) * 1
    )
    return min(score * 10, 100)  # cap at 100


def render_heatmap_badge(idea: dict):
    """Visual heat indicator shown next to idea title."""
    score = compute_heatmap_score(idea)

    if score >= 70:
        color, label, emoji = "#EF4444", "🔥 Trending", "#EF4444"
    elif score >= 40:
        color, label, emoji = "#F59E0B", "⚡ Active", "#F59E0B"
    elif score >= 10:
        color, label, emoji = "#6366F1", "💬 Discussed", "#6366F1"
    else:
        color, label, emoji = "#334155", "❄️ Cold", "#475569"

    st.markdown(
        f'<span style="background:{color}12;color:{color};border:1px solid {color}22;'
        f'border-radius:6px;padding:1px 7px;font-size:0.65rem;font-weight:600;'
        f'font-family:Inter,sans-serif;">{label}</span>',
        unsafe_allow_html=True,
    )
    if score > 0:
        st.progress(score / 100)


# ══════════════════════════════════════════════════════════════════
# 7. AI MEMORY PANEL
# ══════════════════════════════════════════════════════════════════

def save_memory_event(room_id: int, event_type: str, idea_id: int | None, summary: str):
    execute(
        "INSERT INTO ai_memory(room_id, event_type, idea_id, summary) VALUES(%s,%s,%s,%s)",
        (room_id, event_type, idea_id, summary),
    )


def get_room_memory(room_id: int, limit: int = 30) -> list:
    return fetchall(
        """SELECT m.*, i.title as idea_title
           FROM ai_memory m
           LEFT JOIN ideas i ON m.idea_id = i.id
           WHERE m.room_id = %s
           ORDER BY m.created_at DESC
           LIMIT %s""",
        (room_id, limit),
    )


def render_memory_panel(room_id: int):
    """Full AI Memory tab panel."""
    st.markdown(
        '<div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;font-weight:700;'
        'color:#F1F5F9;margin-bottom:0.75rem;">🧠 AI Memory</div>'
        '<div style="color:#475569;font-size:0.78rem;font-family:Inter,sans-serif;'
        'margin-bottom:1rem;">Every decision, rejection and pattern — automatically tracked.</div>',
        unsafe_allow_html=True,
    )

    # ── Room Goal ────────────────────────────────────────────────
    st.markdown("**🎯 Room Goal**")
    current_goal = get_room_goal(room_id)
    with st.form("room_goal_form", border=False):
        new_goal = st.text_input(
            "Team goal",
            value=current_goal,
            placeholder="e.g. Launch MVP by Q2 with focus on retention",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Save goal", type="primary", use_container_width=True):
            save_room_goal(room_id, new_goal)
            st.success("Goal saved!")
            st.rerun()

    st.divider()

    # ── Memory Events ────────────────────────────────────────────
    events = get_room_memory(room_id)
    if not events:
        st.markdown(
            '<div style="text-align:center;padding:2rem;border:1px dashed #1C2030;'
            'border-radius:8px;color:#334155;font-family:Inter,sans-serif;font-size:0.82rem;">'
            '🧠 Memory builds automatically as your team makes decisions.</div>',
            unsafe_allow_html=True,
        )
        return

    # Group by event type
    ICON = {"selected": "✅", "dropped": "❌", "pattern": "🔗"}
    COLOR = {"selected": "#22C55E", "dropped": "#EF4444", "pattern": "#6366F1"}

    # Summary counts
    selected_n = sum(1 for e in events if e["event_type"] == "selected")
    dropped_n  = sum(1 for e in events if e["event_type"] == "dropped")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("✅ Selected", selected_n)
    with c2:
        st.metric("❌ Dropped", dropped_n)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    for ev in events:
        et    = ev.get("event_type","pattern")
        icon  = ICON.get(et, "📌")
        color = COLOR.get(et, "#475569")
        title = ev.get("idea_title") or "General"

        st.markdown(
            f'<div style="border-left:3px solid {color};padding:0.5rem 0.75rem;'
            f'margin-bottom:0.5rem;background:#0C0E14;border-radius:0 6px 6px 0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-size:0.78rem;font-weight:600;color:#CBD5E1;">{icon} {title}</span>'
            f'<span style="font-size:0.65rem;color:#334155;">{str(ev.get("created_at",""))[:10]}</span>'
            f'</div>'
            f'<div style="font-size:0.73rem;color:#475569;margin-top:0.2rem;">{ev.get("summary","")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Pattern Analysis ──────────────────────────────────────────
    st.divider()
    if st.button("🔍 Analyse Patterns", use_container_width=True, key="ai_patterns"):
        if len(events) < 3:
            st.info("Need at least 3 decisions to analyse patterns.")
        else:
            summaries = "\n".join(
                f"- [{e['event_type']}] {e.get('idea_title','?')}: {e.get('summary','')}"
                for e in events[:20]
            )
            prompt = f"""Analyse this team's decision history and identify patterns:

{summaries}

Provide:
### 🔗 Patterns Observed
### 💡 What the Team Values
### ⚠️ Blind Spots or Risks
### 🚀 Recommendation for Next Decisions

Keep it concise and actionable."""
            with st.spinner("Analysing…"):
                result = _call_groq(SYSTEM, prompt, 500)
            st.markdown(result)
