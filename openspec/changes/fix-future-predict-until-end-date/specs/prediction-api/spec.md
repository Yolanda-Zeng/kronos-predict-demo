## MODIFIED Requirements

### Requirement: Poll job status and retrieve results

The API SHALL expose `GET /api/jobs/{job_id}` returning job status, progress message, and result payload when complete.

#### Scenario: Job in progress

- **WHEN** client polls a job that is still running
- **THEN** response includes `status` in (`queued`, `loading_model`, `fetching_data`, `predicting`) and optional `message`

#### Scenario: Job completed successfully

- **WHEN** client polls a completed prediction job
- **THEN** response includes `status: "done"` and `result` containing chart series data, metrics (if backtest mode), output file paths, prediction rows, and pred_start/pred_end matching the actual predicted timestamp range

#### Scenario: Job failed

- **WHEN** prediction fails due to data fetch or model error
- **THEN** response includes `status: "failed"` and `error` with a human-readable message

#### Scenario: Unknown job id

- **WHEN** client requests a non-existent `job_id`
- **THEN** response status is 404
