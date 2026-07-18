import React from 'react'
import Icon from './Icon'
import { type IconSize } from './iconSizes'

interface IconButtonProps {
  /** Material Symbols ligature name. */
  icon: string
  /**
   * Accessible name. Required: an icon-only control is invisible to screen
   * readers without it. Also used as the hover tooltip unless `title` overrides.
   */
  label: string
  size?: IconSize
  filled?: boolean
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void
  disabled?: boolean
  type?: 'button' | 'submit'
  /** Visual styling (colours, background). Layout/touch sizing is fixed here. */
  className?: string
  /** Tooltip text; defaults to `label`. */
  title?: string
  'aria-expanded'?: boolean
}

/**
 * Icon-only button with a guaranteed touch target (44px on mobile, 36px on
 * desktop) and a mandatory accessible label. This is the standard control for
 * the "remove the text, keep the icon" mobile pattern.
 */
const IconButton: React.FC<IconButtonProps> = ({
  icon,
  label,
  size = 'md',
  filled = false,
  onClick,
  disabled = false,
  type = 'button',
  className = '',
  title,
  'aria-expanded': ariaExpanded,
}) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled}
    aria-label={label}
    title={title ?? label}
    aria-expanded={ariaExpanded}
    className={`inline-flex items-center justify-center rounded-full shrink-0 min-h-11 min-w-11 md:min-h-9 md:min-w-9 transition-colors touch-manipulation active:scale-95 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${className}`}
  >
    <Icon name={icon} size={size} filled={filled} />
  </button>
)

export default IconButton
