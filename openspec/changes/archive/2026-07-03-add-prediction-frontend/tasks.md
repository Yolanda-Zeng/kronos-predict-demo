## 1. Extract shared prediction core

- [x] 1.1 Create `kronos_core/` package with data loading, predict, tune, metrics, and chart helpers extracted from `kronos_qlib_predict.py`
- [x] 1.2 Refactor `kronos_qlib_predict.py` CLI to import from `kronos_core` without changing CLI flags or behavior
- [x] 1.3 Add a regression check: same seed/parameters via CLI produce identical CSV output before and after refactor

## 2. Backend API foundation

- [x] 2.1 Create `backend/` with FastAPI app, CORS, and `GET /api/health`
- [x] 2.2 Define Pydantic schemas mirroring CLI parameters for predict and tune requests
- [x] 2.3 Implement in-memory job store with statuses (`queued` → `done`/`failed`) and progress messages
- [x] 2.4 Implement lazy-loaded Kronos model singleton shared across jobs

## 3. Prediction and tune job endpoints

- [x] 3.1 Implement `POST /api/jobs/predict` running prediction in background and returning structured chart series + metrics
- [x] 3.2 Implement `GET /api/jobs/{job_id}` with 404 for unknown jobs
- [x] 3.3 Implement `POST /api/jobs/tune` and include ranked grid-search results in completed job payload
- [x] 3.4 Implement `GET /api/predictions` scanning the predictions directory with parsed metadata
- [x] 3.5 Implement secure file download endpoints for CSV and PNG artifacts

## 4. Frontend scaffold and design system

- [x] 4.1 Scaffold Vite + React + TypeScript app under `frontend/` with Tailwind and shadcn/ui
- [x] 4.2 Apply dark financial terminal theme tokens (colors, typography, tabular nums)
- [x] 4.3 Add app shell with top navigation tabs: Predict, History, Tune
- [x] 4.4 Configure dev proxy from frontend to FastAPI backend

## 5. Predict tab

- [x] 5.1 Build grouped parameter form (basic / model paths / advanced collapsible)
- [x] 5.2 Add data-source contextual hints for akshare, hkshare, usstock, and qlib
- [x] 5.3 Implement job submit, polling, progress UI, and error alerts
- [x] 5.4 Build ECharts panel for history / predicted / actual close series with zoom
- [x] 5.5 Build MAE / RMSE / MAPE metric cards and prediction data table
- [x] 5.6 Add CSV and PNG download actions for completed jobs

## 6. History tab

- [x] 6.1 Build history list view consuming `GET /api/predictions`
- [x] 6.2 Implement click-to-open historical result in chart and metrics view

## 7. Tune tab

- [x] 7.1 Build tune parameter form for grid values and stride settings
- [x] 7.2 Show long-running tune progress and ranked results table
- [x] 7.3 Implement "apply best parameters" action that prefills the Predict form

## 8. Production serving and documentation

- [x] 8.1 Serve built frontend static assets from FastAPI for single-command deployment
- [x] 8.2 Update README with Web UI setup, dev workflow, and note that CLI remains supported
- [x] 8.3 Add optional `docker-compose.yml` or startup script for backend + frontend build

## 9. Verification

- [x] 9.1 Manually verify Predict flow end-to-end for akshare backtest mode with metrics
- [x] 9.2 Manually verify `--future` equivalent mode hides metrics and actual series
- [x] 9.3 Verify responsive layout at desktop and mobile widths
