# prediction-web-ui

Web dashboard for configuring Kronos predictions, viewing charts, browsing history, and running tune jobs.

## Requirements

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
- **THEN** UI explains that predictions extend for horizon trading days after the last K-line through the selected end date

### Requirement: Shared parameter help on Predict tab

The Predict tab advanced section SHALL reuse the same parameter help content pattern as the Tune tab for window, horizon, seed, temperature, top_p, and sample_count.

#### Scenario: Advanced predict parameter help

- **WHEN** user expands advanced parameters on the Predict tab
- **THEN** each advanced field shows a concise Chinese explanation accessible via help affordance

### Requirement: Submit prediction and show job progress

The web UI SHALL submit prediction requests to the API and display asynchronous job progress until completion or failure.

#### Scenario: Start prediction

- **WHEN** user clicks the primary predict action with valid form values
- **THEN** UI disables duplicate submission, shows a progress indicator, and polls job status until done

#### Scenario: Prediction failure

- **WHEN** the job returns `status: "failed"`
- **THEN** UI displays the error message in a visible alert without clearing the form

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

### Requirement: Metrics summary cards

The web UI SHALL display MAE, RMSE, and MAPE metric cards with prominent numeric values and a single concise explanation line when the API returns backtest metrics.

#### Scenario: Metrics available

- **WHEN** backtest metrics are present in the job result
- **THEN** UI shows three labeled cards with formatted numeric values as the primary visual element and one short Chinese subtitle per metric

#### Scenario: Metric detail on demand

- **WHEN** user activates help on a metric card
- **THEN** UI displays extended reading guidance from the metric glossary without removing the metric cards or numeric values from view

#### Scenario: Future mode without metrics

- **WHEN** no metrics are returned
- **THEN** metric cards are hidden or show a neutral empty state

### Requirement: Result table and downloads

The web UI SHALL show a tabular preview of prediction rows and provide download actions for CSV and PNG when available.

#### Scenario: Download CSV

- **WHEN** user clicks download CSV on a completed result
- **THEN** browser downloads the prediction CSV file

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

### Requirement: Tune tab with result apply

The web UI SHALL provide a Tune tab for grid-search jobs with progress display, tuning context summary, visual results, parameter guidance, and ability to apply best parameters to the Predict form.

#### Scenario: Submit tune job

- **WHEN** user configures grid parameters and starts tuning
- **THEN** UI shows long-running progress and displays ranked results with chart and table when complete

#### Scenario: Apply best parameters

- **WHEN** user clicks apply on the best tune result
- **THEN** Predict form fields update to the best window, temperature, top_p, and sample_count values

#### Scenario: Tune guidance available before submit

- **WHEN** user is configuring a tune job
- **THEN** parameter help and debugging playbook are visible without leaving the Tune tab

#### Scenario: Tune context visible

- **WHEN** user is on the Tune tab
- **THEN** UI displays the current instrument, data source, and date range from the shared prediction form

### Requirement: Dark financial terminal visual theme

The web UI SHALL use a dark theme with consistent design tokens, Chinese-friendly typography, and tabular numeric formatting.

#### Scenario: Default appearance

- **WHEN** user loads the application
- **THEN** page uses dark background surfaces, readable contrast, and system Chinese fonts without requiring user theme configuration

### Requirement: Responsive layout

The web UI SHALL use a sidebar parameter panel on wide screens and a stacked layout on narrow screens.

#### Scenario: Desktop layout

- **WHEN** viewport width is at least 1024px
- **THEN** parameter form appears in a left sidebar and results occupy the main content area

#### Scenario: Mobile layout

- **WHEN** viewport width is below 1024px
- **THEN** parameter form stacks above the results area and remains usable without horizontal scrolling for core fields
