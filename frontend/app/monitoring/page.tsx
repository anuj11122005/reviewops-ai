"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Zap, ShieldAlert, Cpu } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

const mockLatencyData = [
  { time: "10:00", ms: 120 },
  { time: "10:05", ms: 135 },
  { time: "10:10", ms: 110 },
  { time: "10:15", ms: 190 },
  { time: "10:20", ms: 150 },
  { time: "10:25", ms: 125 },
];

type MetricsData = {
  system_health: string;
  prediction_accuracy: number;
  drift_report?: {
    drift_score?: number;
  };
  agent_latency_ms?: Record<string, number>;
};

export default function MonitoringPage() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/monitoring/metrics")
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch((err) => console.error(err));
  }, []);

  if (!metrics) return <div className="p-8">Loading System Metrics...</div>;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 space-y-6"
    >
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-primary">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time health, drift reports, and agent latencies.</p>
        </div>
        <Badge variant="outline" className="px-4 py-1 text-success border-success bg-success/10">
          <Activity className="w-4 h-4 mr-2 inline" />
          {metrics.system_health}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Global Prediction Accuracy</CardTitle>
            <ShieldAlert className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics.prediction_accuracy * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Across all models in production</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Data Drift Score</CardTitle>
            <Cpu className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning">{metrics.drift_report?.drift_score?.toFixed(3)}</div>
            <p className="text-xs text-muted-foreground">Evidently AI computed score</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Review Latency</CardTitle>
            <Zap className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">810ms</div>
            <p className="text-xs text-muted-foreground">End-to-end pipeline execution</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Agent Execution Latency (ms)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(metrics.agent_latency_ms || {}).map(([agent, ms]) => (
                <div key={agent} className="flex justify-between items-center">
                  <span className="text-sm font-medium">{agent}</span>
                  <span className="font-mono text-sm text-muted-foreground">{String(ms)}ms</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Inference Latency Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockLatencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262B3B" />
                <XAxis dataKey="time" stroke="#9098AC" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#9098AC" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "#1B2030", borderColor: "#262B3B", borderRadius: "8px" }} />
                <Line type="monotone" dataKey="ms" stroke="#4F7CFF" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
