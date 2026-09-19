# ⚡ Foreman: Autonomous Software Development Engine

> A production-grade, full-stack task orchestration platform that decomposes natural language requirements into an executable Directed Acyclic Graph (DAG), managing real-time agent workflows and code generation.

![Full-Stack Architecture](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20TypeScript-blue)
![WebSocket Status](https://img.shields.io/badge/RealTime-WebSockets-green)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🚀 About The Project

**Foreman** is a sophisticated task orchestration engine built to simulate autonomous software engineering workflows. Instead of standard sequential scripts, Foreman treats complex coding tasks as a **Directed Acyclic Graph (DAG)** — managing strict node dependencies (`PENDING`, `RUNNING`, `PASSED`), executing operations asynchronously, and streaming real-time status updates, logs, and file structures directly to a modern React dashboard via **WebSockets**.

Whether used as a foundation for local code-generation models or as a standalone pipeline engine, Foreman highlights modern full-stack systems engineering, non-blocking concurrency, and clean state synchronization.

---

## ✨ Key Engineering Features

* **🧠 DAG Task Orchestration:** Dynamically processes project parameters into structured task dependency graphs, ensuring code execution order is logically preserved.
* **⚡ Real-Time WebSocket Streaming:** Replaces sluggish HTTP polling with an active, bi-directional event loop that streams state transitions and execution logs live to the browser.
* **⚙️ Asynchronous Backend Engine:** Powered by FastAPI background tasks to handle multi-agent simulation workloads cleanly without blocking API thread performance.
* **📂 Dynamic Workspace Manager:** Automatically aggregates multi-file code outputs into a tabbed UI code viewer complete with syntax highlighting, single-click copy utility, and on-the-fly `.zip` archive generation.

---

## 🛠️ Tech Stack

### Backend
* **Framework:** Python, FastAPI, Uvicorn (ASGI)
* **Validation & Concurrency:** Pydantic, WebSockets, AsyncIO
* **Database & Storage:** SQLite, SQLAlchemy ORM

### Frontend
* **Framework:** React, TypeScript, Vite
* **Styling:** Tailwind CSS, Lucide Icons
* **Real-Time Hook:** Custom WebSocket state synchronization layer

---

## 📂 Project Architecture

```text
foreman/
├── backend/
│   ├── app/
│   │   ├── agents/      # Autonomous agent definitions & execution logic
│   │   ├── core/        # Core orchestrator, DAG logic, database, & WebSockets
│   │   ├── models/      # Pydantic schemas & data models
│   │   ├── routes/      # REST API endpoints & project management
│   │   └── main.py      # FastAPI application entry point
│   ├── Dockerfile.sandbox  # Containerization template for isolated runs
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    └── src/
        ├── components/  # TaskGraphView, WorkspaceViewer, LogStream, etc.
        ├── hooks/       # Custom useWebSocket state hook
        ├── App.tsx      # Root dashboard layout
        └── types.ts     # TypeScript type interfaces
```

---

## ⚙️ Getting Started Locally

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/foreman.git
cd foreman
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Set Up the Frontend

Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

---

## 🗺️ Future Roadmap

- [ ] **Pluggable LLM Integration:** Seamless `BaseAgent` swapping for local models via Ollama or cloud-tier APIs (Google Gemini).
- [ ] **Token-Aware Event Streams:** Token-by-token live streaming directly through the WebSocket pipeline.
- [ ] **AST-Based Code Validation:** Python Abstract Syntax Tree parsing and automated error-feedback loops for self-healing code generation.

---

## 📄 License
- Distributed under the MIT License.