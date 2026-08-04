import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional


class LotteryStore:
    """使用 SQLite 保存抽奖场次，让服务重启后仍能恢复现场。"""

    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lottery_sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def save(self, session_id: str, payload: Dict[str, Any], updated_at: str) -> None:
        serialized = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO lottery_sessions(session_id, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (session_id, serialized, updated_at),
            )
            self._connection.commit()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload FROM lottery_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["payload"])
