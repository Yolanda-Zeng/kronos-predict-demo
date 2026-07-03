## 1. Persist chart metadata on predict

- [x] 1.1 Add `save_run_metadata()` in `kronos_core/history.py` writing `{name}_meta.json` with version, mode, metrics, chart
- [x] 1.2 Call metadata save from `execute_predict` after CSV and PNG are written
- [x] 1.3 Add unit-style sanity check or manual script note for sidecar schema

## 2. Load full chart in history API

- [x] 2.1 Update `list_predictions` to load sidecar when present and set `chart_complete: true`
- [x] 2.2 Fallback to CSV-only predicted series with `chart_complete: false` and `metrics: null`
- [x] 2.3 Expose `chart_complete` in API response (no breaking change to existing fields)

## 3. Fix History tab frontend

- [x] 3.1 Extend `HistoryItem` type with `chart_complete` and full `ChartData` shape
- [x] 3.2 Refactor `HistoryPage.openItem` to use API chart data without stripping actual/history
- [x] 3.3 Show legacy notice banner when `chart_complete` is false; show metrics when available

## 4. Verification

- [x] 4.1 Run a new backtest predict, confirm `_meta.json` exists beside CSV
- [x] 4.2 Open same run in History tab and verify three chart series render
- [x] 4.3 Confirm legacy CSV-only entry shows predicted line plus incomplete notice
