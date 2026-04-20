<div align="center">

```
███╗   ███╗██╗ ██████╗██╗  ██╗
████╗ ████║██║██╔════╝██║ ██╔╝
██╔████╔██║██║██║     █████╔╝ 
██║╚██╔╝██║██║██║     ██╔═██╗ 
██║ ╚═╝ ██║██║╚██████╗██║  ██╗
╚═╝     ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝
          ╰─ by Gyrus Inc ─╯
```

**An open-source, self-hosted agentic framework that turns plain English into PostgreSQL operations.**

  ---                                                                                                                                                                                                                
  ### 🛡️ Trusted & Validated                                                                                                                                                                                         
  **Accelerated by the Confluent Accelerator Program for AI Startups (Cohort-3).**                                                                                                                                   
  MICK's autonomous agent framework for PostgreSQL has been refined and validated through the Confluent AI startup ecosystem.                                                                                        
                                                                                                                                                                                                                     
  🚀 **Get Started Faster:** Need help deploying Mick or want to see the latest PostgreSQL agent recipes?                                                                                                            
  [**Join the Gyrus Discord Community**](https://discord.gg/GpgVzJ6ku) to connect with other database architects and the Gyrus team.                                                                                 
  ---  

  ---                                                                                                                                                                                                                
  ### 🚀 Get Started Faster                                                                                                                                                                                          
  **Need help deploying Mick or want to see the latest PostgreSQL agent recipes?**                                                                                                                                   
  [**Join the Gyrus Discord Community**](https://discord.gg/GpgVzJ6ku) to connect with other database architects and the Gyrus team.                                                                                 
  ---   

[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)](https://www.python.org/)
[![Models](https://img.shields.io/badge/models-Claude%20%7C%20Gemini%20%7C%20OpenAI-green)](#model-provider)
[![Agents](https://img.shields.io/badge/agents-20%2B%20specialists-orange)](#architecture)
[![PostgreSQL](https://img.shields.io/badge/built%20for-PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)

[**Quick Start**](#quick-start) · [**Features**](#spotlight-features) · [**Architecture**](#architecture) · [**Setup**](#setup) · [**Safety**](#safety) · [**Contributing**](#contributing) · [**Discord**](https://discord.gg/Qtncaksxp) · [**Get in Touch**](#get-in-touch)

If you find MICK useful, please consider giving it a ⭐ — it helps others discover the project!

</div>

---

## What is MICK?

MICK is a **multi-agent system** built by [Gyrus Inc](https://www.thegyrus.com) that lets you manage your entire PostgreSQL environment in plain English — from designing schemas to administering security policies.

```
"create a multi-tenant SaaS schema with RLS"
  → Designs tables, indexes, roles, and row-level security policies

"show me the top 10 slowest queries"
  → Queries pg_stat_statements and returns analysis

"set up logical replication to another instance"
  → Creates publication, subscription, and replication slots
```

Unlike other AI tooling for databases, **you host it, you own it, and you pay nothing beyond your LLM tokens** — no additional SaaS platform, no per-seat fees, no extra subscriptions.

---

## Why MICK?

Building a production-ready PostgreSQL environment with proper security, performance tuning, and monitoring is a significant engineering undertaking. MICK compresses that effort from weeks to under an hour.

Beyond building infrastructure, MICK helps you get the most out of PostgreSQL across the full lifecycle:
- **Security hardening** (row-level security, column permissions, password policies) — so your environment is production-ready from day one
- **Performance optimization** (query analysis, index recommendations, vacuum tuning) — so your database performs at scale
- **Data governance** (RLS policies, audit trails, access controls) — so the right people see the right data

All from natural language, in minutes.
  > **Pro Tip:** Fighting a stubborn performance bottleneck or trying to optimize your vacuum settings? Describe your `pg_stat_statements` findings in the `#help-and-support` channel on our                        
**[Discord](https://discord.gg/GpgVzJ6ku)**, and we'll help you refine your agent sequence to fix it.                                                                                                                
```

| | |
|---|---|
| 🏠 **Self-hosted** | Agents run in your environment. Credentials never leave your machine. Every line of logic is readable and modifiable. |
| 🔁 **Bring your own model** | Works with OpenAI, Anthropic Claude, and Google Gemini out of the box. Swap in a single `.env` line — no code changes. |
| 🎯 **Purpose-built for PostgreSQL** | 20+ specialist agents cover the full surface area: data engineering, administration, security, monitoring, and read-only inspection. |
| 🛡️ **Safe by design** | `DROP` is unconditionally blocked in code. `TRUNCATE` requires explicit terminal approval. No parallel execution — one object at a time, in dependency order. |
| 🔍 **Context-aware** | The INSPECTOR_PILLAR maps your live environment before any plan is executed — no assumptions, no hallucinated object names. |
| 💬 **Natural language all the way** | Query data, profile tables, generate synthetic rows, monitor performance, and inspect costs — all from plain English. |

> Want to see it in action? [Schedule a demo →](mailto:priyank@thegyrus.com)

---

## Quick Start

```bash
git clone https://github.com/Gyrus-Dev/Mick.git
cd Mick
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in your PostgreSQL credentials and model API key (see [Configure](#configure)), then:

```bash
python -m src.postgres_ai.objagents.main
```

> Full setup details — authentication, model providers, observability — are in [Setup](#setup) below.

---

## Safety

MICK enforces two independent safeguards before any query reaches PostgreSQL.

### Layer 1 — Agent instructions (prompt-level)

Every agent prefers `CREATE IF NOT EXISTS` or `ALTER` over `DROP`. `DROP` is forbidden outright. Agents may generate `TRUNCATE` only when explicitly requested — and even then, execution gates it with a human approval prompt.

### Layer 2 — `execute_query` safety gate (code-level)

A hard-coded check in `tools.py` intercepts every call before it reaches PostgreSQL:

- **`DROP`** — blocked unconditionally. No prompt, no override.
- **`TRUNCATE`** — execution pauses. The full statement is shown in a red panel; you type `yes` or `no` to proceed or abort.

```
User request
     │
     ▼
Agent generates SQL
     │
     ▼  execute_query safety gate (tools.py)
     │   ├─ contains "DROP"?              → hard blocked, never reaches PostgreSQL
     │   ├─ contains "TRUNCATE"?          → paused, user approval prompt shown
     │   │       ├─ user types "yes"      → passed through
     │   │       └─ user types "no"       → blocked, agent tries alternative
     │   └─ clean                         → passed through
     │
     ▼
execute_query() → PostgreSQL
```

Because Layer 2 is **code, not a prompt**, it cannot be bypassed by prompt injection or model drift.

You can extend the gate in `tools.py` to block any additional patterns your environment requires:

```python
# Add to the hard-block section (alongside DROP):
_hard_blocked = ["DROP ", "TRUNCATE ", "DELETE FROM prod."]
for pattern in _hard_blocked:
    if pattern.upper() in query.upper():
        return {"success": False, "query": query,
                "message": f"Query blocked: '{pattern.strip()}' is not permitted."}
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    CLI  (Rich + prompt_toolkit)                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ user message
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│               MICK  (Manager)                                    │
│   Classifies intent · produces execution plan · delegates        │
│   one task at a time · validates every step via state            │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────┬───┘
       ▼          ▼          ▼          ▼          ▼          ▼
  DATA        ADMIN     SECURITY    INSPECTOR   ACCOUNT    RESEARCH
  ENGINEER                           PILLAR      MONITOR     AGENT
  9+ spec     3 spec    2 spec      3 spec      3 spec     1 spec
       └──────────┴──────────┴──────────┴──────────┴──────────┘
                                 │
                                 ▼
                          execute_query()  ──►  PostgreSQL
                                                    │
                                                    ▼
                                        app:TASKS_PERFORMED
                                (each completed task appended to state)
```

### Agent Pillars

| Pillar | Role | Specialists |
|---|---|---|
| **MICK** | Manager — plans, routes, validates | — |
| **DATA_ENGINEER** | Physical data layer orchestrator | 9+ |
| **ADMINISTRATOR** | Users, roles, privileges | 3 |
| **SECURITY_ENGINEER** | Row-level & column-level access control | 2 |
| **INSPECTOR_PILLAR** | Read-only infrastructure inspection | 3 |
| **ACCOUNT_MONITOR** | Query stats, connections & table health | 3 |
| **RESEARCH_AGENT** | Web search & knowledge cache — shared fallback | — |

### How It Works

1. **You type** a natural language request (e.g. *"Create a multi-tenant SaaS schema with row-level security"*)
2. **The Manager** classifies intent, inspects your live infrastructure via the INSPECTOR_PILLAR, and produces an execution plan
3. **Pillar agents** receive delegated tasks one at a time and produce their own detailed sub-plans
4. **Specialist agents** generate and execute PostgreSQL DDL via `execute_query`
5. **After every step**, the Manager validates success via `get_session_state` before proceeding
6. **SQL panels** display every executed statement in real time
7. **On exit**, all queries are saved to a `.sql` file

---

## Spotlight Features

### 🔍 Natural Language Data Queries

Ask questions about your PostgreSQL data in plain English and get SQL-powered answers — no SQL knowledge required.

```
"how many orders did we get last month?"
"show me the top 10 customers by revenue"
"what's the average order value by region?"
```

The `DATA_ANALYST` specialist discovers your schema, generates accurate PostgreSQL SQL from full column context, enforces a **read-only safety gate** (rejects any non-SELECT statement), and returns a plain-English answer with Markdown tables.

Trigger phrases: *"how many"*, *"show me"*, *"top N"*, *"compare"*, *"query my data"*, *"what's the revenue"*

---

### 📊 Data Profiling

Get a comprehensive statistical report on any table in seconds — no SQL required.

```
"profile the orders table in public schema"
```

The `DATA_PROFILER` runs a **single SQL pass** across all columns (not one query per column), keeping query overhead minimal even on wide tables. Output is a 4-section Markdown report covering table summary, column profiles, value distributions, and data quality flags.

| Flag | Condition |
|---|---|
| ⚠️ High null rate | `null_pct > 20%` |
| ⚠️ All-null column | `null_pct = 100%` |
| ⚠️ Constant column | `distinct_count = 1` |
| ℹ️ High-cardinality ID | `distinct ≈ total_rows` |

Trigger phrases: *"profile"*, *"check data quality"*, *"show null rates"*, *"analyze distribution"*, *"explore table"*

---

### 🧪 Stored Procedure Validation

MICK never writes a stored procedure directly. Every new or updated procedure goes through a mandatory two-step flow.

**Step 1 — Validation (dry run, always rolled back)**

The procedure is created under a unique throwaway name, called with sample args inside a transaction, then **always rolled back** — pass or fail. Nothing persists in PostgreSQL. Syntax errors and runtime failures are caught here before the real procedure is touched.

**Step 2 — Real creation**

Only after validation passes does `execute_query` run the actual statement. If `CREATE OR REPLACE` is needed, the standard approval prompt fires before execution.

If validation fails 5 consecutive times, the `RESEARCH_AGENT` is automatically invoked to look up the latest PostgreSQL docs from the web (with session caching to avoid duplicate fetches), then retries with fresh knowledge.

---

### 🧬 Synthetic Data Generation

Populate any table with realistic sample data — MICK inspects the table structure first and generates contextually appropriate values.

```
"populate the orders table with 10 rows"
```

`\d+ <table>` is the single source of truth — column names are never invented. Values are domain-aware: `email` columns get valid email addresses, `status` columns get enum-appropriate values, `jsonb` columns get minimal valid JSON.

---

### 🌐 Web Search & Research Agent

Specialist agents follow a two-step knowledge hierarchy before generating any DDL or query.

**Step 1 — SKILL.md reference** (when `USE_SKILLS=true`, the default)
Each specialist has a curated reference doc covering every supported parameter, its default value, and when to use it — producing accurate, non-bloated DDL without hallucinating unsupported syntax.

**Step 2 — RESEARCH_AGENT fallback**
If the specialist cannot resolve something from its reference docs, it delegates to the RESEARCH_AGENT for live web lookup. Results are persisted to `app:RESEARCH_RESULTS` in session state — the same answer is never fetched twice within a session.

```
  Gemini models  →  google_search (built-in grounding)
  All others     →  DuckDuckGo · top 5 results (configurable in research/tools.py)
```

---

### 🤔 Thinking & Reasoning (Gemini only)

When using Gemini models, every agent uses `ThinkingConfig` to reason silently before responding — improving decision quality for complex DDL and multi-step plans without surfacing the thinking to the user.

| Agent level | Thinking budget |
|---|---|
| Manager + pillar agents | 1,024 tokens |
| Specialist agents | 512 tokens |

---

### 💾 Chat History & Persistent Sessions

By default MICK uses ADK's `InMemorySessionService` — full conversation context is held in memory for the session and lost on exit.

**Persist session history** — swap to `DatabaseSessionService` in `adksession.py`:

```python
from google.adk.sessions import DatabaseSessionService
session_service = DatabaseSessionService(db_url="sqlite:///mick_sessions.db")
# or: db_url="postgresql://user:pass@host/dbname"
```

**Add long-term memory** — plug in a `memory_service` in `adkrunner.py` to offload conversation summaries to an external store, freeing the context window for the current task:

```python
from google.adk.memory import VertexAiMemoryBankService
runner = ADKRunner(
    agent=agent,
    app_name=app_name,
    session_service=session_service,
    memory_service=VertexAiMemoryBankService(...),
)
```

Any class implementing ADK's `BaseMemoryService` works — SQLite, Redis, a vector database, or any other backend.

---

## PostgreSQL Objects Supported

<details>
<summary><strong>Data Engineering — 35+ object types</strong></summary>

Databases · Schemas · Tables · Views · Materialized Views · Indexes · Sequences · Functions · Stored Procedures · Triggers · Event Triggers · Rules · Types · Domains · Casts · Conversions · Extensions · Tablespaces · Foreign Data Wrappers · Foreign Servers · Foreign Tables · User Mappings · Publications · Subscriptions · Collations · Aggregates · Operators · Operator Classes · Operator Families · Language Definitions · Transforms · Text Search Configurations · Text Search Dictionaries · Text Search Parsers · Text Search Templates · Access Methods · Synthetic Data Generation

</details>

<details>
<summary><strong>Administration — 3 object types</strong></summary>

Users (Roles) · Roles · Grants & Privileges

</details>

<details>
<summary><strong>Security — 2 object types</strong></summary>

Row-Level Security Policies · Column Permissions

</details>

<details>
<summary><strong>Account Monitoring — 3 views across 3 domains</strong></summary>

**Query & Performance** — Query Statistics (pg_stat_statements) · Query Analysis  
**Connections** — Active Connections · Connection Health  
**Storage** — Table & Index Statistics · Bloat Analysis

</details>

---

  ## 🤝 Join the Ecosystem                                                                                                                                                                                           
                                                                                                                                                                                                                     
  Mick is open-source and community-driven. We aren't just building a tool; we're creating a hub for Agentic Data Ops across all major platforms (Snowflake, SQL Server, and PostgreSQL). Join our Discord to:       
                                                                                                                                                                                                                     
  * **🛠️ Get Agent Recipes:** Discover the most effective prompt sequences for automating multi-tenant SaaS schemas and complex RLS policies.                                                                        
  * **🗺️ Influence the Roadmap:** Vote on new features and tell us which database extensions or operational patterns we should automate next.                                                                        
  * **⚡ Direct Access:** Get real-time architectural guidance and support from the creators at Gyrus Inc.                                                                                                           
  * **🧪 Beta Access:** Get early access to new specialist agents and experimental pillars before they hit the main branch.                                                                                          
                                                                                                                                                                                                                     
  [**👉 Enter the Gyrus Discord**](https://discord.gg/GpgVzJ6ku)  

## Setup

### Prerequisites

- Python 3.11+
- A PostgreSQL instance (local or remote)
- An API key for your chosen model provider

### Install

```bash
git clone https://github.com/Gyrus-Dev/Mick.git
cd Mick
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root by copying the provided template:

```bash
cp .env.example .env
```

Then fill in your values — refer to `.env.example` for all available variables and their descriptions.

#### PostgreSQL Connection

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_HOST` | **Yes** | PostgreSQL server hostname (e.g. `localhost`) |
| `POSTGRES_PORT` | No | Port number (default: `5432`) |
| `POSTGRES_DATABASE` | **Yes** | Target database name |
| `POSTGRES_USER` | **Yes** | PostgreSQL username |
| `POSTGRES_PASSWORD` | **Yes** | PostgreSQL password |

#### Application Identity

| Variable | Required | Description |
|---|---|---|
| `APP_USER_NAME` | **Yes** | Display name shown in the session (e.g. your name) |
| `APP_USER_ID` | **Yes** | Unique user ID for session tracking (e.g. `user_001`) |
| `APP_NAME` | **Yes** | Application name for session scoping (e.g. `mick`) |

#### Model Provider

| Variable | Required | Description |
|---|---|---|
| `MODEL_PROVIDER` | No | `google` (default) · `openai` · `anthropic` |
| `GOOGLE_API_KEY` | If `google` | API key for Gemini models |
| `OPENAI_API_KEY` | If `openai` | API key for OpenAI models |
| `ANTHROPIC_API_KEY` | If `anthropic` | API key for Claude models |
| `MODEL_PRIMARY` | No | Override the fast model. Defaults: `gemini-2.5-flash` · `gpt-4o-mini` · `claude-3-5-haiku-20241022` |
| `MODEL_THINKING` | No | Override the reasoning model. Defaults: `gemini-2.5-pro-preview-03-25` · `gpt-4o` · `claude-3-5-sonnet-20241022` |

MICK supports **OpenAI**, **Claude**, and **Gemini** out of the box. Any model supported by Google ADK can also be used — see the [ADK Models documentation](https://google.github.io/adk-docs/agents/models/).

#### Debug & Feature Flags

| Variable | Default | Description |
|---|---|---|
| `MICK_DEBUG` | `0` | Set to `1` to print agent thinking, tool calls, and payloads |
| `USE_SKILLS` | `true` | Agents consult SKILL.md reference docs before generating DDL. Set `false` to rely on model knowledge only (fewer tokens, slightly faster) |

#### Observability (OpenTelemetry + Grafana Cloud)

Built-in OpenTelemetry instrumentation — **off by default**, zero overhead when disabled. Set `OTEL_ENABLED=true` to export to any OTLP-compatible backend (Grafana Cloud, Tempo, Jaeger, etc.).

| Signal | What is captured |
|---|---|
| **Traces** | Root span per user request; span per agent model call; span per PostgreSQL query (with `db.statement`, `db.user`, `db.rows_returned`) |
| **Metrics** | `mick.queries.total`, `mick.queries.errors`, `mick.agent.invocations`, `mick.query.duration_ms` |
| **Logs** | All Python loggers bridged to the OTLP log exporter |

| Variable | Required | Description |
|---|---|---|
| `OTEL_ENABLED` | No | `true` to enable, `false` to disable (default) |
| `OTEL_SERVICE_NAME` | No | Service name in Grafana (default: `mick`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | If enabled | Your OTLP gateway URL |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | No | `http/protobuf` (required for Grafana Cloud) |
| `OTEL_EXPORTER_OTLP_HEADERS` | If enabled | Auth header — use `Basic%20` instead of `Basic ` for Python |

**Grafana Cloud setup:**
1. Go to your stack → **Details** → **OpenTelemetry**
2. Generate a token with `metrics:write`, `logs:write`, `traces:write` scopes
3. Copy the endpoint URL and `Authorization=Basic%20<token>` header value

**Viewing data:**
```
Traces  → Explore → Tempo       → Service name: mick_open_source
Metrics → Explore → Prometheus  → search "mick_"
Logs    → Explore → Loki        → Label: service_name = mick_open_source
```

> Metrics are exported on a 60-second interval. Use `exit` (not Ctrl+C) to trigger a graceful flush of buffered spans.

#### Example `.env`

```env
# --- PostgreSQL ---
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=mydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# --- App identity ---
APP_USER_NAME=John Doe
APP_USER_ID=user_001
APP_NAME=mick

# --- Model provider (default: Google Gemini) ---
GOOGLE_API_KEY=your_google_api_key
# MODEL_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key
# MODEL_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key

# --- Observability / Grafana Cloud (optional) ---
# OTEL_ENABLED=true
# OTEL_SERVICE_NAME=mick_open_source
# OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-3.grafana.net/otlp
# OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
# OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic%20<your-base64-token>
```

### Run

```bash
python -m src.postgres_ai.objagents.main
```

Enable debug output:
```bash
MICK_DEBUG=1 python -m src.postgres_ai.objagents.main
```

### Agent Loading & Warm-up

All specialist agents load **lazily** — nothing is imported at startup. A background thread walks the agent tree level by level and imports each level in parallel, so agents warm up progressively while you work.

The first time a pillar is invoked in a session it may feel slightly slower; the CLI will show: *"Loading {agent} for the first time in this session..."* Within a couple of minutes all agents are pre-warmed and subsequent calls are instant.

---

## CLI Features

| Feature | Description |
|---|---|
| **Boxed input** | `prompt_toolkit` framed text input with cyan border |
| **Animated spinner** | Braille frames tracking the active agent |
| **Response panels** | Markdown-rendered AI responses in blue panels |
| **SQL panels** | Syntax-highlighted executed queries in green panels (monokai theme) |
| **Question panels** | Clarifying questions surfaced in yellow panels |
| **Object counter** | Live terminal title + inline `[● Objects created: N]` counter |
| **Session export** | All executed SQL written to `queries/session_<timestamp>.sql` on exit |
| **Debug mode** | `MICK_DEBUG=1` to print agent thinking, tool calls, and payloads |

---

## Project Structure

```
postgresai/
├── src/
│   └── postgres_ai/
│       └── objagents/
│           ├── agent.py                  # Root agent (POSTGRES_ARCHITECT)
│           ├── main.py                   # CLI entry point & REPL loop
│           ├── prompt.py                 # Manager instructions
│           ├── tools.py                  # execute_query, get_session_state, etc.
│           ├── config.py                 # Model configuration
│           ├── _spinner.py               # Animated terminal spinner
│           └── sub_agents/
│               ├── administrator/        # 3 admin specialists (user, role, grant)
│               ├── dataengineer/         # 35+ data engineering specialists
│               ├── securityengineer/     # 2 security specialists
│               ├── inspector/            # Read-only inspection specialists
│               ├── accountmonitor/       # Query stats, connection & table monitoring
│               └── research/             # Research & web search agent
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Framework | Google ADK 1.0+; OpenAI, Claude, Gemini (2.5 Flash / 2.5 Pro) + [more](https://google.github.io/adk-docs/agents/models/) |
| PostgreSQL | psycopg2-binary 2.9+ |
| Terminal UI | Rich 13+, prompt_toolkit 3+ |
| Validation | Pydantic 2.5+ |
| Observability | OpenTelemetry SDK + OTLP HTTP exporter; Grafana Cloud (Tempo · Mimir · Loki) |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for a guide on adding specialist agents, new pillars, custom safety rules, ADK Skills, and extending MICK with other ADK capabilities.

---

## Build Your Own MICK

MICK is designed to be extended. Fork it, specialize it for your domain — retail, finance, healthcare, logistics — and build your own PostgreSQL-powered agent on top of the same multi-agent architecture.

Whether it's a finance-focused database bot, a security-hardening specialist, or a fully custom data platform agent — the architecture is yours to build on.

Share what you build: [priyank@thegyrus.com](mailto:priyank@thegyrus.com)

---

## Enterprise

For enterprise features and managed hosting — including persistent sessions and long-term memory out of the box — visit [thegyrus.com](https://www.thegyrus.com) or [get in touch](#get-in-touch).

---

## Community

Join our [Discord](https://discord.gg/Qtncaksxp) to ask questions, share what you've built, and connect with other MICK users.

---

## Get in Touch

Interested in a demo, want to discuss your PostgreSQL setup, or just have questions?

- 📧 General enquiries: [info@thegyrus.com](mailto:info@thegyrus.com)
- 📧 Priyank (co-founder): [priyank@thegyrus.com](mailto:priyank@thegyrus.com)
- 📅 Book a call: [Schedule time with Priyank](https://calendar.app.google/LtgREjn9kx1zNqn1A)

---

## License

© 2025 Gyrus Inc — [www.thegyrus.com](https://www.thegyrus.com)
