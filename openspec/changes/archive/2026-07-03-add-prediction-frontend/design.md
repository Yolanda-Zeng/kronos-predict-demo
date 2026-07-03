## Context

`kronos_demo` 是一个 Python CLI 工具：读取 A 股/港美股/qlib 行情，调用 Kronos 模型预测未来 K 线，输出 CSV 与 matplotlib PNG。用户需记忆 20+ 命令行参数，无法交互缩放图表，也难以浏览历史预测结果。

本设计在**不替换 CLI** 的前提下，增加 Web 层：后端复用现有 Python 逻辑，前端提供「金融工作台」式体验——参数可视化、异步任务、交互式图表、历史记录。

**约束：**
- 模型推理在 CPU 上较慢（数十秒至数分钟），UI 必须异步 + 进度反馈。
- 数据源差异大（akshare 需关代理、usstock 需 VPN），需在 UI 给出 contextual hints。
- 用户语言为中文，图表语义需与现有 matplotlib 图例一致（历史/预测/真实三色）。

## Goals / Non-Goals

**Goals:**
- 浏览器内完成：配置参数 → 提交预测 → 查看交互式 K 线 + 误差指标 → 下载 CSV。
- 视觉：深色金融终端风格，信息层次清晰，兼顾「专业感」与「易上手」。
- 架构：CLI 与 Web 共用同一套 Python 预测核心，避免逻辑分叉。
- 首版覆盖：普通预测（含历史回测 / `--future`）、历史记录浏览；调参模式作为进阶 Tab。

**Non-Goals:**
- 用户登录、权限、多用户隔离。
- 实盘交易、券商接口。
- 模型训练、权重管理 UI。
- 移动端专属适配（响应式即可，不做原生 App）。
- 实时推送行情、WebSocket 级联更新。

## Decisions

### 1. 整体架构：FastAPI + React SPA（而非 Streamlit/Gradio）

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Streamlit / Gradio | 极快出原型 | 美观上限低、布局难控、状态模型别扭 | ❌ |
| FastAPI + React SPA | 完全掌控 UX、可做出 TradingView 级图表体验 | 开发量更大 | ✅ 选用 |
| 纯静态 HTML + htmx | 轻量 | 交互图表、复杂表单体验弱 | ❌ |

```
┌─────────────┐     REST/JSON      ┌──────────────────┐
│  React SPA  │ ◀──────────────▶  │  FastAPI         │
│  (Vite)     │                    │  + BackgroundTasks│
└─────────────┘                    └────────┬─────────┘
                                            │ import
                                            ▼
                                   ┌──────────────────┐
                                   │ kronos_core/     │
                                   │ (从 CLI 提取)     │
                                   │ + Kronos 模型     │
                                   └──────────────────┘
                                            │
                                            ▼
                                   predictions/  (CSV + 可选 PNG)
```

### 2. 页面结构与信息架构

采用 **左侧参数栏 + 右侧结果区** 的经典量化工具布局（参考 TradingView、Wind 终端），单页三 Tab：

```
┌──────────────────────────────────────────────────────────────────┐
│  Kronos 预测工作台                          [预测] [历史] [调参]  │
├─────────────────┬────────────────────────────────────────────────┤
│  参数配置        │  结果区                                         │
│                 │  ┌──────────────────────────────────────────┐  │
│  股票代码        │  │  状态条：排队中 / 加载模型 / 推理中 45%    │  │
│  数据源 ▼       │  └──────────────────────────────────────────┘  │
│  日期起止        │  ┌──────────────────────────────────────────┐  │
│  ○ 历史回测      │  │  ECharts：收盘价折线 + 可选 K 线副图       │  │
│  ○ 预测未来      │  │  图例：历史(蓝) 预测(红虚) 真实(绿)       │  │
│                 │  └──────────────────────────────────────────┘  │
│  window         │  ┌────────┐ ┌────────┐ ┌────────┐              │
│  horizon        │  │  MAE   │ │  RMSE  │ │  MAPE  │  ← 回测时有  │
│  seed           │  └────────┘ └────────┘ └────────┘              │
│  [高级 ▼]       │  预测明细表 · [下载 CSV] [下载 PNG]             │
│                 │                                                │
│  [▶ 开始预测]   │                                                │
└─────────────────┴────────────────────────────────────────────────┘
```

**Tab 说明：**

| Tab | 用途 | 核心交互 |
|-----|------|----------|
| **预测** | 主流程 | 表单 + 异步 job + 图表 + 指标 |
| **历史** | 浏览 `predictions/` | 卡片列表（股票/日期/MAPE）→ 点击查看 |
| **调参** | `--tune` 网格搜索 | 网格参数表单 + 长任务进度 + 最优参数一键回填 |

**表单分组（降低认知负担）：**
1. **基础**：股票代码、数据源、日期区间、模式（回测/未来）
2. **模型路径**：model / tokenizer（默认 `./model`、`./tokenizer`，可折叠）
3. **高级**：window、horizon、seed、temperature、top_p、sample_count、adjust

数据源切换时动态显示 hint（如 akshare「请关闭系统代理」、usstock「需 VPN」）。

### 3. 视觉设计系统

**主题：深色金融终端（Dark Terminal）**

| Token | 值 | 用途 |
|-------|-----|------|
| `--bg-base` | `#0d1117` | 页面背景 |
| `--bg-surface` | `#161b22` | 卡片/侧栏 |
| `--bg-elevated` | `#21262d` | 输入框、hover |
| `--text-primary` | `#e6edf3` | 主文字 |
| `--text-muted` | `#8b949e` | 标签、hint |
| `--accent` | `#58a6ff` | 主按钮、链接 |
| `--chart-history` | `#5dade2` | 历史收盘价（对齐现有 `#2c3e50` 语义，略提亮） |
| `--chart-pred` | `#e74c3c` | 预测线 |
| `--chart-actual` | `#2ecc71` | 真实对比线 |
| `--up` | `#f85149` | A 股涨（红） |
| `--down` | `#3fb950` | A 股跌（绿） |

**组件库：** Tailwind CSS + shadcn/ui（Button、Input、Select、Tabs、Card、Progress、Badge、Collapsible）。理由：开箱即用的无障碍组件 + 深色主题友好，无需设计稿即可达到现代 SaaS 水准。

**字体：** `-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`；数字用 `tabular-nums` 对齐。

**动效：** 任务状态切换用 subtle fade；图表 dataZoom 默认开启（弥补静态 PNG 无法缩放的问题）。

### 4. 图表：Apache ECharts（而非 Lightweight Charts）

- ECharts 中文文档完善，折线 + markArea + dataZoom 配置成熟。
- 首版以**收盘价折线**为主（复刻现有 matplotlib 三线图）；二期可加 K 线 candlestick 副图。
- 后端 API 返回结构化 series 数据（timestamps、history、predicted、actual），前端只负责渲染。

### 5. 异步任务模型

预测与调参均为长任务，采用 **Job ID + 轮询**（首版足够简单）：

```
POST /api/jobs/predict  →  { job_id }
GET  /api/jobs/{id}       →  { status, progress, message, result? }
```

- 状态：`queued` → `loading_model` → `fetching_data` → `predicting` → `done` | `failed`
- 实现：`asyncio` + `BackgroundTasks` + 内存 dict（单用户本地工具，无需 Redis）
- 模型单例：进程内 lazy-load 一次 Kronos，后续 job 复用（显著减少等待）

### 6. Python 模块重构

提取 `kronos_core/`（或 `lib/`）：
- `load_kline_data()`, `run_predict()`, `run_tune()`, `compute_metrics()`
- CLI `kronos_qlib_predict.py` 变薄：parse_args → 调用 core
- FastAPI routes 同样调用 core

**不破坏现有用法：** CLI 命令与参数名保持不变。

### 7. 目录布局

```
kronos_demo/
├── kronos_core/           # 提取的共享逻辑
├── backend/
│   ├── main.py            # FastAPI app
│   ├── jobs.py            # 任务状态管理
│   └── schemas.py         # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── pages/         # Predict, History, Tune
│   │   ├── components/    # ParamForm, ChartPanel, MetricCards, JobStatus
│   │   └── api/           # fetch wrappers
│   └── package.json
├── kronos_qlib_predict.py # CLI 入口（调用 kronos_core）
└── predictions/           # 不变
```

### 8. 开发与部署

- 开发：`uvicorn backend.main:app --reload` + `npm run dev`（Vite proxy `/api` → 8000）
- 生产：`npm run build` → `frontend/dist`，FastAPI `StaticFiles` 挂载；一条命令启动
- 可选 `docker-compose.yml` 封装 Python 环境 + Node build

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 重构 CLI 引入回归 | 保留 CLI 集成测试：固定 seed 对比 CSV 输出 |
| CPU 推理超时用户流失 | 明确进度阶段 + 预估时间 hint；支持取消 job |
| 模型加载占内存 | 单例 + 文档说明最低 RAM；可选 `--no-cache-model` |
| 前端与 CLI 参数漂移 | Pydantic schema 为单一参数定义源，CLI 从同一 schema 生成或文档同步 |
| ECharts 包体积 | 按需 import；gzip 后 ~300KB，可接受 |
| akshare/代理问题无法在 UI 内解决 | 数据源旁显示 troubleshooting 链接（README 常见问题） |

## Migration Plan

1. 提取 `kronos_core`，验证 CLI 行为不变。
2. 实现 FastAPI + 单 job 预测 API，curl 可测。
3. 搭建前端 Predict Tab，打通端到端。
4. 加 History Tab、Tune Tab。
5. 更新 README：Web 启动说明 + CLI 仍可用。

**Rollback：** Web 为纯增量；删除 `backend/`、`frontend/`、`kronos_core/` 并恢复 monolithic CLI 即可。

## Open Questions

1. **GPU 支持**：是否在 UI 暴露 device 选择？（建议：高级折叠里提供 cpu/cuda/mps）
2. **调参 Tab 是否首版必做**：工作量大、耗时长；可 Phase 2，proposal 已标为进阶 Tab
3. **是否保留 matplotlib PNG**：API 可同时生成 PNG 供下载，与 ECharts 并存，迁移成本低
