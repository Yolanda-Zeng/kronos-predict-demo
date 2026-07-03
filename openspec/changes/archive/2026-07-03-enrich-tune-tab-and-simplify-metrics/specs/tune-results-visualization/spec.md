## ADDED Requirements

### Requirement: Tune results MAPE chart

The Tune tab SHALL display a bar chart comparing MAPE across the top parameter combinations when tune results are available.

#### Scenario: Chart after successful tune

- **WHEN** a tune job completes with at least one result row
- **THEN** UI shows a bar chart of up to ten combinations sorted by MAPE ascending with MAPE percentage on the vertical axis

#### Scenario: No results yet

- **WHEN** no tune results are loaded
- **THEN** the MAPE chart is not rendered

### Requirement: Sortable tune results table

The Tune tab results table SHALL support client-side sorting by metric and parameter columns.

#### Scenario: Default MAPE sort

- **WHEN** tune results are first displayed
- **THEN** rows are sorted by MAPE ascending by default

#### Scenario: Column header sort toggle

- **WHEN** user clicks a sortable column header
- **THEN** rows reorder by that column and the sort direction toggles between ascending and descending

### Requirement: Tune tab empty state

The Tune tab SHALL show an onboarding empty state in the results area before the user has tune output.

#### Scenario: No tune job results

- **WHEN** user opens the Tune tab and no results are present
- **THEN** UI shows guidance to choose a preset, review workload estimate, and start tuning instead of a blank results panel
