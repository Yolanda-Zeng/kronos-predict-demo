# prediction-run-metadata

Sidecar JSON persistence for full chart replay on historical predictions.

## Requirements

### Requirement: Prediction run metadata sidecar

The prediction core SHALL persist a JSON sidecar alongside each prediction CSV containing chart series data, mode, and metrics when available.

#### Scenario: Backtest run writes full chart metadata

- **WHEN** a backtest prediction completes successfully
- **THEN** a sidecar JSON file is written next to the prediction CSV containing history, predicted, actual chart series and backtest metrics

#### Scenario: Future run writes partial chart metadata

- **WHEN** a future-mode prediction completes successfully
- **THEN** the sidecar JSON contains history and predicted series with null actual and null metrics

#### Scenario: Sidecar naming convention

- **WHEN** prediction CSV is saved as `{name}_predict.csv`
- **THEN** sidecar is saved as `{name}_meta.json` in the same directory
