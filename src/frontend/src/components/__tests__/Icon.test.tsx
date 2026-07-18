import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Icon from '../Icon'
import IconButton from '../IconButton'
import { ICON_SIZES } from '../iconSizes'

describe('Icon', () => {
  it('renders the ligature name as text content', () => {
    render(<Icon name="menu" title="Open menu" />)
    expect(screen.getByText('menu')).toBeInTheDocument()
  })

  it('maps the size token to a fixed pixel font-size', () => {
    render(<Icon name="send" size="sm" title="Send" />)
    const el = screen.getByText('send')
    expect(el.style.fontSize).toBe(`${ICON_SIZES.sm}px`)
  })

  it('defaults to md (22px)', () => {
    render(<Icon name="close" title="Close" />)
    expect(screen.getByText('close').style.fontSize).toBe(`${ICON_SIZES.md}px`)
  })

  it('is decorative (aria-hidden) when no title is given', () => {
    const { container } = render(<Icon name="star" />)
    const el = container.querySelector('.material-symbols-outlined')
    expect(el?.getAttribute('aria-hidden')).toBe('true')
  })

  it('is an accessible img when a title is given', () => {
    render(<Icon name="star" title="Favourite" />)
    expect(screen.getByRole('img', { name: 'Favourite' })).toBeInTheDocument()
  })

  it('applies the FILL axis when filled', () => {
    render(<Icon name="favorite" filled title="Liked" />)
    const el = screen.getByText('favorite')
    expect(el.style.fontVariationSettings).toContain("'FILL' 1")
  })
})

describe('IconButton', () => {
  it('exposes the label as the accessible name', () => {
    render(<IconButton icon="delete" label="Delete message" />)
    expect(screen.getByRole('button', { name: 'Delete message' })).toBeInTheDocument()
  })

  it('fires onClick when pressed', () => {
    const onClick = vi.fn()
    render(<IconButton icon="add" label="New chat" onClick={onClick} />)
    screen.getByRole('button', { name: 'New chat' }).click()
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not fire onClick when disabled', () => {
    const onClick = vi.fn()
    render(<IconButton icon="add" label="New chat" onClick={onClick} disabled />)
    screen.getByRole('button', { name: 'New chat' }).click()
    expect(onClick).not.toHaveBeenCalled()
  })

  it('hides the inner glyph from assistive tech (label lives on the button)', () => {
    const { container } = render(<IconButton icon="send" label="Send" />)
    const glyph = container.querySelector('.material-symbols-outlined')
    expect(glyph?.getAttribute('aria-hidden')).toBe('true')
  })
})
