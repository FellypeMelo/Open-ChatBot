import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { arePropsEqual } from '../messageRowEquality'
import type { MessageRowProps } from '../messageRowEquality'
import ChatView from '../ChatView'
import * as api from '../../services/api'
import type { MessageNode } from '../../hooks/useMessageTree'
import type { Character } from '../../services/api'

vi.mock('../../services/api', () => ({
  fetchJournal: vi.fn()
}))

// A non-memoized stand-in for MessageRenderer so its call count is a direct,
// unambiguous proxy for "did the enclosing MessageRow's render body actually
// execute this pass" -- the real MessageRenderer is itself memoized on
// `content`, which would mask MessageRow's own memoization behavior.
const { messageRendererSpy } = vi.hoisted(() => ({ messageRendererSpy: vi.fn() }))
vi.mock('../MessageRenderer', () => ({
  default: (props: { content: string }) => {
    messageRendererSpy(props)
    return <div>{props.content}</div>
  }
}))

const baseCharacter: Character = {
  id: 1,
  name: 'Aria',
  description: 'A test persona',
  is_active: true,
  tags: []
}

const noop = () => {}

function makeProps(overrides: Partial<MessageRowProps> = {}): MessageRowProps {
  return {
    msg: { id: 1, parent_id: null, role: 'assistant', content: 'Hello', variant_index: 0 },
    characterName: 'Aria',
    isEditing: false,
    editContent: '',
    isStreaming: false,
    displayedContent: '',
    isLoading: false,
    isCopied: false,
    hasSiblings: false,
    currentIndex: 0,
    siblingsLength: 1,
    onEditStart: noop,
    onEditChange: noop,
    onEditCancel: noop,
    onEditSave: noop,
    onDelete: noop,
    onRegenerate: noop,
    onCopyId: noop,
    onPrevVariant: noop,
    onNextVariant: noop,
    ...overrides
  }
}

describe('MessageRow arePropsEqual (memoization comparator)', () => {
  it('treats identical props as equal (bails out)', () => {
    const props = makeProps()
    expect(arePropsEqual(props, { ...props })).toBe(true)
  })

  it('gates on msg content changing', () => {
    const prev = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'A', variant_index: 0 } })
    const next = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'B', variant_index: 0 } })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on msg.request_id arriving (e.g. stream done event)', () => {
    const prev = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'A', variant_index: 0, request_id: undefined } })
    const next = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'A', variant_index: 0, request_id: 'req-1' } })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('treats a new msg object with identical rendered fields as equal', () => {
    const prev = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'A', variant_index: 0 } })
    // Different object reference, different variant_index (not rendered by
    // this row), but every field MessageRow actually renders is the same.
    const next = makeProps({ msg: { id: 1, parent_id: null, role: 'assistant', content: 'A', variant_index: 7 } })
    expect(arePropsEqual(prev, next)).toBe(true)
  })

  it('gates on characterName', () => {
    const prev = makeProps({ characterName: 'Aria' })
    const next = makeProps({ characterName: 'Different Name' })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on isEditing', () => {
    const prev = makeProps({ isEditing: false })
    const next = makeProps({ isEditing: true })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on isStreaming', () => {
    const prev = makeProps({ isStreaming: false })
    const next = makeProps({ isStreaming: true })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on displayedContent ONLY when isStreaming is true for this row', () => {
    const notStreamingPrev = makeProps({ isStreaming: false, displayedContent: 'foo' })
    const notStreamingNext = makeProps({ isStreaming: false, displayedContent: 'foo bar baz' })
    expect(arePropsEqual(notStreamingPrev, notStreamingNext)).toBe(true)

    const streamingPrev = makeProps({ isStreaming: true, displayedContent: 'foo' })
    const streamingNext = makeProps({ isStreaming: true, displayedContent: 'foo bar baz' })
    expect(arePropsEqual(streamingPrev, streamingNext)).toBe(false)
  })

  it('gates on isLoading even though this row never reads it directly (guards stale callback closures)', () => {
    const prev = makeProps({ isLoading: false })
    const next = makeProps({ isLoading: true })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on isCopied', () => {
    const prev = makeProps({ isCopied: false })
    const next = makeProps({ isCopied: true })
    expect(arePropsEqual(prev, next)).toBe(false)
  })

  it('gates on sibling/variant info', () => {
    expect(arePropsEqual(makeProps({ hasSiblings: false }), makeProps({ hasSiblings: true }))).toBe(false)
    expect(arePropsEqual(makeProps({ currentIndex: 0 }), makeProps({ currentIndex: 1 }))).toBe(false)
    expect(arePropsEqual(makeProps({ siblingsLength: 1 }), makeProps({ siblingsLength: 2 }))).toBe(false)
  })

  it('gates on editContent ONLY while isEditing is true', () => {
    const notEditingPrev = makeProps({ isEditing: false, editContent: 'draft one' })
    const notEditingNext = makeProps({ isEditing: false, editContent: 'draft two' })
    expect(arePropsEqual(notEditingPrev, notEditingNext)).toBe(true)

    const editingPrev = makeProps({ isEditing: true, editContent: 'draft one' })
    const editingNext = makeProps({ isEditing: true, editContent: 'draft two' })
    expect(arePropsEqual(editingPrev, editingNext)).toBe(false)
  })

  it('ignores callback prop identity entirely -- fresh closures every render never force a re-render by themselves', () => {
    const prev = makeProps({ onRegenerate: () => 'a', onDelete: () => 'b', onEditStart: () => 'c' })
    const next = makeProps({ onRegenerate: () => 'x', onDelete: () => 'y', onEditStart: () => 'z' })
    expect(arePropsEqual(prev, next)).toBe(true)
  })
})

describe('MessageRow memoization via ChatView (render-count integration)', () => {
  let onSend: ReturnType<typeof vi.fn>
  let onRegenerate: ReturnType<typeof vi.fn>
  let onUpdateState: ReturnType<typeof vi.fn>
  let onClearChat: ReturnType<typeof vi.fn>
  let onSendAction: ReturnType<typeof vi.fn>
  let onEditMessage: ReturnType<typeof vi.fn>
  let onDeleteMessage: ReturnType<typeof vi.fn>
  let setInput: ReturnType<typeof vi.fn>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let defaultProps: any

  beforeEach(() => {
    vi.clearAllMocks()
    messageRendererSpy.mockClear()
    onSend = vi.fn()
    onRegenerate = vi.fn()
    onUpdateState = vi.fn().mockResolvedValue(undefined)
    onClearChat = vi.fn()
    onSendAction = vi.fn().mockResolvedValue(undefined)
    onEditMessage = vi.fn().mockResolvedValue(undefined)
    onDeleteMessage = vi.fn().mockResolvedValue(undefined)
    setInput = vi.fn()

    defaultProps = {
      activeChar: baseCharacter,
      messages: [],
      input: '',
      setInput,
      onSend,
      onRegenerate,
      isLoading: false,
      onUpdateState,
      onClearChat,
      onSendAction,
      onEditMessage,
      onDeleteMessage
    }

    vi.mocked(api.fetchJournal).mockResolvedValue([])
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('editing a user message does not re-render an unrelated assistant row', () => {
    const messages: MessageNode[] = [
      { id: 1, parent_id: null, role: 'user', content: 'Hello', variant_index: 0 },
      { id: 2, parent_id: 1, role: 'assistant', content: 'Untouched reply', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} messages={messages} />)

    expect(screen.getByText('Untouched reply')).toBeInTheDocument()
    const rendersAfterMount = messageRendererSpy.mock.calls.length
    expect(rendersAfterMount).toBeGreaterThan(0)

    fireEvent.click(screen.getByTitle('Edit'))
    expect(screen.getByDisplayValue('Hello')).toBeInTheDocument()

    // The assistant row's MessageRenderer must not have been invoked again --
    // none of its gated props (msg identity, isEditing, isStreaming, isLoading,
    // isCopied, sibling info) changed as a result of editing a different row.
    expect(messageRendererSpy.mock.calls.length).toBe(rendersAfterMount)
    expect(screen.getByText('Untouched reply')).toBeInTheDocument()
  })

  it('only the streaming row re-renders on each token -- a finished sibling row stays byte-identical and is not re-invoked', () => {
    vi.useFakeTimers()

    const messages: MessageNode[] = [
      { id: 1, parent_id: null, role: 'user', content: 'First', variant_index: 0 },
      { id: 2, parent_id: 1, role: 'assistant', content: 'Old reply', variant_index: 0 },
      { id: 3, parent_id: 2, role: 'user', content: 'Second', variant_index: 0 },
      { id: 4, parent_id: 3, role: 'assistant', content: '', variant_index: 0 }
    ]
    const { rerender } = render(
      <ChatView
        {...defaultProps}
        messages={messages}
        isLoading
        streamingMessageId={4}
        streamingContent=""
      />
    )

    expect(screen.getByText('Old reply')).toBeInTheDocument()
    const finishedRowCallsAfterMount = messageRendererSpy.mock.calls.filter(
      (call) => call[0].content === 'Old reply'
    ).length
    expect(finishedRowCallsAfterMount).toBeGreaterThan(0)

    ;['H', 'He', 'Hel', 'Hell', 'Hello'].forEach((content) => {
      rerender(
        <ChatView
          {...defaultProps}
          messages={messages}
          isLoading
          streamingMessageId={4}
          streamingContent={content}
        />
      )
    })

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    // The streaming row picked up the fully drained text...
    expect(screen.getByText('Hello')).toBeInTheDocument()
    // ...while the finished sibling's row was never invoked again, and its
    // rendered text never changed.
    expect(screen.getByText('Old reply')).toBeInTheDocument()
    expect(
      messageRendererSpy.mock.calls.filter((call) => call[0].content === 'Old reply').length
    ).toBe(finishedRowCallsAfterMount)
  })

  it('blocks a regenerate attempt fired while isLoading is true, immediately after a sibling-variant swap', () => {
    const messages: MessageNode[] = [
      { id: 1, parent_id: null, role: 'user', content: 'Hello', variant_index: 0 },
      { id: 2, parent_id: 1, role: 'assistant', content: 'First reply', variant_index: 0 },
      { id: 3, parent_id: 1, role: 'assistant', content: 'Second reply', variant_index: 1 }
    ]
    const { rerender } = render(<ChatView {...defaultProps} messages={messages} isLoading={false} />)

    // Swap to the older sibling variant.
    fireEvent.click(screen.getByText('chevron_left'))
    expect(screen.getByText('First reply')).toBeInTheDocument()

    // A turn starts (isLoading flips true) right after the swap, before the
    // user gets a chance to click Regenerate on the now-visible sibling.
    rerender(<ChatView {...defaultProps} messages={messages} isLoading />)

    fireEvent.click(screen.getByText('Regenerate'))

    // Must still be blocked -- if the row's memoization ever let it keep a
    // stale onRegenerate closure bound to a stale (false) isLoading, this
    // guard would incorrectly let the click through.
    expect(onRegenerate).not.toHaveBeenCalled()
  })

  it('does not leak the live stream onto an older sibling swapped in mid-stream (regression, re-verified under memoization)', () => {
    vi.useFakeTimers()

    const messages: MessageNode[] = [
      { id: 1, parent_id: null, role: 'user', content: 'Hello', variant_index: 0 },
      { id: 2, parent_id: 1, role: 'assistant', content: 'Old final reply', variant_index: 0 },
      { id: 3, parent_id: 1, role: 'assistant', content: '', variant_index: 1 }
    ]
    render(
      <ChatView
        {...defaultProps}
        messages={messages}
        isLoading
        streamingContent="Incoming new"
        streamingMessageId={3}
      />
    )

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByText('Incoming new')).toBeInTheDocument()

    fireEvent.click(screen.getByText('chevron_left'))

    expect(screen.getByText('Old final reply')).toBeInTheDocument()
    expect(screen.queryByText('Incoming new')).not.toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByText('Old final reply')).toBeInTheDocument()
    expect(screen.queryByText('Incoming new')).not.toBeInTheDocument()
  })
})
