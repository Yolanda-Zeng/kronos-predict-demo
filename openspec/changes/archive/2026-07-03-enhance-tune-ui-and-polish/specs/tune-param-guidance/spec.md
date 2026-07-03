## ADDED Requirements

### Requirement: Tune parameter field help

The Tune tab SHALL display Chinese labels and inline help for each grid parameter (`grid_window`, `grid_temp`, `grid_top_p`, `grid_sample_count`, `tune_stride`, `tune_max_windows`), including meaning, recommended value range, and impact on accuracy or runtime.

#### Scenario: User views grid_window help

- **WHEN** user focuses or expands help for `grid_window`
- **THEN** UI shows that it is the candidate lookback window list, suggests values like 64/128/256, and notes it has the largest effect on prediction quality

#### Scenario: User views tune_stride help

- **WHEN** user expands help for `tune_stride`
- **THEN** UI explains it controls rolling backtest step size and that smaller values increase accuracy evaluation density but increase runtime

### Requirement: Tune debugging playbook

The Tune tab SHALL provide a collapsible debugging guide covering recommended tuning order, how to read MAE/RMSE/MAPE, and common failure troubleshooting.

#### Scenario: Playbook visible on Tune tab

- **WHEN** user opens the Tune tab
- **THEN** UI shows a guide panel with at least three sections: recommended tuning workflow, metric interpretation, and troubleshooting

#### Scenario: Metric interpretation guidance

- **WHEN** user expands the metric interpretation section
- **THEN** UI states that MAPE is preferred for cross-stock comparison and lower is better

### Requirement: Tune preset profiles

The Tune tab SHALL offer preset profiles that populate grid and stride fields in one action.

#### Scenario: Apply quick preset

- **WHEN** user selects the quick preset
- **THEN** grid fields update to a smaller search space suitable for a fast trial run

#### Scenario: Apply standard preset

- **WHEN** user selects the standard preset
- **THEN** grid fields match CLI default grid values documented in README

### Requirement: Tune workload estimate before submit

The Tune tab SHALL display the number of parameter combinations and an approximate runtime hint before starting a tune job.

#### Scenario: Combination count updates

- **WHEN** user edits any grid field
- **THEN** UI recalculates and displays the total combination count

#### Scenario: Runtime hint shown

- **WHEN** combination count is greater than zero
- **THEN** UI displays an approximate duration range labeled as an estimate

### Requirement: Tune results readability

The Tune tab SHALL present ranked results with localized column headers and a visible marker on the best row.

#### Scenario: Best row highlighted

- **WHEN** tune results are displayed
- **THEN** the row with lowest RMSE is marked as best

#### Scenario: Localized headers

- **WHEN** results table renders
- **THEN** column headers use Chinese labels or Chinese plus English abbreviations
