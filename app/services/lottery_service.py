from typing import List, Optional, Dict, Any
from app.models.participant import Participant
from app.core.lottery import LotteryEngine


class LotteryService:
    def __init__(self):
        self.engine = LotteryEngine()
        self.current_participants: List[Participant] = []
    
    def set_participants(self, participants_data: List[Dict[str, Any]]) -> List[Participant]:
        self.current_participants = [
            Participant(**data) for data in participants_data
        ]
        self.engine.reset()
        return self.current_participants
    
    def draw(self) -> Optional[Dict[str, Any]]:
        remaining = self.engine.get_remaining(self.current_participants)
        
        if len(remaining) < 2:
            return None
        
        winner = self.engine.draw(remaining)
        
        if winner:
            return {
                "winner": winner.to_dict(),
                "remaining_count": len(self.engine.get_remaining(self.current_participants)),
                "total_participants": len(self.current_participants),
                "draw_number": len(self.engine.history)
            }
        
        return None
    
    def get_winners(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        winners = [p for p in self.current_participants if p.is_winner]
        winners.sort(key=lambda x: x.winner_round or 0)
        
        paginated = winners[offset:offset + limit]
        
        return {
            "winners": [w.to_dict() for w in paginated],
            "total": len(winners),
            "limit": limit,
            "offset": offset
        }
    
    def remove_winner(self, winner_id: str) -> Optional[Dict[str, Any]]:
        winner = next((p for p in self.current_participants if p.id == winner_id), None)
        
        if not winner or not winner.is_winner:
            return None
        
        remaining_count = len(self.engine.get_remaining(self.current_participants))
        
        return {
            "removed_winner": {"id": winner.id, "name": winner.name},
            "remaining_winners": len([p for p in self.current_participants if p.is_winner])
        }
    
    def reset(self) -> Dict[str, Any]:
        cleared_count = len([p for p in self.current_participants if p.is_winner])
        
        for p in self.current_participants:
            p.is_winner = False
            p.winner_round = None
        
        self.engine.reset()
        
        return {
            "message": "抽奖已重置",
            "cleared_winners_count": cleared_count
        }
    
    def get_participants(self) -> List[Participant]:
        return self.current_participants