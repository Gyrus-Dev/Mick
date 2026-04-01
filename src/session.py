import os
import logging
import psycopg2
import psycopg2.extras
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
_debug = os.environ.get("POSTGRESAI_DEBUG")
logger.setLevel(logging.DEBUG if _debug else logging.WARNING)

# Module-level connection cache
_connection_cache: Dict[tuple, Any] = {}


class Session:
    def __init__(self):
        self._host = None
        self._port = 5432
        self._user = None
        self._password = None
        self._database = None
        self._connection = None

    def set_host(self, value): self._host = value
    def set_port(self, value): self._port = int(value) if value else 5432
    def set_user(self, value): self._user = value
    def set_password(self, value): self._password = value
    def set_database(self, value): self._database = value

    def get_connection(self):
        if not self._host or not self._user:
            raise ValueError("PostgreSQL credentials missing — host and user are required.")
        if not self._password:
            raise ValueError("PostgreSQL password is required.")

        cache_key = (self._host, self._port, self._user, self._database)
        if cache_key in _connection_cache:
            conn = _connection_cache[cache_key]
            try:
                conn.isolation_level  # probe liveness
                if not conn.closed:
                    return conn
            except Exception:
                pass
            del _connection_cache[cache_key]

        conn = psycopg2.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database or "postgres",
        )
        conn.autocommit = True
        _connection_cache[cache_key] = conn
        self._connection = conn
        logger.debug("PostgreSQL connection established for user=%s host=%s", self._user, self._host)
        return conn

    def execute(self, query: str) -> list:
        conn = self.get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            return []
