from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.services.lottery_service import (
    LotteryService,
    InvalidDrawCountError,
    NoRemainingParticipantsError,
    NoRemainingSlotsError,
    SessionNotFoundError,
)
from app.services.storage import LotteryStore


router = APIRouter(prefix="/api/lottery", tags=["lottery"])
settings = get_settings()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
storage_path = Path(settings.storage_path)
if not storage_path.is_absolute():
    storage_path = PROJECT_ROOT / storage_path
lottery_service = LotteryService(store=LotteryStore(storage_path))


class CreateSessionRequest(BaseModel):
    participants: List[str] = Field(min_length=1, max_length=settings.max_participants)
    prize_name: str = Field(default="本场抽奖", min_length=1, max_length=100)
    winner_count: Optional[int] = Field(default=None, ge=1, le=settings.max_winners)

    @field_validator("participants")
    @classmethod
    def validate_participants(cls, value: List[str]) -> List[str]:
        names = [name.strip() for name in value if name and name.strip()]
        if not names:
            raise ValueError("至少需要一名参与者")
        if len(names) > settings.max_participants:
            raise ValueError(f"参与者不能超过 {settings.max_participants} 人")
        if any(len(name) > 100 for name in names):
            raise ValueError("单个参与者名称不能超过 100 个字符")
        return names

    @field_validator("prize_name")
    @classmethod
    def validate_prize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("奖项名称不能为空")
        return value


class DrawRequest(BaseModel):
    count: int = Field(default=1, ge=1, le=settings.max_draw_count)


def success(data: Dict[str, Any]) -> Dict[str, Any]:
    return {"success": True, "data": data, "error": None}


def error(code: str, message: str) -> Dict[str, Any]:
    return {"success": False, "data": None, "error": {"code": code, "message": message}}


def get_session_or_404(session_id: str):
    try:
        return lottery_service.snapshot(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error("SESSION_NOT_FOUND", str(exc))) from exc


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(payload: CreateSessionRequest) -> Dict[str, Any]:
    return success(
        lottery_service.create_session(
            payload.participants,
            prize_name=payload.prize_name,
            winner_count=payload.winner_count,
        )
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    return success(get_session_or_404(session_id))


@router.post("/sessions/{session_id}/draw")
async def draw(session_id: str, payload: DrawRequest | None = None) -> Dict[str, Any]:
    try:
        return success(lottery_service.draw(session_id, count=payload.count if payload else 1))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error("SESSION_NOT_FOUND", str(exc))) from exc
    except NoRemainingParticipantsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error("NO_REMAINING_PARTICIPANTS", str(exc))) from exc
    except NoRemainingSlotsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error("NO_REMAINING_SLOTS", str(exc))) from exc
    except InvalidDrawCountError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error("INVALID_DRAW_COUNT", str(exc))) from exc


@router.post("/sessions/{session_id}/reset")
async def reset(session_id: str) -> Dict[str, Any]:
    try:
        return success(lottery_service.reset(session_id))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error("SESSION_NOT_FOUND", str(exc))) from exc


@router.get("/sessions/{session_id}/history")
async def history(session_id: str) -> Dict[str, Any]:
    snapshot = get_session_or_404(session_id)
    return success({"history": snapshot["history"], "total": len(snapshot["history"])})
