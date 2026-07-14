"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "◉" },
  { href: "/repositories", label: "Repositories", icon: "⊞" },
  { href: "/pull-requests", label: "Pull Requests", icon: "⑂" },
  // Phase 2+: Agents, Models, Monitoring, Feedback, Settings
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface border-r border-border flex flex-col z-40">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-sm transition-transform group-hover:scale-105">
            R
          </div>
          <div>
            <span className="text-text-primary font-semibold text-sm block leading-tight">
              ReviewOps AI
            </span>
            <span className="text-text-muted text-xs">v0.1.0</span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                ${
                  isActive
                    ? "bg-primary-muted text-primary"
                    : "text-text-secondary hover:bg-surface-elevated hover:text-text-primary"
                }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-text-muted text-xs">
          <span className="w-2 h-2 rounded-full bg-success inline-block"></span>
          Phase 1 — Platform Foundation
        </div>
      </div>
    </aside>
  );
}
