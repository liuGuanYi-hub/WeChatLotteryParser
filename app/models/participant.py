from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Participant(BaseModel):
    """抽奖参与者。重复昵称也保留为不同的抽奖名额。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=100)
    is_winner: bool = False
    winner_round: Optional[int] = None
    drawn_at: Optional[datetime] = None

    def mark_winner(self, round_number: int) -> None:
        self.is_winner = True
        self.winner_round = round_number
        self.drawn_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
