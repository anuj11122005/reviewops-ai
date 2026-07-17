"use client";

import { useQuery } from "@tanstack/react-query";

interface Repository {
  id: number;
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  url: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface RepositoryListResponse {
  items: Repository[];
  total: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RepositoriesPage() {
  const { data, isLoading: loading, error } = useQuery<RepositoryListResponse, Error>({
    queryKey: ["repositories"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/repositories`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
  });

  return (
    <div>
      <h1 className="text-[28px] font-semibold text-text-primary mb-2">
        Repositories
      </h1>
      <p className="text-text-secondary text-sm mb-8">
        Connected GitHub repositories receiving webhook events.
      </p>

      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-surface rounded-xl border border-border p-6 animate-pulse"
            >
              <div className="h-5 bg-surface-elevated rounded w-48 mb-3"></div>
              <div className="h-3 bg-surface-elevated rounded w-64"></div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-surface rounded-xl border border-danger/30 p-6">
          <p className="text-danger text-sm font-medium">
            Failed to load repositories
          </p>
          <p className="text-text-muted text-xs mt-1">{error.message}</p>
          <p className="text-text-muted text-xs mt-2">
            Make sure the backend is running at {API_BASE}
          </p>
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="bg-surface rounded-xl border border-border p-12 text-center">
          <p className="text-text-secondary text-sm mb-2">
            No repositories connected yet
          </p>
          <p className="text-text-muted text-xs">
            Repositories appear here automatically when a GitHub webhook event
            is received.
          </p>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="space-y-4">
          <p className="text-text-muted text-xs uppercase tracking-wider">
            {data.total} {data.total === 1 ? "repository" : "repositories"}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.items.map((repo) => (
              <div
                key={repo.id}
                className="bg-surface rounded-xl border border-border p-6 hover:border-primary/40 transition-colors duration-150"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-[16px] font-semibold text-text-primary">
                      {repo.name}
                    </h3>
                    <p className="text-text-secondary text-xs font-mono">
                      {repo.full_name}
                    </p>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                      repo.is_active
                        ? "bg-success/10 text-success"
                        : "bg-text-muted/10 text-text-muted"
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        repo.is_active ? "bg-success" : "bg-text-muted"
                      }`}
                    ></span>
                    {repo.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-text-muted text-xs">
                  <span>Owner: {repo.owner}</span>
                  <span>·</span>
                  <span>
                    Added:{" "}
                    {new Date(repo.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
