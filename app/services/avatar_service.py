import cv2
import numpy as np
import base64
from typing import List, Dict, Any, Tuple
from app.core.config import get_settings


class AvatarService:
    def __init__(self, size: int = 100):
        self.size = size
        self.settings = get_settings()
    
    def detect_avatars(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=self.settings.AVATAR_MIN_RADIUS,
            maxRadius=self.settings.AVATAR_MAX_RADIUS
        )
        
        avatars = []
        if circles is not None:
            for circle in circles[0]:
                x, y, r = circle
                x, y, r = int(x), int(y), int(r)
                
                if r > 0 and y - r >= 0 and y + r <= img.shape[0] and x - r >= 0 and x + r <= img.shape[1]:
                    avatar = img[y-r:y+r, x-r:x+r]
                    
                    if avatar.size > 0:
                        cropped = self.crop_circular(avatar, r)
                        resized = self.resize_avatar(cropped)
                        base64_str = self.encode_base64(resized)
                        
                        avatars.append({
                            "x": x,
                            "y": y,
                            "r": r,
                            "base64": base64_str
                        })
        
        return avatars
    
    def crop_circular(self, avatar: np.ndarray, radius: int) -> np.ndarray:
        height, width = avatar.shape[:2]
        
        mask = np.zeros((height, width), dtype=np.uint8)
        center = (width // 2, height // 2)
        
        cv2.circle(mask, center, min(center[0], center[1]), 255, -1)
        
        if len(avatar.shape) == 3:
            result = cv2.bitwise_and(avatar, avatar, mask=mask)
        else:
            result = cv2.bitwise_and(avatar, avatar, mask=mask)
        
        return result
    
    def resize_avatar(self, avatar: np.ndarray) -> np.ndarray:
        return cv2.resize(avatar, (self.size, self.size), interpolation=cv2.INTER_AREA)
    
    def encode_base64(self, avatar: np.ndarray) -> str:
        _, buffer = cv2.imencode('.png', avatar)
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"