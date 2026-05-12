# 微信抽奖解析器 - 技术架构文档

## 1. 系统架构概述

### 1.1 架构风格

采用 **前后端分离** 架构，后端提供 RESTful API，前端独立部署。

```
┌─────────────────────────────────────────────────────────┐
│                     Client (Browser)                    │
│                   HTML + CSS + JavaScript               │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/HTTPS
┌─────────────────────────────────────────────────────────┐
│                      Backend Server                      │
│                        FastAPI                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  API   │  │  OCR    │  │  Lottery │  │  Utils  │   │
│  │ Routes │  │ Service │  │  Engine  │  │ Library │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Local Storage   │
                    │  (Session Only)  │
                    └─────────────────┘
```

### 1.2 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.100+ | 异步高性能 Web 框架 |
| OCR 引擎 | PaddleOCR | 2.7+ | 中文识别能力强 |
| 图像处理 | OpenCV | 4.9+ | 头像检测与裁剪 |
| 图像处理 | Pillow | 10+ | 图片格式转换 |
| 前端框架 | 原生 HTML/JS | - | 无需构建工具 |
| Web 服务器 | Uvicorn | 0.25+ | ASGI 服务器 |
| Python 版本 | Python | 3.8+ | 需要类型注解支持 |

---

## 2. 项目结构

```
WeChatLotteryParser/
├── docs/                          # 项目文档
│   ├── SPEC.md                   # 功能规格说明书
│   ├── API.md                    # API 接口设计
│   ├── ARCHITECTURE.md           # 技术架构文档
│   ├── DESIGN.md                # 前端界面设计
│   └── README.md                # 项目说明
│
├── app/                          # 应用代码
│   ├── __init__.py
│   ├── main.py                  # FastAPI 主入口
│   ├── api/                     # API 路由
│   │   ├── __init__.py
│   │   ├── routes.py            # API 路由定义
│   │   └── dependencies.py      # 依赖注入
│   │
│   ├── core/                    # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理
│   │   ├── lottery.py           # 抽奖引擎
│   │   └── exceptions.py        # 自定义异常
│   │
│   ├── services/                # 服务层
│   │   ├── __init__.py
│   │   ├── ocr_service.py       # OCR 识别服务
│   │   ├── avatar_service.py    # 头像处理服务
│   │   └── lottery_service.py   # 抽奖服务
│   │
│   └── models/                 # 数据模型
│       ├── __init__.py
│       ├── participant.py       # 参与者模型
│       └── lottery_record.py    # 抽奖记录模型
│
├── static/                      # 静态资源
│   ├── css/
│   │   └── style.css           # 样式文件
│   │
│   ├── js/
│   │   └── app.js              # 前端逻辑
│   │
│   └── images/
│       └── logo.png            # Logo 图片
│
├── templates/                   # HTML 模板
│   └── index.html              # 主页面
│
├── tests/                       # 测试代码
│   ├── __init__.py
│   ├── test_ocr.py             # OCR 测试
│   ├── test_lottery.py         # 抽奖测试
│   └── test_api.py             # API 测试
│
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量示例
├── .gitignore                 # Git 忽略文件
└── README.md                   # 项目说明
```

---

## 3. 核心模块设计

### 3.1 OCR 识别服务 (ocr_service.py)

#### 职责
- 调用 PaddleOCR 进行文字识别
- 协调头像检测和昵称识别
- 返回标准化的参与者数据

#### 类图

```
OcrService
├── __init__()
│   └── 初始化 PaddleOCR 模型
│
├── detect_avatars(image: bytes) -> List[AvatarData]
│   ├── 使用霍夫圆变换检测圆形
│   ├── 裁剪并返回头像数据
│   └── 处理异常情况
│
├── recognize_nicknames(image: bytes) -> List[NicknameData]
│   ├── 调用 PaddleOCR
│   ├── 过滤低置信度结果
│   └── 返回昵称列表
│
└── extract_participants(image: bytes) -> List[Participant]
    ├── 调用 detect_avatars
    ├── 调用 recognize_nicknames
    ├── 执行配对算法
    └── 返回参与者列表
```

#### 关键代码

```python
class OcrService:
    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            show_log=False
        )
    
    def detect_avatars(self, image_bytes):
        # 转换为 numpy 数组
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 霍夫圆变换
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=30,
            maxRadius=80
        )
        
        # 裁剪头像
        avatars = []
        if circles is not None:
            for circle in circles[0]:
                x, y, r = circle
                avatar = img[y-r:y+r, x-r:x+r]
                # 转为 Base64
                _, buffer = cv2.imencode('.png', avatar)
                base64_str = base64.b64encode(buffer).decode('utf-8')
                avatars.append({
                    "x": x, "y": y,
                    "base64": base64_str
                })
        
        return avatars
    
    def recognize_nicknames(self, image_bytes):
        result = self.ocr.ocr(image_bytes, cls=True)
        nicknames = []
        
        for line in result[0]:
            text, confidence = line[1]
            if confidence > 0.8 and 2 <= len(text) <= 20:
                nicknames.append({
                    "text": text,
                    "confidence": confidence,
                    "x": line[0][0][0],
                    "y": line[0][0][1]
                })
        
        return nicknames
```

---

### 3.2 头像处理服务 (avatar_service.py)

#### 职责
- 裁剪圆形头像
- 统一头像尺寸
- Base64 编码

#### 类图

```
AvatarService
├── __init__(size: int = 100)
│   └── 设置输出头像尺寸
│
├── crop_circular(avatar: np.ndarray) -> np.ndarray
│   ├── 创建圆形掩码
│   ├── 应用掩码
│   └── 返回圆形头像
│
├── resize_avatar(avatar: np.ndarray) -> np.ndarray
│   └── 统一调整为指定尺寸
│
└── encode_base64(avatar: np.ndarray) -> str
    ├── PNG 编码
    ├── Base64 编码
    └── 返回 Data URI
```

#### 关键代码

```python
class AvatarService:
    def __init__(self, size: int = 100):
        self.size = size
    
    def process_avatar(self, avatar: np.ndarray) -> str:
        # 裁剪圆形
        circular = self.crop_circular(avatar)
        
        # 调整尺寸
        resized = self.resize_avatar(circular)
        
        # Base64 编码
        return self.encode_base64(resized)
    
    def crop_circular(self, avatar: np.ndarray) -> np.ndarray:
        height, width = avatar.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        center = (width // 2, height // 2)
        radius = min(center[0], center[1])
        
        cv2.circle(mask, center, radius, 1, -1)
        
        result = cv2.bitwise_and(avatar, avatar, mask=mask)
        return result
    
    def encode_base64(self, avatar: np.ndarray) -> str:
        _, buffer = cv2.imencode('.png', avatar)
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"
```

---

### 3.3 抽奖引擎 (lottery.py)

#### 职责
- 随机选择中奖者
- 管理参与者池
- 记录抽奖历史

#### 类图

```
LotteryEngine
├── __init__()
│   └── 初始化随机数生成器
│
├── draw(participants: List[Participant]) -> Participant
│   ├── 验证参与者数量
│   ├── 使用时间种子随机选择
│   ├── 标记为中奖者
│   └── 返回中奖者
│
├── get_remaining(participants: List[Participant]) -> List[Participant]
│   └── 返回未中奖的参与者
│
└── reset()
    └── 重置抽奖状态
```

#### 关键代码

```python
import random
import time

class LotteryEngine:
    def __init__(self):
        self.history = []
    
    def draw(self, participants: List[Participant]) -> Optional[Participant]:
        if not participants or len(participants) < 2:
            return None
        
        # 使用微秒级时间戳作为随机种子
        seed = int(time.time() * 1000000) % (2**32)
        random.seed(seed)
        
        # 随机选择
        winner = random.choice(participants)
        winner.is_winner = True
        winner.winner_round = len(self.history) + 1
        
        # 记录历史
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
```

---

## 4. 数据流设计

### 4.1 图片上传与解析流程

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  用户上传截图                                                 │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ 文件验证 │ ─── 格式/大小检查                              │
│  └─────────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ 霍夫圆变换 │ ─── 检测圆形头像区域                         │
│  └─────────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ PaddleOCR│ ─── 识别昵称文本                               │
│  └─────────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ 配对算法 │ ─── 按位置配对头像和昵称                        │
│  └─────────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ Base64编码│ ─── 处理头像，准备传输                        │
│  └─────────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  返回参与者列表                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 抽奖流程

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  前端点击"开始抽奖"                                           │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │ 验证参与人数│ ─── 至少需要 2 人                           │
│  └─────────────┘                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │ 发送抽奖请求 │ ─── POST /api/lottery/draw                │
│  └─────────────┘                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │ 随机选择 │ ─── 时间种子 + random.choice                  │
│  └─────────────┘                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │ 记录中奖者 │ ─── 标记 + 历史记录                           │
│  └─────────────┘                                            │
│       │                                                      │
│       ▼                                                      │
│  返回中奖者信息                                               │
│       │                                                      │
│       ▼                                                      │
│  前端播放动画效果                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 配置文件

### 5.1 config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    
    # FastAPI 配置
    APP_NAME: str = "微信抽奖解析器"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OCR 配置
    OCR_CONFIDENCE_THRESHOLD: float = 0.8
    AVATAR_MIN_RADIUS: int = 30
    AVATAR_MAX_RADIUS: int = 80
    
    # 头像配置
    AVATAR_SIZE: int = 100
    
    # 文件限制
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".png", ".jpg", ".jpeg"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 5.2 .env.example

```env
# 应用配置
APP_NAME=微信抽奖解析器
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8000

# OCR 配置
OCR_CONFIDENCE_THRESHOLD=0.8
AVATAR_MIN_RADIUS=30
AVATAR_MAX_RADIUS=80

# 头像配置
AVATAR_SIZE=100

# 文件限制
MAX_FILE_SIZE=10485760
```

---

## 6. 依赖管理

### 6.1 requirements.txt

```
# Web 框架
fastapi>=0.100.0
uvicorn[standard]>=0.25.0
python-multipart>=0.0.6

# OCR 和图像处理
paddlepaddle>=2.6.0
paddleocr>=2.7.0
opencv-python>=4.9.0
Pillow>=10.0.0

# 数据验证
pydantic>=2.0.0
pydantic-settings>=2.0.0

# 工具库
python-dotenv>=1.0.0

# 开发依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

---

## 7. 部署方案

### 7.1 开发环境

```bash
# 1. 克隆代码
git clone <repo-url>
cd WeChatLotteryParser

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载 PaddleOCR 模型
# 首次运行会自动下载（约 100MB）

# 5. 启动服务
uvicorn app.main:app --reload
```

### 7.2 生产环境

```bash
# 1. 构建 Docker 镜像
docker build -t wechat-lottery .

# 2. 运行容器
docker run -d -p 8000:8000 wechat-lottery
```

### 7.3 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 8. 性能优化

### 8.1 OCR 优化

- 模型预加载（启动时初始化）
- 结果缓存（相同图片不重复识别）
- 并行处理（多线程/多进程）

### 8.2 前端优化

- 图片懒加载
- CSS/JS 压缩
- 使用 CDN 加速静态资源

### 8.3 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_result(image_hash: str):
    """缓存图片识别结果"""
    pass
```

---

## 9. 安全性

### 9.1 输入验证

```python
from pydantic import BaseModel, validator

class Participant(BaseModel):
    name: str
    avatar_base64: str
    
    @validator('name')
    def validate_name(cls, v):
        if not 2 <= len(v) <= 20:
            raise ValueError('昵称长度必须在 2-20 之间')
        return v
    
    @validator('avatar_base64')
    def validate_avatar(cls, v):
        if len(v) > 2 * 1024 * 1024:  # 2MB
            raise ValueError('头像 Base64 太大')
        return v
```

### 9.2 文件上传安全

```python
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_file(file: UploadFile):
    # 检查扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidImageFormat()
    
    # 检查大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise ImageTooLarge()
```

---

## 10. 监控与日志

### 10.1 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 10.2 关键日志点

- 图片上传成功/失败
- OCR 识别开始/结束
- 抽奖执行
- 异常发生

---

## 11. 扩展性

### 11.1 模块化设计

每个模块独立，可以：
- 替换 OCR 引擎（如 EasyOCR）
- 更换前端框架（React/Vue）
- 添加数据库支持

### 11.2 插件系统（未来）

```python
class OcrPlugin(Protocol):
    def detect_avatars(self, image: bytes) -> List[AvatarData]: ...
    def recognize_nicknames(self, image: bytes) -> List[NicknameData]: ...

class LotteryPlugin(Protocol):
    def draw(self, participants: List[Participant]) -> Participant: ...
```

---

## 12. 故障排除

### 12.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| OCR 识别慢 | 首次加载模型 | 预加载模型 |
| 头像检测不准 | 参数不合适 | 调整霍夫圆参数 |
| 前端加载慢 | 图片太大 | 压缩 Base64 |
| 抽奖不随机 | 随机种子重复 | 使用时间戳 |

### 12.2 调试模式

```python
# 开启调试
DEBUG=true uvicorn app.main:app --reload
```

---

## 13. 测试策略

### 13.1 单元测试

```python
def test_lottery_engine():
    engine = LotteryEngine()
    participants = [Participant("张三"), Participant("李四")]
    
    winner = engine.draw(participants)
    assert winner is not None
    assert winner.name in ["张三", "李四"]

def test_avatar_service():
    service = AvatarService()
    avatar = np.zeros((100, 100, 3), dtype=np.uint8)
    
    result = service.process_avatar(avatar)
    assert result.startswith("data:image/png;base64,")
```

### 13.2 集成测试

```python
def test_upload_and_extract():
    client = TestClient(app)
    
    with open("test_screenshot.png", "rb") as f:
        response = client.post("/api/upload", files={"file": f})
    
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    assert len(data["participants"]) > 0
```

---

**文档版本**: 1.0  
**最后更新**: 2026-05-12  
**维护者**: 开发团队