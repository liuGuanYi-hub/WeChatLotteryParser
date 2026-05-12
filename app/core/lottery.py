import random
import time
from typing import List, Optional, Dict, Any
from app.models.participant import Participant


class LotteryEngine:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def draw(self, participants: List[Participant]) -> Optional[Participant]:
        if not participants or len(participants) < 2:
            return None
        
        seed = int(time.time() * 1000000) % (2**32)
        random.seed(seed)
        
        winner = random.choice(participants)
        winner.is_winner = True
        winner.winner_round = len(self.history) + 1
        
        self.history.append({
            "round": len(self.history) + 1,
            "winner": winner.to_dict(),
            "timestamp": time.time()
        })
        
        return winner
    
    def get_remaining(self, participants: List[Participant]) -> List[Participant]:
        return [p for p in participants if not p.is_winner]
    
    def reset(self):
        self.history.clear()
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history