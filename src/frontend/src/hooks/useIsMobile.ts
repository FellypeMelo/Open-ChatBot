import { useSyncExternalStore } from 'react'

/** Tailwind's `md` breakpoint. Below this we treat the viewport as mobile. */
const MOBILE_QUERY = '(max-width: 767px)'

const hasMatchMedia = () =>
  typeof window !== 'undefined' && typeof window.matchMedia === 'function'

function subscribe(onChange: () => void): () => void {
  if (!hasMatchMedia()) return () => {}
  const mql = window.matchMedia(MOBILE_QUERY)
  mql.addEventListener('change', onChange)
  return () => mql.removeEventListener('change', onChange)
}

const getSnapshot = () => (hasMatchMedia() ? window.matchMedia(MOBILE_QUERY).matches : false)

/**
 * True when the viewport is below the `md` breakpoint. Used to render the
 * mobile-only bottom tab bar (and to reserve space for it) without shipping a
 * duplicate nav into the desktop DOM. Backed by `useSyncExternalStore` so it
 * stays in sync with matchMedia without a setState-in-effect.
 */
export function useIsMobile(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, () => false)
}
