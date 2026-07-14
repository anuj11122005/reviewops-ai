"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
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

interface StaticAnalysisIssue {
  path?: string;
  filename?: string;
  line?: number;
  line_number?: number;
  message?: string;
  issue_text?: string;
}

interface StaticAnalysisData {
  status: string;
  error?: string;
  issues?: StaticAnalysisIssue[];
}

interface ExplainabilityData {
  summary?: string;
}

interface ReviewResult {
  id: number;
  pull_request_id: number;
  status: string;
  bug_prediction_results: Record<string, number> | null;
  static_analysis_results: Record<string, StaticAnalysisData> | null;
  security_results: Record<string, string[]> | null;
  explainability_results: ExplainabilityData | null;
  created_at: string;
  updated_at: string;
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

export default function PullRequestDetailPage() {
  const params = useParams();
  const prId = params.id as string;

  const [pr, setPr] = useState<PullRequest | null>(null);
  const [review, setReview] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!prId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch PR details
        const prRes = await fetch(`${API_BASE}/api/pull-requests/${prId}`);
        if (!prRes.ok) throw new Error(`HTTP ${prRes.status} fetching PR`);
        const prData = await prRes.json();
        setPr(prData);

        // Fetch Review details (might 404 if not done yet)
        const revRes = await fetch(`${API_BASE}/api/pull-requests/${prId}/review`);
        if (revRes.ok) {
            const revData = await revRes.json();
            setReview(revData);
        } else if (revRes.status !== 404) {
            console.error(`HTTP ${revRes.status} fetching review`);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [prId]);

  if (loading) {
    return (
        <div>
            <div className="h-8 bg-surface-elevated rounded w-64 mb-4 animate-pulse"></div>
            <div className="h-64 bg-surface rounded-xl border border-border animate-pulse"></div>
        </div>
    );
  }

  if (error || !pr) {
    return (
      <div className="bg-surface rounded-xl border border-danger/30 p-6">
        <p className="text-danger text-sm font-medium">Failed to load pull request {prId}</p>
        <p className="text-text-muted text-xs mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <Link href="/pull-requests" className="text-sm text-text-muted hover:text-primary transition-colors">
          &larr; Back to Pull Requests
        </Link>
      </div>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-[28px] font-semibold text-text-primary mb-2 flex items-center gap-3">
            {pr.title} <span className="text-text-muted font-mono text-xl">#{pr.number}</span>
          </h1>
          <div className="flex items-center gap-4 text-sm text-text-secondary">
            <StatusBadge status={pr.status} />
            <span>opened by <span className="font-medium text-text-primary">{pr.author}</span></span>
            <span className="font-mono bg-surface-elevated px-2 py-0.5 rounded">{pr.head_branch}</span>
            <span>&rarr;</span>
            <span className="font-mono bg-surface-elevated px-2 py-0.5 rounded">{pr.base_branch}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface rounded-xl border border-border overflow-hidden">
            <div className="border-b border-border p-4 bg-surface-elevated/30">
              <h2 className="font-medium text-text-primary">AI Review Status</h2>
            </div>
            <div className="p-6">
              {!review ? (
                <div className="text-center py-8">
                    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-text-primary font-medium">Review in progress...</p>
                    <p className="text-text-muted text-sm mt-1">ReviewOps AI is analyzing this pull request.</p>
                </div>
              ) : (
                <div className="space-y-6">
                    <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            review.status === 'completed' ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'
                        }`}>
                            {review.status.toUpperCase()}
                        </span>
                        <span className="text-text-muted text-xs">
                            Completed at {new Date(review.updated_at).toLocaleString()}
                        </span>
                    </div>
                    
                    {/* Explainability Text */}
                    {review.explainability_results && review.explainability_results.summary && (
                        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-6">
                            <h3 className="text-sm font-medium text-blue-900 mb-2">AI Summary & Reasoning</h3>
                            <p className="text-sm text-blue-800">{review.explainability_results.summary}</p>
                        </div>
                    )}
                    
                    {/* Bug Predictions */}
                    {review.bug_prediction_results && (
                        <div>
                            <h3 className="text-sm font-medium text-text-primary mb-3">Bug Predictions (Heuristic)</h3>
                            <div className="rounded-lg border border-border overflow-hidden">
                                <table className="w-full text-sm">
                                    <thead className="bg-surface-elevated/30">
                                        <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-text-muted">
                                            <th className="p-3">File</th>
                                            <th className="p-3">Probability</th>
                                            <th className="p-3 w-32">Feedback</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Object.entries(review.bug_prediction_results).map(([file, prob]) => (
                                            <tr key={file} className="border-b border-border last:border-0 hover:bg-surface-elevated/30">
                                                <td className="p-3 font-mono text-xs">{file}</td>
                                                <td className="p-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-24 h-1.5 bg-surface-elevated rounded-full overflow-hidden">
                                                            <div 
                                                                className={`h-full ${prob > 0.5 ? 'bg-danger' : prob > 0.2 ? 'bg-warning' : 'bg-success'}`}
                                                                style={{ width: `${prob * 100}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-xs font-medium">{(prob * 100).toFixed(1)}%</span>
                                                    </div>
                                                </td>
                                                <td className="p-3">
                                                    <div className="flex gap-2">
                                                        <button 
                                                            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                                                            onClick={() => alert(`Feedback sent: Accepted for ${file}`)}
                                                        >
                                                            Accept
                                                        </button>
                                                        <button 
                                                            className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200"
                                                            onClick={() => alert(`Feedback sent: Rejected for ${file}`)}
                                                        >
                                                            Reject
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                        {Object.keys(review.bug_prediction_results).length === 0 && (
                                            <tr><td colSpan={3} className="p-4 text-center text-text-muted text-xs">No files analyzed</td></tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                    
                    {/* Static Analysis */}
                    {review.static_analysis_results && (
                        <div>
                            <h3 className="text-sm font-medium text-text-primary mb-3">Static Analysis</h3>
                            <div className="space-y-4">
                                {Object.entries(review.static_analysis_results).map(([tool, data]) => (
                                    <div key={tool} className="border border-border rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-medium text-text-primary">{tool}</h4>
                                            <span className={`text-xs px-2 py-0.5 rounded ${
                                                data.status === 'success' ? 'bg-success/10 text-success' : 
                                                data.status === 'skipped' ? 'bg-surface-elevated text-text-muted' : 
                                                'bg-danger/10 text-danger'
                                            }`}>
                                                {data.status}
                                            </span>
                                        </div>
                                        
                                        {data.status === 'success' && data.issues && data.issues.length > 0 ? (
                                            <ul className="space-y-2 mt-3">
                                                {data.issues.map((issue, idx: number) => (
                                                    <li key={idx} className="text-sm bg-surface-elevated/30 p-3 rounded-md">
                                                        <div className="font-mono text-xs text-text-muted mb-1">
                                                            {issue.path || issue.filename}:{issue.line || issue.line_number || "?"}
                                                        </div>
                                                        <div className="text-text-primary">
                                                            {issue.message || issue.issue_text}
                                                        </div>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : data.status === 'success' ? (
                                            <p className="text-sm text-text-muted">No issues found.</p>
                                        ) : data.status === 'error' ? (
                                            <p className="text-sm text-danger">{data.error}</p>
                                        ) : (
                                            <p className="text-sm text-text-muted">Skipped.</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                </div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
            <div className="bg-surface rounded-xl border border-border p-6">
                <h3 className="font-medium text-text-primary mb-4">Pull Request Info</h3>
                <div className="space-y-4 text-sm">
                    <div>
                        <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Author</p>
                        <p className="text-text-primary font-medium">{pr.author}</p>
                    </div>
                    <div>
                        <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Head SHA</p>
                        <p className="text-text-primary font-mono text-xs">{pr.head_sha}</p>
                    </div>
                    <div>
                        <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Created At</p>
                        <p className="text-text-primary">{new Date(pr.created_at).toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Description</p>
                        <p className="text-text-primary whitespace-pre-wrap">{pr.body || "No description provided."}</p>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
