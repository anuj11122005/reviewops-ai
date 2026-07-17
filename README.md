# ReviewOps AI

**Autonomous Multi-Agent AI Software Engineering Platform**

ReviewOps AI is an autonomous Multi-Agent AI Software Engineering Platform that combines static code analysis, machine learning, Large Language Models (LLMs), and MLOps into a single system. It automatically reviews GitHub Pull Requests, predicts bugs, detects security vulnerabilities, explains issues, generates documentation, recommends reviewers, learns from developer feedback, monitors model performance, and retrains itself over time. It is not a single-model AI code reviewer — it is a coordinated system of independent AI agents that together perform a complete, self-improving software engineering review workflow.

## Documentation

> Full project documentation — including the PRD, architecture, engineering rules, project phases, and design spec — exists locally in the `docs/` directory. These files are **intentionally excluded from version control** via `.gitignore` to keep the repo focused on source code. If you're cloning this repo for the first time, ask a team member for the docs bundle or refer to the project's internal documentation source.

## Project Structure

```
reviewops-ai/
├── backend/          # FastAPI modular-monolith backend
├── frontend/         # Next.js dashboard
├── ml-pipeline/      # DVC datasets, notebooks, MLflow config
├── infra/            # Docker Compose, Prometheus, Grafana, K8s (future)
├── .github/          # GitHub Actions CI/CD workflows
├── docs/             # (local only, gitignored) Project documentation
└── README.md
```

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | FastAPI · SQLAlchemy · Alembic · Pydantic · Python 3.12 |
| Frontend | Next.js · TypeScript · Tailwind CSS · Shadcn UI · React Query · Framer Motion |
| Orchestration | LangGraph |
| ML | Scikit-learn (RandomForest) · HTTP Inference API |
| MLOps | MLflow · DVC · Evidently AI |
| Data | PostgreSQL · Redis · Qdrant · MinIO |
| Monitoring | Prometheus · Grafana |
| Infra | Docker · Docker Compose · GitHub Actions |

## License

TBD
