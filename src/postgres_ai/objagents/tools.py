import logging
import time
from google.adk.tools import ToolContext
from src.postgres_ai.telemetry import tracer, query_counter, query_errors, query_latency


def execute_query(query: str, tool_context: ToolContext) -> dict:
    """Execute a PostgreSQL query using credentials from session state."""
    with tracer.start_as_current_span("postgres.execute_query") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.statement", query[:500])
        t0 = time.monotonic()
        try:
            logger = logging.getLogger(__name__)
            from src.session import Session as PostgresSession

            pg_user = tool_context.state.get("user:PG_USER")
            pg_host = tool_context.state.get("app:PG_HOST")
            if not pg_user or not pg_host:
                raise ValueError("Missing PostgreSQL credentials in session state.")

            sess = PostgresSession()
            sess.set_host(pg_host)
            sess.set_port(tool_context.state.get("app:PG_PORT", 5432))
            sess.set_user(pg_user)
            sess.set_password(tool_context.state.get("user:PG_PASSWORD"))
            db = tool_context.state.get("app:PG_DATABASE")
            if db:
                sess.set_database(db)

            # Safety gate: block DROP unconditionally
            if "DROP " in query.upper():
                return {"success": False, "query": query,
                        "message": "Query blocked: 'DROP' is not permitted. Use ALTER or CREATE IF NOT EXISTS instead."}

            # Safety gate: require human approval for TRUNCATE
            if "TRUNCATE" in query.upper():
                from ._spinner import spinner as _sp
                from rich.console import Console as _Console
                from rich.panel import Panel as _Panel
                from rich.syntax import Syntax as _Syntax
                import sys as _sys
                _con = _Console()
                _sp.stop()
                _con.print(_Panel(
                    _Syntax(query, "sql", theme="monokai", word_wrap=True),
                    title="[bold red]⚠  TRUNCATE — Approval Required[/bold red]",
                    border_style="red", padding=(1, 2),
                ))
                _sys.stdout.write("  Proceed? [yes/no]: ")
                _sys.stdout.flush()
                try:
                    answer = _sys.stdin.readline().strip().lower()
                except (EOFError, KeyboardInterrupt):
                    answer = "no"
                if answer not in ("yes", "y"):
                    return {"success": False, "query": query,
                            "message": "Query blocked: user declined TRUNCATE."}

            result_dicts = sess.execute(query)

            tasks = tool_context.state.get("app:TASKS_PERFORMED") or []
            tasks.append({"OPERATION_STATUS": "SUCCESS", "GENERATED_QUERY": query})
            tool_context.state["app:TASKS_PERFORMED"] = tasks

            queries = tool_context.state.get("user:QUERIES_EXECUTED") or []
            queries.append(query)
            tool_context.state["user:QUERIES_EXECUTED"] = queries

            query_counter.add(1, {"status": "success"})
            query_latency.record((time.monotonic() - t0) * 1000, {"status": "success"})
            return {"success": True, "query": query, "result": result_dicts,
                    "message": f"Query executed successfully. Rows returned: {len(result_dicts)}"}

        except Exception as e:
            query_errors.add(1, {"error_type": type(e).__name__})
            query_latency.record((time.monotonic() - t0) * 1000, {"status": "error"})
            tasks = tool_context.state.get("app:TASKS_PERFORMED") or []
            tasks.append({"OPERATION_STATUS": "FAILED", "GENERATED_QUERY": query, "ERROR_STATUS": str(e)})
            tool_context.state["app:TASKS_PERFORMED"] = tasks
            return {"success": False, "query": query, "error": str(e),
                    "message": f"Query execution failed: {str(e)}"}


def get_session_state(tool_context: ToolContext) -> dict:
    """Retrieve current session state — tasks performed, queries executed."""
    try:
        return {
            "success": True,
            "tasks_performed": tool_context.state.get("app:TASKS_PERFORMED") or [],
            "tasks_performed_count": len(tool_context.state.get("app:TASKS_PERFORMED") or []),
            "queries_executed": tool_context.state.get("user:QUERIES_EXECUTED") or [],
            "queries_executed_count": len(tool_context.state.get("user:QUERIES_EXECUTED") or []),
            "pg_host": tool_context.state.get("app:PG_HOST") or "",
            "pg_database": tool_context.state.get("app:PG_DATABASE") or "",
        }
    except Exception as e:
        return {"success": False, "tasks_performed": [], "tasks_performed_count": 0,
                "queries_executed": [], "queries_executed_count": 0, "error": str(e)}


def get_research_results(object_type: str, tool_context: ToolContext) -> dict:
    """Retrieve cached research results for a given PostgreSQL object type."""
    try:
        key = object_type.strip().upper()
        research_results = tool_context.state.get("app:RESEARCH_RESULTS") or {}
        results = research_results.get(key, "")
        return {"found": bool(results), "object_type": key, "results": results}
    except Exception as e:
        return {"found": False, "object_type": object_type, "results": "", "error": str(e)}
