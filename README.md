# 🤖 Proactive Maintenance Agent

The **Proactive Maintenance Agent** is an autonomous, event-driven CI/CD AI pipeline designed to safeguard your codebase against upstream API deprecations without direct human intervention.

When third-party providers (like OpenAI, Google, Stripe, etc.) send automated deprecation alerts via email, this agent springs into action. It parses the deprecation notice, discovers where the legacy API is used in your codebase using Semantic RAG search, uses an AI Orchestrator to rewrite the code, pushes a branch, opens a Pull Request, and notifies your engineering team on Slack.

## ✨ Features

- **📧 Automated Email Ingestion:** Listens to an inbox for developer alert emails (e.g., "deprecation", "migration").
- **🧠 Intelligent Parsing:** Uses Gemini to extract structured payload data (Old API, New API, Deadlines).
- **🕸️ RAG Codebase Search:** Vectorizes your local repository and performs high-accuracy semantic searches to locate every file utilizing the deprecated API.
- **🛠️ AI Code Rewriting:** Modifies only the affected files using a strict LLM orchestrator prompt to ensure code remains valid and runnable.
- **🐙 Git & GitHub Automation:** Automatically commits changes, pushes headless branches, and generates Pull Requests.
- **💬 Slack Notifications:** Pings the engineering channel via a rich Block Kit Slack Webhook with a direct link to the PR.

## 🚀 How It Works

1. **Phase 1: Ingestion & Extraction**  
   The `master_agent.py` pulls unread emails. If it detects a deprecation alert, it hands the payload off to `email_parser.py` (powered by Gemini) to cleanly map the variables.
   
2. **Phase 2: Discovery via RAG**  
   `rag_agent.py` embeds the codebase into an in-memory ChromaDB vector store. It searches the codebase for explicit or implicit references to the deprecated API.
   
3. **Phase 3: AI Code Patching**  
   `orchestrator.py` loops over the affected files, instructing the AI to perform surgical updates replacing the `old_api` with the `new_api`.

4. **Phase 4: The CI/CD Loop**  
   A new branch is created natively. A Git push is authorized via your `GITHUB_TOKEN`, and `github_agent.py` opens the PR. Finally, a beautifully formatted Slack message alerts the team.

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/proactive_maintenance_agent.git
   cd proactive_maintenance_agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add the following keys:
   ```env
   # LLM Tokens
   GEMINI_API_KEY=your_gemini_key

   # Email Configuration (for the inbox receiving alerts)
   EMAIL_HOST=imap.gmail.com
   EMAIL_USER=your_email@domain.com
   EMAIL_PASSWORD=your_app_password

   # GitHub Automation
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_REPO=username/repo-name

   # Slack Integration
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

## 🏃‍♂️ Running the Agent

Start the master daemon:
```bash
python master_agent.py
```
*The agent will spin up, initialize the embedding models, and begin polling the inbox every 60 seconds.*

## 📂 Architecture Overview

- `master_agent.py`: The entry point and event loop.
- `orchestrator.py`: Manages the patching process, Git logic, and Slack alerts.
- `rag_agent.py`: ChromaDB semantic search engine.
- `email_fetcher.py` / `email_parser.py`: IMAP listener and Gemini extraction pipeline.
- `github_agent.py`: GitHub API interface for Pull Requests.
- `models.py`: Pydantic schemas.

---
*Built to ensure zero downstream breakages for the modern developer community.*

