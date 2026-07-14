"use client";

import { useEffect, useState } from "react";

type PRAgentStatus = {
  id: string;
  pull_number: number;
  status: string;
  current_agent: string;
  logs: string[];
};

export default function AgentStatusPage() {
  // In a real application, you would fetch this from an API endpoint
  // that tracks the status of the LangGraph orchestrator runs.
  // For the dashboard, we will render a static/mock view as requested for Phase 3
  
  const [statuses, setStatuses] = useState<PRAgentStatus[]>([
    {
      id: "run_123",
      pull_number: 142,
      status: "running",
      current_agent: "SecurityAgent",
      logs: [
        "DataAgent fetched PR 142",
        "ValidationAgent passed",
        "FeatureEngineeringAgent computed complexity: 8.4",
        "BugPredictionAgent predicted bug prob: 0.12",
        "SecurityAgent scanning..."
      ]
    },
    {
      id: "run_124",
      pull_number: 143,
      status: "completed",
      current_agent: "Done",
      logs: [
        "DataAgent fetched PR 143",
        "ValidationAgent passed",
        "FeatureEngineeringAgent computed complexity: 12.1",
        "BugPredictionAgent predicted bug prob: 0.78",
        "SecurityAgent passed",
        "ExplainabilityAgent generated report",
        "ReviewAgent posted comment"
      ]
    }
  ]);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Agent Execution Status</h1>
      <div className="grid gap-6">
        {statuses.map((run) => (
          <div key={run.id} className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">
                PR #{run.pull_number}
              </h2>
              <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                run.status === 'running' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
              }`}>
                {run.status.toUpperCase()}
              </span>
            </div>
            <div className="px-6 py-4">
              <div className="mb-4">
                <span className="text-sm font-medium text-gray-500">Current Agent: </span>
                <span className="text-sm font-semibold text-gray-900">{run.current_agent}</span>
              </div>
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-gray-300 overflow-y-auto max-h-48">
                {run.logs.map((log, idx) => (
                  <div key={idx} className="mb-1">{`> ${log}`}</div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
