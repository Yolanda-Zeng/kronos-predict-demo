## 1. Parameter help content

- [x] 1.1 Create `frontend/src/content/paramHelp.ts` with tune grid help, predict advanced help, playbook sections, three preset definitions, and `metricHelp` for MAE/RMSE/MAPE
- [x] 1.2 Add `estimateTuneWorkload()` to compute combination count and approximate duration from grid inputs

## 2. Shared UI components

- [x] 2.1 Create `ParamHelpField` component (label, input, expandable help text)
- [x] 2.2 Create `TuneGuidePanel` accordion component for debugging playbook
- [x] 2.3 Create `TunePresetPicker` for quick / standard / thorough presets

- [x] 2.4 Create or enhance `MetricCards` to show metric full names, interpretations, and expandable help from `metricHelp`

## 3. Tune tab enhancements

- [x] 3.1 Refactor `TunePage` to use `ParamHelpField` for all grid fields
- [x] 3.2 Add workload estimate banner (combos + time hint) above submit button
- [x] 3.3 Integrate `TuneGuidePanel` in results column layout
- [x] 3.4 Localize results table headers, add metric header help for MAE/RMSE/MAPE, and highlight best row by RMSE
- [x] 3.5 Wire preset picker to populate grid and stride fields

## 4. Predict tab metrics and parity

- [x] 4.1 Wire enhanced metric cards on Predict page with glossary text and backtest context note
- [x] 4.2 Add help affordances to `ParamForm` advanced fields using `predictParamHelp`
- [x] 4.3 Add tune results CSV download button when job result includes `csv_path`

## 5. Documentation

- [x] 5.1 Update README 调参 section to mention Web Tune tab inline guidance
- [x] 5.2 Verify help text aligns with README best practices and error metrics table (MAE/RMSE/MAPE)

## 6. Verification

- [x] 6.1 Manually verify preset switching updates all grid fields correctly
- [x] 6.2 Manually verify combination count matches manual calculation for sample grids
- [x] 6.3 Manually verify playbook and field help render on desktop and mobile widths
- [x] 6.4 Manually verify Predict backtest shows metric cards with Chinese explanations; future mode hides them
