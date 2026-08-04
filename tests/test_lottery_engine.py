from app.core.lottery import LotteryEngine, deterministic_random
from app.models.participant import Participant


def test_engine_draws_from_available_participants_only():
    participants = [Participant(name="张三"), Participant(name="李四")]
    participants[0].is_winner = True

    winner = LotteryEngine(deterministic_random(3)).draw(LotteryEngine.remaining(participants))

    assert winner.name == "李四"


def test_engine_rejects_empty_participants():
    try:
        LotteryEngine(deterministic_random()).draw([])
    except ValueError as exc:
        assert str(exc) == "参与者列表不能为空"
    else:
        raise AssertionError("empty participants should raise ValueError")
