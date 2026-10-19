---
paths:
  - "web/**"
---
# UI rules (loaded when touching web/)
- One page, no build step: `web/index.html`, `web/styles.css`, `web/app.js`. No framework, no bundler.
- Design tokens live in `:root` in `styles.css`; never hard-code a color or a font size in a component rule.
- Lanes keep the same anatomy: label, two tracks (original, record), live readouts (time, peak memory or gas), verdict chip.
- Readouts use the mono font with tabular numbers; units are always shown (s, GiB, gas).
- Respect `prefers-reduced-motion`: no animation beyond opacity when it is set.
- Check 1440x900 and 390x844 before closing a UI change.
