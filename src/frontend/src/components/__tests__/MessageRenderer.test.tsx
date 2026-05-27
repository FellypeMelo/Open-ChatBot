import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MessageRenderer from '../MessageRenderer'

describe('MessageRenderer', () => {
  it('renders plain text content correctly', () => {
    render(<MessageRenderer content="Hello world" />)
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('renders text with *italic* markers as styled elements', () => {
    render(<MessageRenderer content="*I hope they like this.* Hello there!" />)
    const thought = screen.getByText('I hope they like this.')
    expect(thought).toHaveClass('italic')
    expect(thought).toHaveClass('text-on-surface-variant/70')
    // Using a regex or function to match text that might have spaces/be split
    expect(screen.getByText(/Hello there!/)).toBeInTheDocument()
  })

  it('renders text with **bold** markers as action elements', () => {
    render(<MessageRenderer content="**She smiles warmly.** Hi!" />)
    const action = screen.getByText('She smiles warmly.')
    expect(action).toHaveClass('font-bold')
    expect(action).toHaveClass('text-primary')
    expect(screen.getByText(/Hi!/)).toBeInTheDocument()
  })

  it('renders mixed narrative markers correctly', () => {
    render(<MessageRenderer content="*Thinking...* **Acting!** Talking." />)
    const thought = screen.getByText('Thinking...')
    const action = screen.getByText('Acting!')
    const speech = screen.getByText(/Talking\./)

    expect(thought).toHaveClass('italic')
    expect(action).toHaveClass('font-bold')
    expect(speech).toBeInTheDocument()
  })

  it('handles nested-like markers with ** taking precedence', () => {
    render(<MessageRenderer content="**Bold *not* italic**" />)
    const action = screen.getByText('Bold *not* italic')
    expect(action).toHaveClass('font-bold')
  })

  it('handles empty content gracefully', () => {
    const { container } = render(<MessageRenderer content="" />)
    // First child is the div wrapper
    expect(container.firstChild).toHaveClass('whitespace-pre-wrap')
  })
})
