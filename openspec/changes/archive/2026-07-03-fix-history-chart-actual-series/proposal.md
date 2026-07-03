## Why

历史 Tab 点击某条回测记录后，图表只显示预测曲线（红虚线），缺少历史 K 线（蓝）和真实对比线（绿）。根因是：预测 CSV 仅保存 `timestamps/close` 预测列；`list_predictions` 只从中解析 `predicted`；前端 `HistoryPage.openItem` 还将 `history` 置空、`actual` 硬编码为 `null`。用户在 Predict Tab 能看到的完整三曲线，在历史回放时无法复现。

## What Changes

- **预测完成时写入 sidecar JSON**（如 `*_meta.json`）：保存完整 `chart`（history / predicted / actual / bridge）、`metrics`、`mode`。
- **扩展 `list_predictions`**：优先加载 sidecar；无 sidecar 的旧记录降级为仅 predicted，并标记 `chart_complete: false`。
- **修复 `HistoryPage`**：直接使用 API 返回的 chart，不再丢弃 actual/history；sidecar 缺失时显示提示。
- **（顺带）** 历史列表条目可展示 MAPE（sidecar 中有 metrics 时）。

## Capabilities

### New Capabilities

- `prediction-run-metadata`: 预测 run 的 sidecar 持久化与加载（chart + metrics + mode）。

### Modified Capabilities

- `prediction-api`: `GET /api/predictions` 返回完整 chart 与 metrics（有 sidecar 时）。
- `prediction-web-ui`: 历史 Tab 图表与 Predict Tab 一致展示三曲线（回测模式）。

## Impact

- **kronos_core**: `predict.py` 写 sidecar；`history.py` 读 sidecar
- **frontend**: `HistoryPage.tsx` 修复 chart 组装逻辑
- **磁盘**: 每条预测多一个 JSON 文件（体量小）
- **兼容**: 旧 CSV-only 记录无法自动补全 actual，需重新跑预测或接受降级提示
