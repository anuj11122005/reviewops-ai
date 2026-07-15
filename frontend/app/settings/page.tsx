"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function SettingsPage() {
  const [theme, setTheme] = useState("dark");

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    if (newTheme === "light") {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
    } else {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-8 space-y-6 max-w-4xl"
    >
      <div>
        <h1 className="text-3xl font-semibold text-primary mb-2">Settings</h1>
        <p className="text-muted-foreground">Manage your ReviewOps AI configuration, appearance, and integrations.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Theme Preference</p>
              <p className="text-sm text-muted-foreground">Toggle between Light and Dark mode.</p>
            </div>
            <Button onClick={toggleTheme} variant="outline">
              {theme === "dark" ? "Switch to Light" : "Switch to Dark"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>GitHub Integration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Webhook Secret</label>
            <input 
              type="password" 
              defaultValue="****************" 
              disabled 
              className="w-full p-2 bg-surface-elevated border border-border rounded-md text-sm text-muted-foreground"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">App Installation ID</label>
            <input 
              type="text" 
              defaultValue="12345678" 
              disabled 
              className="w-full p-2 bg-surface-elevated border border-border rounded-md text-sm text-muted-foreground"
            />
          </div>
          <Button disabled className="mt-4 opacity-50">Update Configuration</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Slack Alerts</p>
              <p className="text-sm text-muted-foreground">Receive messages when drift is detected.</p>
            </div>
            <input type="checkbox" defaultChecked className="w-4 h-4 accent-primary" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Summaries</p>
              <p className="text-sm text-muted-foreground">Weekly PR review throughput and AI acceptance rate.</p>
            </div>
            <input type="checkbox" defaultChecked className="w-4 h-4 accent-primary" />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
