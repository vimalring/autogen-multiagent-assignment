# 🏢 Enterprise Multi-Agent Support Portal

A context-aware, multi-agent customer support system built with **Streamlit** and **AutoGen v0.4+ (AgentChat)**. A dedicated **Triage Router** analyzes each incoming query with GPT-4o and routes the conversation to the specialized grounded agent — Finance, IT, HR, or Product & Engineering — best suited to handle it.

---

## 🌟 Key Features

### 🧠 Intelligent Query Routing
Every user message is classified by `ai_triage_router()` in [agents_config.py](agents_config.py), a raw GPT-4o call (not a full agent) that reads the latest query plus a rolling window of the last few messages and returns one of four category labels. If the model returns anything outside the four known categories, the router falls back to the **Product & Engineering Agent** so the request is never dropped.

### 💎 Live Telemetry Sidebar
[app.py](app.py) renders a persistent sidebar that shows:
- **Current Focus** — whether the system is idle or actively assigned to an agent.
- **Persistent Routing History** — a running log of every query and the agent it was routed to, with timestamps.
- **Active Pipeline Progress** — live status messages ("Triage Manager inspecting...", "Initializing workspace runtime context...", "Frame cycle processing complete.") as each request moves through the pipeline.

### 🛡️ Tool-Grounded Agents
Two of the four agents call real Python functions instead of answering from model knowledge alone:
- **Finance Agent** — calls `query_invoice_ledger()`, which looks up an invoice ID against a small in-memory mock ERP ledger and returns its payment status.
- **HR Team Agent** — calls `search_hr_policy_handbook()`, a keyword-matched lookup (leave/holiday, insurance/health) standing in for a vector-backed HR policy handbook.

IT Support and Product & Engineering currently answer from their system prompts alone, with no attached tools.

### 🔄 Per-Session Memory & Typewriter Streaming
- Each `AssistantAgent` maintains its own internal message history for the life of the Streamlit session, so follow-up questions to the same agent retain context.
- Responses aren't dumped to the screen — `get_agent_response()` runs the agent to completion, then `st.write_stream()` replays the text word-by-word (with a small delay) for a live-typing effect, after a `st.spinner()` "thinking" indicator while the actual agent call is in flight.

---

## ⚙️ How It Works (Data Flow)

1. **User Input** — an employee submits a query via `st.chat_input()`.
2. **Triage** — `ai_triage_router(query, history)` sends the query and recent chat history to GPT-4o and gets back a category name.
3. **Routing** — the sidebar and session state update to show which agent (e.g. `HR Team Agent`) was assigned.
4. **Agent Execution** — `get_agents()[agent_name].run(task=query)` executes that `AssistantAgent`'s full AutoGen run loop, invoking its tool (if any) when needed.
5. **Response Rendering** — the final message content is streamed word-by-word into the chat via `st.write_stream()`, and the exchange is appended to `st.session_state.messages`.

If the agent run raises an exception, `app.py` catches it, logs the fault to the pipeline sidebar, and shows the stack trace in an expandable panel instead of crashing the app.

---

## 🛠️ Project Structure

```text
Autogen_Customer_Support_AI/
│
├── app.py                # Streamlit frontend: session state, sidebar telemetry,
│                          # chat rendering, async execution, streaming output.
│
├── agents_config.py       # Orchestration layer: OpenAI model client, mock tools,
│                          # the four AssistantAgent definitions, and the triage router.
│
├── requirements.txt       # Pinned dependencies (streamlit, autogen-*, dotenv, pydantic).
│
├── .env                   # Local-only config storing OPENAI_API_KEY (not committed).
│
└── README.md               # This file.
```

---

## 🚀 Setup & Run

**1. Create a virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure your API key**

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**3. Launch the app**
```bash
streamlit run app.py
```

---

## 🧩 The Four Agents

| Agent | Handles | Tool |
|---|---|---|
| **Finance Agent** | Payroll, expenses, tax, invoices | `query_invoice_ledger` (mock ERP lookup) |
| **IT Support Agent** | Hardware, software access, VPN, password resets | — |
| **HR Team Agent** | Leaves, holidays, health benefits, onboarding | `search_hr_policy_handbook` (mock keyword lookup) |
| **Product & Engineering Agent** | Software bugs, downtime, feature requests | — (also the default fallback if routing is ambiguous) |

---

## 📌 Notes & Current Limitations

- All model calls use `gpt-4o` at `temperature=0.2`, defined once in `agents_config.py` and shared across the router and all four agents.
- The invoice ledger and HR handbook are **in-memory mock data**, not live/external systems — swap in real API/database calls to productionize.
- Conversational memory lives only in Streamlit's session state and each agent's in-memory run history; nothing is persisted across app restarts.
- `execute_coroutine()` in `app.py` works around Streamlit's synchronous execution model to safely run AutoGen's async agent calls.
