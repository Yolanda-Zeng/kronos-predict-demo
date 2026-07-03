# future-chart-viewport

Future-mode chart viewport, markers, and prediction range labels.

## Requirements

### Requirement: Future mode chart viewport

The web UI SHALL default the prediction chart viewport to include all future predicted timestamps when the result mode is future prediction.

#### Scenario: Future prediction visible on load

- **WHEN** user completes a future-mode prediction with horizon greater than zero
- **THEN** chart initial zoom includes the full predicted date range beyond the last known K-line timestamp

#### Scenario: Last known K-line marker

- **WHEN** future-mode chart is displayed
- **THEN** UI marks the last known historical K-line timestamp and shows prediction interval dates pred_start through pred_end
