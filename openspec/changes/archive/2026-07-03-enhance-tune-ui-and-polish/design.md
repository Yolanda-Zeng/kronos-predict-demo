## Context

当前 `TunePage.tsx` 仅展示英文字段名输入框与结果表格，README 中的调参说明（window 优先、MAPE 排序、stride 控耗时等）未进入 UI。用户刚跑通 Web，下一步自然需求是「敢调、会调、调错了知道怎么办」。

Predict Tab 的 `ParamForm` 已有数据源 hint 与高级参数折叠，但 window/horizon/temperature 等仍无释义——Tune 与 Predict 应共享同一套参数知识库。

## Goals / Non-Goals

**Goals:**
- 调参 Tab 内嵌参数说明 + 调试 playbook，无需翻 README 也能上手。
- 提供 3 档预设，降低首次调参认知负担。
- 提交前展示 grid 组合数，帮助用户判断是否会「挂一晚上」。
- 结果表格更易读（中文表头、最优行标记、指标解读一句提示）。
- Predict Tab 的 MAE/RMSE/MAPE 卡片展示**中文释义与读数提示**（无需翻 README）。

**Non-Goals:**
- 不改 Kronos 调参算法本身（仍调用 `execute_tune`）。
- 不做自动选参 ML/meta-learning。
- Phase 1 不做 Job 取消、批量预测（列入 roadmap）。

## Decisions

### 1. 参数知识库：前端静态 `paramHelp.ts`（而非后端 API）

| 方案 | 优点 | 缺点 |
|------|------|------|
| 静态 TS 模块 | 零延迟、与 UI 同版本、易维护 | 改文案需发版 |
| 后端 `/api/help` | 可热更新 | 过度设计 |
| 嵌入 README | 单源 | 前端解析 markdown 重 |

选用 **`frontend/src/content/paramHelp.ts`**，结构：

```ts
export const tuneParamHelp = {
  grid_window: { label, summary, range, impact, debugTip },
  ...
};
export const tunePlaybook = [{ title, steps: string[] }, ...];
export const tunePresets = { quick, standard, thorough };
export const metricHelp = {
  mae: { fullName, summary, interpretation, tip },
  rmse: { ... },
  mape: { ... },
};
```

README 调参章节与「误差指标解读」表格与 `paramHelp.ts` 保持语义一致。

### 2. UI 布局：右侧「指南抽屉」+ 字段旁 `?` 提示

```
┌─────────────────────────────────────────────────────────────┐
│  [调参表单]              │  [调试指南]  [参数说明]            │
│  grid_window  [?]       │  ▼ 推荐调参顺序                   │
│  预设: 快速|标准|精细      │  ▼ 怎么看 MAPE/RMSE              │
│  组合数: 12 · 约 15min   │  ▼ 常见失败排查                   │
│  [开始调参]               │                                   │
└─────────────────────────────────────────────────────────────┘
```

- **`ParamHelpField`**：label + input + hover/click 展开 `summary` + `debugTip`。
- **`TuneGuidePanel`**：右侧 card，accordion 展示 playbook。
- **组合数**：前端解析逗号列表算 `∏ len(grid_*)`，预估时间 = `combos × max_windows × 常数秒`（保守写「约 X–Y 分钟」）。

### 3. 预设方案

| 预设 | grid_window | grid_temp | grid_top_p | grid_sample_count | stride | max_windows |
|------|-------------|-----------|------------|-------------------|--------|-------------|
| 快速试跑 | 64,128 | 1.0 | 0.9 | 1 | 10 | 30 |
| 标准 | 64,128,256 | 1.0,0.9 | 0.95,0.9 | 1,5 | 5 | 120 |
| 精细 | 64,128,256,384 | 1.0,0.9,0.7 | 0.95,0.9,0.8 | 1,5,10 | 3 | 200 |

默认选中「标准」，与 CLI 默认 grid 一致。

### 4. 结果区增强

- 表头中文化：`window → 窗口`, `T → 温度`, `mape → MAPE(%)` 等。
- 最优行（RMSE 最小）左侧加 badge「最优」。
- 表格上方固定一句：`MAPE 越小越好，横向对比股票时优先看 MAPE`。
- 表头 MAE/RMSE/MAPE 列可 hover 或点击 `?` 展示 `metricHelp` 摘要（与 Predict Tab 同源）。

### 5. 预测指标卡片（MetricCards）

将 `MetricCards.tsx` 升级为 **`MetricHelpCard`** 或增强现有卡片：

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ MAE  [?]            │  │ RMSE [?]            │  │ MAPE [?]  ★推荐    │
│ 平均绝对误差         │  │ 均方根误差           │  │ 平均绝对百分比误差   │
│ 0.0639              │  │ 0.0773              │  │ 0.80%               │
│ 预测均价差（元）      │  │ 对大偏差更敏感       │  │ 横向对比首选        │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

文案来源（与 README 一致）：

| 指标 | 全称 | 一句话 | 读数提示 |
|------|------|--------|----------|
| MAE | 平均绝对误差 | 预测收盘价平均偏离真实值多少**元** | 受股价绝对值影响，跨股票对比参考价值有限 |
| RMSE | 均方根误差 | 类似 MAE，但对偏差大的天惩罚更重 | 通常 ≥ MAE；越接近 MAE 说明误差越均匀 |
| MAPE | 平均绝对百分比误差 | 预测平均偏离真实价格的**百分比** | **优先看此指标**；< 1% 算不错 |

- 历史回测模式才显示；`--future` 模式仍隐藏。
- 卡片下方可选一行：`本结果为历史回测，扣留最后 horizon 天与真实值对比。`

### 6. Phase 2：Predict Tab 复用 + 调参 CSV 下载

- `ParamForm` 高级区字段接 `predictParamHelp`（同文件不同 section）。
- 调参完成后若 `result.csv_path` 存在，显示下载按钮（复用 `downloadUrl`）。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 文案过长占屏幕 | accordion 默认折叠，字段 hint 单行 summary |
| 预估时间不准 | 标注「仅供参考」，按 CPU 环境说明 |
| 与 README 漂移 | tasks 含「同步检查 README 调参章节」 |
| 预设误导（股票差异大） | preset 旁注「每只股票建议单独调参」 |

## Migration Plan

1. 新增 content 模块与 UI 组件。
2. 改造 `TunePage` 布局（lg 三列或两列+指南）。
3. Phase 2 扩展 `ParamForm`、Tune 下载。
4. 更新 README 一句「Web 调参 Tab 内含参数说明」。

无后端迁移，可独立发版前端 static build。

## Open Questions

1. 是否在 Predict Tab 同步做参数说明（建议 Phase 2 一并做，体验一致）？
2. 预估耗时常数是否暴露为「高级设置」（默认隐藏）？
