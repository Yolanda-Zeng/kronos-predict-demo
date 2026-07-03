## Context

`execute_predict` 已调用 `build_chart_series` 生成含 `history`、`predicted`、`actual` 的完整 chart，并通过 job result 返回给 Predict Tab。但落盘时只写 `pred_df` CSV + PNG，**chart 未持久化**。

`kronos_core/history.py::_load_chart_from_csv` 仅从 CSV 读 predicted。`HistoryPage.openItem` 进一步写死：

```ts
history: { timestamps: [], close: [] },
actual: null,
```

因此历史回放必然缺线。

## Goals / Non-Goals

**Goals:**
- 新预测 run 在历史 Tab 可完整回放三曲线（与 Predict Tab 一致）。
- sidecar 同时持久化 metrics，历史列表可显示 MAPE。
- 旧记录优雅降级 + 用户可理解的提示。

**Non-Goals:**
- 不为旧 CSV-only 记录自动 re-fetch 行情重建 actual（缺少 data_source/start/end 等参数，不可靠）。
- 不改 PNG 生成逻辑（PNG 本身已含三线，但 Web 用 ECharts 需 JSON 数据）。

## Decisions

### 1. Sidecar 文件：`{csv_basename}_meta.json`

与 predict CSV 同目录，命名规则：将 `_predict.csv` 替换为 `_meta.json`。

内容 schema：

```json
{
  "version": 1,
  "mode": "backtest",
  "metrics": { "mae": 0.06, "rmse": 0.08, "mape": 0.8 },
  "chart": { "history": {...}, "predicted": {...}, "actual": {...}, "bridge": {...} }
}
```

- `future` 模式：`actual` 为 null，`metrics` 为 null。
- 写入时机：`execute_predict` 保存 CSV 之后、return 之前。

**Why JSON sidecar vs 扩展 CSV?** chart 为嵌套结构，JSON 与现有 API `ChartData` 类型一致，解析简单。

### 2. `list_predictions` 加载策略

```
if meta.json exists:
  chart = meta.chart, metrics = meta.metrics, chart_complete = true
else:
  chart = { predicted from CSV only }, metrics = null, chart_complete = false
```

### 3. 前端 `HistoryPage`

- 删除手工拼装 chart 的逻辑；使用 `item.chart` 全量字段。
- 若 `chart_complete === false`（或缺少 history/actual）：显示 amber 提示「该记录为旧格式，仅含预测曲线；重新运行回测可查看真实对比」。
- `ChartPanel` 无需修改（已支持 actual series）。

### 4. 类型扩展

`HistoryItem` 增加可选 `chart_complete?: boolean`。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 旧记录仍缺 actual | 明确降级提示；新 run 自动有 sidecar |
| sidecar 与 CSV 不同步 | 同一次 write 事务顺序写 CSV 再写 JSON |
| JSON 体积 | chart 通常 < window+horizon 点数，可接受 |

## Migration Plan

1. 实现 sidecar 写入（predict.py）。
2. 更新 history.py 加载。
3. 修复 HistoryPage。
4. 验证：新跑一次回测 → 历史 Tab 应见三线。

## Open Questions

1. 是否在 sidecar 中额外存 `data_source/start/end` 以便未来 re-fetch？（建议 v1 不做，YAGNI）
