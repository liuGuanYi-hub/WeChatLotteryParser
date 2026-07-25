# 微信抽奖解析器

一个基于 FastAPI 的 Web 抽奖工具：从微信红包/抽奖截图中识别头像和昵称，生成参与者池，并通过动画流程完成多轮抽奖。

## 功能

- 上传 PNG、JPG/JPEG 截图并检测圆形头像区域。
- 使用 OpenCV、Pillow 和 PaddleOCR 识别头像与昵称。
- 支持多轮抽奖、中奖者移除、结果查询和重置。
- 浏览器端提供上传、抽奖动画和结果导出入口。

## 动态系统架构图

![微信抽奖解析器动态系统架构图](docs/architecture/dynamic-archify-architecture.svg)

- [打开交互式动态架构图](docs/architecture/dynamic-archify-architecture.html)
- [查看架构源数据](docs/architecture/dynamic-archify-architecture.json)

## 技术栈

- 后端：Python 3.8+、FastAPI、Uvicorn
- 图像处理：OpenCV、Pillow
- OCR：PaddleOCR
- 前端：原生 HTML、CSS、JavaScript
- 状态：本地会话状态，不依赖外部数据库

## 快速开始

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器访问 `http://localhost:8000`，API 文档位于 `/docs` 和 `/redoc`。

## 核心流程

1. 浏览器上传截图。
2. FastAPI 校验文件并交给 OCR/头像处理服务。
3. 系统按位置配对头像与昵称，形成参与者列表。
4. 抽奖引擎随机选择中奖者并维护剩余池。
5. 前端播放抽奖动画并展示、导出结果。

## 项目结构

app/               # API、核心逻辑、模型和服务
static/            # CSS 和 JavaScript
templates/         # HTML 模板
tests/             # 测试
docs/              # 规格、API、设计和架构文档
requirements.txt   # Python 依赖

## 文档与测试

- [功能规格](docs/SPEC.md)
- [API 设计](docs/API.md)
- [技术架构](docs/ARCHITECTURE.md)
- `pytest`

## 许可证

MIT License
