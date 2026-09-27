# 🎨 UI/UX DESIGN SYSTEM & MOTION SPECIFICATION
## TG KindSync Pro (Enterprise Master Edition v15.0)

---

## 1. Design Philosophy: Luxury Cyber-Glass & Tactile UI
`TG KindSync Pro` interfaces (Terminal TUI, Telegram Cards, and Web Sentinel Dashboard) adhere to a **high-contrast, deep-dark luxury aesthetic with glassmorphism, micro-animations, and fluid physics-based transitions**.

### Anti-AI Slop Standards:
* **No Generic Colors:** Avoid harsh default reds, blues, or greens. Use curated HSL and Hex gradients (e.g., Deep Obsidian `#07090e`, Neon Emerald `#10b981`, Cyber Cyan `#06b6d4`, Electric Indigo `#6366f1`, Crimson Alert `#f43f5e`).
* **Strict Spacing Scale:** 4px / 8px grid system across all margins, paddings, and card layouts.
* **Modern Typography Pairing:** Google Fonts `Inter`, `Outfit`, and `JetBrains Mono` for code and telemetry data.

---

## 2. Color Palette & Design Tokens

| Token | Hex Value | Semantic Usage |
| :--- | :--- | :--- |
| `--bg-canvas` | `#07090e` | Deep obsidian main backdrop |
| `--bg-card` | `rgba(13, 17, 23, 0.75)` | Glassmorphism card surface with `backdrop-filter: blur(16px)` |
| `--bg-card-hover` | `rgba(22, 27, 34, 0.85)` | Hover state elevation with subtle glow border |
| `--border-subtle` | `rgba(255, 255, 255, 0.08)` | Standard card boundary divider |
| `--border-focus` | `rgba(6, 182, 212, 0.5)` | Cyber cyan focus outline |
| `--accent-cyan` | `#06b6d4` | Primary brand accent & active gauges |
| `--accent-emerald` | `#10b981` | Success states, 100% health badges, online indicators |
| `--accent-indigo` | `#6366f1` | Deep intelligence, AI supervisor, and routing matrix |
| `--accent-amber` | `#f59e0b` | Warnings, rate limits, FloodWait pauses |
| `--accent-rose` | `#f43f5e` | Errors, emergency kill switches, DLQ alerts |
| `--text-primary` | `#f8fafc` | High-contrast main headers & metrics |
| `--text-muted` | `#94a3b8` | Subtitles, timestamps, and secondary captions |

---

## 3. Emil Kowalski Motion & Micro-Interaction Standards

### 3.1 Physics-Based Spring Timing
* **Spring Standard:** `cubic-bezier(0.16, 1, 0.3, 1)` for all layout transitions, card reveals, and modal popups.
* **Duration Standard:**
  * Micro-interactions (Button hover, badge glow): `150ms - 200ms`
  * Sheet & Modal Transitions: `280ms - 350ms`
  * Page / Tab cross-fades: `250ms ease-out`

### 3.2 Key Web Dashboard Components
1. **Speedometer Upload Velocity Gauge:** SVG circular arc with gradient sweep animating dynamically according to active MB/s throughput.
2. **Active Media Stream Bar:** Real-time percentage fill with pulse shimmer animation during multipart uploads.
3. **Interactive Route Matrix Modal:** Smooth fade-and-scale backdrop overlay with dynamic topic search autocomplete.
4. **Live Terminal Stream Box:** Monospace log output with automatic smooth auto-scroll lock and color-coded tags.

---

## 4. Telegram Message Card Styling Standards
* **Header Dividers:** Clean Unicode block borders (`━━━━━━━━━━━━━━━━━━━━━━━━━━━━`) with concise emoji anchors.
* **Clickable Links:** Markdown direct entity anchors `[Title](https://t.me/c/...)`.
* **Footer Signatures:** Official branding `Kind Doctor & Team • Medical Education & Technology`.
