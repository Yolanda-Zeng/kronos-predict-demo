## MODIFIED Requirements

### Requirement: Metrics summary cards

The web UI SHALL display MAE, RMSE, and MAPE metric cards with prominent numeric values and a single concise explanation line when the API returns backtest metrics.

#### Scenario: Metrics available

- **WHEN** backtest metrics are present in the job result
- **THEN** UI shows three labeled cards with formatted numeric values as the primary visual element and one short Chinese subtitle per metric

#### Scenario: Metric detail on demand

- **WHEN** user activates help on a metric card
- **THEN** UI displays extended reading guidance without removing the metric cards or numeric values from view

#### Scenario: Future mode without metrics

- **WHEN** no metrics are returned
- **THEN** metric cards are hidden or show a neutral empty state

### Requirement: Tune tab with result apply

The web UI SHALL provide a Tune tab for grid-search jobs with progress display, tuning context summary, visual results, and ability to apply best parameters to the Predict form.

#### Scenario: Submit tune job

- **WHEN** user configures grid parameters and starts tuning
- **THEN** UI shows long-running progress and displays ranked results with chart and table when complete

#### Scenario: Apply best parameters

- **WHEN** user clicks apply on the best tune result
- **THEN** Predict form fields update to the best window, temperature, top_p, and sample_count values

#### Scenario: Tune context visible

- **WHEN** user is on the Tune tab
- **THEN** UI displays the current instrument, data source, and date range from the shared prediction form
