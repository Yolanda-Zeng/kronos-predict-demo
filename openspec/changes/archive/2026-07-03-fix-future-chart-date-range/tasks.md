## 1. Mode hints and types

- [x] 1.1 Add backtest vs future date-semantics hints under prediction mode radios in `ParamForm`
- [x] 1.2 Pass `mode`, `predStart`, `predEnd` from `PredictPage` to `ChartPanel`

## 2. ChartPanel future viewport

- [x] 2.1 Extend `ChartPanel` with optional mode and prediction range props
- [x] 2.2 Implement future-mode default `dataZoom` focusing on last history segment plus full prediction range
- [x] 2.3 Add markLine at last known K-line and update title/subtitle for future vs backtest

## 3. Backend guard and tests

- [x] 3.1 Add unit test that `make_future_timestamps` returns dates strictly after last_ts
- [x] 3.2 Add test or assert that future-mode `build_chart_series` predicted max timestamp exceeds history max timestamp

## 4. Verification

- [x] 4.1 Manual: future mode horizon=5 shows X-axis extending beyond end date with visible red prediction segment
- [x] 4.2 Manual: backtest mode confirms chart ends at selected end date with hint text visible
