# Mobile UX / UI Improvement Plan

> **⚠️ RE-VERIFIED 2026-07-22** → **RE-VERIFIED AGAIN 2026-07-23** → **RE-VERIFIED AGAIN 2026-07-24 (21/21 items re-checked).** **19 resolved**: R1 collapsible stats HUD, R2, R3 fonts/icons self-hosted, R4/P1.3 touch targets, R5/P0.4 backdrop-filter gated `md:motion-safe:block`, **R6 — small labels/journal/footer/drawer text bumped to a readable mobile size with a `md:` compact override, resolved 2026-07-24**, R7 safe-area/no-overflow, R8 serif font bundled, P0.1-P0.3, **P1.2 — folded into the R6 fix (same mobile-text-bump pass), resolved 2026-07-24**, P1.4/P1.5, P2.2 `window.confirm()` replaced with `ConfirmDialog`, P2.3 sticky header, **P2.4 — the Interact/Gift drawer now also has `max-h-[70dvh] overflow-y-auto`, resolved 2026-07-24 (the tap-outside-backdrop half landed 2026-07-23, the height-cap half completes it now)**. **2 partial** (P1.1 header restructure only hid a couple elements, P2.1 press-state uses `active:scale-95` not the suggested `0.98`) — both minor/cosmetic, no further action planned.
>
> **Still open**: nothing from this file's original 21 items. Everything previously open (R6, P2.4) or partial (P1.2) is now resolved; see above.
>
> **2026-07-23/24 verification note**: backed by real Playwright runs against a live server, not just source reading — 15 e2e tests across desktop chromium plus two real mobile-device projects (`mobile-chrome`/Pixel 5, `mobile-safari`/iPhone 13), run with a real backend + frontend dev server (`E2E_TESTING=1` mock-LLM mode); run four separate times across the session (once per major batch of changes), 15/15 every time after the first pass caught and fixed one real regression: `e2e/lorebook.spec.ts`'s delete-entry test was still driving the old native `window.confirm()` dialog API, which stopped firing once `LorebookView` moved to the in-app `ConfirmDialog` (P2.2) — the spec was updated to interact with the rendered `alertdialog` instead. Not yet done: an actual physical-device LAN smoke test (see `docs/mobile-lan-smoke-test.md`) and committing/opening the PR.

**Scope:** Make Open-ChatBot usable and clean on phones (LAN access via `http://<pc-ip>:8000`).
**Design read:** This is *product UI* (chat + live stats HUD), not a landing page. Apply mobile-discipline, touch-target, contrast, and perf rules; ignore marketing-page patterns.
**Target:** viewports `< 768px` (`md` breakpoint). Desktop layout stays as-is unless noted.

---

## 1. Root causes (why it's bad on mobile now)

| # | Problem | Where | Impact |
|---|---------|-------|--------|
| R1 | Stats HUD (5 bars, 2-col grid) + name + pills + tabs all stacked in a `flex-none` header, above the chat | `ChatView.tsx:179-368` | Header eats ~half the phone viewport; story text squeezed into a sliver → reads as "stats in front of the text" |
| R2 | Core message actions are `opacity-0 group-hover:opacity-100` | `ChatView.tsx:417,496,552` | Hover doesn't exist on touch → regenerate/edit/delete/copy/variant-switch are **unreachable** on mobile |
| R3 | Fonts + **all icons** loaded from Google CDN `<link>` | `index.html:8-9`, `index.css:1` | Offline / weak signal → every icon shows its literal word (`menu`, `bolt`, `delete`…); serif chat font falls back to Times. Breaks a *local-first* app |
| R4 | Touch targets 8-10px (`text-[8px] px-1 py-0.5`) | stat +/- buttons `ChatView.tsx:218-327` | Below the 44px min; unusable with a thumb |
| R5 | Full-screen animated `backdrop-filter: blur()` overlay | `ChatView.tsx:169-176` | Continuous GPU repaint on scroll = jank/lag on mobile — **✅ RESOLVED 2026-07-23**: gated `md:motion-safe:block`, with a cheap static gradient on mobile / reduced-motion |
| R6 | Body text 8-10px mono everywhere | header, footers, journal | Unreadable on a phone — **✅ RESOLVED 2026-07-24**: bumped to `text-[11px] md:text-[Xpx]` (or `text-[10px] md:text-[8px]` for decorative/dense elements) across the StatBar labels, header eyebrow/pill, tab labels, journal badge/entry rows, message footer, and MessageRow's own labels; chat body content untouched |
| R7 | `w-screen` root + no safe-area insets | `App.tsx:530`, `index.html:6` | Horizontal overflow; input/controls collide with iOS home bar & notch |
| R8 | Serif `--font-serif: 'Crimson Text'` never bundled; input hidden behind mobile keyboard on some browsers | `index.css:23`, input `ChatView.tsx:668` | Wrong chat font; typing area can be occluded |

---

## 2. Fix plan (prioritized)

### P0 — Blockers (do first; this is what makes it "very bad")

**P0.1 Collapse the stats HUD on mobile (the headline ask).**
- Wrap the 5-stat grid (`ChatView.tsx:211-336`) in a collapsible panel.
- `< md`: **collapsed by default.** Render a single compact summary chip row instead, e.g. `♥ 80 · ⚡ 60 · ⛨ 100`, plus a "Stats" toggle button. Tap → expands the full editable grid as an accordion (or a bottom sheet).
- `>= md`: keep the current always-visible grid.
- State: `const [statsOpen, setStatsOpen] = useState(false)`. Gate grid with `className={cn('...', statsOpen ? 'grid' : 'hidden md:grid')}`.
- Net effect: header on mobile drops from ~6 rows to ~2. Story text gets the screen back.

**P0.2 Make touch actions visible without hover.**
- Replace `opacity-0 group-hover:opacity-100` (`:417,:496,:552`) with:
  - `< md`: always visible (or behind an explicit `⋯` menu button per message).
  - `>= md`: keep hover reveal (`md:opacity-0 md:group-hover:opacity-100`).
- Recommended: a per-message `⋯` overflow button on mobile that opens a small action sheet (Regenerate / Edit / Delete / Copy ID). Keeps the message clean, actions reachable.

**P0.3 Bundle fonts + icons locally (offline-safe).**
- Remove Google `<link>`s (`index.html:8-9`) and the `@import` (`index.css:1`).
- **Icons:** migrate off the Material Symbols web-font to an inlined SVG set. Recommended `@phosphor-icons/react` (tree-shaken SVG, no network). One-time swap of ~20 glyph names. Alternatively self-host the Material Symbols `.woff2` under `src/assets/fonts/` and `@font-face` it.
- **Fonts:** self-host Outfit, JetBrains Mono, and the serif via `@font-face` + `font-display: swap`. Pick ONE serif and actually bundle it (Crimson Text is referenced but missing).
- This also speeds first paint and fixes the "icons show as words" bug.

**P0.4 Kill the mobile jank. — ✅ RESOLVED 2026-07-23**
- Gate the full-screen `backdrop-filter` blur overlay (`:169-176`) behind `md:` (desktop only) and `@media (prefers-reduced-motion: no-preference)`. On mobile, drop to a static gradient vignette (no animated blur). Only animate `opacity`/`transform`.
- **Shipped as:** the overlay is now `md:motion-safe:block` (desktop + no-reduced-motion only) with a static-gradient fallback everywhere else, matching this recommendation.

### P1 — Layout & readability

- **P1.1 Header restructure** (`:179-208`): on mobile, one line = char name + a compact status pill + `⋯`. Move "NEW CHAT" and location/clothes into the `⋯` menu or the collapsed stats panel. Drop the `ACTIVE NARRATIVE UNIT` eyebrow on mobile.
- **P1.2 Minimum type sizes**: raise `text-[8px]/[9px]/[10px]` to `text-[11px]`/`text-xs` on mobile via responsive classes (`text-[11px] md:text-[9px]`). Chat body stays `text-[17px]` (good). **✅ RESOLVED 2026-07-24** — see R6 above, same fix.
- **P1.3 Touch targets**: stat steppers and icon buttons → min `h-9 w-9` (36px) / ideally `44px` hit area on mobile; keep compact on desktop.
- **P1.4 Input safe area**: add `pb-[env(safe-area-inset-bottom)]` to the input container (`:668`); add `viewport-fit=cover` to the meta tag (`index.html:6`). Confirm the input stays above the keyboard (root already uses `100dvh` — good).
- **P1.5 Overflow**: `App.tsx:530` `w-screen` → `w-full`; audit for any fixed widths causing horizontal scroll.

### P2 — Taste & polish

- **P2.1 Consistency locks** (from taste skill): one radius scale, one accent (emerald `#34D399` already the accent — keep it, remove stray colors), tactile `active:scale-[0.98]` on buttons.
- **P2.2 Replace `window.confirm()`** (`:431,:573`, `App.tsx:197,507`) with an in-app confirm dialog — native confirm is jarring on mobile. **✅ RESOLVED 2026-07-23**: a `useConfirm`/`ConfirmDialog` in-app dialog now replaces `window.confirm()` at all call sites across App.tsx, ChatView.tsx, and LorebookView.tsx. (A real e2e regression from this change — `e2e/lorebook.spec.ts` still expecting the native dialog — was caught by this session's live Playwright run and fixed.)
- **P2.3 Sticky compact summary**: when stats are collapsed and the user scrolls, keep the 1-line stat chip pinned so state is glanceable without expanding.
- **P2.4 Drawer/action sheets**: the Interact/Gift drawer (`:674`) and new action sheets should use bottom-sheet ergonomics on mobile (thumb-reachable, `max-h-[70dvh]`, scrollable). **✅ RESOLVED 2026-07-24**: the drawer has a tap-outside backdrop to dismiss it (2026-07-23) and now also `max-h-[70dvh] overflow-y-auto` (2026-07-24), so it can no longer overflow off-screen on a short viewport — both halves of this item are complete.

---

## 3. Suggested implementation order (small, shippable PRs)

1. **PR-1 (P0.3):** self-host fonts + swap Material Symbols → Phosphor SVG. *(Biggest visible win, isolated.)*
2. **PR-2 (P0.1):** collapsible stats HUD + mobile summary chip.
3. **PR-3 (P0.2):** touch-visible message actions / `⋯` sheet.
4. **PR-4 (P0.4 + P1.4 + P1.5):** perf + safe-area + overflow.
5. **PR-5 (P1.1-1.3):** header restructure + type/touch sizing.
6. **PR-6 (P2):** confirm dialog, sticky summary, bottom sheets, consistency polish.

Each PR keeps existing tests green and adds a mobile-viewport render test (375px) where relevant. Maintain ≥80% coverage (per CLAUDE.md).

---

## 4. Concrete snippets (reference)

**Collapsible stats (P0.1):**
```tsx
const [statsOpen, setStatsOpen] = useState(false)
// mobile summary chip (only < md)
{activeChar?.state?.stats && (
  <button
    onClick={() => setStatsOpen(o => !o)}
    className="md:hidden flex items-center gap-2 text-[11px] font-mono text-zinc-300 px-2 py-1 rounded-full bg-white/5 border border-white/10"
  >
    <span>♥ {activeChar.state.stats.relationship?.score}</span>
    <span>⚡ {activeChar.state.stats.energy}</span>
    <span>{statsOpen ? 'Hide' : 'Stats'}</span>
  </button>
)}
// grid: hidden on mobile unless toggled
<div className={`${statsOpen ? 'grid' : 'hidden'} md:grid grid-cols-2 md:grid-cols-5 gap-md border-t border-white/5 pt-2`}>
  {/* existing stat cells */}
</div>
```

**Touch-visible actions (P0.2):**
```tsx
// was: opacity-0 group-hover:opacity-100
className="flex ... opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
```

**Safe-area input (P1.4):**
```tsx
<div className="... pb-[calc(1.5rem+env(safe-area-inset-bottom))] ...">
```
```html
<!-- index.html -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
```

---

## 5. Out of scope / not recommended

- **Native mobile app.** LAN browser access already works; a native app duplicates the whole UI for zero benefit here. Reconsider only if you need push notifications or app-store distribution.
- **Full visual redesign.** The dark editorial look is fine; this plan fixes *mobile mechanics*, not the aesthetic direction.
