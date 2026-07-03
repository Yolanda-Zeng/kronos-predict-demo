## ADDED Requirements

### Requirement: Shared parameter help on Predict tab

The Predict tab advanced section SHALL reuse the same parameter help content pattern as the Tune tab for window, horizon, seed, temperature, top_p, and sample_count.

#### Scenario: Advanced predict parameter help

- **WHEN** user expands advanced parameters on the Predict tab
- **THEN** each advanced field shows a concise Chinese explanation accessible via help affordance

## MODIFIED Requirements

### Requirement: Metrics summary cards

The web UI SHALL display MAE, RMSE, and MAPE metric cards with numeric values and Chinese explanations when the API returns backtest metrics.

#### Scenario: Metrics available

- **WHEN** backtest metrics are present in the job result
- **THEN** UI shows three labeled cards with formatted numeric values, Chinese full names, and one-line interpretations

#### Scenario: Metric help affordance

- **WHEN** user activates help on a metric card
- **THEN** UI displays extended reading guidance from the metric glossary

#### Scenario: Future mode without metrics

- **WHEN** no metrics are returned
- **THEN** metric cards are hidden or show a neutral empty state

### Requirement: Tune tab with result apply

The web UI SHALL provide a Tune tab for grid-search jobs with progress display, parameter guidance, and ability to apply best parameters to the Predict form.

#### Scenario: Submit tune job

- **WHEN** user configures grid parameters and starts tuning
- **THEN** UI shows long-running progress and displays ranked results when complete

#### Scenario: Apply best parameters

- **WHEN** user clicks apply on the best tune result
- **THEN** Predict form fields update to the best window, temperature, top_p, and sample_count values

#### Scenario: Tune guidance available before submit

- **WHEN** user is configuring a tune job
- **THEN** parameter help and debugging playbook are visible without leaving the Tune tab
