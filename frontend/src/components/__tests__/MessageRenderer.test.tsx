import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MessageRenderer from '../MessageRenderer'

describe('MessageRenderer', () => {
  it('renders speech content correctly', () => {
    const fallback = { content: 'Hello world' }
    render(<MessageRenderer fallback={fallback} />)
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('renders thought blocks with italic styling', () => {
    const sequence = [{ type: 'thought', content: 'Hmm...' }] as any
    render(<MessageRenderer sequence={sequence} />)
    const thought = screen.getByText('Hmm...')
    expect(thought).toHaveClass('font-serif')
    expect(thought).toHaveClass('italic')
  })

  it('applies spatial-field class', () => {
    const fallback = { content: 'Test' }
    const { container } = render(<MessageRenderer fallback={fallback} />)
    expect(container.querySelector('.spatial-field')).toBeInTheDocument()
  })

  it('renders with revealing animation when isLatest is true', () => {
    const fallback = { content: 'This is a long test message' }
    const { container } = render(<MessageRenderer fallback={fallback} isLatest={true} />)
    // Should contain animated spans
    expect(container.querySelector('.animate-word-reveal')).toBeInTheDocument()
  })

  it('renders instantly when isLatest is false', () => {
    const fallback = { content: 'Instant message' }
    const { container } = render(<MessageRenderer fallback={fallback} isLatest={false} />)
    expect(container.querySelector('.animate-word-reveal')).not.toBeInTheDocument()
    expect(screen.getByText('Instant message')).toBeInTheDocument()
  })

  it('renders sequence blocks correctly', () => {
    const sequence: any[] = [
      { type: 'speech', content: 'Hello' },
      { type: 'thought', content: 'Think' },
      { type: 'action', content: 'Walk' }
    ]
    render(<MessageRenderer sequence={sequence} />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Think')).toBeInTheDocument()
    expect(screen.getByText('Walk')).toBeInTheDocument()
  })

  it('renders fallback actions and thoughts', () => {
    const fallback = {
      content: 'Main content',
      thought: 'Internal thought',
      actions: ['Action 1', 'Action 2']
    }
    render(<MessageRenderer fallback={fallback} />)
    expect(screen.getByText('Main content')).toBeInTheDocument()
    expect(screen.getByText('Internal thought')).toBeInTheDocument()
    expect(screen.getByText('**Action 1** **Action 2**')).toBeInTheDocument()
  })

  it('applies action styling to action blocks', () => {
    const sequence: any[] = [{ type: 'action', content: 'Runs' }]
    render(<MessageRenderer sequence={sequence} />)
    const action = screen.getByText('Runs')
    expect(action).toHaveClass('font-bold')
    expect(action).toHaveClass('text-zinc-300')
  })

  it('RevealingText clusters words correctly', () => {
    const fallback = { content: 'one two three four five six seven eight nine' }
    const { container } = render(<MessageRenderer fallback={fallback} isLatest={true} />)
    const spans = container.querySelectorAll('.animate-word-reveal')
    // targetWordsPerCluster is 4. 
    // "one two three four " (4 words)
    // "five six seven eight " (4 words)
    // "nine" (1 word)
    // Total 3 clusters
    expect(spans.length).toBe(3)
  })
})
