/// <reference types="node" />
import { describe, it, expect } from 'vitest'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// Regression guard for a config that once hardcoded a machine-specific
// absolute repo path, then (in a first fix attempt) used bare `__dirname`
// to derive it instead -- which throws `ReferenceError: __dirname is not
// defined` under Playwright's real Node ESM config loader, because
// src/frontend/package.json sets "type": "module". Vitest's own module
// runner (vite-node) silently polyfills `__dirname` even in ESM, so an
// ordinary `import()` of the config here would NOT catch that regression;
// only invoking Playwright's actual CLI does.
const frontendDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const playwrightCli = path.join(frontendDir, 'node_modules', '@playwright', 'test', 'cli.js')

describe('playwright demo config guard', () => {
  it('loads under Playwright\'s Node ESM config loader without throwing', () => {
    const output = execFileSync(
      process.execPath,
      [playwrightCli, 'test', '-c', 'playwright.demo.config.ts', '--list'],
      { cwd: frontendDir, encoding: 'utf-8' },
    )

    expect(output).toContain('Total: 1 test in 1 file')
  }, 30_000)
})
