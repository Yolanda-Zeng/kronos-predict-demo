## MODIFIED Requirements

### Requirement: Interactive prediction chart

The web UI SHALL render an interactive chart comparing historical, predicted, and actual close prices when data is available.

#### Scenario: Backtest result display

- **WHEN** a completed job includes ground-truth comparison data
- **THEN** chart shows three series with colors matching design tokens (history blue, prediction red dashed, actual green) and supports zoom/pan

#### Scenario: Future-only prediction

- **WHEN** a completed job has no ground-truth data
- **THEN** chart shows history and prediction series only, without an actual series, and the time axis includes predicted future timestamps beyond the last historical bar

#### Scenario: Future chart title and range label

- **WHEN** a completed future-mode job is displayed
- **THEN** chart title or subtitle states the prediction date range through pred_end
