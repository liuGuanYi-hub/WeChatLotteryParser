from app.core.lottery import LotteryEngine, deterministic_random
from app.services.lottery_service import LotteryService, NoRemainingParticipantsError


def test_session_supports_multiple_rounds_without_duplicate_winners():
    service = LotteryService(LotteryEngine(deterministic_random(5)))
    session = service.create_session(["张三", "李四", "王五"])

    first = service.draw(session["session_id"])
    second = service.draw(session["session_id"])
    snapshot = service.snapshot(session["session_id"])

    assert first["winner"]["id"] != second["winner"]["id"]
    assert snapshot["drawn_count"] == 2
    assert snapshot["remaining_count"] == 1


def test_session_can_be_reset():
    service = LotteryService(LotteryEngine(deterministic_random(1)))
    session = service.create_session(["张三", "李四"])
    service.draw(session["session_id"])

    reset = service.reset(session["session_id"])

    assert reset["cleared_count"] == 1
    assert reset["drawn_count"] == 0
    assert reset["remaining_count"] == 2


def test_drawing_after_all_participants_are_used_returns_domain_error():
    service = LotteryService(LotteryEngine(deterministic_random(1)))
    session = service.create_session(["张三"])
    service.draw(session["session_id"])

    try:
        service.draw(session["session_id"])
    except NoRemainingParticipantsError as exc:
        assert str(exc) == "没有可抽取的参与者"
    else:
        raise AssertionError("drawing an empty session should fail")
