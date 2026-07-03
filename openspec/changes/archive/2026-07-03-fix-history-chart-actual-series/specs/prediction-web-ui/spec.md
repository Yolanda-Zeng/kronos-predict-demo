## MODIFIED Requirements

### Requirement: History tab

The web UI SHALL provide a History tab listing past predictions with ability to reopen a result in the chart view.

#### Scenario: Browse history

- **WHEN** user opens the History tab
- **THEN** UI lists prior runs sorted by recency with instrument, prediction date range, and MAPE when known

#### Scenario: Open historical result

- **WHEN** user selects a history entry
- **THEN** UI loads and displays that run's chart and metadata in the result area

#### Scenario: Backtest history shows actual series

- **WHEN** user opens a historical backtest entry with complete chart metadata
- **THEN** chart shows history, predicted, and actual close price series matching the Predict tab backtest view

#### Scenario: Legacy entry missing actual series

- **WHEN** user opens a historical entry without complete chart metadata
- **THEN** UI shows available series and displays a notice that full ground-truth comparison requires re-running the prediction
