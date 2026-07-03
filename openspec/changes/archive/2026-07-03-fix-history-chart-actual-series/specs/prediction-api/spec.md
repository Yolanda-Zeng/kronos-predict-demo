## MODIFIED Requirements

### Requirement: List historical prediction outputs

The API SHALL expose `GET /api/predictions` listing prior outputs found under the configured predictions directory.

#### Scenario: Predictions exist

- **WHEN** client requests the predictions list
- **THEN** response includes entries with instrument, date range, run timestamp, file paths, parsed metrics when available, and full chart series when a metadata sidecar exists

#### Scenario: Legacy prediction without sidecar

- **WHEN** a prediction CSV exists without a metadata sidecar
- **THEN** response includes predicted series only and indicates the chart is incomplete for history replay

#### Scenario: Empty predictions directory

- **WHEN** no prediction files exist
- **THEN** response returns an empty list with status 200
