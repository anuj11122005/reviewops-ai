# Project Phases — ReviewOps AI

The project is built incrementally across four major phases (versions). Each phase must be functionally complete and stable before starting the next — no phase depends on unfinished work from a later phase.

---

## Phase 1 — Platform Foundation

**Goal:** Get a working skeleton end-to-end, with no AI yet.

- Set up monorepo structure (`backend/`, `frontend/`, `infra/`, `docs/`).
- FastAPI backend scaffold with health check, config, logging.
- PostgreSQL database + initial schema: users, repositories, pull requests.
- Alembic migrations set up.
- GitHub App/webhook integration: receive and store PR-opened events.
- Docker Compose environment (backend + Postgres + Redis).
- Next.js frontend scaffold with Tailwind + Shadcn UI.
- Basic dashboard: list connected repositories, list received PRs.
- GitHub Actions CI: lint + test on push.

**Exit criteria:** Opening a PR on a connected repo creates a visible record in the dashboard, with zero AI involved yet.

---

## Phase 2 — Static Analysis, Embeddings & First AI Review

**Goal:** Produce a real (if simple) AI-assisted review.

- Data Agent: download PR files + metadata.
- Validation Agent: file integrity, language support checks.
- Feature Engineering Agent: complexity, nesting depth, comment ratio, etc.
- Integrate static analysis tools: Semgrep, Bandit, Pylint, ESLint.
- Embedding Agent + Qdrant integration for semantic similarity.
- Hugging Face integration via the Model Gateway (routing, caching, fallback).
- Bug Prediction Agent (first ML model, can be simple baseline).
- Review Agent: compile static + ML findings into a review comment posted to GitHub.
- Dashboard: show live AI review results per PR.

**Exit criteria:** A PR receives an automated review comment on GitHub combining static analysis and a first-pass ML/LLM assessment.

---

## Phase 3 — Multi-Agent Orchestration & MLOps Core

**Goal:** Turn the single-pass reviewer into a coordinated, self-monitoring multi-agent system.

- Introduce LangGraph orchestrator to coordinate all agents via shared state.
- Security Agent (SQLi, XSS, hardcoded secrets, insecure APIs, dangerous calls).
- Explainability Agent: plain-language reasoning for every prediction.
- Feedback Agent: capture accepted/rejected suggestions.
- MLflow integration: experiment tracking for all model training runs.
- DVC integration: dataset versioning.
- Monitoring Agent: latency, throughput, prediction quality metrics → Prometheus.
- Grafana dashboards for operational metrics.
- Evidently AI integration: data drift + concept drift detection.
- Retraining Agent: automatically triggered pipeline when drift/degradation is detected.
- Model Registry: candidate models evaluated against production baseline before promotion.

**Exit criteria:** The system detects a drop in prediction quality or drift, automatically retrains, and registers a new candidate model — without manual intervention.

---

## Phase 4 — Advanced Capabilities & Production Hardening

**Goal:** Reach feature-complete, production-quality platform status.

- Documentation Agent: function docs, PR summaries, release notes.
- Test Generation Agent: proposed unit tests for new functionality.
- Reviewer Recommendation Agent: suggest human reviewer from repo history.
- Deployment Agent: canary deployment + rollback support for models.
- Full dashboard: agent status, model registry visualization, feedback analytics, security alerts, drift reports, deployment history, system configuration.
- Performance/security hardening pass across backend and frontend.
- Kubernetes support (exploratory/future-facing, not required for v1 production).
- Full documentation pass (README, architecture, API docs).

**Exit criteria:** ReviewOps AI operates as a complete, self-improving AI engineering teammate — reviewing, explaining, documenting, testing, recommending, monitoring, and retraining — matching the vision in `prd.md`.

---

## Cross-Phase Rules

- No phase begins until the previous phase's exit criteria are met and demoable.
- Each phase ends with a documentation update (`architecture.md`, `rules.md` as needed) reflecting what was actually built.
- Each phase must maintain the CI quality gates defined in `rules.md` — they are never relaxed to "move faster."
