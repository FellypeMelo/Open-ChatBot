import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act, within } from '@testing-library/react'
import ChatView from '../ChatView'
import * as api from '../../services/api'
import type { MessageNode } from '../../hooks/useMessageTree'
import type { Character, JournalEntry } from '../../services/api'

vi.mock('../../services/api', () => ({
  fetchJournal: vi.fn()
}))

const baseCharacter: Character = {
  id: 1,
  name: 'Aria',
  description: 'A test persona',
  is_active: true,
  tags: []
}

function withStats(overrides: Record<string, unknown> = {}): Character {
  return {
    ...baseCharacter,
    state: {
      location: '',
      mood: 'calm',
      clothes: '',
      interaction_count: 3,
      stats: {
        energy: 80,
        hunger: 20,
        happiness: 50,
        social: 50,
        is_sleeping: false,
        relationship: { score: 50 },
        ...overrides
      }
    }
  }
}

const userMsg: MessageNode = { id: 1, parent_id: null, role: 'user', content: 'Hello world', variant_index: 0 }

describe('ChatView', () => {
  let onSend: ReturnType<typeof vi.fn>
  let onRegenerate: ReturnType<typeof vi.fn>
  let onUpdateState: ReturnType<typeof vi.fn>
  let onClearChat: ReturnType<typeof vi.fn>
  let onSendAction: ReturnType<typeof vi.fn>
  let onEditMessage: ReturnType<typeof vi.fn>
  let onDeleteMessage: ReturnType<typeof vi.fn>
  let onNewChat: ReturnType<typeof vi.fn>
  let setInput: ReturnType<typeof vi.fn>

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let defaultProps: any

  beforeEach(() => {
    vi.clearAllMocks()
    onSend = vi.fn()
    onRegenerate = vi.fn()
    onUpdateState = vi.fn().mockResolvedValue(undefined)
    onClearChat = vi.fn()
    onSendAction = vi.fn().mockResolvedValue(undefined)
    onEditMessage = vi.fn().mockResolvedValue(undefined)
    onDeleteMessage = vi.fn().mockResolvedValue(undefined)
    onNewChat = vi.fn()
    setInput = vi.fn()

    defaultProps = {
      activeChar: null,
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
      onDeleteMessage,
      onNewChat
    }

    vi.mocked(api.fetchJournal).mockResolvedValue([])
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ---- Basic rendering ----

  it('renders the idle empty state and default title when there is no active character', () => {
    render(<ChatView {...defaultProps} />)

    expect(screen.getByText('Narrative Core')).toBeInTheDocument()
    expect(screen.getByText('Core Idle. Input prompt.')).toBeInTheDocument()
    expect(screen.queryByText('NEW CHAT')).not.toBeInTheDocument()

    const textarea = screen.getByPlaceholderText('Write a prompt for Core...')
    expect(textarea).toBeDisabled()
  })

  it('renders the active character name and NEW CHAT button when a character is active', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    expect(screen.getByText('Aria')).toBeInTheDocument()
    expect(screen.getByText('NEW CHAT')).toBeInTheDocument()
  })

  it('calls onNewChat (non-destructive) when the NEW CHAT button is clicked', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByText('NEW CHAT'))

    expect(onNewChat).toHaveBeenCalledTimes(1)
    // NEW CHAT must not trigger the destructive reset.
    expect(onClearChat).not.toHaveBeenCalled()
  })

  it('calls onClearChat when the destructive reset button is clicked', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))

    expect(onClearChat).toHaveBeenCalledTimes(1)
  })

  it('renders user and assistant messages from the active path', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    expect(screen.getByText('Hello world')).toBeInTheDocument()
    expect(screen.getByText('Hi there')).toBeInTheDocument()
  })

  // ---- Sending messages ----

  it('calls onSend when the send button is clicked with non-empty input', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hello there" />)

    fireEvent.click(screen.getByText('arrow_upward'))

    expect(onSend).toHaveBeenCalledTimes(1)
  })

  it('disables the send button when input is empty', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="   " />)

    expect(screen.getByText('arrow_upward').closest('button')).toBeDisabled()
  })

  it('replaces the send button with a Stop control while loading', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hi" isLoading />)

    expect(screen.queryByText('arrow_upward')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Stop generating' })).toBeInTheDocument()
  })

  it('calls onCancelStream when the Stop control is clicked while loading', () => {
    const onCancelStream = vi.fn()
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hi" isLoading onCancelStream={onCancelStream} />)

    fireEvent.click(screen.getByRole('button', { name: 'Stop generating' }))

    expect(onCancelStream).toHaveBeenCalledTimes(1)
  })

  it('sends on Enter key without shift', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hi" />)

    const textarea = screen.getByPlaceholderText('Write a prompt for Aria...')
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })

    expect(onSend).toHaveBeenCalledTimes(1)
  })

  it('does not send on Shift+Enter', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hi" />)

    const textarea = screen.getByPlaceholderText('Write a prompt for Aria...')
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true })

    expect(onSend).not.toHaveBeenCalled()
  })

  it('updates input through setInput as the user types', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    const textarea = screen.getByPlaceholderText('Write a prompt for Aria...')
    fireEvent.change(textarea, { target: { value: 'New text' } })

    expect(setInput).toHaveBeenCalledWith('New text')
  })

  it('auto-grows the composer to fit its content as the value changes', () => {
    const { rerender } = render(<ChatView {...defaultProps} activeChar={baseCharacter} input="" />)
    const textarea = screen.getByPlaceholderText('Write a prompt for Aria...') as HTMLTextAreaElement
    Object.defineProperty(textarea, 'scrollHeight', { value: 72, configurable: true })

    rerender(<ChatView {...defaultProps} activeChar={baseCharacter} input={'line1\nline2\nline3'} />)

    expect(textarea.style.height).toBe('72px')
  })

  it('caps the composer height so tall content scrolls instead of growing unbounded', () => {
    const { rerender } = render(<ChatView {...defaultProps} activeChar={baseCharacter} input="" />)
    const textarea = screen.getByPlaceholderText('Write a prompt for Aria...') as HTMLTextAreaElement
    Object.defineProperty(textarea, 'scrollHeight', { value: 999, configurable: true })

    rerender(<ChatView {...defaultProps} activeChar={baseCharacter} input={'a\nb\nc\nd\ne\nf\ng\nh'} />)

    expect(textarea.style.height).toBe('160px')
  })

  // ---- Regenerate ----

  it('calls onRegenerate with the parent id when Regenerate is clicked', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    fireEvent.click(screen.getByText('Regenerate'))

    expect(onRegenerate).toHaveBeenCalledWith(1)
  })

  it('does not regenerate while loading', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading />)

    fireEvent.click(screen.getByText('Regenerate'))

    expect(onRegenerate).not.toHaveBeenCalled()
  })

  it('does not regenerate a root-level assistant message with no parent', () => {
    const messages: MessageNode[] = [
      { id: 5, parent_id: null, role: 'assistant', content: 'Standalone', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    fireEvent.click(screen.getByText('Regenerate'))

    expect(onRegenerate).not.toHaveBeenCalled()
  })

  it('navigates between sibling variants', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'First reply', variant_index: 0 },
      { id: 3, parent_id: 1, role: 'assistant', content: 'Second reply', variant_index: 1 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    // Defaults to the latest variant
    expect(screen.getByText('Second reply')).toBeInTheDocument()
    expect(screen.getByText('2 / 2')).toBeInTheDocument()

    fireEvent.click(screen.getByText('chevron_left'))
    expect(screen.getByText('First reply')).toBeInTheDocument()
    expect(screen.getByText('1 / 2')).toBeInTheDocument()
    expect(screen.getByText('chevron_left').closest('button')).toBeDisabled()

    fireEvent.click(screen.getByText('chevron_right'))
    expect(screen.getByText('Second reply')).toBeInTheDocument()
    expect(screen.getByText('chevron_right').closest('button')).toBeDisabled()
  })

  // ---- Editing messages ----

  it('edits and saves a user message', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Edit'))
    const textarea = screen.getByDisplayValue('Hello world')
    fireEvent.change(textarea, { target: { value: 'Hello universe' } })
    fireEvent.click(screen.getByText('SAVE'))

    expect(onEditMessage).toHaveBeenCalledWith(1, 'Hello universe')
    expect(screen.queryByDisplayValue('Hello universe')).not.toBeInTheDocument()
  })

  it('cancels editing a user message without saving', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Edit'))
    const textarea = screen.getByDisplayValue('Hello world')
    fireEvent.change(textarea, { target: { value: 'Changed but not saved' } })
    fireEvent.click(screen.getByText('CANCEL'))

    expect(onEditMessage).not.toHaveBeenCalled()
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('edits and saves an assistant message', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    fireEvent.click(screen.getByText('Edit'))
    const textarea = screen.getByDisplayValue('Reply text')
    fireEvent.change(textarea, { target: { value: 'Updated reply' } })
    fireEvent.click(screen.getByText('SAVE'))

    expect(onEditMessage).toHaveBeenCalledWith(2, 'Updated reply')
  })

  it('sizes the user-message edit textarea at 16px on mobile to prevent iOS Safari auto-zoom, compact on desktop', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Edit'))
    const textarea = screen.getByDisplayValue('Hello world')

    expect(textarea.className).toContain('text-base')
    expect(textarea.className).toContain('md:text-sm')
  })

  // ---- Deleting messages ----

  it('deletes a user message when confirmed', async () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Delete'))
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText('Delete this message?')).toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))

    await waitFor(() => expect(onDeleteMessage).toHaveBeenCalledWith(1))
  })

  it('does not delete a user message when confirmation is cancelled', async () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Delete'))
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Cancel' }))

    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    expect(onDeleteMessage).not.toHaveBeenCalled()
  })

  it('deletes an assistant message when confirmed', async () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    fireEvent.click(screen.getByText('Delete'))
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))

    await waitFor(() => expect(onDeleteMessage).toHaveBeenCalledWith(2))
  })

  it('does not render delete controls when onDeleteMessage is not provided', () => {
    render(
      <ChatView
        {...defaultProps}
        activeChar={baseCharacter}
        messages={[userMsg]}
        onDeleteMessage={undefined}
      />
    )

    expect(screen.queryByTitle('Delete')).not.toBeInTheDocument()
  })

  // ---- Copy request id ----

  it('disables the copy id button when the message has no request id', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    const copyBtn = screen.getByTitle('Request ID not available yet')
    expect(copyBtn).toBeDisabled()
  })

  it('copies the request id and shows a confirmation that clears after a timeout', () => {
    vi.useFakeTimers()
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(window.navigator, 'clipboard', {
      value: { writeText },
      configurable: true
    })

    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0, request_id: 'req-999-xyz' }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    const copyBtn = screen.getByTitle('Copy Request ID')
    fireEvent.click(copyBtn)

    expect(writeText).toHaveBeenCalledWith('req-999-xyz')
    expect(screen.getByText('Copied')).toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(1500)
    })

    expect(screen.queryByText('Copied')).not.toBeInTheDocument()
  })

  it('falls back to execCommand copy when navigator.clipboard is unavailable (plain-http LAN origin)', () => {
    const originalClipboard = window.navigator.clipboard
    Object.defineProperty(window.navigator, 'clipboard', {
      value: undefined,
      configurable: true
    })
    const execCommand = vi.fn().mockReturnValue(true)
    document.execCommand = execCommand

    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0, request_id: 'req-abc-123' }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    try {
      fireEvent.click(screen.getByTitle('Copy Request ID'))

      expect(execCommand).toHaveBeenCalledWith('copy')
      expect(screen.getByText('Copied')).toBeInTheDocument()
    } finally {
      Object.defineProperty(window.navigator, 'clipboard', {
        value: originalClipboard,
        configurable: true
      })
    }
  })

  // ---- Action & gift drawer ----

  it('opens the interact drawer and triggers an action', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle('Interact & Gift'))
    expect(screen.getByText('Hug')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Hug'))

    expect(onSendAction).toHaveBeenCalledWith('hug')
    expect(screen.queryByText('Hug')).not.toBeInTheDocument()
  })

  it('switches to the gifts tab and triggers a gift', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle('Interact & Gift'))
    fireEvent.click(screen.getByText('Gifting'))
    expect(screen.getByText('Book')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Book'))

    expect(onSendAction).toHaveBeenCalledWith('book')
    expect(screen.queryByText('Book')).not.toBeInTheDocument()
  })

  it('closes the drawer via the close button', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle('Interact & Gift'))
    expect(screen.getByText('Hug')).toBeInTheDocument()

    fireEvent.click(screen.getByTitle('Close Drawer'))

    expect(screen.queryByText('Hug')).not.toBeInTheDocument()
  })

  it('closes the drawer when tapping the outside backdrop', () => {
    const { container } = render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle('Interact & Gift'))
    expect(screen.getByText('Hug')).toBeInTheDocument()

    const backdrop = container.querySelector('.bg-black\\/40') as HTMLElement
    expect(backdrop).toBeTruthy()
    fireEvent.click(backdrop)

    expect(screen.queryByText('Hug')).not.toBeInTheDocument()
  })

  it('caps the interact drawer height and gives it its own scroll region so it cannot overflow a short mobile viewport', () => {
    const { container } = render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByTitle('Interact & Gift'))
    const panel = container.querySelector('.slide-in-from-bottom-4') as HTMLElement

    expect(panel).toBeTruthy()
    expect(panel.className).toContain('max-h-[70dvh]')
    expect(panel.className).toContain('overflow-y-auto')
  })

  // ---- Stat bars ----

  it('toggles the sleep state', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ is_sleeping: false })} />)

    fireEvent.click(screen.getByText('Sleep'))

    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { is_sleeping: true } })
  })

  it('feeds the character, clamping hunger to a minimum of 0', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ hunger: 20 })} />)

    fireEvent.click(screen.getByText('Feed'))

    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { hunger: 0 } })
  })

  it('disables the feed button when hunger is already 0', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ hunger: 0 })} />)

    expect(screen.getByText('Feed')).toBeDisabled()
  })

  it('increments happiness clamped to a maximum of 100', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ happiness: 95 })} />)

    const plusButtons = screen.getAllByText('+')
    fireEvent.click(plusButtons[0])

    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { happiness: 100 } })
  })

  it('decrements happiness clamped to a minimum of 0', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ happiness: 5 })} />)

    const minusButtons = screen.getAllByText('-')
    fireEvent.click(minusButtons[0])

    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { happiness: 0 } })
  })

  it('increments and decrements the social stat clamped between 0 and 100', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ social: 95 })} />)

    fireEvent.click(screen.getAllByText('+')[1])
    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { social: 100 } })

    fireEvent.click(screen.getAllByText('-')[1])
    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { social: 85 } })
  })

  it('increments and decrements the relationship score clamped between 0 and 100', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ relationship: { score: 5 } })} />)

    fireEvent.click(screen.getAllByText('-')[2])
    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { relationship_score: 0 } })

    fireEvent.click(screen.getAllByText('+')[2])
    expect(onUpdateState).toHaveBeenCalledWith(1, { stats: { relationship_score: 15 } })
  })

  it('sizes the +/- stat steppers to the 44px mobile touch-target minimum, compact on desktop', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ happiness: 50 })} />)

    const plusButtons = screen.getAllByText('+')
    const minusButtons = screen.getAllByText('-')

    for (const btn of [...plusButtons, ...minusButtons]) {
      expect(btn.className).toContain('min-w-11')
      expect(btn.className).toContain('min-h-11')
      expect(btn.className).toContain('md:min-w-0')
      expect(btn.className).toContain('md:min-h-0')
    }
  })

  it('sizes the Sleep/Feed stat buttons to the 44px mobile touch-target minimum, compact on desktop', () => {
    render(<ChatView {...defaultProps} activeChar={withStats({ is_sleeping: false, hunger: 20 })} />)

    const sleepBtn = screen.getByText('Sleep')
    const feedBtn = screen.getByText('Feed')

    for (const btn of [sleepBtn, feedBtn]) {
      expect(btn.className).toContain('min-w-11')
      expect(btn.className).toContain('min-h-11')
      expect(btn.className).toContain('md:min-w-0')
      expect(btn.className).toContain('md:min-h-0')
    }
  })

  it('stacks stat rows in a single mobile column so the larger 44px steppers have room and never collide with the label', () => {
    const { container } = render(<ChatView {...defaultProps} activeChar={withStats()} />)

    const statsGrid = container.querySelector('.grid-cols-1.md\\:grid-cols-5') as HTMLElement
    expect(statsGrid).toBeTruthy()
  })

  // ---- Journal tab ----

  it('loads and displays journal entries when switching tabs', async () => {
    const entries: JournalEntry[] = [
      {
        id: 1,
        timestamp: '2026-01-01T10:00:00Z',
        content: 'A reflective entry',
        summary: '',
        mood_at_time: 'happy',
        relationship_score: 80,
        energy_level: 70
      }
    ]
    vi.mocked(api.fetchJournal).mockResolvedValue(entries)

    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
    fireEvent.click(screen.getByText('Private Journal'))

    await waitFor(() => {
      expect(screen.getByText(/A reflective entry/)).toBeInTheDocument()
    })
    expect(api.fetchJournal).toHaveBeenCalledWith(1)
  })

  it('shows an empty state when there are no journal entries', async () => {
    vi.mocked(api.fetchJournal).mockResolvedValue([])

    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
    fireEvent.click(screen.getByText('Private Journal'))

    await waitFor(() => {
      expect(screen.getByText('No journal entries yet.')).toBeInTheDocument()
    })
  })

  it('logs an error when journal loading fails', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.mocked(api.fetchJournal).mockRejectedValue(new Error('boom'))

    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
    fireEvent.click(screen.getByText('Private Journal'))

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to load journal entries', expect.any(Error))
    })

    consoleErrorSpy.mockRestore()
  })

  // ---- Streaming ----

  it('shows the streaming indicator while loading with no delta yet', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: '', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading />)

    expect(screen.getByText('LOGGING RESPONSE STREAM...')).toBeInTheDocument()
  })

  // ---- Misc coverage: scroll handling & header badge ----

  it('updates the at-bottom state when the message canvas is scrolled', () => {
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 }
    ]
    const { container } = render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    const main = container.querySelector('main') as HTMLElement
    Object.defineProperty(main, 'scrollHeight', { value: 1000, configurable: true })
    Object.defineProperty(main, 'clientHeight', { value: 400, configurable: true })
    Object.defineProperty(main, 'scrollTop', { value: 50, configurable: true })

    fireEvent.scroll(main)

    // No assertion error means the handler ran without throwing; verify component still renders
    expect(screen.getByText('Hi there')).toBeInTheDocument()
  })

  it('collapses the HUD on downward scroll, ignores small upward nudges, and re-expands on a deliberate upward scroll (mobile)', async () => {
    // Force useIsMobile's mobile branch (setup.ts defaults matchMedia to no-match).
    const realMatchMedia = window.matchMedia
    window.matchMedia = ((query: string) => ({
      matches: true,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia
    const onImmersiveChange = vi.fn()
    try {
      const messages: MessageNode[] = [
        userMsg,
        { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 },
      ]
      const { container } = render(
        <ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} onImmersiveChange={onImmersiveChange} />
      )
      const main = container.querySelector('main') as HTMLElement
      const scrollTo = (value: number) => {
        Object.defineProperty(main, 'scrollTop', { value, configurable: true })
        fireEvent.scroll(main)
      }

      // Scroll down -> HUD collapses (immersive on).
      scrollTo(300)
      await waitFor(() => expect(onImmersiveChange).toHaveBeenLastCalledWith(true))

      // Small upward nudges (15px + 15px, well under the 140px reveal
      // threshold) must NOT bring it back -- this was the twitchy behavior.
      onImmersiveChange.mockClear()
      scrollTo(285)
      scrollTo(270)
      expect(onImmersiveChange).not.toHaveBeenCalledWith(false)

      // A deliberate upward scroll past the threshold re-expands it.
      scrollTo(110)
      await waitFor(() => expect(onImmersiveChange).toHaveBeenLastCalledWith(false))
    } finally {
      window.matchMedia = realMatchMedia
    }
  })

  it('keeps the HUD pinned on desktop regardless of scroll direction', () => {
    const onImmersiveChange = vi.fn()
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 },
    ]
    const { container } = render(
      <ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} onImmersiveChange={onImmersiveChange} />
    )
    const main = container.querySelector('main') as HTMLElement
    Object.defineProperty(main, 'scrollTop', { value: 500, configurable: true })
    fireEvent.scroll(main)
    // Desktop (matchMedia no-match) never collapses -- only the initial false.
    expect(onImmersiveChange).not.toHaveBeenCalledWith(true)
  })

  it('shows the location/clothes badge when present on the character state', () => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    const character = withStats()
    character.state = { ...character.state!, location: 'Garden', clothes: 'Sundress' }

    render(<ChatView {...defaultProps} activeChar={character} />)

    expect(screen.getByText('GARDEN • SUNDRESS')).toBeInTheDocument()
  })

  it('falls back to NEUTRAL mood label when a journal entry has no mood_at_time', async () => {
    const entries: JournalEntry[] = [
      {
        id: 2,
        timestamp: '2026-02-02T10:00:00Z',
        content: 'No mood entry',
        summary: '',
        mood_at_time: '',
        relationship_score: 40,
        energy_level: 60
      }
    ]
    vi.mocked(api.fetchJournal).mockResolvedValue(entries)

    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
    fireEvent.click(screen.getByText('Private Journal'))

    await waitFor(() => {
      expect(screen.getByText(/MOOD: NEUTRAL/)).toBeInTheDocument()
    })
  })

  it('streams assistant content token by token while loading', () => {
    vi.useFakeTimers()
    vi.spyOn(console, 'warn').mockImplementation(() => {})

    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading />)

    act(() => {
      vi.advanceTimersByTime(200)
    })

    expect(screen.getByText('Hi')).toBeInTheDocument()
  })

  it('streams from the dedicated streamingContent prop, ignoring the (unchanged) message content', () => {
    vi.useFakeTimers()

    const messages: MessageNode[] = [
      userMsg,
      // App.tsx no longer writes streamed tokens into `messages` -- this
      // placeholder's content stays stale/empty for the whole turn.
      { id: 2, parent_id: 1, role: 'assistant', content: 'stale', variant_index: 0 }
    ]
    render(
      <ChatView
        {...defaultProps}
        activeChar={baseCharacter}
        messages={messages}
        isLoading
        streamingContent="Fresh streamed text"
      />
    )

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(screen.getByText('Fresh streamed text')).toBeInTheDocument()
    expect(screen.queryByText('stale')).not.toBeInTheDocument()
  })

  it('picks up a growing streamingContent value across rerenders without needing the messages array to change', () => {
    vi.useFakeTimers()

    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: '', variant_index: 0 }
    ]
    const { rerender } = render(
      <ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading streamingContent="" />
    )

    // Same `messages` array reference on every rerender -- only
    // streamingContent grows, exactly as App.tsx now drives it per token.
    ;['H', 'He', 'Hel', 'Hell', 'Hello'].forEach((content) => {
      rerender(
        <ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading streamingContent={content} />
      )
    })

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('does not leak the live stream onto an older sibling variant swapped in mid-stream (regression)', () => {
    vi.useFakeTimers()

    // Regenerate produces a sibling (id 3) alongside the old, already-
    // finished reply (id 2) under the same parent. streamingMessageId
    // identifies id 3 as the one actually streaming -- App.tsx always wires
    // this through once a turn starts.
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Old final reply', variant_index: 0 },
      { id: 3, parent_id: 1, role: 'assistant', content: '', variant_index: 1 }
    ]
    render(
      <ChatView
        {...defaultProps}
        activeChar={baseCharacter}
        messages={messages}
        isLoading
        streamingContent="Incoming new"
        streamingMessageId={3}
      />
    )

    // Defaults to the latest variant (id 3), which is actively streaming.
    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByText('Incoming new')).toBeInTheDocument()
    expect(screen.getByText('2 / 2')).toBeInTheDocument()

    // Swipe to the older sibling while id 3 is still streaming. The swipe
    // controls have no isLoading guard by design -- the fix is that the old
    // sibling must render its OWN static content, never the live stream.
    fireEvent.click(screen.getByText('chevron_left'))

    expect(screen.getByText('Old final reply')).toBeInTheDocument()
    expect(screen.queryByText('Incoming new')).not.toBeInTheDocument()

    // Still true after more of the stream drains while looking away --
    // nothing about viewing the old sibling should leak in later either.
    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByText('Old final reply')).toBeInTheDocument()
    expect(screen.queryByText('Incoming new')).not.toBeInTheDocument()
  })

  it('uses instant scroll while the typewriter is actively draining and smooth scroll once it settles', () => {
    vi.useFakeTimers()
    const scrollMock = vi.mocked(window.HTMLElement.prototype.scrollIntoView)

    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Hi there', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} isLoading />)

    // Mounting with isLoading enqueues the content immediately, so the
    // typewriter is already draining by the time effects settle.
    expect(scrollMock).toHaveBeenLastCalledWith({ behavior: 'auto' })

    act(() => {
      vi.advanceTimersByTime(500)
    })

    expect(scrollMock).toHaveBeenLastCalledWith({ behavior: 'smooth' })
  })

  // ---- Mobile text sizing (R6) ----

  it('bumps small header/footer/journal label text to a readable mobile size with a compact md: override', () => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    const character = withStats()
    character.state = { ...character.state!, location: 'Garden', clothes: 'Sundress' }
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0, request_id: 'req-111-abc' }
    ]

    render(<ChatView {...defaultProps} activeChar={character} messages={messages} />)

    const locationPill = screen.getByText('GARDEN • SUNDRESS')
    expect(locationPill.className).toContain('text-[11px]')
    expect(locationPill.className).toContain('md:text-[9px]')

    const storyLogTab = screen.getByText('Story Log')
    expect(storyLogTab.className).toContain('text-[11px]')
    expect(storyLogTab.className).toContain('md:text-[10px]')

    const reqBadge = screen.getByText(/^REQ: /)
    expect(reqBadge.className).toContain('text-[11px]')
    expect(reqBadge.className).toContain('md:text-[9px]')

    const promptAction = screen.getByText('PROMPT ACTION')
    expect(promptAction.className).toContain('text-[11px]')
    expect(promptAction.className).toContain('md:text-[9px]')
  })

  it('bumps the Narrative Ingest divider and journal-tab entry-count badge text for mobile readability', async () => {
    const entries: JournalEntry[] = [
      {
        id: 1,
        timestamp: '2026-01-01T10:00:00Z',
        content: 'A reflective entry',
        summary: '',
        mood_at_time: 'happy',
        relationship_score: 80,
        energy_level: 70
      }
    ]
    vi.mocked(api.fetchJournal).mockResolvedValue(entries)

    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    const divider = screen.getByText('Narrative Ingest')
    expect(divider.className).toContain('text-[10px]')
    expect(divider.className).toContain('md:text-[8px]')

    fireEvent.click(screen.getByText('Private Journal'))

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
    const badge = screen.getByText('1')
    expect(badge.className).toContain('text-[10px]')
    expect(badge.className).toContain('md:text-[8px]')
  })

  // ---- Mobile keyboard occlusion (visualViewport fallback) ----

  it('does not throw when window.visualViewport is unavailable (jsdom default, and older browsers)', () => {
    expect(window.visualViewport).toBeUndefined()

    expect(() => render(<ChatView {...defaultProps} activeChar={baseCharacter} />)).not.toThrow()
  })

  it('scrolls the focused composer back into view when the visual viewport shrinks significantly (keyboard opens)', () => {
    const listeners: Record<string, () => void> = {}
    const fakeViewport = {
      height: 800,
      addEventListener: vi.fn((event: string, cb: () => void) => {
        listeners[event] = cb
      }),
      removeEventListener: vi.fn()
    }
    Object.defineProperty(window, 'visualViewport', { value: fakeViewport, configurable: true })

    try {
      const { unmount } = render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
      const textarea = screen.getByPlaceholderText('Write a prompt for Aria...') as HTMLTextAreaElement
      const scrollMock = vi.mocked(window.HTMLElement.prototype.scrollIntoView)
      scrollMock.mockClear()
      textarea.focus()

      fakeViewport.height = 500
      act(() => {
        listeners.resize()
      })

      expect(scrollMock).toHaveBeenCalledWith({ block: 'nearest' })

      unmount()
      expect(fakeViewport.removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function))
    } finally {
      Object.defineProperty(window, 'visualViewport', { value: undefined, configurable: true })
    }
  })

  it('does not scroll the composer on a minor visual-viewport change (no keyboard, e.g. address bar chrome)', () => {
    const listeners: Record<string, () => void> = {}
    const fakeViewport = {
      height: 800,
      addEventListener: vi.fn((event: string, cb: () => void) => {
        listeners[event] = cb
      }),
      removeEventListener: vi.fn()
    }
    Object.defineProperty(window, 'visualViewport', { value: fakeViewport, configurable: true })

    try {
      render(<ChatView {...defaultProps} activeChar={baseCharacter} />)
      const textarea = screen.getByPlaceholderText('Write a prompt for Aria...') as HTMLTextAreaElement
      const scrollMock = vi.mocked(window.HTMLElement.prototype.scrollIntoView)
      scrollMock.mockClear()
      textarea.focus()

      fakeViewport.height = 770
      act(() => {
        listeners.resize()
      })

      expect(scrollMock).not.toHaveBeenCalledWith({ block: 'nearest' })
    } finally {
      Object.defineProperty(window, 'visualViewport', { value: undefined, configurable: true })
    }
  })
})
