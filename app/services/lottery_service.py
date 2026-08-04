from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.core.lottery import LotteryEngine
from app.models.participant import Participant


class SessionNotFoundError(LookupError):
    pass


class NoRemainingParticipantsError(ValueError):
    pass


class LotterySession:
    def __init__(self, participants: List[Participant]):
        self.id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.participants = participants
        self.history: List[Dict[str, Any]] = []


class LotteryService:
    """管理多个独立抽奖场次，业务状态不暴露给前端自行决定。"""

    def __init__(self, engine: Optional[LotteryEngine] = None):
        self.engine = engine or LotteryEngine()
        self.sessions: Dict[str, LotterySession] = {}
        self._lock = RLock()

    def create_session(self, names: List[str]) -> Dict[str, Any]:
        participants = [Participant(name=name) for name in names]
        session = LotterySession(participants)
        with self._lock:
            self.sessions[session.id] = session
        return self.snapshot(session.id)

    def snapshot(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            remaining = self._remaining(session)
            return {
                "session_id": session.id,
                "created_at": session.created_at.isoformat(),
                "participants": [deepcopy(item).to_dict() for item in session.participants],
                "history": deepcopy(session.history),
                "total_count": len(session.participants),
                "remaining_count": len(remaining),
                "drawn_count": len(session.history),
            }

    def draw(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            remaining = self._remaining(session)
            if not remaining:
                raise NoRemainingParticipantsError("没有可抽取的参与者")

            winner = self.engine.draw(remaining)
            round_number = len(session.history) + 1
            winner.mark_winner(round_number)
            record = {
                "round": round_number,
                "winner": deepcopy(winner).to_dict(),
                "drawn_at": winner.drawn_at.isoformat() if winner.drawn_at else None,
            }
            session.history.append(record)
            return {
                "winner": deepcopy(winner).to_dict(),
                "record": deepcopy(record),
                "remaining_count": len(self._remaining(session)),
                "total_count": len(session.participants),
                "drawn_count": len(session.history),
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
            return {
                "message": "抽奖已重置",
                "cleared_count": cleared_count,
                **self.snapshot(session_id),
            }

    def _get_session(self, session_id: str) -> LotterySession:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise SessionNotFoundError("抽奖场次不存在或已过期") from exc

    @staticmethod
    def _remaining(session: LotterySession) -> List[Participant]:
        return LotteryEngine.remaining(session.participants)
