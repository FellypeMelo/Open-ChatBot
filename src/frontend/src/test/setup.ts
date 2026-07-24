import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = vi.fn()

// jsdom has no matchMedia. Default every media query to "no match" so
// components gated on a viewport (e.g. the mobile bottom tab bar via
// useIsMobile) render their desktop branch under test.
window.matchMedia =
  window.matchMedia ||
  ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }) as unknown as MediaQueryList)
