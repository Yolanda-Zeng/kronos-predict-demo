## Why

用户将**结束日期设为 7 月 10 日**并期望看到预测延伸到 7 月 10 日，但图表最远只到**今日（7 月 3 日）**——最后一根真实 K 线所在日。根因是参数语义与实现不一致：

1. **`--end` 目前只控制历史数据拉取上界**，行情接口最多返回到「最新交易日」（今天），不会返回到未来的 7 月 10 日。
2. **`--future` 模式下预测长度由 `horizon` 固定**，调用 `make_future_timestamps(last_ts, horizon)`，**未使用用户填写的 `end` 作为预测终点**。
3. 若用户未开启「预测未来」而留在**历史回测**，预测区间是数据末尾的 horizon 天，**本来就会止于最后一根 K 线（今天）**。

上一轮 `fix-future-chart-date-range` 只修了图表视口与文案，**未改预测时间轴生成逻辑**，因此用户体感「还是无法预测到 7 月 10 日」。

## What Changes

- **`--future` 模式**：当 `end` 晚于最后一根 K 线日期时，预测区间改为 **(last_kline, end]** 内的全部**交易日**，而非固定 `horizon` 天；若 `end ≤ last_kline` 则仍用 `horizon` 作为回退。
- **新增 `make_future_timestamps_until(last_ts, end_ts)`**（或等价函数），生成 business day 序列并设上限（如 60 个交易日）防误填。
- **Web UI**：未来模式下将「结束日期」标注为「预测至 / 数据截止」；提交前展示「最后 K 线 → 预测终点」预览；`horizon` 在未来模式且 `end > last_kline` 时标注为回退项。
- **日志与 result**：打印实际预测起止日期；`pred_start`/`pred_end` 反映真实预测区间。
- **README**：澄清 `end` 在 future 模式下的双重含义。

## Capabilities

### New Capabilities

- `future-prediction-date-range`: future 模式下按 end 日期生成预测时间轴与 pred_len。

### Modified Capabilities

- `prediction-api`: 文档化 future 模式 result 中 pred_start/pred_end 语义。
- `prediction-web-ui`: 未来模式日期字段标签、预测区间预览、horizon 说明。

## Impact

- **kronos_core**: `data.py`, `predict.py`
- **frontend**: `ParamForm.tsx`（可选预估组件）
- **tests**: 新增 until-end 时间轴单测
- **CLI/Web 行为变更**：future + end 在未来时，预测天数可能 ≠ horizon（**非 BREAKING**，但用户需知 horizon 不再是唯一控制项）
