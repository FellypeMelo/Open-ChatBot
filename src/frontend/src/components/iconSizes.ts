/**
 * The single icon size scale for the whole app. Five deliberate sizes replace
 * the ad-hoc `text-[Npx]` values that previously drove every glyph.
 */
export const ICON_SIZES = {
  xs: 16, // inline with tiny meta text / badges
  sm: 18, // dense action rows, message controls
  md: 22, // default: toolbars, nav, primary buttons
  lg: 28, // prominent / emphasis
  xl: 48, // empty-state illustrations
} as const

export type IconSize = keyof typeof ICON_SIZES
