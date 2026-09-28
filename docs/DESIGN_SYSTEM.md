# 🎨 TG_KindSync_Pro: World-Class Design System Specification

> **Design Standard**: Obsidian Cyber-Glass & Linear-Grade Minimalist Precision  
> **Target Products**: Desktop Web, Tablet & Mobile Telemetry Viewports  
> **Key Foundations**: Impeccable Design Heuristics, Emil Kowalski Physics Motion

---

## 1. Color Palette Architecture (Semantic Tokens)

```css
:root {
    /* Canvas & Surfaces (Obsidian Obsidian Layering) */
    --bg-canvas: #05070B;             /* Ultra-deep obsidian base */
    --bg-surface: #0B0E17;            /* Primary card & sidebar surface */
    --bg-surface-elevated: #111624;   /* Modals, drawers, and active cards */
    --bg-surface-hover: #181F33;      /* Interactive hover state */
    --bg-subtle: #080B12;             /* Input backgrounds & subtle insets */

    /* Glassmorphism Overlays */
    --glass-bg: rgba(11, 14, 23, 0.75);
    --glass-blur: blur(20px);
    --glass-border: 1px solid rgba(255, 255, 255, 0.08);

    /* Borders & Dividers */
    --border-subtle: rgba(255, 255, 255, 0.06);
    --border-medium: rgba(255, 255, 255, 0.12);
    --border-strong: rgba(255, 255, 255, 0.22);
    --border-focus: rgba(56, 189, 248, 0.6);

    /* Typography Hierarchy */
    --text-primary: #F8FAFC;          /* Headings & key metrics (High contrast) */
    --text-secondary: #94A3B8;        /* Body text & labels */
    --text-tertiary: #64748B;         /* Metadata, captions & subtle labels */
    --text-muted: #475569;            /* Disabled states & placeholders */

    /* Semantic Accents */
    --accent-cyan: #38BDF8;           /* Live telemetry, speed, primary actions */
    --accent-indigo: #6366F1;         /* Routing, video media, branding */
    --accent-emerald: #10B981;        /* Operational health, success, verified */
    --accent-amber: #F59E0B;          /* Warnings, queue backlog, standby */
    --accent-rose: #F43F5E;           /* Errors, DLQ, emergency stop */
    --accent-purple: #A855F7;         /* AI Studio, model council, research */
}
```

---

## 2. Typography Hierarchy

* **Display & Headings**: `'Outfit'`, sans-serif (Weights: 600, 700, 800) — distinctive, geometric, modern.
* **Body & UI**: `'Plus Jakarta Sans'`, sans-serif (Weights: 400, 500, 600) — maximum readability, neutral geometry.
* **Technical Data, Numbers & Code**: `'JetBrains Mono'`, monospace with `font-variant-numeric: tabular-nums` — perfect column alignment without jitter.

---

## 3. Spacing & Spatial Rhythm (Strict 4px / 8px Scale)

```css
--space-1: 4px;   /* Micro-spacing: tags, badges, icon gaps */
--space-2: 8px;   /* Sub-element padding, row gap */
--space-3: 12px;  /* Input padding, table cell padding */
--space-4: 16px;  /* Standard card interior padding */
--space-5: 20px;  /* Card-to-card gap */
--space-6: 24px;  /* Section margins */
--space-8: 32px;  /* Viewport margins */
```

---

## 4. Radii & Elevation Shadows

```css
--radius-sm: 6px;    /* Badges, micro-buttons */
--radius-md: 10px;   /* Text inputs, small buttons */
--radius-lg: 16px;   /* Metric cards, Bento tiles */
--radius-xl: 22px;   /* Modal dialogs, floating drawers */
--radius-full: 9999px; /* Status pills, avatar circles */

--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.4);
--shadow-md: 0 8px 24px rgba(0, 0, 0, 0.6);
--shadow-glow-cyan: 0 0 20px rgba(56, 189, 248, 0.2);
--shadow-glow-emerald: 0 0 20px rgba(16, 185, 129, 0.2);
```

---

## 5. Emil Kowalski Motion Language

* **Timing Function**: `cubic-bezier(0.16, 1, 0.3, 1)` (Physics-based spring deceleration).
* **Hover State**: `transform: translateY(-2px); transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1);`
* **Active State**: `transform: translateY(0px) scale(0.98);`
* **Live Radar Pulse**: High-frequency subtle glowing ring animation for active streaming channels.
* **Accessibility**: Full `@media (prefers-reduced-motion: reduce)` support with zero animation layout shifts.

---

## 6. Human Microcopy Guidelines

* Replace generic alerts with informative contextual feedback (e.g., *"✨ Snapshot saved: history_core_backup_Monday_28-Sep-2026.sqlite (700 KB)"* instead of *"Success"*).
* Clear Empty States: Every empty tab displays an icon, description, and direct action button (e.g., *"No Forwarding Routes Found — [➕ Add First Route]"*).
