# metric-glossary

Chinese explanations for MAE, RMSE, and MAPE used across Predict and Tune tabs.

## Requirements

### Requirement: Metric glossary content

The web UI SHALL provide consistent Chinese explanations for MAE, RMSE, and MAPE aligned with README definitions, including full name, one-line summary, and reading guidance.

#### Scenario: MAE definition available

- **WHEN** metric help content is loaded
- **THEN** MAE is described as mean absolute error in yuan with note that cross-stock comparison is less reliable

#### Scenario: MAPE emphasized for comparison

- **WHEN** metric help content is loaded
- **THEN** MAPE is marked as the preferred metric for comparing stocks or parameter sets and lower is better

### Requirement: Predict tab metric card explanations

The Predict tab SHALL display metric cards with numeric values and visible explanations when backtest metrics are returned.

#### Scenario: Metrics with explanations

- **WHEN** a completed prediction job includes backtest metrics
- **THEN** UI shows MAE, RMSE, and MAPE cards each with Chinese full name and a concise interpretation line

#### Scenario: Expand metric detail

- **WHEN** user activates help on a metric card
- **THEN** UI shows the full reading tip from the glossary including MAPE reference threshold guidance where applicable

#### Scenario: Future mode hides metrics

- **WHEN** no backtest metrics are returned
- **THEN** metric cards and glossary remain hidden

### Requirement: Tune tab metric column help

The Tune tab results table SHALL expose the same metric glossary for MAE, RMSE, and MAPE column headers.

#### Scenario: Tune table header help

- **WHEN** tune results table is displayed
- **THEN** MAE, RMSE, and MAPE headers include access to the same glossary explanations as Predict metric cards
