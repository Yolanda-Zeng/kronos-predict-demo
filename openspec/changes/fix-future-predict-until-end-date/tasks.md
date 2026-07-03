## 1. Core prediction date range

- [x] 1.1 Add `make_future_timestamps_until(last_ts, end_ts, max_periods=60)` in `kronos_core/data.py`
- [x] 1.2 Update `execute_predict` future branch to use until-end timestamps when end > last_kline, else horizon fallback
- [x] 1.3 Pass computed `pred_len = len(y_timestamp)` to predictor; log actual pred_start/pred_end

## 2. Tests

- [x] 2.1 Test until-end: last=2026-07-03, end=2026-07-10 yields last predicted business day on or before 2026-07-10
- [x] 2.2 Test fallback when end <= last_kline uses horizon count
- [x] 2.3 Test backtest path unchanged

## 3. Web UI and docs

- [x] 3.1 Update `ParamForm` future-mode end date label and hint (预测至日期 + 延伸至 end 的说明)
- [x] 3.2 Update horizon help in future mode (fallback when end not beyond last bar)
- [x] 3.3 Update README future 模式 section: end 作为预测终点（当 end 晚于最新 K 线）

## 4. Verification

- [x] 4.1 Manual: future mode, end=7/10, last kline ~7/3 → chart red line extends to 7/10
- [x] 4.2 Manual: backtest mode still ends at last historical bar
