## Why

当前 Kronos 预测能力完全依赖命令行：参数多、学习成本高，结果以静态 PNG/CSV 落在 `predictions/` 目录，不便于交互查看与对比。用户希望在不牺牲现有脚本工作流的前提下，增加一个兼顾实用与美观的 Web 界面，让选股、调参、跑预测、看 K 线对比和误差指标可以在浏览器里一站式完成。

## What Changes

- 新增 **FastAPI 后端**，封装现有 `kronos_qlib_predict.py` 的数据加载、预测、调参逻辑，提供 REST API 与异步任务状态查询（CPU 推理耗时长，需后台 job）。
- 新增 **Web 前端单页应用**，提供表单化参数配置、实时任务进度、交互式 K 线对比图、误差指标卡片、历史预测记录浏览。
- 采用 **金融终端风格** 的视觉设计：深色主题、信息密度适中、红涨绿跌（A 股习惯），与现有 matplotlib 图例语义保持一致。
- 保留 CLI 为唯一真相来源：Web 层调用同一套 Python 函数，不复制业务逻辑。
- **Non-goals（首版不做）**：用户账号/权限、多租户、实盘交易下单、模型训练、移动端原生 App。

## Capabilities

### New Capabilities

- `prediction-api`：预测与调参 REST API、异步任务队列、结果文件访问、健康检查。
- `prediction-web-ui`：参数表单、任务中心、交互式图表、历史记录、响应式布局与视觉规范。

### Modified Capabilities

（无——项目尚无既有 OpenSpec 规格）

## Impact

- **新增目录**：`backend/`（FastAPI）、`frontend/`（Vite + React）、可选 `docker-compose.yml` 便于一键启动。
- **依赖**：FastAPI、uvicorn、（前端）React、ECharts 或 Lightweight Charts、Tailwind CSS。
- **现有代码**：`kronos_qlib_predict.py` 需小幅重构——将核心函数提取为可 import 的模块，供 CLI 与 API 共用；CLI 入口行为保持不变。
- **运行方式**：本地开发时后端 + 前端 dev server；生产可静态构建前端并由 FastAPI 托管。
- **性能**：单次预测仍受 CPU/GPU 与模型加载限制；UI 通过异步 job + 进度反馈管理用户预期。
