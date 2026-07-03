## MODIFIED Requirements

### Requirement: Prediction parameter form

The web UI SHALL provide a form covering CLI-equivalent parameters grouped into basic, model path, and advanced sections.

#### Scenario: Basic parameters visible by default

- **WHEN** user opens the Predict tab
- **THEN** form shows instrument, data source, date range, and mode toggle (backtest vs future)

#### Scenario: Advanced parameters collapsed

- **WHEN** user has not expanded the advanced section
- **THEN** window, horizon, seed, temperature, top_p, and sample_count are hidden behind an expandable control

#### Scenario: Data source contextual hint

- **WHEN** user selects `akshare` or `usstock` as data source
- **THEN** UI displays a hint about proxy/VPN requirements matching README guidance

#### Scenario: Backtest mode hint

- **WHEN** user selects historical backtest mode
- **THEN** UI explains that the chart ends at the selected end date and horizon is used for held-out comparison days

#### Scenario: Future mode hint

- **WHEN** user selects future prediction mode
- **THEN** UI explains that historical K-lines stop at the latest trading day, and when the selected end date is later than that day predictions extend through the end date; otherwise predictions use horizon trading days

#### Scenario: Future mode end date label

- **WHEN** user selects future prediction mode
- **THEN** the end date field label indicates it is the prediction-through date, not only a data fetch bound
