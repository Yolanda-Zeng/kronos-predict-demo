## Why

用户开启「预测未来（--future）」并设置 horizon 后，期望图表 X 轴延伸到**最后已知 K 线之后的未来交易日**，但界面上最远日期仍停在「今日/结束日期」，看不到预测段。常见原因有两类：（1）**模式误解**——历史回测模式下 horizon 表示扣留最后 N 天对比，图表本来就不会超过 `end`；（2）**图表视口**——未来时间戳已生成，但 ECharts 默认展示全量历史，预测段挤在最右端或被 dataZoom 视口忽略，用户误以为「没有未来」。

## What Changes

- **模式说明强化**：Predict Tab 在 future / backtest 模式下显示明确文案（结束日期 vs 预测延伸区间）。
- **ChartPanel 视口**：future 模式默认 zoom 到「末尾历史 + 全部预测段」；增加「最后已知 K 线」标记线与 `pred_end` 副标题。
- **数据校验**：确认 `make_future_timestamps` 与 `build_chart_series` 在 future 模式下 predicted 最后时间戳晚于 history 最后时间戳；API result 携带 `pred_start`/`pred_end` 供前端展示。
- **ChartPanel 标题**：future 模式改为「预测延伸至 YYYY-MM-DD」，backtest 模式保持「预测 vs 真实」。

## Capabilities

### New Capabilities

- `future-chart-viewport`: 未来预测模式下图表时间轴视口、标记线与区间标注。

### Modified Capabilities

- `prediction-web-ui`: ChartPanel 与预测模式说明的行为要求。
- `prediction-run-metadata`: sidecar 写入 `pred_start`/`pred_end`（若 sidecar change 已落地则对齐；否则在 chart 层补充）。

## Impact

- **frontend**: `ChartPanel.tsx`, `PredictPage.tsx`, `ParamForm.tsx`（模式 hint）
- **kronos_core**: 可选在 `build_chart_series` 返回 `pred_start`/`pred_end` 字段；`predict.py` 已有 pred_start/end 在 result 层
- **tests**: `make_future_timestamps` 与 chart 时间单调性单测

## Impact note

与 `fix-history-chart-actual-series` 互补：该 change 修历史回放缺线；本 change 修 future 模式时间轴可见性与模式说明。
