from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.core.lottery import LotteryEngine
from app.models.participant import Participant
from app.services.storage import LotteryStore


class SessionNotFoundError(LookupError):
    pass


class NoRemainingParticipantsError(ValueError):
    pass


class NoRemainingSlotsError(ValueError):
    pass


class InvalidDrawCountError(ValueError):
    pass


class LotterySession:
    def __init__(
        self,
        participants: List[Participant],
        prize_name: str = "本场抽奖",
        winner_count: Optional[int] = None,
        session_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        self.id = session_id or str(uuid4())
        self.created_at = created_at or datetime.now(timezone.utc)
        self.participants = participants
        self.prize_name = prize_name
        self.winner_count = winner_count
        self.history: List[Dict[str, Any]] = history or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "created_at": self.created_at.isoformat(),
            "prize_name": self.prize_name,
            "winner_count": self.winner_count,
            "participants": [participant.to_dict() for participant in self.participants],
            "history": deepcopy(self.history),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "LotterySession":
        return cls(
            participants=[Participant.model_validate(item) for item in payload["participants"]],
            prize_name=payload.get("prize_name", "本场抽奖"),
            winner_count=payload.get("winner_count"),
            session_id=payload["session_id"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            history=payload.get("history", []),
        )


class LotteryService:
    """管理多个独立抽奖场次，业务状态不暴露给前端自行决定。"""

    def __init__(self, engine: Optional[LotteryEngine] = None, store: Optional[LotteryStore] = None):
        self.engine = engine or LotteryEngine()
        self.store = store or LotteryStore("data/lottery.sqlite3")
        self._lock = RLock()

    def create_session(
        self,
        names: List[str],
        prize_name: str = "本场抽奖",
        winner_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        participants = [Participant(name=name) for name in names]
        session = LotterySession(participants, prize_name=prize_name, winner_count=winner_count)
        with self._lock:
            self._save_session(session)
        return self.snapshot(session.id)

    def snapshot(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            remaining = self._remaining(session)
            return {
                "session_id": session.id,
                "created_at": session.created_at.isoformat(),
                "prize_name": session.prize_name,
                "winner_count": session.winner_count,
                "participants": [deepcopy(item).to_dict() for item in session.participants],
                "history": deepcopy(session.history),
                "total_count": len(session.participants),
                "remaining_count": len(remaining),
                "drawn_count": len(session.history),
                "remaining_slots": self._remaining_slots(session),
            }

    def draw(self, session_id: str, count: int = 1) -> Dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            if count < 1:
                raise InvalidDrawCountError("本次抽取人数必须大于 0")
            remaining = self._remaining(session)
            if not remaining:
                raise NoRemainingParticipantsError("没有可抽取的参与者")
            remaining_slots = self._remaining_slots(session)
            if remaining_slots is not None and remaining_slots <= 0:
                raise NoRemainingSlotsError("本场中奖名额已抽完")
            if remaining_slots is not None and count > remaining_slots:
                raise InvalidDrawCountError(f"本次最多可抽取 {remaining_slots} 人")
            if count > len(remaining):
                raise InvalidDrawCountError(f"本次最多可抽取 {len(remaining)} 人")

            winners: List[Dict[str, Any]] = []
            records: List[Dict[str, Any]] = []
            for _ in range(count):
                winner = self.engine.draw(self._remaining(session))
                round_number = len(session.history) + 1
                winner.mark_winner(round_number)
                winner_payload = deepcopy(winner).to_dict()
                record = {
                    "round": round_number,
                    "prize_name": session.prize_name,
                    "winner": winner_payload,
                    "drawn_at": winner.drawn_at.isoformat() if winner.drawn_at else None,
                }
                session.history.append(record)
                winners.append(winner_payload)
                records.append(deepcopy(record))
            self._save_session(session)
            snapshot = self._snapshot_payload(session)
            return {
                "winners": winners,
                "records": records,
                "winner": winners[0],
                "record": records[0],
                **snapshot,
            }

    def reset(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            cleared_count = len(session.history)
            for participant in session.participants:
                participant.is_winner = False
                participant.winner_round = None
                participant.drawn_at = None
            session.history.clear()
            self._save_session(session)
            return {
                "message": "抽奖已重置",
                "cleared_count": cleared_count,
                **self._snapshot_payload(session),
            }

    def _get_session(self, session_id: str) -> LotterySession:
        payload = self.store.get(session_id)
        if payload is None:
            raise SessionNotFoundError("抽奖场次不存在或已过期")
        return LotterySession.from_dict(payload)

    def _save_session(self, session: LotterySession) -> None:
        payload = session.to_dict()
        self.store.save(session.id, payload, updated_at=datetime.now(timezone.utc).isoformat())

    def _snapshot_payload(self, session: LotterySession) -> Dict[str, Any]:
        remaining = self._remaining(session)
        return {
            "session_id": session.id,
            "created_at": session.created_at.isoformat(),
            "prize_name": session.prize_name,
            "winner_count": session.winner_count,
            "participants": [deepcopy(item).to_dict() for item in session.participants],
            "history": deepcopy(session.history),
            "total_count": len(session.participants),
            "remaining_count": len(remaining),
            "drawn_count": len(session.history),
            "remaining_slots": self._remaining_slots(session),
        }

    @staticmethod
    def _remaining_slots(session: LotterySession) -> Optional[int]:
        if session.winner_count is None:
            return None
        return max(session.winner_count - len(session.history), 0)

    @staticmethod
    def _remaining(session: LotterySession) -> List[Participant]:
        return LotteryEngine.remaining(session.participants)
