---
name: Obsidian Narrative
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c4c7c8'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8d9192'
  outline-variant: '#434748'
  surface-tint: '#c3c7c8'
  primary: '#ffffff'
  on-primary: '#2c3132'
  primary-container: '#dfe3e4'
  on-primary-container: '#606566'
  inverse-primary: '#5a5f60'
  secondary: '#adceb9'
  on-secondary: '#193627'
  secondary-container: '#2f4d3d'
  on-secondary-container: '#9cbda8'
  tertiary: '#ffffff'
  on-tertiary: '#372e2b'
  tertiary-container: '#efdfd9'
  on-tertiary-container: '#6d625d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dfe3e4'
  primary-fixed-dim: '#c3c7c8'
  on-primary-fixed: '#181c1d'
  on-primary-fixed-variant: '#434849'
  secondary-fixed: '#c9ebd5'
  secondary-fixed-dim: '#adceb9'
  on-secondary-fixed: '#022113'
  on-secondary-fixed-variant: '#2f4d3d'
  tertiary-fixed: '#efdfd9'
  tertiary-fixed-dim: '#d2c3be'
  on-tertiary-fixed: '#221a17'
  on-tertiary-fixed-variant: '#4f4541'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 0.5rem
  sm: 1rem
  md: 1.5rem
  lg: 2.5rem
  xl: 4rem
  container-max: 800px
---

## Brand & Style

This design system is built for deep focus and narrative immersion. It adopts an **Ultra-Minimalist Dark** aesthetic that prioritizes content over interface. The brand personality is quiet, sophisticated, and invisible, drawing inspiration from high-end terminal interfaces and literary platforms.

The target audience consists of writers, roleplayers, and power users who seek a distraction-free environment. The emotional response should be one of "infinite depth"—where the interface melts away, leaving only the user's interaction with the AI. There are no decorative elements; every line and pixel serves a functional or structural purpose.

## Colors

The palette is strictly dark-mode, anchored by a pure obsidian black background. Hierarchy is established through a grayscale of deep zinc and slate tones rather than traditional lighting or shadows.

- **Primary:** A soft, "paper" white used sparingly for high-emphasis text and primary actions.
- **Accent:** A muted emerald, used only for status indicators or subtle successes, evoking a vintage terminal feel without the glow.
- **Surfaces:** Very dark zinc is used for secondary containers; slate is used for hover states and interactive depth.
- **Borders:** Extremely low-contrast borders define structure without breaking the visual continuity of the black void.

## Typography

The system utilizes **Inter** for its neutral, utilitarian character and exceptional legibility at small sizes. For technical metadata and labels, a secondary monospaced font (**JetBrains Mono**) is used to provide a subtle structural contrast.

Text is the primary UI element. To maintain the minimalist aesthetic, line heights are generous (1.5x minimum) to ensure readability during long-form reading sessions. Font weights are kept between 400 and 600; heavy weights are avoided to prevent the UI from feeling "loud."

## Layout & Spacing

This design system employs a **Fixed Centered Grid** for narrative content. By constraining the maximum width of the reading area to 800px, we reduce eye strain and mimic the layout of a physical book or a clean manuscript.

- **Margins:** Generous "dead space" on the left and right sides focuses the eye on the center.
- **Rhythm:** An 8px linear scale guides vertical rhythm.
- **Mobile:** On smaller screens, margins shrink to 1rem (16px) to maximize horizontal real estate, but the single-column focus remains absolute.
- **Whitespace:** Spacing is used as a separator in place of lines or dividers wherever possible.

## Elevation & Depth

In a pure black environment, traditional shadows are ineffective. Instead, this design system uses **Tonal Layering** and **Subtle Outlines**:

1.  **Level 0 (Base):** #000000. The infinite void where the narrative lives.
2.  **Level 1 (Surfaces):** #09090B. Used for input areas or sidebars that need to feel slightly "closer" to the user.
3.  **Level 2 (Overlays):** #111111. Used for menus or modals, paired with a 1px border of #1A1A1A.

No glow, blur, or transparency is permitted. Depth is perceived solely through the subtle shift in black-to-zinc values.

## Shapes

The shape language is "Soft" (4px - 8px radius). This provides just enough curvature to prevent the UI from feeling aggressive or "brutalist," while maintaining a precise, engineered feel. 

Buttons and input fields use a consistent 4px radius. High-level containers like chat bubbles (if used) or profile images may use up to 8px. Circular elements are reserved exclusively for avatars.

## Components

**Buttons**
Primary buttons are solid soft-white with black text. Secondary buttons are transparent with a 1px zinc border and white text. There are no shadows; state changes are indicated by a slight increase in border brightness.

**Input Fields**
Minimalist text entry. No background box; only a bottom border that brightens from #1A1A1A to #333333 on focus. The cursor is a solid block or thin line in the accent emerald.

**Chat Rendering**
Avoid traditional bubbles. Instead, use "Direct Text" rendering where the name or avatar sits to the left, and the text flows naturally on the background. Use a subtle zinc vertical line to group long responses if necessary.

**Chips & Labels**
Small, monospaced text in #71717A. If interactive, they gain a 1px border.

**Cards**
Used only for character selection. No shadow. A 1px border of #0F172A which transitions to #1A1A1A on hover. Background remains pure black.