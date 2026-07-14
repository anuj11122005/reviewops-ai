"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface PullRequest {
  id: number;
  repository_id: number;
  github_pr_id: number;
  number: number;
  title: string;
  author: string;
  status: string;
  head_sha: string;
  base_branch: string;
  head_branch: string;
  body: string | null;
  opened_at: string | null;
  created_at: string;
  updated_at: string;
}

interface PullRequestListResponse {
  items: PullRequest[];
  total: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    open: "bg-success/10 text-success",
    closed: "bg-danger/10 text-danger",
    merged: "bg-primary/10 text-primary",
  };
  const dotStyles: Record<string, string> = {
    open: "bg-success",
    closed: "bg-danger",
    merged: "bg-primary",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
        styles[status] || "bg-text-muted/10 text-text-muted"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          dotStyles[status] || "bg-text-muted"
        }`}
      ></span>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

export default function PullRequestsPage() {
  const [data, setData] = useState<PullRequestListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/pull-requests`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: PullRequestListResponse) => {
        setData(json);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1 className="text-[28px] font-semibold text-text-primary mb-2">
        Pull Requests
      </h1>
      <p className="text-text-secondary text-sm mb-8">
        All PRs received via GitHub webhooks. AI review output will appear here
        in Phase 2.
      </p>

      {loading && (
        <div className="bg-surface rounded-xl border border-border overflow-hidden">
          <div className="p-4 space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse flex items-center gap-4">
                <div className="h-4 bg-surface-elevated rounded w-12"></div>
                <div className="h-4 bg-surface-elevated rounded w-64"></div>
                <div className="flex-1"></div>
                <div className="h-4 bg-surface-elevated rounded w-16"></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-surface rounded-xl border border-danger/30 p-6">
          <p className="text-danger text-sm font-medium">
            Failed to load pull requests
          </p>
          <p className="text-text-muted text-xs mt-1">{error}</p>
          <p className="text-text-muted text-xs mt-2">
            Make sure the backend is running at {API_BASE}
          </p>
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="bg-surface rounded-xl border border-border p-12 text-center">
          <p className="text-text-secondary text-sm mb-2">
            No pull requests received yet
          </p>
          <p className="text-text-muted text-xs">
            PRs appear here when a GitHub webhook delivers a pull_request event.
          </p>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div>
          <p className="text-text-muted text-xs uppercase tracking-wider mb-4">
            {data.total} pull {data.total === 1 ? "request" : "requests"}
          </p>
          <div className="bg-surface rounded-xl border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                  <th className="text-left p-4 font-medium">#</th>
                  <th className="text-left p-4 font-medium">Title</th>
                  <th className="text-left p-4 font-medium">Author</th>
                  <th className="text-left p-4 font-medium">Branch</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Opened</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((pr) => (
                  <tr
                    key={pr.id}
                    className="border-b border-border last:border-b-0 hover:bg-surface-elevated/50 transition-colors duration-100"
                  >
                    <td className="p-4 font-mono text-text-muted text-xs">
                      {pr.number}
                    </td>
                    <td className="p-4">
                      <Link href={`/pull-requests/${pr.id}`} className="text-text-primary font-medium hover:text-primary transition-colors">
                        {pr.title}
                      </Link>
                      <span className="block text-text-muted text-xs font-mono mt-0.5">
                        {pr.head_sha.substring(0, 7)}
                      </span>
                    </td>
                    <td className="p-4 text-text-secondary">{pr.author}</td>
                    <td className="p-4">
                      <span className="font-mono text-xs text-text-secondary bg-surface-elevated px-2 py-1 rounded">
                        {pr.head_branch}
                      </span>
                      <span className="text-text-muted mx-1">→</span>
                      <span className="font-mono text-xs text-text-secondary bg-surface-elevated px-2 py-1 rounded">
                        {pr.base_branch}
                      </span>
                    </td>
                    <td className="p-4">
                      <StatusBadge status={pr.status} />
                    </td>
                    <td className="p-4 text-text-muted text-xs">
                      {pr.opened_at
                        ? new Date(pr.opened_at).toLocaleDateString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
