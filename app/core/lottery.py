import secrets
from random import Random
from typing import List, Protocol, Sequence, TypeVar

from app.models.participant import Participant


ParticipantType = TypeVar("ParticipantType")


class RandomSource(Protocol):
    def randrange(self, stop: int) -> int: ...


class LotteryEngine:
    """无状态抽奖引擎，生产使用密码学安全随机源，测试可注入确定性随机源。"""

    def __init__(self, random_source: RandomSource | None = None):
        self._random_source = random_source or secrets.SystemRandom()

    def draw(self, participants: Sequence[Participant]) -> Participant:
        if not participants:
            raise ValueError("参与者列表不能为空")
        return participants[self._random_source.randrange(len(participants))]

    @staticmethod
    def remaining(participants: Sequence[Participant]) -> List[Participant]:
        return [participant for participant in participants if not participant.is_winner]


def deterministic_random(seed: int = 0) -> Random:
    """测试辅助函数，生产代码不应使用固定种子。"""

    return Random(seed)
