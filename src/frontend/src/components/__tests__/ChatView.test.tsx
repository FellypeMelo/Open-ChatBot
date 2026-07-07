import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
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
      onDeleteMessage
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

  it('renders the active character name and clear chat button when a character is active', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    expect(screen.getByText('Aria')).toBeInTheDocument()
    expect(screen.getByText('NEW CHAT')).toBeInTheDocument()
  })

  it('calls onClearChat when the NEW CHAT button is clicked', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} />)

    fireEvent.click(screen.getByText('NEW CHAT'))

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

  it('disables the send button while loading', () => {
    render(<ChatView {...defaultProps} activeChar={baseCharacter} input="Hi" isLoading />)

    expect(screen.getByText('arrow_upward').closest('button')).toBeDisabled()
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

  // ---- Deleting messages ----

  it('deletes a user message when confirmed', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Delete'))

    expect(onDeleteMessage).toHaveBeenCalledWith(1)
  })

  it('does not delete a user message when confirmation is cancelled', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={[userMsg]} />)

    fireEvent.click(screen.getByTitle('Delete'))

    expect(onDeleteMessage).not.toHaveBeenCalled()
  })

  it('deletes an assistant message when confirmed', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const messages: MessageNode[] = [
      userMsg,
      { id: 2, parent_id: 1, role: 'assistant', content: 'Reply text', variant_index: 0 }
    ]
    render(<ChatView {...defaultProps} activeChar={baseCharacter} messages={messages} />)

    fireEvent.click(screen.getByText('Delete'))

    expect(onDeleteMessage).toHaveBeenCalledWith(2)
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
})
