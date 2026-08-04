# 简易名单抽奖器

一个基于 FastAPI 的本地名单抽奖器。手动输入参与者名单，由服务端安全随机抽取并记录多轮中奖结果。

## 当前功能

- 每行输入一名参与者。
- 重复昵称按独立抽奖名额处理。
- 创建独立抽奖场次。
- 服务端使用 `secrets.SystemRandom` 抽奖。
- 多轮抽奖自动排除已中奖者。
- 查看参与者状态和中奖历史。
- 重置本场抽奖。
- 导出文本中奖名单。

当前版本不读取图片、不识别头像、不加载 OCR，也不需要数据库或外部服务。

## 快速开始

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：<http://127.0.0.1:8000>

API 文档：<http://127.0.0.1:8000/docs>

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/lottery/sessions` | 创建抽奖场次 |
| GET | `/api/lottery/sessions/{session_id}` | 查询场次状态 |
| POST | `/api/lottery/sessions/{session_id}/draw` | 抽取一人 |
| POST | `/api/lottery/sessions/{session_id}/reset` | 重置本场 |
| GET | `/api/lottery/sessions/{session_id}/history` | 查询中奖历史 |
| GET | `/healthz` | 健康检查 |

创建场次示例：

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/lottery/sessions `
  -ContentType 'application/json' `
  -Body '{"participants":["张三","李四","王五"]}'
```

## 项目结构

```text
app/
├── api/routes.py                 # 抽奖 API
├── core/lottery.py               # 无状态安全随机引擎
├── core/config.py                # 应用配置
├── models/participant.py         # 参与者模型
├── services/lottery_service.py   # 场次和中奖状态
└── main.py                       # FastAPI 入口
static/                           # CSS 和 JavaScript
templates/                        # HTML 页面
tests/                            # 自动化测试
docs/LOTTERY_V2.md                # 当前设计说明
```

## 测试

```powershell
python -m pytest -q
python -m compileall -q app tests
```

## 当前限制

- 场次状态保存在进程内，服务重启后会丢失。
- 当前没有登录、权限和多人协作功能。
- 当前不保存原始名单文件。

如未来需要跨重启保存结果，再增加 SQLite；如需要多人协作，再增加数据库、缓存和权限控制。

## 许可证

MIT License
