## ADDED Requirements

### Requirement: Health check endpoint

The API SHALL expose `GET /api/health` returning service status and whether the Kronos model is loaded.

#### Scenario: Service is running

- **WHEN** client sends `GET /api/health`
- **THEN** response status is 200 with JSON body containing `status: "ok"`

### Requirement: Submit async prediction job

The API SHALL accept `POST /api/jobs/predict` with prediction parameters equivalent to the CLI script and return a `job_id` immediately without blocking until inference completes.

#### Scenario: Valid predict request

- **WHEN** client submits required fields (instrument, start, end, data_source, model_path, tokenizer_path) with optional prediction parameters
- **THEN** response status is 202 with JSON body containing a unique `job_id` and `status: "queued"`

#### Scenario: Missing required field

- **WHEN** client omits a required field such as `instrument`
- **THEN** response status is 422 with validation error details

#### Scenario: Qlib source without provider URI

- **WHEN** client sets `data_source` to `qlib` and omits `provider_uri`
- **THEN** response status is 422 with an error indicating `provider_uri` is required

### Requirement: Poll job status and retrieve results

The API SHALL expose `GET /api/jobs/{job_id}` returning job status, progress message, and result payload when complete.

#### Scenario: Job in progress

- **WHEN** client polls a job that is still running
- **THEN** response includes `status` in (`queued`, `loading_model`, `fetching_data`, `predicting`) and optional `message`

#### Scenario: Job completed successfully

- **WHEN** client polls a completed prediction job
- **THEN** response includes `status: "done"` and `result` containing chart series data, metrics (if backtest mode), output file paths, and prediction rows

#### Scenario: Job failed

- **WHEN** prediction fails due to data fetch or model error
- **THEN** response includes `status: "failed"` and `error` with a human-readable message

#### Scenario: Unknown job id

- **WHEN** client requests a non-existent `job_id`
- **THEN** response status is 404

### Requirement: Submit async tune job

The API SHALL accept `POST /api/jobs/tune` with grid-search parameters equivalent to CLI `--tune` mode and return a `job_id`.

#### Scenario: Valid tune request

- **WHEN** client submits tune parameters including grid values and tune stride settings
- **THEN** response status is 202 with a unique `job_id`

### Requirement: List historical prediction outputs

The API SHALL expose `GET /api/predictions` listing prior outputs found under the configured predictions directory.

#### Scenario: Predictions exist

- **WHEN** client requests the predictions list
- **THEN** response includes entries with instrument, date range, run timestamp, file paths, and parsed metrics when available

#### Scenario: Empty predictions directory

- **WHEN** no prediction files exist
- **THEN** response returns an empty list with status 200

### Requirement: Download result files

The API SHALL expose endpoints to download CSV and optional PNG artifacts for a completed job or historical entry.

#### Scenario: Download CSV

- **WHEN** client requests CSV for a valid result path
- **THEN** response returns the file with `Content-Type: text/csv`

#### Scenario: Invalid file path

- **WHEN** client requests a path outside the predictions directory
- **THEN** response status is 403 or 404

### Requirement: Shared prediction core with CLI

The API MUST invoke the same Python prediction functions used by `kronos_qlib_predict.py`, not a reimplemented copy of the logic.

#### Scenario: Equivalent parameters produce equivalent output

- **WHEN** the same instrument, date range, seed, and model parameters are used via CLI and via API
- **THEN** the predicted close prices in the output CSV match within floating-point tolerance
