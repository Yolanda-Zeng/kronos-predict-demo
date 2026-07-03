## ADDED Requirements

### Requirement: Future prediction through end date

When future prediction mode is enabled and the configured end date is after the last historical K-line timestamp, the prediction core SHALL generate prediction timestamps for all business days from the day after the last K-line through the configured end date inclusive.

#### Scenario: End date beyond last K-line

- **WHEN** future mode is active, last K-line is 2026-07-03, and end date is 2026-07-10
- **THEN** prediction timestamps cover business days after 2026-07-03 through 2026-07-10 and pred_end reflects the last predicted trading day in that range

#### Scenario: End date not beyond last K-line

- **WHEN** future mode is active and end date is on or before the last K-line date
- **THEN** prediction timestamps fall back to horizon business days after the last K-line

#### Scenario: Maximum future span cap

- **WHEN** the business-day count from last K-line to end date exceeds the configured maximum
- **THEN** the system caps prediction length, logs a warning, and still returns a valid result

#### Scenario: Backtest mode unchanged

- **WHEN** future mode is not active
- **THEN** prediction timestamp generation behavior is unchanged from historical backtest logic
