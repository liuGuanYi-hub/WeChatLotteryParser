# 纯名单抽奖器 2.0

## 目标

把项目收敛为一个不依赖图片、头像和 OCR 的本地名单抽奖器：参与者由用户手动输入，抽奖由服务端完成，浏览器只负责展示。

## 运行流程

```text
逐行输入名单
  -> 创建抽奖场次
  -> 服务端保存场次状态
  -> 安全随机抽取一人
  -> 标记中奖并写入历史
  -> 前端更新剩余人数、参与者状态和导出内容
```

## 后端边界

- `app/core/lottery.py`：无状态随机抽奖引擎。
- `app/services/lottery_service.py`：管理多个独立场次和多轮中奖状态。
- `app/api/routes.py`：创建场次、抽奖、查询、重置和历史接口。
- `app/models/participant.py`：参与者和中奖状态模型。
- `app/main.py`：应用入口、静态资源和健康检查。

## 抽奖规则

- 每行文本对应一个抽奖名额。
- 重复昵称不会自动合并，会作为不同名额保留。
- 每次只从未中奖参与者中抽取一人。
- 最后一名参与者也可以被抽取。
- 前端动画不能决定中奖结果。
- 生产环境使用 `secrets.SystemRandom`；测试通过注入确定性随机源复现结果。

## 2026-08-04 GitHub 对比优化

本轮参考了 Live Countdown Picker、LottoPickerPWA、Magpie-LuckyDraw 和 Random Name Picker 的公开设计方向：

- 采用奖项名额和批量抽取模型，满足年会、课堂等一次产生多个中奖者的场景。
- 抽奖仍由服务端 `secrets.SystemRandom` 完成，前端动画或按钮不能决定中奖结果。
- 使用 SQLite 保存完整场次快照，保存参与者状态、中奖轮次和中奖时间，进程重启后可恢复。
- 使用浏览器 `localStorage` 保存最近场次 ID，页面刷新后自动读取服务端快照。
- 只借鉴功能边界，不引入头像识别、OCR、3D 标签云、React 或外部数据库，保持项目可本地运行和可测试。

新增字段：

- 创建场次：`prize_name`、`winner_count`。
- 抽取请求：`count`，用于一次抽取多人。
- 场次快照：`remaining_slots`，表示奖项剩余名额；未设置名额时为 `null`。

持久化文件默认位于项目目录 `data/lottery.sqlite3`，已加入 `.gitignore`，避免把真实参与者名单提交到仓库。

## 当前限制

- 当前没有用户登录和多人协作权限。
- 当前不保存原始名单文件，也不上传任何图片。

如果需要多人同时参与，再考虑 Redis、数据库和权限控制。

## 测试

```powershell
python -m pytest -q
python -m compileall -q app
```

测试覆盖抽奖引擎、重复中奖防止、场次重置、空场次错误、健康检查和 API 主流程。
