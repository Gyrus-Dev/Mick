"""
Tests for the execute_query safety gate in tools.py.
These tests verify DROP/TRUNCATE blocking logic without requiring
a live PostgreSQL connection or ADK session.
"""
import types
import pytest


def _make_tool_context(state: dict):
    """Minimal ToolContext stub with a state dict."""
    ctx = types.SimpleNamespace()
    ctx.state = state
    return ctx


def _call_safety_gate(query: str) -> dict:
    """
    Invoke only the safety-gate portion of execute_query by patching
    the session import so no real DB connection is attempted.
    """
    import importlib
    import sys
    import unittest.mock as mock

    # Stub out session and telemetry so imports don't fail
    fake_sess = mock.MagicMock()
    fake_sess.execute.return_value = [{"ok": True}]
    fake_session_module = types.ModuleType("src.session")
    fake_session_module.Session = mock.MagicMock(return_value=fake_sess)

    fake_tracer = mock.MagicMock()
    fake_span = mock.MagicMock()
    fake_tracer.start_as_current_span.return_value.__enter__ = mock.MagicMock(return_value=fake_span)
    fake_tracer.start_as_current_span.return_value.__exit__ = mock.MagicMock(return_value=False)
    fake_telemetry = types.ModuleType("src.postgres_ai.telemetry")
    fake_telemetry.tracer = fake_tracer
    fake_telemetry.query_counter = mock.MagicMock()
    fake_telemetry.query_errors = mock.MagicMock()
    fake_telemetry.query_latency = mock.MagicMock()

    with mock.patch.dict(sys.modules, {
        "src.session": fake_session_module,
        "src.postgres_ai.telemetry": fake_telemetry,
        "google.adk.tools": mock.MagicMock(),
    }):
        if "src.postgres_ai.objagents.tools" in sys.modules:
            del sys.modules["src.postgres_ai.objagents.tools"]

        from src.postgres_ai.objagents import tools

        state = {
            "user:PG_USER": "test_user",
            "app:PG_HOST": "localhost",
            "app:PG_PORT": 5432,
            "user:PG_PASSWORD": "test_pass",
            "app:PG_DATABASE": "testdb",
        }
        ctx = _make_tool_context(state)
        return tools.execute_query(query, ctx)


class TestDropBlocked:
    def test_drop_table_blocked(self):
        result = _call_safety_gate("DROP TABLE users")
        assert result["success"] is False
        assert "DROP" in result["message"]

    def test_drop_schema_blocked(self):
        result = _call_safety_gate("DROP SCHEMA public CASCADE")
        assert result["success"] is False

    def test_drop_lowercase_blocked(self):
        result = _call_safety_gate("drop table orders")
        assert result["success"] is False

    def test_drop_mixed_case_blocked(self):
        result = _call_safety_gate("Drop Table accounts")
        assert result["success"] is False


class TestSafeQueriesAllowed:
    def test_select_allowed(self):
        result = _call_safety_gate("SELECT 1")
        assert result["success"] is True

    def test_create_table_allowed(self):
        result = _call_safety_gate(
            "CREATE TABLE IF NOT EXISTS test (id serial PRIMARY KEY)"
        )
        assert result["success"] is True

    def test_alter_table_allowed(self):
        result = _call_safety_gate("ALTER TABLE test ADD COLUMN name TEXT")
        assert result["success"] is True
