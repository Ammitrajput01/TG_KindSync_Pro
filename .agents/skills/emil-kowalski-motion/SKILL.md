---
name: emil-kowalski-motion
description: "High-end UI motion and animation skill based on Emil Kowalski's principles. Physics-based springs, cubic-bezier timing, micro-interactions, layout transitions, and anti-slop animation standards."
---

# 🎭 Emil Kowalski Motion & Micro-Interactions Skill

## Core Philosophy
> **"Good animation is felt, not noticed. Great animation provides spatial continuity without making the user wait."**  
> Never animate just for decoration. Animation must communicate state change, spatial origin, or physics-backed tactile feedback.

---

## 📐 1. The Motion Decision Framework
Before adding any animation or transition, answer these 3 questions:
1. **Does it orient the user?** (e.g., drawer opening from where it was clicked).
2. **Does it provide tactile feedback?** (e.g., button depression `scale(0.97)` on active).
3. **Does it block the user?** If an animation delays user action by even 100ms, **cut the duration or remove it**.

---

## ⚡ 2. Physics-Based Curves & Timings

### Recommended Easing Curves:
* **The Crisp Natural Pop (Enter)**:
  `cubic-bezier(0.16, 1, 0.3, 1)` (Duration: `180ms - 260ms`)
  *Use for:* Dialogs, dropdown menus, tooltips, cards appearing.
* **The Smooth Decelerate**:
  `cubic-bezier(0.05, 0.7, 0.1, 1.0)` (Duration: `200ms - 300ms`)
  *Use for:* Page transitions, accordions expanding.
* **The Snappy Exit**:
  `cubic-bezier(0.4, 0, 1, 1)` (Duration: `120ms - 180ms`)
  *Crucial Rule:* Exit animations must always be ~30%-40% faster than entrance animations.

### Micro-Distances:
* Never slide elements by 50px or 100px unless it's a full off-canvas drawer.
* Modals, popovers, and list items should move only **4px to 10px** along the Y axis while fading in (`opacity: 0 -> 1`, `transform: translateY(6px) -> translateY(0)`).

---

## 🎛️ 3. Tactile Micro-Interactions
* **Buttons / Clickables**:
  ```css
  .btn {
    transition: transform 120ms cubic-bezier(0.2, 0, 0, 1), background-color 150ms ease;
  }
  .btn:hover {
    transform: translateY(-1px);
  }
  .btn:active {
    transform: scale(0.97) translateY(0);
  }
  ```
* **Staggered Entry**:
  * Stagger delay between items should be **25ms to 35ms** (never more than 50ms, otherwise it feels sluggish).

---

## ♿ 4. Accessibility Requirement
Always include:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
