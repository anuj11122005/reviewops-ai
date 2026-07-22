# Engineering Rules — ReviewOps AI

These are binding conventions for anyone (human or AI) contributing code to this project. Follow them unless a documented exception exists.

## 1. General Principles

- Modular architecture always. No tightly coupled code between agents.
- Each agent has exactly one responsibility. If an agent starts doing two things, split it.
- Agents never call Hugging Face or any model provider directly — always go through the **Model Gateway**.
- Static analysis results are never overridden by ML/LLM output — they are merged, not replaced.
- Every prediction must ship with an explanation. No agent returns a bare score/label without the Explainability Agent processing it first.
- Prefer boring, well-understood solutions over clever ones. This is a production-style system, not a research prototype.

## 2. What To Do

- Write type-annotated Python (Python 3.12) everywhere. Use Pydantic models for all API request/response schemas.
- Validate all external input (GitHub webhook payloads, uploaded files) before it touches any agent.
- Use dependency injection (FastAPI `Depends`) for DB sessions, config, and shared clients — don't instantiate them inline.
- Version every dataset with DVC and every experiment with MLflow before it's considered "real."
- Write a migration (Alembic) for every schema change. Never hand-edit the production schema.
- Log structured events (JSON logs) for every agent step: start, input summary, output summary, duration, errors.
- Write unit tests for every agent and every static-analysis wrapper before merging.
- Keep secrets in environment variables (`.env`, not committed) and load them through `core/config.py`.
- Cache expensive/deterministic model calls in the Model Gateway (Redis-backed).
- Document every new module with a short docstring header explaining its responsibility.
- Use feature branches + meaningful commit messages tied to the feature lifecycle (understand → design → implement → test → document → commit).
- Use `uv` (not `pip`) for dependency installation in all Dockerfiles — it provides faster resolution, better caching, and more reliable wheel negotiation.

## 3. What To Avoid

- Do not let any agent talk directly to another agent's internals — communication goes through the orchestrator's shared state object.
- Do not hardcode model names, API keys, or endpoints — route through config and the Model Gateway.
- Do not use `print()` for anything — use the logging module.
- Do not swallow exceptions silently (`except: pass`). Every caught exception is logged with context and either re-raised or explicitly handled.
- Do not put business logic in API route handlers — routes call services/agents, they don't contain logic themselves.
- Do not bypass the Validation Agent for "trusted" input. All PR data is treated as untrusted.
- Do not commit datasets, model binaries, or `.env` files to Git — use DVC/MinIO and `.gitignore`.
- Do not introduce a new library without checking the approved list below first.
- Do not deploy a retrained model directly to production — it must pass canary evaluation against the baseline first.
- Do not skip tests "temporarily." If a test is broken, fix or explicitly skip with a tracked reason.

## 4. Approved Libraries

| Purpose | Library |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Orchestration | LangGraph |
| Classical ML | Scikit-learn (RandomForestClassifier is used for bug prediction; XGBoost/LightGBM removed as unnecessary) |
| LLM / embeddings | HTTP Inference API (local Hugging Face Transformers removed as API calls are used) |
| Experiment tracking | MLflow |
| Dataset versioning | DVC |
| Vector store | Qdrant |
| Cache | Redis |
| Object storage | MinIO |
| Static analysis (Python) | Bandit, Pylint |
| Static analysis (JS/TS) | ESLint |
| Static analysis (multi-lang, semantic rules) | Semgrep |
| Code parsing | Tree-sitter |
| ML monitoring / drift | Evidently AI |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Frontend framework | Next.js + TypeScript |
| Styling | Tailwind CSS + Shadcn UI |
| Frontend data fetching | React Query |
| Frontend animation | Framer Motion |
| Code formatting/linting (backend) | Black, Ruff, isort, mypy |
| CI/CD | GitHub Actions |
| Containerization | Docker, Docker Compose |
| Package installation (Dockerfiles) | `uv` (replaces pip for speed and reliability) |
| S3/artifact upload | boto3 (required by mlflow for MinIO artifact storage) |

Do not introduce a competing library for something already on this list (e.g., no Poetry-vs-pip debates mid-project, no swapping XGBoost for CatBoost without a documented reason) without updating this file first.

### Dependency Pins

| Pin | Reason |
|---|---|
| `setuptools<78` (ml-pipeline) | mlflow 2.14.3 imports `pkg_resources`, removed from setuptools ≥78 |
| `mlflow-skinny==2.14.3` (backend) | Lightweight MLflow client — avoids pulling scipy/sklearn into the backend |
| `mlflow==2.14.3` (ml-pipeline) | Full MLflow with model logging, artifact upload, and UI support |

## 5. Error Handling

- **API layer**: all exceptions are caught by a global FastAPI exception handler and converted into a consistent JSON error shape (`{"error": {"code": ..., "message": ..., "details": ...}}`). Never leak raw stack traces to API responses.
- **Agent layer**: each agent wraps its core logic in a try/except that logs the failure with the agent name, PR id, and input hash, then re-raises a typed exception (e.g., `AgentExecutionError`) so the orchestrator can decide whether to retry, skip, or fail the whole pipeline.
- **Model Gateway**: on a model call failure, attempt the configured fallback model once; if that also fails, return a structured "unavailable" result rather than raising — downstream agents must handle partial results gracefully (e.g., Review Agent posts a comment noting a section couldn't be analyzed).
- **Static analysis tools**: a single tool crashing (e.g., ESLint config missing) must not abort the pipeline — log and continue with the remaining tools' results.
- **Database**: use transactions for multi-step writes; roll back fully on failure. Never leave partial review records.
- **Retraining/Deployment**: any failure during canary evaluation blocks promotion to production automatically — there is no manual override path that skips validation.
- **Retries**: use exponential backoff for transient failures (network calls to GitHub API, Hugging Face API, DB connection blips). Cap retries (max 3) and then fail loud.
- **User-facing errors** (dashboard): show a clear, non-technical message plus a correlation/request ID for support/debugging.

## 6. Code Quality Gates (CI)

Every PR to this repo must pass, via GitHub Actions:
1. Black + Ruff + isort formatting checks.
2. mypy type checking.
3. Unit tests (backend).
4. ESLint + TypeScript checks (frontend).
5. No secrets detected in diff.

Merges are blocked if any gate fails.

## Agent Limitations
- **BugPredictionAgent**: The current heuristic relies purely on LOC, cyclomatic complexity, and comment density, which is blind to actual security flaws or code content. Consider feeding the static analysis findings count (e.g. Bandit/Pylint findings) as an input feature to the bug probability heuristic so files with real findings score higher.
