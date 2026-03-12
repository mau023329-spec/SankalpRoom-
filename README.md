# ⚡ SankalpRoom

> AI-Powered Team Collaboration Platform — Where ideas become decisions, and decisions become action.

SankalpRoom is a Streamlit-based MVP for async team collaboration. Teams move through a structured workflow:

**Discuss → Analyze → Vote → Decide → Split → Execute**

---

## ✨ Features

### 🏠 Rooms (Decision Hubs)
- Create or join rooms with invite codes
- Team chat with @mention support
- Type `/ai <question>` or `@ai` in chat to get instant AI responses

### 💡 Ideas Board
- Submit and manage ideas in real time
- Vote with 👍 Like · 🔥 High Priority · ⏳ Do Later
- Statuses: Open → Selected → In Progress → Dropped
- Filter and sort ideas

### 🔬 Subgroups (Execution Spaces)
- Create focused execution teams within a room
- Kanban board (To Do / Doing / Done)
- Task assignment, priorities, deadlines
- Subgroup chat

### 🤖 SankalpAI
- Brainstorm ideas on any topic
- Deep-analyze individual ideas (pros/cons/risks/effort)
- Cluster similar ideas and find themes
- Impact vs Effort 2×2 matrix
- Break selected ideas into tasks with subgroup assignments
- Weekly team summaries
- Discussion summarizer

### 🔐 Auth
- Email + password registration & login
- Invite-code based room access
- Users can belong to multiple rooms

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sankalproom.git
cd sankalproom
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AI (Optional but Recommended)

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your Anthropic API key:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Get your API key at: https://console.anthropic.com

> **Note:** The app works without an API key in demo mode — AI responses will be placeholder content.

### 5. Run the App

```bash
streamlit run app.py
```

Open your browser to: **http://localhost:8501**

---

## 📁 Project Structure

```
sankalproom/
│
├── app.py                  # Main Streamlit app entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore
│
├── .streamlit/
│   ├── config.toml         # Streamlit theme & server config
│   └── secrets.toml        # API keys (not committed to git)
│
├── database/
│   └── db.py               # SQLite schema, init, and helpers
│
├── auth/
│   └── auth.py             # Registration, login, session management
│
├── rooms/
│   └── rooms.py            # Rooms, subgroups, messages, members
│
├── ideas/
│   └── ideas.py            # Idea CRUD, voting, status management
│
├── tasks/
│   └── tasks.py            # Task CRUD and Kanban board
│
├── ai/
│   └── ai_assistant.py     # Claude AI integrations
│
└── ui/
    └── components.py       # Reusable UI components and global CSS
```

---

## 🎨 Design

Dark-first UI with custom Streamlit theming:

| Token      | Color     |
|------------|-----------|
| Base       | `#0F1115` |
| Primary    | `#4F46E5` |
| AI Accent  | `#8B5CF6` |
| Success    | `#22C55E` |
| Warning    | `#F59E0B` |

Fonts: **Syne** (headings) + **DM Sans** (body)

---

## 💡 Usage Tips

| Action | How |
|--------|-----|
| Create a room | Sidebar → "➕ Create Room" |
| Invite teammates | Share the **INVITE CODE** shown in your room |
| Join a room | Sidebar → "🔗 Join Room" → enter code |
| Submit an idea | Ideas Board → "➕ Add Idea" |
| Vote on an idea | 👍 🔥 ⏳ buttons on each idea card |
| Ask AI in chat | Type `/ai your question` or `@ai your question` |
| Create subgroup | Subgroups tab → "➕ New Subgroup" |
| Move Kanban task | → To Do / → Doing / → Done buttons on cards |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.32+
- **Backend**: Python 3.10+
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **AI**: Anthropic Claude API (`claude-opus-4-6`)
- **Auth**: SHA-256 hashed passwords (suitable for MVP)

---

## 📦 Create a Downloadable ZIP

To package the project:

```bash
# From parent directory
zip -r sankalproom.zip sankalproom/ \
  --exclude "sankalproom/.venv/*" \
  --exclude "sankalproom/__pycache__/*" \
  --exclude "sankalproom/*.db" \
  --exclude "sankalproom/.streamlit/secrets.toml"
```

Or on Windows (PowerShell):
```powershell
Compress-Archive -Path .\sankalproom -DestinationPath sankalproom.zip -CompressionLevel Optimal
```

---

## 🌐 Push to GitHub

```bash
cd sankalproom
git init
git add .
git commit -m "Initial commit: SankalpRoom MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sankalproom.git
git push -u origin main
```

---

## 🔮 Roadmap

- [ ] Real-time updates with Streamlit's `st.experimental_rerun` + polling
- [ ] File attachments in chat
- [ ] Email notifications for task deadlines
- [ ] OAuth (Google/GitHub login)
- [ ] Export ideas & tasks to PDF/CSV
- [ ] Streamlit Community Cloud deployment

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ⚡ Streamlit + 🤖 Claude AI*
