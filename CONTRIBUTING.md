# Contributing to PostgresAI

PostgresAI is built on [Google ADK](https://google.github.io/adk-docs/) — a multi-agent framework for building LLM-powered agent hierarchies. This guide explains how to extend PostgresAI using ADK patterns already established in the codebase.

---

## Developer Certificate of Origin (DCO)

All contributions must be signed off under the [Developer Certificate of Origin v1.1](DCO). This certifies that you wrote the contribution or have the right to submit it under the project's open source license.

**Sign off every commit** by adding a `Signed-off-by` trailer to your commit message:

```bash
git commit -s -m "feat: add new specialist agent for X"
```

This produces a commit message like:

```
feat: add new specialist agent for X

Signed-off-by: Jane Smith <jane@example.com>
```

To sign off retroactively on the last N commits:

```bash
git rebase HEAD~N --signoff
```

A GitHub Actions workflow checks every PR for a valid sign-off on all commits. PRs without it will fail the DCO check and cannot be merged.

If you forget to sign off, you can amend the most recent commit:

```bash
git commit --amend --signoff
git push --force-with-lease
```

---

## Adding a new specialist agent

Each specialist lives in a sub-directory under its pillar folder:

```
src/postgres_ai/objagents/sub_agents/<pillar>/<specialist_name>/
    agent.py      # defines the ADK Agent
    prompt.py     # system instructions
    tools.py      # optional specialist-scoped tools
```

**Minimal agent.py:**

```python
from google.adk.agents import LlmAgent
from ..config import PRIMARY_MODEL, get_planner
from .prompt import INSTRUCTIONS

ag_my_specialist = LlmAgent(
    name="MY_SPECIALIST",
    description="One sentence describing what this specialist handles.",
    model=PRIMARY_MODEL,
    instruction=INSTRUCTIONS,
    planner=get_planner(thinking_budget=512),  # 512 for specialist-level
    tools=[],  # add tools here
)
```

Then register it in the pillar's `agent.py` via `LazyAgentTool`:

```python
LazyAgentTool(
    module_path="postgres_ai.objagents.sub_agents.<pillar>.<specialist_name>.agent",
    agent_attr="ag_my_specialist",
    name="MY_SPECIALIST",
    description="One sentence describing what this specialist handles.",
)
```

The `LazyAgentTool` pattern defers the module import until the first invocation — nothing is loaded at startup. The background pre-warmer will pick it up automatically via BFS traversal once it's registered in the pillar.

---

## Adding a new pillar

1. Create `src/postgres_ai/objagents/sub_agents/<new_pillar>/agent.py` following the same pattern as existing pillars (e.g. `administrator/agent.py`).
2. Set `planner=get_planner(thinking_budget=1024)` — pillar agents get the higher budget.
3. Populate it with `LazyAgentTool` entries for each specialist.
4. Register the new pillar in `src/postgres_ai/objagents/agent.py` using `LazyAgentTool`.
5. Add a row to the Agent Hierarchy table in `README.md`.

---

## Extending the safety callback

The `execute_query` tool in `tools.py` intercepts every query before it reaches PostgreSQL. Extend the safety checks to block any additional patterns:

```python
# Safety gate: block DROP unconditionally
if "DROP " in query.upper():
    return {"success": False, "query": query,
            "message": "Query blocked: 'DROP' is not permitted. Use ALTER or CREATE IF NOT EXISTS instead."}

# Safety gate: require human approval for TRUNCATE
if "TRUNCATE" in query.upper():
    # ... approval logic ...
```

You can add additional safety checks here for other dangerous operations.

---

## Swapping the model provider

Set `MODEL_PROVIDER` in your `.env` to switch all agents at once:

| Provider | `MODEL_PROVIDER` | Notes |
|---|---|---|
| Google Gemini | `google` (default) | Enables `BuiltInPlanner` with `ThinkingConfig` |
| OpenAI | `openai` | Routed via LiteLLM; planner disabled |
| Anthropic Claude | `anthropic` | Routed via LiteLLM; planner disabled |
| Any LiteLLM model | `openai` or `anthropic` | Set `MODEL_PRIMARY` / `MODEL_THINKING` to the LiteLLM model string |

`config.py` resolves `PRIMARY_MODEL` and `THINKING_MODEL` from env vars — no code changes needed to switch providers.

---

## Adjusting thinking budgets

`get_planner(thinking_budget)` in `config.py` returns a `BuiltInPlanner` for Google models, `None` otherwise. The budget controls how many tokens the model may spend reasoning before it responds.

Recommended tiers (already used in PostgresAI):

| Agent level | Budget |
|---|---|
| Manager + pillar agents | 1 024 |
| Specialist agents | 512 |
| Sub-pipeline agents | 256 |

Raise the budget if an agent makes poor multi-step decisions; lower it to reduce latency and token cost.

---

## Adding a web search backend

The Research Agent selects its search tool based on `IS_GOOGLE_MODEL` (set in `config.py`):

- **Gemini** — uses `google_search`, a built-in ADK tool with native retrieval augmentation
- **All other models** — uses `web_search` (DuckDuckGo via `duckduckgo-search`)

To swap in a different search backend, edit `src/postgres_ai/objagents/sub_agents/research/tools.py` and replace the tool passed to the inner search agent. Any callable that accepts a query string and returns text works.

---

## Session state conventions

PostgresAI uses ADK's scoped session state. Follow existing conventions when writing to state from a new agent or tool:

| Prefix | Scope | Examples |
|---|---|---|
| `user:` | Per user, persists across sessions | `user:PG_USER`, `user:PG_PASSWORD` |
| `app:` | Shared across all users in a session | `app:TASKS_PERFORMED`, `app:RESEARCH_RESULTS` |
| `temp:` | Single turn, discarded after | Intermediate scratchpad values |

Append completed tasks to `app:TASKS_PERFORMED` so the Manager can validate progress:

```python
state["app:TASKS_PERFORMED"].append({"task": "...", "result": "..."})
```

---

## PostgreSQL-specific considerations

When adding new PostgreSQL object types or features:

1. **Check PostgreSQL version compatibility** - Some features are version-specific (e.g., generated columns in PG12+, partitioning improvements in PG10+)
2. **Use information_schema and pg_catalog appropriately** - Inspection agents should query the appropriate system catalogs
3. **Consider security implications** - New object types may have different privilege models
4. **Test with different authentication methods** - Support for password, md5, scram-sha-256, etc.

---

## Testing your changes

1. **Unit tests** - Add tests for new tools or utility functions
2. **Integration tests** - Test agent interactions with a test PostgreSQL instance
3. **Safety tests** - Verify that dangerous operations are properly blocked
4. **Performance tests** - Ensure new agents don't significantly impact response times

Use the included pytest configuration to run tests:

```bash
cd postgresai
python -m pytest tests/ -v
```

---

## ADK resources

- [Google ADK documentation](https://google.github.io/adk-docs/)
- [ADK models](https://google.github.io/adk-docs/agents/models/) — full list of supported providers
- [ADK tools](https://google.github.io/adk-docs/tools/) — built-in tools including `google_search`, `AgentTool`, code execution
- [ADK session state](https://google.github.io/adk-docs/sessions/state/) — scoped state management reference
- [BuiltInPlanner / ThinkingConfig](https://google.github.io/adk-docs/agents/llm-agents/#built-in-planning) — native reasoning for Gemini models

---

## PostgreSQL resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Official documentation
- [PostgreSQL System Catalogs](https://www.postgresql.org/docs/current/catalogs.html) - Reference for inspection queries
- [PostgreSQL Extension Network](https://pgxn.org/) - Community extensions
- [PostgreSQL Wiki](https://wiki.postgresql.org/) - Community knowledge base