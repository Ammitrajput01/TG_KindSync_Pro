---
name: impeccable-design
description: "Anti-AI Slop design system skill. Provides strict visual rhythm, 4px/8px spacing scales, typography pairing, tactile micro-states, and high-end handcrafted aesthetic standards."
---

# 💎 Impeccable Design System — Anti-AI Slop Standard

## Core Philosophy
> **"Eliminate AI Slop permanently."**  
> AI Slop is characterized by: generic Inter font, saturated purple/blue gradients, flat white card containers with harsh 10px blur shadows, and lifeless generic layouts. Handcrafted interfaces feel intentional, grounded, and tactile.

---

## 📐 1. Spatial Rhythm & Spacing Scales
Never use arbitrary padding or margins (like `17px` or `23px`). Stick strictly to the **4px / 8px Modular Scale**:

| Token | Size | Primary Usage |
|---|---|---|
| `space-1` | 4px | Micro padding, gap between icon and text |
| `space-2` | 8px | Button inline gap, badge padding |
| `space-3` | 12px | Compact form input padding, list item gap |
| `space-4` | 16px | Standard card padding, container gutter |
| `space-6` | 24px | Section separation, modal inner margins |
| `space-8` | 32px | Major component gaps, page headers |
| `space-12`| 48px | Hero layout breaks |

---

## 🎨 2. Palette & Contrast Architecture

### Curated Premium Themes (Choose 1 per project):
1. **Midnight Obsidian (Dark Tech/Fintech)**:
   - Background: `#0B0D13` | Surface: `#131620` | Border: `rgba(255, 255, 255, 0.07)`
   - Accent: `#38BDF8` (Sky) or `#10B981` (Emerald) | Text: `#F1F5F9` / Secondary: `#94A3B8`
2. **Warm Editorial / Swiss Modern (Clean Light)**:
   - Background: `#FBFBFA` | Surface: `#FFFFFF` | Border: `#E5E5E2`
   - Accent: `#D97706` (Warm Ochre) or `#0F172A` (Ink) | Text: `#18181B` / Secondary: `#71717A`
3. **Cyber Luminescent (Monitoring & Real-Time Ops)**:
   - Background: `#070A0F` | Surface: `#0E1420` | Border: `rgba(0, 240, 255, 0.12)`
   - Accent: `#00F0FF` (Cyan Neon) / `#00FFA3` (Terminal Mint) | Text: `#E2F1FF`

---

## 🔤 3. Typography Pairings
* **Pairing A (Modern Engineering)**: `Geist` or `Plus Jakarta Sans` for Headings + `JetBrains Mono` for data/metrics.
* **Pairing B (High-End Product)**: `Cabinet Grotesk` or `Outfit` for Headings + `Inter` for dense body copy.
* **Pairing C (Editorial/Prestige)**: `Fraunces` or `Instrument Serif` for Hero Display + `Instrument Sans` for body.

---

## 🔍 4. The `/polish` Quality Checklist
Before claiming any frontend or dashboard is complete:
- [ ] Are all borders subtle (`1px solid rgba(...)`) rather than thick harsh borders?
- [ ] Are shadows multi-layered (soft ambient shadow + subtle contact shadow)?
- [ ] Do all interactive elements have `:hover`, `:active`, and `:focus-visible` rings?
- [ ] Is there proper empty-state handling for when lists or data have 0 items?
- [ ] Does numerical data use tabular numbers (`font-variant-numeric: tabular-nums`) to prevent jitter?
