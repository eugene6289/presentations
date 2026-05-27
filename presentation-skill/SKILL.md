---
name: dark-report-deck
description: |
  Build a dark-themed 16:9 HTML presentation deck using the in-house "進度報告"
  visual system (sky/emerald accents, KPI dashboards, progress tables, repo
  health grids, AI-skills matrix with modal, timeline).

  **Trigger ONLY when** the user explicitly references this template — e.g.
  "用 presentation-skill 那套樣式"、"照上次網頁提升計畫進度報告的風格做一份"、
  "用我們報告的 deck template"、"用 dark-report-deck"、"參考 web-improvement
  presentation 的樣式". Do NOT trigger for generic "做一份簡報" / "做 slides" /
  ".pptx" requests — those should go through the pptx skill or a fresh design.
---

# Dark Report Deck

A reusable HTML presentation system for **internal monthly progress reports**.
The reference implementation lives at
`/Users/eugenechua/Projects/presentations/web-improvement/presentation.html`,
the editable skeleton is `./template.html` next to this file.

This is an **editable skill** — when the design system evolves (new tokens,
new components, new visual rules), update this file *and* `template.html` so
they stay in sync.

---

## 1. When to use

Use only when the user references this template by name or asks for "上次那套
風格" / 引用 web-improvement deck. For brand-new design requests, build fresh
instead — this skill is a *style lock-in*, not a generic deck generator.

---

## 2. Output convention

- Drop the new deck under `/Users/eugenechua/Projects/presentations/<topic>/presentation.html`
- After creation, append a new card to `/Users/eugenechua/Projects/presentations/index.html` (REPORT / SKILL / etc.)
- File the user views is a single self-contained `.html` (CSS + JS inline)

---

## 3. Architecture (don't break these)

**Stage / scaling**
- Fixed 1280×720 stage (`--slide-w`, `--slide-h`)
- `.stage` flex-centers `.slide-wrap`; `fitStage()` computes uniform scale so the deck fits any viewport
- All slides absolute-positioned inside `.slide-wrap`, toggled via `.active`

**Data → Renderer pattern**
- ALL slide content lives in the `slideData` object at the top of the `<script>` block
- Each slide is a pure render function `renderSlideX(): string` that consumes a slice of `slideData`
- The `renderers` array dictates slide order — reorder by editing this array, not by moving HTML
- Adding a slide = (1) add data block to `slideData`, (2) write `renderSlideN()`, (3) push to `renderers`

**Navigation**
- Keyboard: `←` / `→` / `Space` / `PageUp` / `PageDown` / `Home` / `End`
- Bottom nav pill with dots; clicking a dot jumps to that slide
- Modal blocks slide navigation (Esc closes modal)

---

## 4. Design system

### Color tokens (CSS custom properties on `:root`)

| Token | Value | Used for |
|---|---|---|
| `--bg` | `#0d0d0d` | Page / slide background |
| `--bg-2` | `#141414` | Card surface |
| `--bg-3` | `#1a1a1a` | Inner card / table head / nested surface |
| `--border` | `#262626` | Default card border |
| `--border-2` | `#333` | Stronger border (nav buttons, modal close) |
| `--text` | `#f5f5f5` | Primary text |
| `--text-dim` | `#a3a3a3` | Secondary text |
| `--text-mute` | `#737373` | Meta / labels / muted captions |
| `--accent` | `#38bdf8` (sky) | **Primary accent** — eyebrows, in-progress, links, buttons |
| `--accent-2` | `#10b981` (emerald) | **Success accent** — done / completed |
| `--accent-warn` | `#fbbf24` | Reserved (warn) |
| `--accent-danger` | `#f43f5e` | Reserved (danger) |

### Typography

- Primary: `'Inter', 'Noto Sans TC'` — body / titles
- Mono: `'JetBrains Mono'` — dates, metadata, code-like labels, nav pos
- Title scale: 36px (slide title), 23–24px (card title), 17–20px (subtitle/row title), 13–14px (eyebrow/meta)
- Eyebrow style: uppercase, `letter-spacing: 0.18em`, `--accent` colored

### Spacing

- Slide padding: `48px 64px`
- Card padding: `20px 22px` (compact) → `28px 32px` (feature)
- Card radius: `12px` (cards) / `8px` (inner stats) / `999px` (pills, buttons)
- Section gaps: `14–22px`

---

## 5. Visual language rules (the most important section)

These rules separate interactive affordances from information badges. **Do not
collapse them** — that's how everything ends up looking like a clickable button.

| Role | Treatment | Examples |
|---|---|---|
| **Button / link (interactive)** | **Outlined**: transparent-ish background `rgba(56,189,248,0.08)`, 1px solid `rgba(56,189,248,0.45)` border, accent text. Hover: bg `0.18`, border solid `--accent`, text `#fff`, `translateY(-1px)` | `.row-action` (查看進度 ↗), `.open-modal-btn` (modal 觸發器), `.nav button`, `.modal-close` |
| **Status pill (info)** | **Filled tag**: NO border, soft filled background `rgba(<accent>,0.14)`, accent text, optional `::before` dot. Cursor stays default. | `.pill.done`, `.pill.progress` |
| **KPI value / timeline node** | **Solid accent color** as foreground only (text/marker), no surrounding box | `.kpi .value.accent`, `.tl-item::before` |

**The rule of thumb:** if a user *can click it*, it has a border. If it just
*shows status*, it has a filled background and no border. If it's pure data,
it's just colored text/dot. Never mix.

---

## 6. Component catalog

All components live inside the `<style>` block of `template.html`. They render
through the data → renderer pattern in section 3.

### 6.1 Cover slide (`renderSlideCover`)
Centered title with accent rule above; date pinned to bottom in mono.
Data: `slideData.cover = { title, date }`.

### 6.2 Dashboard with KPI row (`renderSlide1`)
4-column `.kpi-row` + `.highlight-card` bullet summary.
- KPI tones: `success` (emerald), `accent` (sky), `highlight` (gradient bg)
- Data: `slideData.overview = { title, subtitle, lastUpdated, kpis[], highlights[] }`
- Each kpi: `{ value, label, hint, tone }`

### 6.3 Progress table (`renderSlide2` / `buildProgressRow`)
Table with 3 progress bars per row (Prepare / Execute / Verify) + status pill.
- `progressBar(pct)` colors itself: ≥100 → done (emerald), >0 → partial (sky), 0 → idle (gray)
- Data: array of `{ name, owner, date, prepare, execute, verify, status }`

### 6.4 Phase / focus card grid (`renderSlide2b`)
2-column card grid with title, owner, pain-point, current-state, 3-bar progress strip.
- `p2-grid-tall` modifier makes cards fill the body height
- Data: `{ name, owner, status, pain, progress, prepare, execute, verify }`

### 6.5 Repo health grid (`renderSlide3`)
2×2 grid of repos, each with 3 inner stat tiles (Lint / Security / CD).
- Data: `{ type, repo, tech, lint, security, cd }`

### 6.6 AI skills matrix + modal (`renderSlide4`)
Wide table: Skill / Owner / Note / 4 checkbox columns / Action button column.
- Last column conditionally renders `.row-action` (with `↗`) if `link` is set, otherwise `.row-action-empty` ("尚未提供")
- Top-right has `.open-modal-btn` (`⊕ 四大驗收標準`) → opens overlay modal listing acceptance criteria
- Data: `{ skillsList: [{ name, owner, note, feasibility, landing, doc, cross, link }], standards: [{ name, criterion }], todayNote }`

### 6.7 Timeline (`renderSlide5`)
Vertical timeline with dot + glow on current item.
- Modifiers: `.success` (emerald dot), `.current` (sky glow + `NOW` tag)
- Data: `{ when, title, detail, success, current }`

### 6.8 Modal (`#standardsModal`)
Generic overlay pattern: dark backdrop blur, centered card, close button top-right, Esc to close, click-outside to close. Pre-populated on mount from `slideData.aiSkills.standards`.

---

## 7. Adding a new slide

1. Add a new key to `slideData` with whatever shape you need
2. Write `renderSlideN()` returning a string with `.slide-header` + `.slide-body` skeleton
3. Push the function into `renderers` at the desired position
4. (Optional) If the slide uses a new component, add CSS scoped to a unique class root and document it in section 6 of this file

**Skeleton:**

```js
function renderSlideN() {
  const d = slideData.myNewKey;
  return `
  <div class="slide-header">
    <div class="left">
      <span class="eyebrow">PART X · 區段名</span>
      <h1 class="slide-title">${esc(d.title)}</h1>
      <div class="slide-subtitle">${esc(d.subtitle)}</div>
    </div>
    <div class="right">
      <!-- optional pill / button / meta -->
    </div>
  </div>
  <div class="slide-body">
    <!-- content -->
  </div>
  `;
}
```

---

## 8. Editing this skill

- **New token?** Add to `:root` in `template.html` *and* the token table here
- **New component?** Add CSS + renderer to `template.html`, document in section 6
- **New visual rule?** Update section 5 — that table is the source of truth
- **Want to change accent palette?** Edit `--accent` / `--accent-2` — every component pulls from these, so the whole deck re-tones in one place

Keep `template.html` runnable on its own (open it in a browser, see a placeholder deck). The placeholder data is intentional — it serves as a live preview while editing the design system.

---

## 9. Quick start (for Claude executing this skill)

1. Read `template.html` (sibling of this file)
2. Copy it to `/Users/eugenechua/Projects/presentations/<topic>/presentation.html`
3. Edit ONLY the `slideData` block — leave CSS / renderers / nav untouched unless the user explicitly asks for a design change
4. After writing, append a card to `/Users/eugenechua/Projects/presentations/index.html`
5. Share the file via a `computer://` link
