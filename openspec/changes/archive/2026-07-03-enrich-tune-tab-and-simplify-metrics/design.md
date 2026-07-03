## Context

Predict Tab 的 `MetricCards` 当前每张卡片默认展示：缩写、全称、大号数值、summary、interpretation，以及可展开的 tip——信息完整但卡片偏高，用户希望**数值仍是第一视觉焦点**。

Tune Tab 已有预设、workload 预估、playbook、中文化表格，但结果区缺少图表与排序；用户进入 Tab 时也不清楚当前调参针对哪只股票/区间（表单在 Predict Tab，Tune Tab 无摘要）。

## Goals / Non-Goals

**Goals:**
- 指标卡片：**大数字 + 一行短说明 + 可选详细 help**，不减少指标种类与展示时机。
- 调参 Tab 更有「仪表盘感」：上下文、图表、可排序表格、空状态引导。
- 全部纯前端，复用 ECharts 与现有 `TuneRow` 数据。

**Non-Goals:**
- 不调 Kronos 调参算法、不加后端 incremental 结果流。
- 不做 window×temperature 二维热力图（组合维度 >2 时易误导，留后续）。
- 不做跨 session 调参历史持久化。

## Decisions

### 1. 指标卡片：Number-first 布局

```
┌─────────────────────┐
│ MAE          [?]    │
│ 0.0639              │  ← 2xl 数值，视觉主元素
│ 平均偏离约 X 元      │  ← 单行 subtitle（来自 metricHelp.summary 精简）
└─────────────────────┘
```

- MAPE 卡片 subtitle 旁保留「推荐」小 badge。
- `?` 点击展开现有 `tip` 全文；移除卡片内默认显示的 fullName、interpretation 第二行。
- 区块标题可选：`回测误差指标` + 一行 `优先看 MAPE`。

**Why not tooltip-only?** 用户要求「简短说明」默认可见，tooltip  alone 不够直观。

### 2. 调参上下文条 `TuneContextBanner`

展示：`{instrument} · {data_source} · {start} ~ {end}`，附文案「调参使用预测 Tab 中的股票与日期，请先在预测 Tab 确认后再跑」。

只读，不提供在 Tune Tab 改 instrument（避免双表单漂移）。

### 3. MAPE 柱状图 `TuneResultsChart`

- 取 results 按 MAPE 升序 Top 10。
- X 轴：`w{window}/T{temp}/p{top_p}/s{sample}` 简写标签。
- Y 轴：MAPE (%)。
- 最优柱高亮 accent 色；无结果时不渲染。

复用 `echarts-for-react`，与 `ChartPanel` 同 dark theme。

### 4. 表格排序（客户端）

- state: `sortKey`, `sortDir`。
- 默认 `mape` asc（与 README「优先看 MAPE」一致）。
- 列头点击切换 asc/desc；最优行高亮逻辑不变（仍按 backend `best.rmse`）。

### 5. 空状态 `TuneEmptyState`

Tune Tab 结果列在无 job、无 results 时显示：
- 图标/标题「尚未开始调参」
- 三 bullet：选预设 → 看组合数预估 → 开始调参
- 折叠链到 `TuneGuidePanel` 第一条

表单列与 guide 列保持现有布局。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 柱状图标签过长 | 截断 + tooltip 展示完整参数 |
| 排序与 backend best 不一致 | best badge 仍跟 `best.rmse`；表头注明默认按 MAPE 排序 |
| 卡片变「太简」丢失信息 | `?` 保留完整 README 对齐释义 |

## Migration Plan

1. 调整 `MetricCards` 布局（Predict + History 若复用则一并受益）。
2. 新增 Tune 子组件并接入 `TunePage`。
3. 手动验证 Predict 回测仍显示三指标；Tune 完成后图表+排序可用。

## Open Questions

1. History Tab 打开历史记录时是否也展示精简版 MetricCards？（建议 yes，同一组件）
2. Top N 柱状图 N=10 是否可配置？（默认固定 10，不做 UI 配置）
