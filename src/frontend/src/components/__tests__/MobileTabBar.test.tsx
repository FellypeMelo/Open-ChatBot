import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import MobileTabBar from '../MobileTabBar'

describe('MobileTabBar', () => {
  it('renders the four primary destinations', () => {
    render(<MobileTabBar currentView="chat" setView={vi.fn()} />)
    expect(screen.getByText('Characters')).toBeInTheDocument()
    expect(screen.getByText('Chat')).toBeInTheDocument()
    expect(screen.getByText('Lore')).toBeInTheDocument()
    expect(screen.getByText('Tags')).toBeInTheDocument()
  })

  it('marks the current view as the active page', () => {
    render(<MobileTabBar currentView="library" setView={vi.fn()} />)
    const lore = screen.getByRole('button', { name: /Lore/ })
    expect(lore).toHaveAttribute('aria-current', 'page')
    const chat = screen.getByRole('button', { name: /Chat/ })
    expect(chat).not.toHaveAttribute('aria-current')
  })

  it('switches view when a tab is pressed', () => {
    const setView = vi.fn()
    render(<MobileTabBar currentView="chat" setView={setView} />)
    fireEvent.click(screen.getByRole('button', { name: /Tags/ }))
    expect(setView).toHaveBeenCalledWith('archives')
  })
})
