# 微信抽奖解析器 - API 接口设计文档

## 1. API 概述

### 1.1 基本信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 响应格式

所有 API 响应统一使用以下格式：

```json
{
    "success": true,
    "data": {},
    "error": null
}
```

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述"
    }
}
```

---

## 2. 接口列表

### 2.1 抽奖端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/lottery/draw` | 执行抽奖 |
| GET | `/api/lottery/winners` | 获取中奖者列表 |
| DELETE | `/api/lottery/winners/{id}` | 删除指定中奖者 |
| POST | `/api/lottery/reset` | 重置抽奖 |

---

## 3. 接口详细设计

### 3.1 执行抽奖

**POST** `/api/lottery/draw`

#### 请求头

```
Content-Type: application/json
```

#### 请求体

```json
{
    "participants": [
        {
            "id": "uuid-123456",
            "name": "张三",
            "avatar_base64": "data:image/png;base64,iVBORw0KG..."
        },
        {
            "id": "uuid-789012",
            "name": "李四",
            "avatar_base64": "data:image/png;base64,iVBORw0KG..."
        }
    ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| participants | array | 是 | 参与者列表 |
| participants[].id | string | 是 | 参与者唯一标识 |
| participants[].name | string | 是 | 昵称（2-20字符） |
| participants[].avatar_base64 | string | 是 | Base64 编码的头像 |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/lottery/draw \
  -H "Content-Type: application/json" \
  -d '{
    "participants": [
      {"id": "1", "name": "张三", "avatar_base64": "..."},
      {"id": "2", "name": "李四", "avatar_base64": "..."}
    ]
  }'
```

#### 响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "winner": {
            "id": "uuid-123456",
            "name": "张三",
            "avatar_base64": "data:image/png;base64,iVBORw0KG...",
            "confidence": 0.95
        },
        "remaining_count": 28,
        "total_participants": 30,
        "draw_number": 2
    },
    "error": null
}
```

#### 错误响应 (400 Bad Request)

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "EMPTY_PARTICIPANTS",
        "message": "参与者列表不能为空"
    }
}
```

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "INSUFFICIENT_PARTICIPANTS",
        "message": "参与者数量不足，至少需要 2 人"
    }
}
```

#### 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| EMPTY_PARTICIPANTS | 400 | 参与者列表为空 |
| INVALID_PARTICIPANT | 400 | 参与者数据格式错误 |
| INSUFFICIENT_PARTICIPANTS | 400 | 参与者数量不足 |
| LOTTERY_IN_PROGRESS | 409 | 抽奖正在进行中 |
| SYSTEM_ERROR | 500 | 系统内部错误 |

---

### 3.2 获取中奖者列表

**GET** `/api/lottery/winners`

#### 查询参数

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| limit | integer | 否 | 返回数量限制 | 100 |
| offset | integer | 否 | 偏移量（分页） | 0 |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/lottery/winners?limit=10&offset=0"
```

#### 响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "winners": [
            {
                "id": "uuid-123456",
                "name": "张三",
                "avatar_base64": "data:image/png;base64,iVBORw0KG...",
                "winner_round": 1,
                "draw_time": "2026-05-12T10:30:00Z"
            },
            {
                "id": "uuid-789012",
                "name": "李四",
                "avatar_base64": "data:image/png;base64,iVBORw0KG...",
                "winner_round": 2,
                "draw_time": "2026-05-12T10:31:00Z"
            }
        ],
        "total": 2,
        "limit": 10,
        "offset": 0
    },
    "error": null
}
```

---

### 3.3 删除指定中奖者

**DELETE** `/api/lottery/winners/{winner_id}`

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| winner_id | string | 中奖者 ID |

#### 请求示例

```bash
curl -X DELETE http://localhost:8000/api/lottery/winners/uuid-123456
```

#### 响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "removed_winner": {
            "id": "uuid-123456",
            "name": "张三"
        },
        "remaining_winners": 1
    },
    "error": null
}
```

#### 错误响应 (404 Not Found)

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "WINNER_NOT_FOUND",
        "message": "未找到指定的中奖者"
    }
}
```

---

### 3.4 重置抽奖

**POST** `/api/lottery/reset`

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/lottery/reset
```

#### 响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "message": "抽奖已重置",
        "cleared_winners_count": 5
    },
    "error": null
}
```

---

## 4. WebSocket 接口 (可选功能)

### 4.1 抽奖状态同步

**WebSocket** `/ws/lottery`

用于实时同步抽奖动画状态（如果前端需要精确的动画控制）。

#### 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/lottery');
```

#### 消息类型

**服务端 → 客户端**

```json
{
    "type": "LOTTERY_START",
    "data": {
        "total_participants": 30
    }
}
```

```json
{
    "type": "LOTTERY_PROGRESS",
    "data": {
        "phase": "fast_blink",
        "candidate_ids": ["id1", "id2", "id3"],
        "time_elapsed_ms": 500
    }
}
```

```json
{
    "type": "LOTTERY_RESULT",
    "data": {
        "winner": {
            "id": "uuid-123456",
            "name": "张三",
            "avatar_base64": "..."
        },
        "time_elapsed_ms": 3500
    }
}
```

**客户端 → 服务端**

```json
{
    "type": "LOTTERY_DRAW_REQUEST",
    "data": {
        "participants": [...]
    }
}
```

---

## 5. API 版本控制

### 5.1 版本策略

- 当前版本：`v1`
- 未来版本：`v2`、`v3`
- 版本通过 URL 路径区分：`/api/v1/`、`/api/v2/`

### 5.2 兼容性

- 当前版本 API 保持稳定
- 新增字段保持向后兼容
- 废弃接口提前通知（至少 3 个月）

---

## 6. 安全考虑

### 6.1 速率限制

- 每分钟最多 60 次请求
- 超出限制返回 `429 Too Many Requests`

### 6.2 输入验证

- 所有输入进行严格验证
- 防止 SQL 注入、XSS 攻击
- Base64 数据大小限制（最大 2MB）

### 6.3 错误信息

- 不在错误响应中暴露系统内部细节
- 错误日志仅记录错误码和基本信息

---

## 7. 开发与测试

### 7.1 本地开发

```bash
# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API 文档地址
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### 7.2 测试请求

```bash
# 测试抽奖接口
python -m requests_test.py

# 测试性能
python -m load_test.py
```

---

## 8. 未来扩展

### 8.1 计划中的接口

| 方法 | 路径 | 描述 | 优先级 |
|------|------|------|--------|
| POST | `/api/participants/import` | 批量导入参与者 | P1 |
| GET | `/api/lottery/history` | 获取抽奖历史 | P1 |
| POST | `/api/lottery/export` | 导出抽奖结果 | P1 |
| GET | `/api/statistics` | 获取统计数据 | P2 |

### 8.2 长期规划

- 用户认证与权限管理
- 多房间/多活动支持
- 数据持久化存储
- 第三方集成（钉钉、企业微信）