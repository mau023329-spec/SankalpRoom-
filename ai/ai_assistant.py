"""
SankalpRoom - AI Assistant Module
Powered by Groq (llama-3.3-70b-versatile) for fast, smart collaboration features.
"""

import os
import streamlit as st

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# ── Client ────────────────────────────────────────────────────────────────────

def _get_client():
    api_key = st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key or not GROQ_AVAILABLE:
        return None
    return Groq(api_key=api_key)


def _is_configured() -> bool:
    return bool(
        st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    )


# ── Core call ─────────────────────────────────────────────────────────────────

def _call_groq(system: str, user_message: str, max_tokens: int = 800) -> str:
    client = _get_client()
    if not client:
        return _fallback_response()
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq Error: {str(e)}"


def _fallback_response() -> str:
    return (
        "🤖 **SankalpAI** (Demo Mode)\n\n"
        "Add `GROQ_API_KEY` to your Streamlit secrets to unlock full AI features.\n\n"
        "**Sample ideas to get you started:**\n"
        "- **Leverage team strengths** to tackle the core challenge head-on\n"
        "- **Break the problem into sprints** for faster, measurable progress\n"
        "- **Gather user feedback early** to validate before you build\n\n"
        "_Get a free Groq API key at [console.groq.com](https://console.groq.com)_"
    )


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM = (
    "You are SankalpAI, an expert team collaboration and innovation strategist "
    "embedded in SankalpRoom. Your job is to help teams brainstorm effectively, "
    "analyze ideas critically, and make great decisions. "
    "Be concise, practical, and energizing. Use markdown formatting. "
    "Keep responses focused and actionable."
)


# ── Public AI functions ───────────────────────────────────────────────────────

def brainstorm_ideas(topic: str, context: str = "") -> str:
    prompt = f"""Generate 5 creative, diverse brainstorming ideas for this topic:

**Topic:** {topic}
{f'**Context:** {context}' if context else ''}

For each idea provide:
- 💡 **Idea title** (bold)
- One-line description
- Key benefit

Make ideas diverse in approach (technical, creative, process-oriented, collaborative, etc.)"""
    return _call_groq(SYSTEM, prompt, 700)


def expand_idea(title: str, description: str) -> str:
    prompt = f"""Provide a comprehensive analysis of this idea:

**Idea:** {title}
**Description:** {description}

Structure your analysis as:
### ✅ Pros
### ⚠️ Cons
### 🎯 Risks
### ⚡ Effort (Low / Medium / High) with brief explanation
### 🚀 Quick Win
One thing the team can do in the next 48 hours to validate this idea."""
    return _call_groq(SYSTEM, prompt, 600)


def cluster_ideas(ideas: list) -> str:
    if not ideas:
        return "No ideas to cluster yet."
    idea_list = "\n".join(f"- {i['title']}: {i.get('description', '')}" for i in ideas)
    prompt = f"""Cluster these ideas into themes and identify patterns:

{idea_list}

Output:
### 🗂️ Idea Clusters
Group similar ideas with cluster name and brief rationale.

### 🔗 Common Threads
What underlying themes or goals connect these ideas?

### 🏆 Top Recommendation
Which cluster should the team focus on first and why?"""
    return _call_groq(SYSTEM, prompt, 600)


def impact_effort_analysis(ideas: list) -> str:
    if not ideas:
        return "No ideas to analyze yet."
    idea_list = "\n".join(f"- {i['title']}" for i in ideas)
    prompt = f"""Rate each idea on a 2x2 Impact vs Effort matrix:

Ideas:
{idea_list}

For each idea assign:
- Impact: Low / Medium / High
- Effort: Low / Medium / High
- Quadrant: Quick Win / Major Project / Fill-In / Avoid

Format as a clear table:
| Idea | Impact | Effort | Quadrant | Recommendation |

Then give a 2-sentence strategic recommendation."""
    return _call_groq(SYSTEM, prompt, 700)


def summarize_discussion(messages: list, ideas: list) -> str:
    if not messages:
        return "No discussion to summarize yet."
    chat_text   = "\n".join(f"{m['user_name']}: {m['content']}" for m in messages[-30:])
    idea_titles = ", ".join(i["title"] for i in ideas[:10])
    prompt = f"""Summarize this team discussion:

**Chat excerpt:**
{chat_text}

**Ideas on the board:** {idea_titles or 'None yet'}

Provide:
### 📋 Discussion Summary (3-4 sentences)
### 🔑 Key Points Raised
### 💡 Ideas Getting Traction
### ⚡ Suggested Next Steps"""
    return _call_groq(SYSTEM, prompt, 600)


def break_idea_into_tasks(idea_title: str, idea_description: str, subgroups: list) -> str:
    sg_names = ", ".join(sg["name"] for sg in subgroups) if subgroups else "No subgroups defined"
    prompt = f"""Break this selected idea into executable tasks:

**Idea:** {idea_title}
**Description:** {idea_description}
**Available Subgroups:** {sg_names}

Provide:
### 📋 Task Breakdown
List 5-8 specific, actionable tasks. For each task:
- **Task name**
- Suggested subgroup assignment (from the list above, or suggest creating a new one)
- Priority: 🔴 Critical / 🟠 High / 🟡 Medium / 🔵 Low
- Estimated effort: hours / days

### 📅 Suggested Timeline
A simple week-by-week execution plan.

### ⚠️ Dependencies & Risks
Key blockers to watch out for."""
    return _call_groq(SYSTEM, prompt, 800)


def weekly_summary(room_name: str, messages: list, ideas: list, tasks: list) -> str:
    stats = {
        "messages":       len(messages),
        "ideas":          len(ideas),
        "ideas_selected": len([i for i in ideas if i["status"] == "Selected"]),
        "tasks_done":     len([t for t in tasks if t.get("status") == "done"]),
        "tasks_total":    len(tasks),
    }
    prompt = f"""Generate a weekly progress report for the team room "{room_name}":

**Activity Stats:**
- {stats['messages']} messages exchanged
- {stats['ideas']} ideas submitted, {stats['ideas_selected']} selected
- {stats['tasks_done']}/{stats['tasks_total']} tasks completed

**Top Ideas:**
{chr(10).join('- ' + i['title'] for i in ideas[:5])}

Write a motivating, professional weekly summary including:
### 🏆 Week Highlights
### 📊 Progress Metrics
### 💡 Standout Ideas
### 🚀 Next Week Focus
Keep it concise and encouraging. Max 250 words."""
    return _call_groq(SYSTEM, prompt, 500)


def chat_with_ai(user_message: str, room_context: str = "") -> str:
    system = SYSTEM + "\nYou are in a team chat. Be helpful, concise, and collaborative."
    prompt = (f"Room context: {room_context}\n" if room_context else "") + user_message
    return _call_groq(system, prompt, 500)


# ── Render AI Panel ───────────────────────────────────────────────────────────

def render_ai_panel(room_id: int, ideas: list, messages: list, subgroups: list):
    st.markdown("### 🤖 SankalpAI — Powered by Groq")

    if not _is_configured():
        st.info(
            "💡 **Enable AI:** open your app's **Settings → Secrets** and add:\n"
            "```\nGROQ_API_KEY = \"gsk_...\"\n```\n"
            "Get a free key at [console.groq.com](https://console.groq.com)"
        )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💡 Brainstorm", "🔍 Analyze", "📋 Break Down", "📊 Summary", "🔬 Assign", "🧠 Memory"])

    with tab1:
        topic   = st.text_input("What should the team brainstorm?", placeholder="e.g., Product launch strategy")
        context = st.text_area("Context (optional)", placeholder="Team size, constraints, goals...", height=80)
        if st.button("🚀 Generate Ideas", type="primary", use_container_width=True, key="ai_brainstorm"):
            if topic:
                with st.spinner("SankalpAI is thinking..."):
                    result = brainstorm_ideas(topic, context)
                st.markdown(result)

    with tab2:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Expand Idea", "Cluster", "Impact/Effort"])

        with sub_tab1:
            if ideas:
                idea_titles    = [i["title"] for i in ideas]
                selected_title = st.selectbox("Select idea to expand", idea_titles, key="expand_sel")
                selected       = next((i for i in ideas if i["title"] == selected_title), None)
                if st.button("🔍 Deep Analyze", type="primary", use_container_width=True, key="ai_expand"):
                    with st.spinner("Analyzing..."):
                        result = expand_idea(selected["title"], selected.get("description", ""))
                    st.markdown(result)
            else:
                st.info("Add some ideas first!")

        with sub_tab2:
            if st.button("🗂️ Cluster All Ideas", type="primary", use_container_width=True, key="ai_cluster"):
                if ideas:
                    with st.spinner("Clustering ideas..."):
                        result = cluster_ideas(ideas)
                    st.markdown(result)
                else:
                    st.info("Add some ideas first!")

        with sub_tab3:
            if st.button("📊 Impact vs Effort Matrix", type="primary", use_container_width=True, key="ai_matrix"):
                if ideas:
                    with st.spinner("Analyzing impact and effort..."):
                        result = impact_effort_analysis(ideas)
                    st.markdown(result)
                else:
                    st.info("Add some ideas first!")

    with tab3:
        selected_ideas = [i for i in ideas if i["status"] in ["Selected", "In Progress"]]
        if selected_ideas:
            sel_titles = [i["title"] for i in selected_ideas]
            chosen     = st.selectbox("Choose selected idea", sel_titles, key="breakdown_sel")
            idea_obj   = next((i for i in selected_ideas if i["title"] == chosen), None)
            if st.button("⚙️ Break Into Tasks", type="primary", use_container_width=True, key="ai_tasks"):
                with st.spinner("Creating task breakdown..."):
                    result = break_idea_into_tasks(idea_obj["title"], idea_obj.get("description", ""), subgroups)
                st.markdown(result)
        else:
            st.info("Mark an idea as **Selected** to break it into tasks.")

    with tab4:
        if st.button("📋 Generate Weekly Summary", type="primary", use_container_width=True, key="ai_summary"):
            with st.spinner("Generating summary..."):
                from rooms.rooms import get_room
                room      = get_room(room_id)
                tasks_all = []
                for sg in subgroups:
                    from tasks.tasks import get_subgroup_tasks
                    tasks_all.extend(get_subgroup_tasks(sg["id"]))
                result = weekly_summary(room["name"] if room else "Team", messages, ideas, tasks_all)
            st.markdown(result)

        if st.button("💬 Summarize Discussion", use_container_width=True, key="ai_discuss"):
            with st.spinner("Summarizing discussion..."):
                result = summarize_discussion(messages, ideas)
            st.markdown(result)

    # ── NEW: Smart Subgroup Assignment tab ────────────────────────
    with tab5:
        from ai.ai_features import suggest_subgroup_assignments
        selected_ideas = [i for i in ideas if i["status"] in ["Selected","In Progress"]]
        if not selected_ideas:
            st.info("Mark an idea as **Selected** first.")
        else:
            sel_titles = [i["title"] for i in selected_ideas]
            chosen     = st.selectbox("Pick selected idea", sel_titles, key="sg_assign_sel")
            idea_obj   = next((i for i in selected_ideas if i["title"] == chosen), None)
            if st.button("🔬 Suggest Subgroup Tasks", type="primary", use_container_width=True, key="ai_sg_assign"):
                if not subgroups:
                    st.warning("Create subgroups first so AI can assign tasks.")
                else:
                    with st.spinner("Mapping tasks to subgroups…"):
                        result = suggest_subgroup_assignments(
                            idea_obj["title"],
                            idea_obj.get("description",""),
                            subgroups,
                        )
                    st.markdown(result)

    # ── NEW: AI Memory tab ────────────────────────────────────────
    with tab6:
        from ai.ai_features import render_memory_panel
        render_memory_panel(room_id)
