from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from app.services.ocr_service import OcrService
from app.services.lottery_service import LotteryService
from app.core.exceptions import (
    InvalidImageFormat,
    ImageTooLarge,
    NoAvatarDetected,
    EmptyParticipants,
    InsufficientParticipants
)
from app.core.config import get_settings

router = APIRouter(prefix="/api/lottery", tags=["lottery"])

lottery_service = LotteryService()
ocr_service = OcrService()
settings = get_settings()


@router.post("/participants")
async def upload_and_extract(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        if not file.filename:
            raise InvalidImageFormat()
        
        ext = "." + file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise InvalidImageFormat()
        
        contents = await file.read()
        
        if len(contents) > settings.MAX_FILE_SIZE:
            raise ImageTooLarge()
        
        participants_data = ocr_service.extract_participants(contents)
        
        if not participants_data:
            raise NoAvatarDetected()
        
        participants = lottery_service.set_participants(participants_data)
        
        return {
            "success": True,
            "data": {
                "participants": [p.to_dict() for p in participants],
                "total": len(participants)
            },
            "error": None
        }
    
    except InvalidImageFormat as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": e.code, "message": e.message}
        }
    except ImageTooLarge as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": e.code, "message": e.message}
        }
    except NoAvatarDetected as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": e.code, "message": e.message}
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "SYSTEM_ERROR", "message": str(e)}
        }


@router.post("/draw")
async def draw() -> Dict[str, Any]:
    try:
        remaining = lottery_service.get_participants()
        
        if not remaining:
            raise EmptyParticipants()
        
        remaining_not_winner = [p for p in remaining if not p.is_winner]
        
        if len(remaining_not_winner) < 2:
            raise InsufficientParticipants()
        
        result = lottery_service.draw()
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
    
    except EmptyParticipants as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": e.code, "message": e.message}
        }
    except InsufficientParticipants as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": e.code, "message": e.message}
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "SYSTEM_ERROR", "message": str(e)}
        }


@router.get("/winners")
async def get_winners(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    result = lottery_service.get_winners(limit, offset)
    
    return {
        "success": True,
        "data": result,
        "error": None
    }


@router.delete("/winners/{winner_id}")
async def remove_winner(winner_id: str) -> Dict[str, Any]:
    result = lottery_service.remove_winner(winner_id)
    
    if not result:
        return {
            "success": False,
            "data": None,
            "error": {"code": "WINNER_NOT_FOUND", "message": "未找到指定的中奖者"}
        }
    
    return {
        "success": True,
        "data": result,
        "error": None
    }


@router.post("/reset")
async def reset() -> Dict[str, Any]:
    result = lottery_service.reset()
    
    return {
        "success": True,
        "data": result,
        "error": None
    }