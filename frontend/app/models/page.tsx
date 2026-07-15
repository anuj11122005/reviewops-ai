"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ModelsPage() {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/models")
      .then((res) => res.json())
      .then((data) => {
        setModels(data.models || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching models", err);
        setLoading(false);
      });
  }, []);

  const promote = async (modelName: string, version: string) => {
    await fetch(`http://localhost:8000/api/models/${modelName}/versions/${version}/promote`, { method: "POST" });
    window.location.reload();
  };

  const rollback = async (modelName: string, version: string) => {
    await fetch(`http://localhost:8000/api/models/${modelName}/versions/${version}/rollback`, { method: "POST" });
    window.location.reload();
  };

  if (loading) return <div className="p-8">Loading Model Registry...</div>;

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-semibold mb-4 text-primary">Model Registry</h1>
      <p className="text-muted-foreground mb-8">Manage ML models, view evaluation metrics, and handle deployments.</p>

      {models.map((model, idx) => (
        <Card key={idx} className="bg-surface border-border shadow-sm">
          <CardHeader>
            <CardTitle>{model.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {model.latest_versions?.map((v: any, vIdx: number) => (
                <div key={vIdx} className="flex flex-col md:flex-row justify-between p-4 border rounded-lg bg-surface-elevated items-center">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">v{v.version}</span>
                      <Badge variant={v.stage === "Production" ? "default" : "secondary"}>
                        {v.stage}
                      </Badge>
                    </div>
                    <div className="text-sm text-text-secondary">
                      Accuracy: {v.metrics?.accuracy ? (v.metrics.accuracy * 100).toFixed(1) + "%" : "N/A"} | 
                      Precision: {v.metrics?.precision ? (v.metrics.precision * 100).toFixed(1) + "%" : "N/A"}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2 mt-4 md:mt-0">
                    <Button 
                      variant="outline" 
                      onClick={() => rollback(model.name, v.version)}
                      disabled={v.stage === "Archived"}
                    >
                      Rollback
                    </Button>
                    <Button 
                      onClick={() => promote(model.name, v.version)}
                      disabled={v.stage === "Production"}
                      className="bg-primary hover:bg-primary-hover text-white"
                    >
                      Promote
                    </Button>
                  </div>
                </div>
              ))}
              {(!model.latest_versions || model.latest_versions.length === 0) && (
                <div className="text-sm text-muted-foreground">No versions found.</div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
      
      {models.length === 0 && (
        <div className="text-center p-12 border border-dashed rounded-lg text-text-muted">
          No models found in MLflow registry.
        </div>
      )}
    </div>
  );
}
