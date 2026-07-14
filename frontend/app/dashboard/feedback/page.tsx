"use client";

import { useEffect, useState } from "react";

type FeedbackStats = {
  total: number;
  accepted: number;
  rejected: number;
  acceptance_rate: number;
};

export default function FeedbackPage() {
  const [stats, setStats] = useState<FeedbackStats>({
    total: 0,
    accepted: 0,
    rejected: 0,
    acceptance_rate: 0,
  });

  useEffect(() => {
    // In a real application, fetch from /api/feedback/stats
    // fetch("http://localhost:8000/api/feedback/stats")
    //   .then(res => res.json())
    //   .then(data => setStats(data));
    
    // Mock data for Phase 3 dashboard implementation
    setStats({
      total: 42,
      accepted: 31,
      rejected: 11,
      acceptance_rate: 0.738,
    });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">AI Suggestion Feedback</h1>
      
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="text-sm font-medium text-gray-500 mb-1">Total Suggestions</div>
          <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
        </div>
        <div className="bg-white rounded-xl border border-green-200 p-6 shadow-sm">
          <div className="text-sm font-medium text-green-600 mb-1">Accepted (True Positives)</div>
          <div className="text-3xl font-bold text-gray-900">{stats.accepted}</div>
        </div>
        <div className="bg-white rounded-xl border border-red-200 p-6 shadow-sm">
          <div className="text-sm font-medium text-red-600 mb-1">Rejected (False Positives)</div>
          <div className="text-3xl font-bold text-gray-900">{stats.rejected}</div>
        </div>
        <div className="bg-white rounded-xl border border-blue-200 p-6 shadow-sm">
          <div className="text-sm font-medium text-blue-600 mb-1">Acceptance Rate</div>
          <div className="text-3xl font-bold text-gray-900">{(stats.acceptance_rate * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Recent Feedback History</h2>
        </div>
        <table className="w-full text-left text-sm text-gray-500">
          <thead className="bg-gray-50 text-gray-700 uppercase">
            <tr>
              <th className="px-6 py-3 border-b">PR ID</th>
              <th className="px-6 py-3 border-b">Category</th>
              <th className="px-6 py-3 border-b">Status</th>
              <th className="px-6 py-3 border-b">Comment</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="px-6 py-4 font-medium text-gray-900">#142</td>
              <td className="px-6 py-4">Security: SQL Injection</td>
              <td className="px-6 py-4 text-green-600 font-medium">Accepted</td>
              <td className="px-6 py-4">"Good catch on the unparameterized query."</td>
            </tr>
            <tr className="border-b">
              <td className="px-6 py-4 font-medium text-gray-900">#140</td>
              <td className="px-6 py-4">Bug Prediction</td>
              <td className="px-6 py-4 text-red-600 font-medium">Rejected</td>
              <td className="px-6 py-4">"False positive, this code path is unreachable."</td>
            </tr>
            <tr>
              <td className="px-6 py-4 font-medium text-gray-900">#139</td>
              <td className="px-6 py-4">Security: Hardcoded Secret</td>
              <td className="px-6 py-4 text-green-600 font-medium">Accepted</td>
              <td className="px-6 py-4">"Forgot to remove the test token."</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
