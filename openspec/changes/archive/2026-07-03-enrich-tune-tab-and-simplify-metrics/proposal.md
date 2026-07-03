## Why

上一轮 `enhance-tune-ui-and-polish` 已为预测 Tab 增加了 MAE/RMSE/MAPE 释义，但卡片信息层叠较多，**大数字的视觉重心被稀释**；用户明确要求指标**必须继续 prominently 展示**，只需简短说明即可。调参 Tab 虽已具备参数 help 与 playbook，结果区仍以表格为主，**缺少可视化与交互**，整体观感偏「工具表单」、不够丰富。

## What Changes

- **预测 Tab 指标卡片精简**：保留 MAE / RMSE / MAPE 三卡片与大号数值；每条仅一行简短说明（subtitle）；详细释义收进 `?` 或 hover，不再默认堆叠全称 + summary + interpretation。
- **调参 Tab 上下文条**：顶部展示当前股票、数据源、日期区间（来自共享 Predict 表单），提醒用户「正在为谁调参」。
- **调参结果 MAPE 柱状图**：完成后用 ECharts 展示 Top N 组合的 MAPE 对比（复用现有 chart 栈）。
- **结果表可排序**：点击列头按 MAPE / RMSE / window 等排序，默认 MAPE 升序。
- **调参空状态**：未跑过任务时展示引导卡片（预设推荐 + 链到调试指南），避免大片空白。
- **单行指标解读条**：结果区顶部保留「MAPE 越小越好…」一句，与图表、表格形成信息层次。

## Capabilities

### New Capabilities

- `tune-results-visualization`: 调参结果 MAPE 柱状图、表格排序、空状态引导。

### Modified Capabilities

- `prediction-web-ui`: 指标卡片 number-first 布局；调参 Tab 上下文条与结果区视觉增强。

## Impact

- **前端**：`MetricCards.tsx`、`TunePage.tsx`、新增 `TuneContextBanner.tsx`、`TuneResultsChart.tsx`、`TuneEmptyState.tsx`
- **后端**：无变更
- **依赖**：复用现有 ECharts / `paramHelp.ts` / 共享 form state
