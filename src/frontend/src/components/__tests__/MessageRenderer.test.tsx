import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MessageRenderer from '../MessageRenderer'

describe('MessageRenderer', () => {
  it('renders plain text content correctly', () => {
    render(<MessageRenderer content="Hello world" />)
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('renders text with *italic* markers as styled <em> elements', () => {
    render(<MessageRenderer content="*She looks up slowly.* Hello there!" />)
    const em = screen.getByText('She looks up slowly.')
    expect(em.tagName).toBe('EM')
    expect(screen.getByText('Hello there!')).toBeInTheDocument()
  })

  it('renders multiple italic segments', () => {
    render(<MessageRenderer content={'*Thinks* "Says something" *Acts*'} />)
    expect(screen.getByText('Thinks').tagName).toBe('EM')
    expect(screen.getByText('Acts').tagName).toBe('EM')
    expect(screen.getByText('"Says something"')).toBeInTheDocument()
  })

  it('handles empty content gracefully', () => {
    render(<MessageRenderer content="" />)
    expect(document.querySelector('.whitespace-pre-wrap')).toBeInTheDocument()
  })
})
