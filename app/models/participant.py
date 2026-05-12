from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class Participant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    avatar_base64: str
    confidence: float = 1.0
    is_winner: bool = False
    winner_round: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "avatar_base64": self.avatar_base64,
            "confidence": self.confidence,
            "is_winner": self.is_winner,
            "winner_round": self.winner_round
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "张三",
                "avatar_base64": "data:image/png;base64,iVBORw0KG...",
                "confidence": 0.95,
                "is_winner": False,
                "winner_round": None
            }
        }