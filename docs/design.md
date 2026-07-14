# Design Document — ReviewOps AI

This defines the visual and UX language for the ReviewOps AI dashboard. The goal is a product that reads as a **serious engineering tool** — closer to Linear, Vercel, or Datadog than a generic admin template.

## 1. Design Principles

- **Data-dense but calm.** The dashboard shows a lot of information (agent status, metrics, PRs, models) — use whitespace, grouping, and hierarchy so it never feels cluttered.
- **Dark-mode first.** Engineers live in this dashboard for long stretches; dark mode is the default, light mode is a supported alternative, not an afterthought.
- **Status must be instantly legible.** Any agent, model, or deployment state (healthy/degraded/failed/running) should be readable at a glance via color + icon, not just text.
- **No decorative AI clichés.** Avoid generic "glowing gradient robot" AI aesthetics. This is an engineering product — treat it like developer tooling, not a consumer AI app.

## 2. Color System

### Base (Dark theme — default)
| Token | Hex | Usage |
|---|---|---|
| `background` | `#0B0E14` | App background |
| `surface` | `#131722` | Cards, panels |
| `surface-elevated` | `#1B2030` | Modals, dropdowns |
| `border` | `#262B3B` | Dividers, card borders |
| `text-primary` | `#E6E8EF` | Primary text |
| `text-secondary` | `#9098AC` | Secondary/meta text |
| `text-muted` | `#5C6479` | Disabled/placeholder text |

### Accent (Brand)
| Token | Hex | Usage |
|---|---|---|
| `primary` | `#4F7CFF` | Primary actions, links, active states |
| `primary-hover` | `#6B90FF` | Hover state |
| `primary-muted` | `#1E2A4A` | Subtle backgrounds for primary elements |

### Semantic (Status Colors)
| Token | Hex | Meaning |
|---|---|---|
| `success` | `#3DD68C` | Healthy agent, passed check, deployed model |
| `warning` | `#F5B94D` | Drift detected, degraded performance, pending review |
| `danger` | `#F0556B` | Failed agent, security vulnerability, rejected model |
| `info` | `#5AC8FA` | Informational states, running/in-progress |

### Light theme (secondary)
| Token | Hex |
|---|---|
| `background` | `#F7F8FA` |
| `surface` | `#FFFFFF` |
| `border` | `#E4E7ED` |
| `text-primary` | `#14171F` |
| `text-secondary` | `#5C6479` |

Semantic and primary accent colors stay the same across themes for consistency; only neutrals swap.

## 3. Typography

- **Primary UI font:** `Inter` — clean, highly legible at small sizes, standard for dev-tool UIs.
- **Monospace font:** `JetBrains Mono` — used for code snippets, diffs, PR file paths, metric values, log output.

| Style | Font | Size | Weight |
|---|---|---|---|
| Page title (H1) | Inter | 28px | 600 |
| Section heading (H2) | Inter | 20px | 600 |
| Card title (H3) | Inter | 16px | 600 |
| Body text | Inter | 14px | 400 |
| Small / meta text | Inter | 12px | 400 |
| Code / diffs / metrics | JetBrains Mono | 13px | 400 |
| Buttons / labels | Inter | 14px | 500 |

Line height: 1.5 for body text, 1.3 for headings.

## 4. Layout & UX Patterns

### Navigation
- Persistent left sidebar: Dashboard, Repositories, Pull Requests, Agents, Models, Monitoring, Feedback, Settings.
- Top bar: search, active repo/org switcher, user menu, notification bell.

### Core Screens
1. **Dashboard (home):** high-level KPIs (open PRs, avg. review time, model health, active drift alerts) as cards, plus a recent-activity feed.
2. **Repositories:** list/grid of connected repos with connection status and quick stats.
3. **Pull Request Detail:** file diff view + inline AI review comments + tabs for Static Analysis / Bug Prediction / Security / Explanation / Reviewer Suggestion.
4. **Agent Status:** live grid of all agents (Data, Validation, Feature Eng., Review, Bug Prediction, Security, Explainability, Documentation, Test Gen, Reviewer Rec., Feedback, Monitoring, Retraining, Deployment) with per-agent status (idle/running/error) and last-run timestamp.
5. **Model Registry:** table of models, versions, metrics vs. baseline, promote/rollback actions.
6. **Monitoring:** embedded Grafana-style charts (latency, throughput, accuracy) and Evidently-style drift reports.
7. **Feedback Analytics:** acceptance/rejection rate over time, broken down by agent/suggestion type.
8. **Settings:** GitHub App config, notification preferences, team management.

### Components (Shadcn UI-based)
- **Status badge:** colored dot + label, using semantic colors (success/warning/danger/info).
- **Metric card:** large number, trend arrow, sparkline, muted label.
- **Diff viewer:** monospace, syntax-highlighted, inline comment threads anchored to lines.
- **Agent pipeline visual:** horizontal step indicator showing the orchestration flow, current agent highlighted.
- **Toast notifications:** for real-time events (new PR review completed, drift alert, deployment finished).

### Interaction & Motion
- Use Framer Motion for: page transitions (subtle fade/slide), status badge changes (brief pulse), and live-updating metric cards (smooth number count-up) — never gratuitous animation.
- Loading states use skeleton screens, not spinners, for anything above ~300ms.
- Real-time agent status updates via WebSocket/SSE, reflected with a subtle pulse animation on the status dot rather than a full re-render.

## 5. Iconography

- Use a single consistent icon set (e.g., Lucide, which pairs naturally with Shadcn UI).
- Icons are functional, not decorative — every icon should map to a real status, action, or entity type (agent, model, repo, PR, alert).

## 6. Accessibility

- Minimum contrast ratio 4.5:1 for body text against background in both themes.
- Status must never be conveyed by color alone — always paired with an icon or text label (colorblind-safe).
- All interactive elements keyboard-navigable; focus states use a visible `primary`-colored outline.
