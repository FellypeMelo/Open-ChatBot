# Mobile real-device LAN smoke test

A short manual pass to run on an actual phone whenever mobile-facing UI
changes. This is **not** a substitute for the automated suite — it exists
specifically to catch what automation structurally cannot (see the last
section). Takes about 5 minutes.

## 1. Get it running on the LAN

1. From the repo root, run `run.bat` (no `local` argument — that binds
   localhost-only and phones can't reach it).
2. It builds the frontend, then prints the LAN IP itself, e.g.:
   ```
   LAN mode ON. On your phone (same Wi-Fi) open:
       http://192.168.1.23:8000
   ```
   No need to run `ipconfig` — the console output is the URL to use. If it
   ever fails to detect an IP, fall back to `ipconfig` (look for the IPv4
   address on your Wi-Fi/Ethernet adapter) and build the URL yourself.
3. On first connection you may get a Windows Firewall prompt on the PC —
   allow Python on **private networks**.
4. Open that `http://<lan-ip>:8000` URL in the phone's browser (Safari on
   iOS, Chrome on Android — check both if you're touching layout/viewport
   code).

## 2. Checklist

- [ ] **Sidebar hamburger** — tap to open, backdrop appears, tap backdrop
  (or hamburger again) to close. No layout jump.
- [ ] **Bottom tab bar** (`MobileTabBar`) — visible at the bottom on mobile
  widths, switches between views (Chat/Characters/Library/etc.), the active
  tab is visually distinct.
- [ ] **Send a message** — composer auto-grows as you type a multi-line
  prompt (does not stay locked to one line); after sending, tap a message's
  action buttons (Regenerate / Edit / Delete / Copy ID) directly — they must
  be tappable on first touch, with **no hover step** required.
- [ ] **Stats HUD** — collapse/expand toggle works on the mobile summary
  chip; expanded grid is legible and stat +/- controls are hittable with a
  thumb.
- [ ] **No horizontal scroll/overflow** — swipe/scroll sideways on each main
  screen (Characters, Chat, Lorebook, Tags) and confirm the page never pans
  horizontally, no matter which screen or modal you're on.
- [ ] **Keyboard vs. composer** (⚠️ known-weaker area — watch this one
  closely). Tap the chat input to bring up the on-screen keyboard and check
  that the composer and Send button are still visible above it, not hidden
  behind the keyboard or a home-bar/gesture area. Only safe-area padding has
  shipped so far; there's no `visualViewport` resize handling yet, so this
  is the most likely thing to still be broken, especially on Android Chrome
  or with a floating/split keyboard. Report exactly what you see (fully
  hidden input, partially covered, fine) rather than a pass/fail — this is
  expected to need follow-up work.
- [ ] **Add to Home Screen / PWA install** — on iOS Safari use Share → "Add
  to Home Screen"; on Android Chrome use the install prompt (menu → "Install
  app", or the automatic banner). Confirm a real icon shows (not a blank/
  broken image) and the installed app opens standalone (no browser chrome).

## 3. Why this can't be replaced by Playwright

CI now runs Playwright's `mobile-chrome` (Pixel 5) and `mobile-safari`
(iPhone 13) device emulation projects. That coverage is real and should stay
green, but device emulation cannot reproduce:

- iOS Safari's actual `100dvh` behavior as the address bar shows/hides.
- Real `env(safe-area-inset-*)` values on a notched/home-indicator device.
- Native momentum scrolling and on-screen keyboard occlusion.
- Real "Add to Home Screen" install and standalone-mode rendering.

Emulation checks the DOM/CSS logic; this checklist checks what an actual
browser engine does with it. Run both — automated tests on every change,
this manual pass before shipping anything that touches mobile layout, the
composer, the HUD, safe-area, or the manifest/service worker.
