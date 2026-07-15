# Architecture Document — ReviewOps AI

## 1. Architecture Style

**Modular Monolith** — one deployable FastAPI backend, internally split into clearly bounded modules/agents, rather than microservices. This reduces operational complexity early on while preserving clean seams for a future microservices split.

## 2. High-Level System Diagram (conceptual)

```
Developer → GitHub PR → GitHub Webhook
                              │
                              ▼
                    FastAPI API Gateway
                              │
                              ▼
                  LangGraph Orchestrator
                              │
        ┌─────────────┬───────┴───────┬─────────────┐
        ▼             ▼               ▼             ▼
   Data Agent   Validation Agent  Feature Eng.   Embedding Agent
                                    Agent
        │             │               │             │
        └─────────────┴───────┬───────┴─────────────┘
                              ▼
                     Review Agent (coordinator)
                              │
        ┌─────────────┬───────┼───────┬─────────────┬──────────────┐
        ▼             ▼       ▼       ▼             ▼              ▼
   Bug Prediction  Security  Explain- Documentation  Test Gen   Reviewer Rec.
      Agent         Agent   ability     Agent         Agent       Agent
                              Agent
                              │
                              ▼
                    Model Gateway (routing/caching/fallback)
                              │
                              ▼
                     Hugging Face Models + Static Analysis Tools
                              │
                              ▼
              PostgreSQL / Redis / Qdrant / MLflow / MinIO
                              │
                              ▼
                   GitHub Review Comment Posted Back
                              │
                              ▼
                     Feedback Agent (stores accept/reject)
                              │
                              ▼
        Monitoring Agent → Drift Detection → Retraining Agent → Deployment Agent
```

## 3. App Flow (End-to-End)

1. Developer opens/updates a GitHub PR.
2. GitHub sends a webhook event to the FastAPI backend.
3. Backend validates and forwards the event to the LangGraph Orchestrator.
4. **Data Agent** downloads modified files + commit/PR metadata.
5. **Validation Agent** checks file integrity, supported languages, duplicates, corruption.
6. **Feature Engineering Agent** computes code metrics (complexity, nesting, comment ratio, etc.).
7. **Embedding Agent** generates vector representations, stored in Qdrant.
8. Static analysis tools (Semgrep, Bandit, Pylint, ESLint) run in parallel for deterministic checks.
9. **Bug Prediction**, **Security**, and other ML/LLM agents run through the **Model Gateway**, which routes requests to the correct Hugging Face model, applies caching, and handles fallback.
10. **Explainability Agent** converts raw scores/predictions into plain-language reasoning.
11. **Review Agent** compiles everything into review comments and a PR summary, then posts them to GitHub via the GitHub API.
12. **Documentation Agent** and **Test Generation Agent** produce supplementary docs/tests if applicable.
13. **Reviewer Recommendation Agent** suggests a human reviewer based on repo history.
14. Developer accepts/rejects AI suggestions → **Feedback Agent** stores the outcome.
15. **Monitoring Agent** continuously tracks latency, accuracy, drift, and acceptance rate.
16. When degradation/drift is detected, the **Retraining Agent** launches a new training pipeline (tracked in MLflow, versioned via DVC).
17. **Deployment Agent** validates the candidate model against the production baseline and performs a canary rollout, with rollback support.
18. Dashboard (Next.js) reflects all of the above in near real time.

## 4. Folder & File Structure

```
reviewops-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── webhooks.py      # GitHub webhook endpoint
│   │   │   │   ├── repositories.py
│   │   │   │   ├── reviews.py
│   │   │   │   ├── feedback.py
│   │   │   │   ├── models.py        # model registry endpoints
│   │   │   │   └── monitoring.py
│   │   │   └── deps.py              # shared FastAPI dependencies
│   │   ├── core/
│   │   │   ├── config.py            # settings via Pydantic BaseSettings
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── orchestrator/
│   │   │   ├── graph.py             # LangGraph workflow definition
│   │   │   └── state.py             # shared orchestration state schema
│   │   ├── agents/
│   │   │   ├── data_agent.py
│   │   │   ├── validation_agent.py
│   │   │   ├── feature_engineering_agent.py
│   │   │   ├── embedding_agent.py
│   │   │   ├── review_agent.py
│   │   │   ├── bug_prediction_agent.py
│   │   │   ├── security_agent.py
│   │   │   ├── explainability_agent.py
│   │   │   ├── documentation_agent.py
│   │   │   ├── test_generation_agent.py
│   │   │   ├── reviewer_recommendation_agent.py
│   │   │   ├── feedback_agent.py
│   │   │   ├── monitoring_agent.py
│   │   │   ├── retraining_agent.py
│   │   │   └── deployment_agent.py
│   │   ├── model_gateway/
│   │   │   ├── gateway.py           # routing, caching, fallback
│   │   │   ├── providers/
│   │   │   │   └── huggingface.py
│   │   │   └── cache.py             # Redis-backed cache
│   │   ├── static_analysis/
│   │   │   ├── semgrep_runner.py
│   │   │   ├── bandit_runner.py
│   │   │   ├── pylint_runner.py
│   │   │   └── eslint_runner.py
│   │   ├── ml/
│   │   │   ├── training/            # training scripts
│   │   │   ├── inference/           # inference wrappers
│   │   │   └── features/            # feature transforms
│   │   ├── db/
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   ├── session.py
│   │   │   └── migrations/          # Alembic
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── integrations/
│   │   │   └── github_client.py
│   │   └── monitoring/
│   │       ├── metrics.py           # Prometheus metrics
│   │       └── drift.py             # Evidently AI checks
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── app/                         # Next.js app router
│   │   ├── dashboard/
│   │   ├── repositories/
│   │   ├── reviews/
│   │   ├── models/
│   │   ├── monitoring/
│   │   └── settings/
│   ├── components/
│   │   └── ui/                      # Shadcn UI components
│   ├── lib/
│   ├── hooks/
│   ├── styles/
│   ├── package.json
│   └── Dockerfile
│
├── ml-pipeline/
│   ├── dvc.yaml
│   ├── data/                        # DVC-tracked datasets
│   ├── notebooks/
│   └── mlflow/
│
├── infra/
│   ├── docker-compose.yml
│   ├── prometheus/
│   ├── grafana/
│   └── k8s/                         # future
│
├── .github/
│   └── workflows/                   # CI/CD (GitHub Actions)
│
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   ├── rules.md
│   ├── phases.md
│   └── design.md
│
└── README.md
```

## 5. Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Shadcn UI
- React Query
- Framer Motion

### Backend
- FastAPI
- SQLAlchemy
- Alembic (migrations)
- Pydantic (validation)
- Python 3.12

### Agent Orchestration
- LangGraph

### Machine Learning
- Scikit-learn
- XGBoost
- LightGBM
- Hugging Face Transformers

### MLOps
- MLflow (experiment tracking, model registry)
- DVC (dataset versioning)
- Evidently AI (ML quality / drift monitoring)

### Data Layer
- PostgreSQL (relational data)
- Redis (caching)
- Qdrant (vector embeddings)
- MinIO (artifact/model file storage)

### Monitoring
- Prometheus (metrics collection)
- Grafana (operational dashboards)

### Infrastructure
- Docker + Docker Compose (current)
- Kubernetes (future)
- GitHub Actions (CI/CD)

## 6. Key Architectural Decisions

- **Modular monolith over microservices**: reduces early complexity; module boundaries are enforced by folder structure and internal interfaces so a future split is low-risk.
- **Model Gateway as a single choke point**: agents never call Hugging Face directly. This isolates model routing, caching, versioning, and fallback logic, so swapping/upgrading models doesn't touch agent code.
- **LangGraph for orchestration**: gives explicit, inspectable state transitions between agents instead of ad-hoc function chaining.
- **Static analysis + ML + LLM as three distinct layers**: deterministic checks are never replaced by probabilistic ones — they run alongside each other, and outputs are merged by the Review Agent.

## 7. Phase 4 Deviations
- **Model Registry Database**: Instead of duplicating `MLModel` and `MLDeployment` records into the PostgreSQL database using SQLAlchemy, the `models.py` API route and `DeploymentAgent` interface directly with `mlflow.client.MlflowClient`. This avoids maintaining state in two places and relies on MLflow as the source of truth.
- **Frontend Dashboard**: Components were implemented manually using Tailwind CSS for Phases 1-3, and Shadcn UI was introduced in Phase 4 via CLI (`npx shadcn@latest init`).
- **Kubernetes**: Exploratory K8s manifests added to `infra/k8s/` are standard boilerplate and not actively deployed since we are currently running on Docker Compose.
