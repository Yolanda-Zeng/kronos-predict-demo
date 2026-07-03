## ADDED Requirements

### Requirement: Future mode chart viewport

The web UI SHALL default the prediction chart viewport to include all future predicted timestamps when the result mode is future prediction.

#### Scenario: Future prediction visible on load

- **WHEN** user completes a future-mode prediction with horizon greater than zero
- **THEN** chart initial zoom includes the full predicted date range beyond the last known K-line timestamp

#### Scenario: Last known K-line marker

- **WHEN** future-mode chart is displayed
- **THEN** UI marks the last known historical K-line timestamp and shows prediction interval dates pred_start through pred_end

### Requirement: Prediction mode date semantics hint

The Predict tab SHALL explain how the end date and horizon interact for backtest versus future modes.

#### Scenario: Backtest mode hint

- **WHEN** user selects historical backtest mode
- **THEN** UI explains that the chart ends at the selected end date and horizon is used for held-out comparison days

#### Scenario: Future mode hint

- **WHEN** user selects future prediction mode
- **THEN** UI explains that predictions extend for horizon trading days after the last K-line through the selected end date
