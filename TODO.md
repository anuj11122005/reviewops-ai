# Outstanding Tasks & Technical Debt

## Frontend (React Query Migration)
- The `repositories/page.tsx` was successfully migrated to use React Query.
- The remaining pages still need to be migrated to React Query to ensure consistent data fetching and caching:
  - `pull-requests/page.tsx`
  - `pull-requests/[id]/page.tsx`
  - `monitoring/page.tsx`
  - `models/page.tsx`

## Phase 3 Gaps (Feedback Agent)
- The `feedback/page.tsx` currently runs on hardcoded mock data, not real Feedback Agent output. This is a critical gap for Phase 3's "continuous learning" core loop. This needs to be wired up to the actual Feedback Agent output.

## Dependency Management Notes
- When building the Python backend, the default `pip` resolver has a known bug/limitation when simultaneously resolving `mlflow`, `langgraph`, and `langchain-core` on Python 3.12-slim (resulting in spurious `docker` availability errors or `ResolutionImpossible`). 
- **Solution:** The `backend/Dockerfile` now uses `uv pip install` instead of standard `pip` to bypass this completely. Maintain this approach if adding new complex dependencies.
