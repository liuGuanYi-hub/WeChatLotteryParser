# 微信红包/抽奖参与者解析与抽奖系统

一个基于 Web 的微信抽奖工具，可以从截图自动提取参与者信息并进行抽奖。

## 🎯 功能特性

- 📷 **智能截图识别** - 自动从微信截图提取头像和昵称
- 🎲 **多种抽奖模式** - 支持头像球展示 + 随机弹出效果
- ✨ **流畅动画** - 快速闪烁 → 减速 → 爆炸，突出中奖者
- 👥 **多轮抽奖** - 支持连续抽取，中奖者自动移除
- 📊 **结果导出** - 导出中奖名单
- 🌐 **Web 界面** - 无需安装，浏览器即可使用

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd WeChatLotteryParser
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **启动服务**

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **打开浏览器**

访问 http://localhost:8000

## 📖 使用指南

### 1. 上传截图

点击上传区域或拖拽微信红包/抽奖截图到页面。

**支持的截图格式：**
- PNG
- JPG/JPEG
- 最大 10MB

### 2. 等待识别

系统会自动：
1. 检测圆形头像区域
2. 识别昵称文本
3. 配对头像和昵称

### 3. 开始抽奖

点击"开始抽奖"按钮，观看动画效果：
- 阶段1：快速闪烁（1秒）
- 阶段2：减速过渡（1.5秒）
- 阶段3：爆炸展示（0.5秒）

### 4. 继续抽奖

中奖者会自动从池中移除，可以继续抽取下一位。

### 5. 导出结果

点击"导出结果"按钮，可以复制或下载中奖名单。

## 🏗️ 项目结构

```
WeChatLotteryParser/
├── docs/                    # 开发文档
│   ├── SPEC.md             # 功能规格说明
│   ├── API.md              # 接口设计文档
│   ├── ARCHITECTURE.md     # 技术架构文档
│   └── DESIGN.md           # 界面设计文档
│
├── app/                    # 应用代码
│   ├── main.py            # FastAPI 主入口
│   ├── api/               # API 路由
│   ├── services/          # 服务层
│   └── models/            # 数据模型
│
├── static/                 # 静态资源
│   ├── css/               # 样式文件
│   └── js/                # 前端脚本
│
├── templates/              # HTML 模板
│   └── index.html
│
├── tests/                  # 测试代码
│
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明
```

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| **后端** | FastAPI + Uvicorn |
| **图像处理** | OpenCV + Pillow |
| **文字识别** | PaddleOCR |
| **前端** | 原生 HTML/CSS/JavaScript |
| **Python** | 3.8+ |

## 📝 API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 前端页面 |
| POST | `/api/lottery/draw` | 执行抽奖 |
| GET | `/api/lottery/winners` | 获取中奖者列表 |
| POST | `/api/lottery/reset` | 重置抽奖 |

## ⚙️ 配置

环境变量配置文件：`.env`

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
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_lottery.py

# 带覆盖率测试
pytest --cov=app tests/
```

## 🐛 故障排除

### OCR 识别慢
首次运行需要下载 PaddleOCR 模型（约 100MB），请耐心等待。

### 头像检测不准
- 确保截图清晰
- 头像应该是圆形
- 避免截图中包含太多无关元素

### 抽奖不随机
每次抽奖使用时间戳作为随机种子，确保真正的随机性。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 引擎
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代 Python Web 框架
- [OpenCV](https://github.com/opencv/opencv) - 计算机视觉库

---

**版本**: 1.0.0  
**最后更新**: 2026-05-12