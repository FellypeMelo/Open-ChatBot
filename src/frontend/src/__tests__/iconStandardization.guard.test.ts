import { describe, it, expect } from 'vitest'

// Guards the icon-standardization work: every glyph must go through the <Icon>
// wrapper (the single place allowed to touch the raw Material Symbols class), so
// sizing/weight stay consistent. A raw `material-symbols-outlined` span in any
// component reintroduces the ad-hoc `text-[Npx]` sizing this refactor removed.
//
// Uses Vite's import.meta.glob (typed via the project's existing "vite/client"
// types) instead of node:fs so this compiles under the frontend's tsc build
// config, which has no Node type definitions.
const files = import.meta.glob('../**/*.tsx', { eager: true, query: '?raw', import: 'default' }) as Record<
  string,
  string
>

describe('icon standardization guard', () => {
  it('has no raw material-symbols-outlined spans outside the <Icon> wrapper', () => {
    const offenders = Object.entries(files)
      .filter(([path]) => !path.endsWith('/Icon.tsx') && !path.includes('__tests__/'))
      .filter(([, content]) =>
        content
          .split('\n')
          .some((line) => line.includes('material-symbols-outlined') && !line.trimStart().startsWith('import')),
      )
      .map(([path]) => path)

    expect(offenders, `Use <Icon> instead of a raw span in:\n${offenders.join('\n')}`).toEqual([])
  })
})
