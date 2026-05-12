# 微信抽奖解析器 - 功能规格说明书

## 1. 项目概述

### 1.1 项目名称
微信红包/抽奖参与者解析与抽奖系统

### 1.2 核心功能
从微信截图或红包领取页面截图中，自动提取参与者的头像和昵称，并提供一个交互式的抽奖界面。

### 1.3 目标用户
- 微信群活动组织者
- 需要进行抽奖活动的个人或团队
- 想要自动化抽奖流程的用户

### 1.4 使用场景
1. 微信群红包领取名单抽奖
2. 活动参与者随机抽取
3. 线上/线下活动抽奖

---

## 2. 功能列表

### 2.1 核心功能 (Core Features)

#### F1: 图片上传与解析
- 支持拖拽上传截图
- 支持点击选择文件上传
- 支持 PNG、JPG、JPEG 格式
- 文件大小限制：最大 10MB
- 显示上传进度

#### F2: OCR 头像与昵称提取
- 自动识别圆形头像区域
- 提取用户昵称文本
- 头像与昵称自动配对
- 支持中文昵称识别
- 过滤无效/低置信度数据

#### F3: 头像处理
- 圆形裁剪头像
- Base64 编码存储
- 保持原色（不添加滤镜）
- 统一尺寸处理（100x100px）

#### F4: 抽奖界面展示
- 30个真实头像网格展示
- 头像保持原始颜色
- 昵称标签显示
- 已中奖者标记（灰色+删除线）

#### F5: 抽奖动画效果
- 点击"开始抽奖"触发
- 快速闪烁阶段：所有头像随机闪烁（1秒）
- 减速阶段：闪烁频率降低（1-2秒）
- 最终选择：目标头像突出显示（1秒）
- 总动画时长：3-4秒

#### F6: 多轮抽奖
- 支持连续多轮抽取
- 中奖者自动从池中移除
- 已中奖者列表展示
- 可查看历史中奖记录

#### F7: 结果导出
- 导出中奖名单为文本
- 支持复制到剪贴板
- 显示抽取轮次

### 2.2 辅助功能 (Helper Features)

#### F8: 错误提示
- 图片格式不正确提示
- 未检测到参与者提示
- OCR 识别失败提示
- 网络错误提示

#### F9: 界面操作
- 重新上传新截图
- 清空当前抽奖池
- 重新开始（重置所有状态）

---

## 3. 用户故事 (User Stories)

### 3.1 主要用户故事

**US-1: 截图上传**
```
作为：活动组织者
我想要：上传微信截图
以便：提取参与者信息进行抽奖
```

**US-2: 自动解析**
```
作为：活动组织者
我想要：系统自动识别头像和昵称
以便：无需手动输入参与者信息
```

**US-3: 抽奖互动**
```
作为：活动组织者
我想要：通过点击按钮进行抽奖
以便：参与者可以看到抽奖过程
```

**US-4: 多轮抽取**
```
作为：活动组织者
我想要：连续抽取多个中奖者
以便：进行多奖项抽奖活动
```

**US-5: 结果导出**
```
作为：活动组织者
我想要：导出中奖名单
以便：记录和公示抽奖结果
```

---

## 4. 抽奖算法设计

### 4.1 随机抽取算法

#### 核心算法：加权随机 + 时间种子

```python
import random
import time

def lottery_draw(participants: list) -> dict:
    """
    抽奖算法：
    1. 使用时间戳作为随机种子，确保每次抽奖的随机性
    2. 从参与者列表中随机选择
    3. 返回中奖者信息
    """
    if not participants:
        return None
    
    # 重新设置随机种子
    random.seed(int(time.time() * 1000000) % (2**32))
    
    # 随机选择
    winner = random.choice(participants)
    
    return winner
```

#### 算法特点：
- **真随机**：使用微秒级时间戳作为种子
- **均匀分布**：每个参与者中奖概率相等
- **不可预测**：每次抽奖结果独立，无法预测
- **可复现**：相同输入 + 相同种子 = 相同结果（调试用）

### 4.2 动画阶段设计

```
┌────────────────────────────────────────────┐
│                                            │
│  阶段1: 快速闪烁 (0-1000ms)                │
│  - 所有头像快速闪烁（100ms间隔）            │
│  - 透明度随机变化（0.3-1.0）                │
│  - 背景色轻微变化                           │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  阶段2: 减速过渡 (1000-2000ms)             │
│  - 闪烁间隔逐渐增大（100→200→400ms）       │
│  - 2-3个头像候选突出                        │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  阶段3: 最终选择 (2000-3000ms)             │
│  - 锁定目标头像                             │
│  - 爆炸放大效果                             │
│  - 显示中奖者信息                           │
│                                            │
└────────────────────────────────────────────┘
```

---

## 5. OCR 识别流程

### 5.1 头像检测流程

```python
def detect_avatars(image_path):
    """
    头像检测步骤：
    1. 读取图片并转换为灰度图
    2. 使用霍夫圆变换检测圆形区域
    3. 过滤不符合尺寸的圆
    4. 裁剪并返回头像区域
    """
    # Step 1: 读取图片
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Step 2: 霍夫圆变换
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,           # 分辨率比例
        minDist=50,       # 圆心最小距离
        param1=50,        # Canny 边缘检测阈值
        param2=30,        # 圆心检测阈值
        minRadius=30,     # 最小半径
        maxRadius=80      # 最大半径
    )
    
    # Step 3: 裁剪头像
    avatars = []
    if circles is not None:
        for circle in circles[0]:
            x, y, r = circle
            avatar = img[y-r:y+r, x-r:x+r]
            avatars.append({"avatar": avatar, "x": x, "y": y})
    
    return avatars
```

### 5.2 昵称识别流程

```python
def recognize_nicknames(image_path):
    """
    昵称识别步骤：
    1. 使用 PaddleOCR 识别图片文字
    2. 过滤低置信度结果
    3. 按位置排序
    4. 返回昵称列表
    """
    # Step 1: OCR 识别
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    result = ocr.ocr(image_path, cls=True)
    
    # Step 2: 提取文本
    nicknames = []
    for line in result[0]:
        text, confidence = line[1][0], line[1][1]
        
        # 过滤条件：
        # - 置信度 > 0.8
        # - 文本长度 2-20 字符
        # - 不包含特殊符号（可能是金额）
        if confidence > 0.8 and 2 <= len(text) <= 20:
            nicknames.append({
                "name": text,
                "confidence": confidence,
                "x": line[0][0][0],
                "y": line[0][0][1]
            })
    
    return nicknames
```

### 5.3 头像与昵称配对

```python
def pair_avatar_with_nickname(avatars, nicknames):
    """
    配对算法：
    - 按 Y 坐标（垂直位置）分组
    - 同一行（Y 坐标差 < 20px）的头像和昵称配对
    - 优先使用最近邻匹配
    """
    paired = []
    
    for avatar in avatars:
        best_match = None
        min_distance = float('inf')
        
        for nickname in nicknames:
            # 计算距离
            distance = abs(avatar["y"] - nickname["y"])
            
            if distance < 20 and distance < min_distance:
                min_distance = distance
                best_match = nickname
        
        if best_match:
            paired.append({
                "name": best_match["name"],
                "avatar": avatar["avatar"],
                "confidence": best_match["confidence"]
            })
            nicknames.remove(best_match)
    
    return paired
```

---

## 6. 数据模型

### 6.1 参与者数据模型

```python
class Participant:
    """参与者数据模型"""
    def __init__(self, name: str, avatar_base64: str, confidence: float = 1.0):
        self.id = generate_unique_id()      # 唯一标识符
        self.name = name                     # 昵称
        self.avatar_base64 = avatar_base64  # Base64 编码的头像
        self.confidence = confidence         # OCR 识别置信度
        self.is_winner = False               # 是否已中奖
        self.winner_round = None             # 中奖轮次
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "avatar_base64": self.avatar_base64,
            "confidence": self.confidence,
            "is_winner": self.is_winner,
            "winner_round": self.winner_round
        }
```

### 6.2 抽奖记录数据模型

```python
class LotteryRecord:
    """抽奖记录数据模型"""
    def __init__(self, round_number: int, winner: Participant):
        self.round = round_number            # 抽奖轮次
        self.winner = winner                 # 中奖者
        self.timestamp = get_current_time()  # 抽奖时间
    
    def to_dict(self):
        return {
            "round": self.round,
            "winner": self.winner.to_dict(),
            "timestamp": self.timestamp
        }
```

---

## 7. 异常处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 用户提示 |
|---------|---------|---------|
| InvalidImageFormat | 上传非图片文件 | "请上传 PNG、JPG 或 JPEG 格式的图片" |
| ImageTooLarge | 文件超过 10MB | "图片大小不能超过 10MB" |
| NoAvatarDetected | 未检测到头像 | "未检测到参与者头像，请上传清晰的截图" |
| NoNicknameDetected | 未识别到昵称 | "未识别到昵称，请确保图片清晰" |
| OCRError | OCR 识别失败 | "文字识别失败，请重试" |
| NetworkError | 网络连接问题 | "网络连接失败，请检查网络" |

### 7.2 异常处理策略

```python
try:
    # 图片上传和解析
    participants = parse_screenshot(image_path)
    
except InvalidImageFormat as e:
    return {"error": str(e), "code": "INVALID_FORMAT"}
    
except NoAvatarDetected as e:
    return {"error": str(e), "code": "NO_AVATAR"}
    
except OCRError as e:
    return {"error": str(e), "code": "OCR_ERROR"}
    
except Exception as e:
    # 记录错误日志
    log_error(str(e))
    return {"error": "系统错误，请重试", "code": "SYSTEM_ERROR"}
```

---

## 8. 性能要求

### 8.1 响应时间

| 操作 | 最大响应时间 | 说明 |
|------|-------------|------|
| 图片上传 | 2秒 | 10MB 文件上传 |
| OCR 识别 | 5秒 | 首次加载模型 10秒 |
| 抽奖动画 | 4秒 | 固定时长 |
| 界面渲染 | 1秒 | 前端渲染 |

### 8.2 并发支持

- 单用户单次操作
- 不支持多人同时抽奖
- 不需要数据库持久化

---

## 9. 验收标准

### 9.1 功能验收

- [ ] 可以上传 PNG/JPG 格式截图
- [ ] 自动识别并提取头像（圆形裁剪）
- [ ] 自动识别并提取昵称
- [ ] 头像与昵称正确配对
- [ ] 30个头像网格展示
- [ ] 点击"开始"触发抽奖动画
- [ ] 动画效果：闪烁 → 减速 → 爆炸
- [ ] 中奖者突出显示
- [ ] 支持多轮抽奖
- [ ] 中奖者自动移除
- [ ] 已中奖名单展示
- [ ] 结果可导出

### 9.2 体验验收

- [ ] 界面美观大方
- [ ] 动画流畅无卡顿
- [ ] 错误提示清晰
- [ ] 操作简单直观
- [ ] 加载速度快

---

## 10. 版本规划

### Version 1.0 (MVP)
- 图片上传
- OCR 识别
- 基础抽奖功能
- 单轮抽奖

### Version 1.1
- 多轮抽奖
- 结果导出

### Version 2.0 (Future)
- 批量导入
- 奖项设置
- 中奖概率调整
- 数据持久化
