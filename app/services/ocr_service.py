from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.services.avatar_service import AvatarService


class OcrService:
    def __init__(self):
        self.settings = get_settings()
        self.avatar_service = AvatarService()
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
    
    def extract_participants(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        avatars = self.avatar_service.detect_avatars(image_bytes)
        
        if not avatars:
            return []
        
        nicknames = self.recognize_nicknames(image_bytes)
        
        paired = self.pair_avatar_with_nickname(avatars, nicknames)
        
        return paired
    
    def recognize_nicknames(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
        
        result = self.ocr.ocr(image_bytes, cls=True)
        
        nicknames = []
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                if len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    if confidence > self.settings.OCR_CONFIDENCE_THRESHOLD:
                        if 2 <= len(text) <= 20:
                            if self._is_valid_nickname(text):
                                bbox = line[0]
                                if bbox and len(bbox) > 0:
                                    nicknames.append({
                                        "text": text,
                                        "confidence": confidence,
                                        "x": bbox[0][0],
                                        "y": bbox[0][1]
                                    })
        
        return nicknames
    
    def _is_valid_nickname(self, text: str) -> bool:
        if not text or len(text.strip()) < 2:
            return False
        
        text = text.strip()
        
        if text[0].isdigit():
            return False
        
        if text.startswith('+') or text.startswith('-'):
            return False
        
        keywords = ['红包', '已领取', '元', '领取', '未领取']
        for keyword in keywords:
            if keyword in text:
                return False
        
        return True
    
    def pair_avatar_with_nickname(self, avatars: List[Dict[str, Any]], 
                                  nicknames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        paired = []
        used_nicknames = set()
        
        for avatar in avatars:
            best_match = None
            min_distance = float('inf')
            
            for nickname in nicknames:
                if id(nickname) in used_nicknames:
                    continue
                
                distance = abs(avatar["y"] - nickname["y"])
                
                if distance < 30 and distance < min_distance:
                    min_distance = distance
                    best_match = nickname
            
            if best_match:
                used_nicknames.add(id(best_match))
                paired.append({
                    "name": best_match["text"],
                    "avatar_base64": avatar["base64"],
                    "confidence": best_match["confidence"]
                })
        
        return paired