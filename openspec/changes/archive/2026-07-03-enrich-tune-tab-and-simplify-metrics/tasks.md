## 1. Simplify metric cards (Predict Tab)

- [x] 1.1 Refactor `MetricCards` to number-first layout: large value, single subtitle line, optional `?` for full tip
- [x] 1.2 Add section heading「回测误差指标」with one-line MAPE priority hint above cards
- [x] 1.3 Keep all three metrics visible in backtest mode; verify future mode still hides cards

## 2. Tune context and empty state

- [x] 2.1 Create `TuneContextBanner` showing instrument, data source, and date range from shared form
- [x] 2.2 Create `TuneEmptyState` onboarding card for results column when no tune output exists
- [x] 2.3 Integrate banner and empty state into `TunePage` layout

## 3. Tune results visualization

- [x] 3.1 Create `TuneResultsChart` ECharts bar chart for Top 10 MAPE combinations
- [x] 3.2 Add client-side table sorting with default MAPE ascending; clickable column headers
- [x] 3.3 Wire chart + sorted table into TunePage results flow; preserve best-row highlight and CSV download

## 4. Verification

- [x] 4.1 Build frontend and confirm Predict metrics show large numbers with brief subtitles
- [x] 4.2 Confirm Tune tab shows context banner, empty state, chart, and sortable table after mock or real tune run
