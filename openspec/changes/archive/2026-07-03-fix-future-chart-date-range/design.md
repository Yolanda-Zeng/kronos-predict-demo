## Context

`execute_predict` 在 `--future` 模式下：
- 用 `[start, end]` 全部 K 线作输入窗口；
- `make_future_timestamps(last_ts, horizon)` 生成 `last_ts` 之后的 N 个交易日；
- `build_chart_series` 将 predicted 序列从 `last_ts` 桥接到未来时间戳。

逻辑上 predicted 应超出 history 最后一点。用户仍反馈「最远日期是今日」，经分析更可能是：

1. **误用回测模式**：未勾选「预测未来」，horizon 只影响扣留对比天数，图表最远日期 = 表单 `结束日期`。
2. **视口问题**：历史数据很长时，future 5 天仅占 X 轴极右 0.x%，视觉上像「停在今天」。
3. **少数数据 bug**：predicted timestamps 未正确序列化（需单测 guard）。

## Goals / Non-Goals

**Goals:**
- future 模式下图表**默认可见**完整预测段（X 轴 zoom 到 relevant range）。
- 用户一眼能区分 backtest vs future 的日期语义。
- 标记最后已知 K 线与预测区间 `[pred_start, pred_end]`。

**Non-Goals:**
- 不改变 Kronos 模型推理逻辑。
- 不自动把 `end` 日期改成系统今日（用户仍控制数据拉取区间）。

## Decisions

### 1. 模式说明（ParamForm）

| 模式 | 文案要点 |
|------|----------|
| 历史回测 | 图表最远日期 = **结束日期**；horizon 为末尾对比天数 |
| 预测未来 | 图表在 **结束日期之后** 再延伸 horizon 个交易日；无真实对比线 |

在 radio 下方动态显示，减少误选。

### 2. ChartPanel 视口策略

计算时间边界：
```
lastHistory = max(history.timestamps)
lastPredicted = max(predicted.timestamps)
```

**future 模式**（由 props `mode?: 'backtest' | 'future'` 传入）：
- `dataZoom` 初始范围：从 `lastHistory - 60 calendar days` 到 `lastPredicted + 2 days`（或 history 不足 60 天则从头）。
- `markLine` 在 `lastHistory`：`最后已知K线`
- 副标题 / title：`预测区间 {pred_start} ~ {pred_end}`

**backtest 模式**：
- 保持现有全量 zoom 或 focus 到预测+对比段（末 `horizon+window` 天），不延伸超过 `end`。

### 3. API / 类型

`PredictPage` 向 `ChartPanel` 传入 `mode={result.mode}`、`predStart`、`predEnd`（result 已有字段）。

`ChartData` 可选增加 `last_known_ts`（bridge.timestamp 已有，复用 bridge）。

### 4. 后端 guard（轻量）

在 `build_chart_series` 或 `execute_predict` future 分支：
- assert / log if `predicted` 最后时间戳 ≤ `last_ts`（除 bridge 点外）→ 便于发现数据 bug
- 单测：`make_future_timestamps` 输出 strictly after `last_ts`

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 用户其实在 backtest | 模式 hint 明确说明 |
| zoom 窗口 60 天 magic number | 常量 `FUTURE_CHART_LOOKBACK_DAYS`，后续可配置 |
| markLine 与中文 legend 重叠 | 放 grid top margin |

## Migration Plan

1. ParamForm hint
2. ChartPanel props + zoom + markLine
3. PredictPage wire mode/dates
4. 单测 + 手动 future 模式验证

## Open Questions

1. History Tab 打开 future 记录时同样应用 zoom？（建议 yes，传 mode from sidecar）
