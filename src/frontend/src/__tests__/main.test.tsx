import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Keep this a pure bootstrap test: stub the real App tree so mounting it
// doesn't pull in the whole app's API calls/effects.
vi.mock('../App.tsx', () => ({
  default: () => null,
}))

const registerSW = vi.fn()
vi.mock('virtual:pwa-register', () => ({ registerSW }))

describe('main.tsx service worker registration', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>'
    vi.resetModules()
    registerSW.mockClear()
  })

  afterEach(() => {
    document.body.innerHTML = ''
    vi.unstubAllEnvs()
    // @ts-expect-error -- test-only cleanup of a property defined only for one case
    delete window.navigator.serviceWorker
  })

  it('does not attempt registration outside a production build', async () => {
    vi.stubEnv('PROD', false)
    Object.defineProperty(window.navigator, 'serviceWorker', {
      value: {},
      configurable: true,
    })

    await import('../main.tsx')

    expect(registerSW).not.toHaveBeenCalled()
  })

  it('does not attempt registration when the browser has no serviceWorker support', async () => {
    vi.stubEnv('PROD', true)

    await import('../main.tsx')

    expect(registerSW).not.toHaveBeenCalled()
  })

  it('registers the service worker in a production build when supported', async () => {
    vi.stubEnv('PROD', true)
    Object.defineProperty(window.navigator, 'serviceWorker', {
      value: {},
      configurable: true,
    })

    await import('../main.tsx')

    await vi.waitFor(() => {
      expect(registerSW).toHaveBeenCalledWith({ immediate: true })
    })
  })
})
