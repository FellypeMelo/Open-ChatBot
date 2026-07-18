import React from 'react'
import { ICON_SIZES, type IconSize } from './iconSizes'

interface IconProps {
  /** Material Symbols ligature name, e.g. "menu", "send", "delete". */
  name: string
  /** Fixed size token. Defaults to `md` (22px). */
  size?: IconSize
  /** Render the filled variant (FILL axis) instead of the outline. */
  filled?: boolean
  className?: string
  /**
   * When set, the icon is exposed to assistive tech with this label and a
   * tooltip. Omit it (the default) for decorative icons that sit next to a
   * visible text label -- those are hidden from the a11y tree.
   */
  title?: string
}

/**
 * A Material Symbols glyph at a fixed size with a locked weight/grade/optical
 * size. Decorative by default (`aria-hidden`); pass `title` to make it a
 * labelled `img`. Icon-only controls should instead put the label on the
 * wrapping `<IconButton>`.
 */
const Icon: React.FC<IconProps> = ({ name, size = 'md', filled = false, className = '', title }) => {
  const px = ICON_SIZES[size]
  const a11y = title
    ? { role: 'img' as const, 'aria-label': title, title }
    : { 'aria-hidden': true }
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={{
        fontSize: `${px}px`,
        // Lock the variable-font axes so every icon shares one visual weight
        // regardless of where it is used.
        fontVariationSettings: `'FILL' ${filled ? 1 : 0}, 'wght' 400, 'GRAD' 0, 'opsz' ${px}`,
        lineHeight: 1,
      }}
      {...a11y}
    >
      {name}
    </span>
  )
}

export default Icon
