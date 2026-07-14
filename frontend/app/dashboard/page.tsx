export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-[28px] font-semibold text-text-primary mb-2">
        Dashboard
      </h1>
      <p className="text-text-secondary text-sm mb-8">
        ReviewOps AI — Platform Overview
      </p>

      {/* Phase 1 placeholder KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-surface rounded-xl border border-border p-6">
          <p className="text-text-muted text-xs uppercase tracking-wider mb-1">
            Connected Repos
          </p>
          <p className="text-3xl font-semibold text-text-primary font-mono">
            —
          </p>
          <p className="text-text-muted text-xs mt-2">
            View in Repositories page
          </p>
        </div>
        <div className="bg-surface rounded-xl border border-border p-6">
          <p className="text-text-muted text-xs uppercase tracking-wider mb-1">
            Open PRs
          </p>
          <p className="text-3xl font-semibold text-text-primary font-mono">
            —
          </p>
          <p className="text-text-muted text-xs mt-2">
            View in Pull Requests page
          </p>
        </div>
        <div className="bg-surface rounded-xl border border-border p-6">
          <p className="text-text-muted text-xs uppercase tracking-wider mb-1">
            AI Reviews
          </p>
          <p className="text-3xl font-semibold text-text-muted font-mono">
            Phase 2
          </p>
          <p className="text-text-muted text-xs mt-2">Coming soon</p>
        </div>
      </div>

      {/* Phase 1 status */}
      <div className="bg-surface rounded-xl border border-border p-6">
        <h2 className="text-[20px] font-semibold text-text-primary mb-4">
          Phase 1 — Platform Foundation
        </h2>
        <div className="space-y-3">
          {[
            { label: "Backend scaffold (FastAPI)", done: true },
            { label: "PostgreSQL + Alembic migrations", done: true },
            { label: "GitHub webhook ingestion", done: true },
            { label: "Docker Compose environment", done: true },
            { label: "Frontend scaffold (Next.js)", done: true },
            { label: "CI pipeline (GitHub Actions)", done: true },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-3">
              <span
                className={`w-2 h-2 rounded-full ${
                  item.done ? "bg-success" : "bg-text-muted"
                }`}
              ></span>
              <span
                className={`text-sm ${
                  item.done ? "text-text-primary" : "text-text-muted"
                }`}
              >
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
