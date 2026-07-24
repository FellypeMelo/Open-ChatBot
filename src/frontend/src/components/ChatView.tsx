import React, { useRef, useEffect, useState, useCallback } from 'react'
import Icon from './Icon'
import IconButton from './IconButton'
import MessageRow from './MessageRow'
import { useIsMobile } from '../hooks/useIsMobile'
import { useMessageTree } from '../hooks/useMessageTree'
import type { MessageNode } from '../hooks/useMessageTree'
import { useTokenQueue } from '../hooks/useTokenQueue'
import { useAtmosphere } from '../hooks/useAtmosphere'
import { useAudio } from '../hooks/useAudio'
import { useConfirm } from '../hooks/useConfirm'
import { fetchJournal } from '../services/api'
import type { JournalEntry, Character, ChatSession } from '../services/api'

// Best-effort clipboard fallback for contexts where navigator.clipboard is
// unavailable (e.g. the app served over plain http://<lan-ip> is a
// non-secure origin, so the Clipboard API is undefined on mobile browsers).
const fallbackCopyToClipboard = (text: string) => {
  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.setAttribute('readonly', '')
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
  } catch {
    // Clipboard genuinely unavailable -- the request id is still visible in the UI.
  }
}

const ACTIONS = [
  { id: 'hug', name: 'Hug', icon: 'favorite', effect: 'HAPPINESS +5 • SOCIAL +10 • RELATION +2' },
  { id: 'pat_head', name: 'Pat Head', icon: 'emoji_emotions', effect: 'HAPPINESS +3 • SOCIAL +5 • RELATION +1' },
  { id: 'tease', name: 'Tease', icon: 'theater_comedy', effect: 'HAPPINESS +2 • SOCIAL +8 • RELATION +1' },
  { id: 'hold_hand', name: 'Hold Hand', icon: 'handshake', effect: 'HAPPINESS +4 • SOCIAL +8 • RELATION +2' }
]

// Composer grows with its content up to this height, then scrolls internally.
const COMPOSER_MAX_HEIGHT = 160

const GIFTS = [
  { id: 'coffee', name: 'Hot Coffee', icon: 'local_cafe', effect: 'HUNGER -10 • ENERGY +15 • RELATION +2' },
  { id: 'croissant', name: 'Croissant', icon: 'bakery_dining', effect: 'HUNGER -35 • ENERGY +5 • RELATION +3' },
  { id: 'book', name: 'Book', icon: 'book', effect: 'HAPPINESS +8 • SOCIAL +5 • RELATION +4' },
  { id: 'necklace', name: 'Necklace', icon: 'diamond', effect: 'HAPPINESS +15 • SOCIAL +10 • RELATION +8' }
]

// Stat gauge shell: label row + progress bar. The right-hand value and controls
// vary per stat, so each caller passes them as children.
const StatBar: React.FC<{
  label: string
  percent?: number
  barClass?: string
  children: React.ReactNode
}> = ({ label, percent, barClass = 'bg-white', children }) => (
  <div className="flex flex-col gap-1">
    <div className="flex items-center justify-between gap-2 font-mono text-[11px] md:text-[9px] text-[#71717A]">
      <span>{label}</span>
      <div className="flex items-center gap-1.5 shrink-0">{children}</div>
    </div>
    <div className="h-1 bg-white/5 rounded-full overflow-hidden">
      <div className={`h-full ${barClass} transition-all duration-500`} style={{ width: `${percent}%` }} />
    </div>
  </div>
)

// Shared styling for the compact stat controls (+/- steppers and Sleep/Feed).
// Meets the 44px mobile touch-target minimum, compact on desktop, with a
// pressed state so a thumb gets feedback. Replaces the old ~16px text-[8px] targets.
const STAT_CONTROL_CLASS =
  'inline-flex items-center justify-center bg-white/5 border border-white/10 rounded ' +
  'min-w-11 min-h-11 md:min-w-0 md:min-h-0 md:px-1 md:py-0.5 ' +
  'text-xs md:text-[9px] leading-none font-mono hover:bg-white/10 text-[#A1A1AA] hover:text-white ' +
  'transition-colors cursor-pointer select-none touch-manipulation active:scale-95 ' +
  'disabled:opacity-20 disabled:pointer-events-none'

// The identical minus/plus pair used by happiness / social / relationship.
// A slightly wider gap than the control's own internal spacing so two
// full-size 44px targets don't read as a single fused hit area on mobile.
const AdjustButtons: React.FC<{ onDecrement: () => void; onIncrement: () => void }> = ({ onDecrement, onIncrement }) => (
  <div className="flex gap-1.5">
    <button type="button" onClick={onDecrement} className={STAT_CONTROL_CLASS} aria-label="Decrease">
      -
    </button>
    <button type="button" onClick={onIncrement} className={STAT_CONTROL_CLASS} aria-label="Increase">
      +
    </button>
  </div>
)

interface ChatViewProps {
  activeChar: Character | null
  messages: MessageNode[]
  // The in-flight assistant reply's accumulated text, owned by the parent
  // OUTSIDE the `messages` array so a token never forces a `messages` array
  // reference change (see App.tsx). When absent, falls back to reading the
  // streaming node's content straight off `messages` (used by callers/tests
  // that drive ChatView directly without this dedicated channel).
  streamingContent?: string | null
  // The id of the assistant placeholder `streamingContent` belongs to. Only
  // the message whose id matches this is ever treated as "currently
  // streaming" -- this is what stops a sibling-variant swap (or a
  // character/chat switch) mid-stream from making an unrelated, already-
  // finished message display someone else's in-flight text. When omitted
  // (e.g. tests driving ChatView directly), falls back to the legacy
  // positional behavior of treating whichever node is last in the active
  // path as the stream target.
  streamingMessageId?: number | null
  input: string
  setInput: (val: string) => void
  onSend: (parentId?: number) => void
  onRegenerate: (parentId: number) => void
  isLoading: boolean
  onCancelStream?: () => void
  onUpdateState: (charId: number, stateUpdate: Record<string, unknown>) => Promise<void>
  onClearChat: () => void
  onSendAction: (actionId: string, parentId?: number) => Promise<void>
  onEditMessage?: (messageId: number, content: string) => Promise<void>
  onDeleteMessage?: (messageId: number) => Promise<void>
  chats?: ChatSession[]
  activeChatId?: number | null
  greetings?: string[]
  onNewChat?: (greetingIndex?: number) => void
  onSelectChat?: (chatId: number) => void
  onDeleteChat?: (chatId: number) => void
  // Mobile immersive reading: fired `true` when the HUD collapses (scrolling
  // down into the transcript) and `false` when it returns, so the parent can
  // hide the app top bar + bottom tab bar in sync. No-op on desktop.
  onImmersiveChange?: (immersive: boolean) => void
}

const ChatView: React.FC<ChatViewProps> = ({
  activeChar,
  messages,
  streamingContent,
  streamingMessageId,
  input,
  setInput,
  onSend,
  onRegenerate,
  isLoading,
  onCancelStream,
  onUpdateState,
  onClearChat,
  onSendAction,
  onEditMessage,
  onDeleteMessage,
  chats = [],
  activeChatId = null,
  greetings = [],
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onImmersiveChange
}) => {
  // Which opening greeting seeds the next "New Chat" (only relevant when the
  // character has more than one greeting).
  const [greetingChoice, setGreetingChoice] = useState(0)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const composerRef = useRef<HTMLTextAreaElement>(null)
  const isMobile = useIsMobile()
  // Mobile immersive reading: the HUD collapses when scrolling down into the
  // transcript so the story owns the screen. It comes back only on a
  // DELIBERATE upward scroll (accumulated past a threshold) or near the very
  // top -- a tiny nudge up must NOT re-expand it (that was the twitchy feel).
  const [hudCollapsed, setHudCollapsed] = useState(false)
  const lastScrollTopRef = useRef(0)
  const upAccumRef = useRef(0)
  const { activePath, nextVariant, prevVariant, getSiblings } = useMessageTree(messages)
  const { playTypewriterClick, resumeAudio, playAmbient, stopAmbient } = useAudio()
  const { displayedContent, enqueue, reset, isDraining } = useTokenQueue(20, playTypewriterClick)
  const { blurAmount, textOpacity } = useAtmosphere(displayedContent)
  const { confirm, dialog } = useConfirm()
  const prevContentLength = useRef(0)
  const [isAtBottom, setIsAtBottom] = useState(true)
  const [currentTab, setCurrentTab] = useState<'chat' | 'journal'>('chat')
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([])
  const [isJournalLoading, setIsJournalLoading] = useState(false)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [drawerTab, setDrawerTab] = useState<'actions' | 'gifts'>('actions')
  const [editingMessageId, setEditingMessageId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')
  // Mobile: stats HUD is collapsed by default so the story text owns the
  // viewport. Tapping the summary chip expands the full editable grid.
  const [statsExpanded, setStatsExpanded] = useState(false)

  useEffect(() => {
    let active = true
    const loadJournalData = async () => {
      if (currentTab !== 'journal' || !activeChar) return
      await Promise.resolve()
      if (!active) return
      setIsJournalLoading(true)
      try {
        const data = await fetchJournal(activeChar.id)
        if (active) {
          setJournalEntries(data)
        }
      } catch (err) {
        console.error('Failed to load journal entries', err)
      } finally {
        if (active) {
          setIsJournalLoading(false)
        }
      }
    }
    loadJournalData()
    return () => {
      active = false
    }
  }, [currentTab, activeChar])

  useEffect(() => {
    if (activeChar?.state?.location) {
      playAmbient(activeChar.state.location)
    } else {
      stopAmbient()
    }
  }, [activeChar, playAmbient, stopAmbient])

  // 'auto' while the typewriter is actively draining tokens (fires up to
  // ~50x/sec during streaming, so a smooth-scroll animation per tick reads as
  // jank/rubber-banding); 'smooth' for user-initiated moments (send, tab
  // switch, once streaming settles).
  const scrollToBottom = useCallback((force = false) => {
    if (force || isAtBottom) {
      chatEndRef.current?.scrollIntoView({ behavior: isDraining ? 'auto' : 'smooth' })
    }
  }, [isAtBottom, isDraining])

  const handleScroll = (e: React.UIEvent<HTMLElement>) => {
    const el = e.currentTarget
    const offset = 100
    const atBottom = el.scrollHeight - el.scrollTop <= el.clientHeight + offset
    setIsAtBottom(atBottom)

    // Immersive reading (mobile only). Hysteresis so it doesn't flip on jitter:
    //  - near the top -> always expanded (and reset the up-scroll accumulator),
    //  - scrolling down past a small margin -> collapse, clearing the accumulator
    //    so a later reveal needs a fresh deliberate up-swipe,
    //  - scrolling up -> accumulate the distance and only re-expand once it
    //    passes UP_REVEAL_PX; small upward nudges never cross it.
    if (!isMobile) return
    const TOP_ZONE_PX = 56
    const UP_REVEAL_PX = 140
    const st = el.scrollTop
    const delta = st - lastScrollTopRef.current
    lastScrollTopRef.current = st
    if (st < TOP_ZONE_PX) {
      upAccumRef.current = 0
      setHudCollapsed(false)
    } else if (delta > 4) {
      upAccumRef.current = 0
      setHudCollapsed(true)
    } else if (delta < 0) {
      upAccumRef.current += -delta
      if (upAccumRef.current > UP_REVEAL_PX) setHudCollapsed(false)
    }
  }

  // Tell the parent so it can hide the app top bar + bottom tab bar in sync.
  useEffect(() => {
    onImmersiveChange?.(hudCollapsed)
  }, [hudCollapsed, onImmersiveChange])

  // Never leave the HUD stuck collapsed across a context change (new character,
  // or flipping to the Journal tab). Render-time reset (React's documented
  // "adjust state on prop change" pattern), so it applies before paint.
  const contextKey = `${activeChar?.id ?? ''}:${currentTab}`
  const [hudContextKey, setHudContextKey] = useState(contextKey)
  if (contextKey !== hudContextKey) {
    setHudContextKey(contextKey)
    if (hudCollapsed) setHudCollapsed(false)
  }

  useEffect(() => {
    scrollToBottom()
  }, [activePath, displayedContent, scrollToBottom])

  // Auto-grow the composer with its content (capped), and shrink it back when
  // the value is cleared after a send. Keyed on `input` so it also reacts to
  // external resets/edits, not only keystrokes.
  useEffect(() => {
    const el = composerRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, COMPOSER_MAX_HEIGHT)}px`
  }, [input])

  // Fallback keyboard-occlusion fix for browsers that don't yet honor the
  // `interactive-widget=resizes-content` viewport hint (index.html): when the
  // on-screen keyboard opens, visualViewport shrinks -- if the composer is
  // what's focused at that moment, nudge it back into view so the user can
  // see what they're typing. Feature-detected: a no-op (no listener attached)
  // wherever window.visualViewport doesn't exist.
  useEffect(() => {
    const viewport = window.visualViewport
    if (!viewport) return
    let lastHeight = viewport.height
    const handleViewportResize = () => {
      const currentHeight = viewport.height
      const shrunk = lastHeight - currentHeight > 150
      lastHeight = currentHeight
      if (shrunk && document.activeElement === composerRef.current) {
        composerRef.current?.scrollIntoView({ block: 'nearest' })
      }
    }
    viewport.addEventListener('resize', handleViewportResize)
    return () => viewport.removeEventListener('resize', handleViewportResize)
  }, [])

  useEffect(() => {
    if (isLoading) {
      reset()
      prevContentLength.current = 0
    }
  }, [isLoading, reset])

  useEffect(() => {
    if (isLoading && activePath.length > 0) {
      const lastMsg = activePath[activePath.length - 1]
      // Only feed the queue for the exact node this stream belongs to (see
      // streamingMessageId's prop doc) -- otherwise, swiping to a different,
      // already-finished sibling mid-stream would misread its static content
      // as a fresh delta to type out.
      const isStreamTarget = streamingMessageId === undefined || streamingMessageId === lastMsg.id
      if (lastMsg.role === 'assistant' && isStreamTarget) {
        // Prefer the dedicated streaming channel (App.tsx) over re-reading
        // `messages`, which no longer gets a token-by-token content update.
        const source = streamingContent ?? lastMsg.content
        if (source.length > prevContentLength.current) {
          const delta = source.substring(prevContentLength.current)
          enqueue(delta)
          prevContentLength.current = source.length
        }
      }
    }
  }, [activePath, isLoading, enqueue, streamingContent, streamingMessageId])

  const handleRegenerate = (node: MessageNode) => {
    if (isLoading || node.parent_id === null) return
    resumeAudio()
    onRegenerate(node.parent_id)
  }

  const handleSend = () => {
    resumeAudio()
    onSend()
  }

  const handleActionTrigger = (actionId: string) => {
    if (isLoading) return
    resumeAudio()
    setIsDrawerOpen(false)
    onSendAction(actionId)
  }

  const [copiedId, setCopiedId] = useState<string | null>(null)

  const handleCopyID = (id: string) => {
    if (!id) return
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(id).catch(() => fallbackCopyToClipboard(id))
    } else {
      fallbackCopyToClipboard(id)
    }
    setCopiedId(id)
    setTimeout(() => setCopiedId((prev) => (prev === id ? null : prev)), 1500)
  }

  // Nudge a 0-100 stat by delta (clamped) and persist. Shared by every stat button.
  const adjustStat = (key: string, current: number, delta: number) => {
    if (!activeChar) return
    const next = Math.max(0, Math.min(100, current + delta))
    onUpdateState(activeChar.id, { stats: { [key]: next } })
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] overflow-hidden relative">
      {/* Background vignette & blur gradients. The animated backdrop-filter
          blur is desktop-only and motion-safe: full-screen blur is one of
          the most GPU-expensive mobile operations and repaints on every
          scroll/atmosphere change for near-zero visual payoff on a phone, so
          small screens and prefers-reduced-motion get a cheap static
          gradient instead. Desktop with no motion preference is unchanged. */}
      <div
        className="hidden md:motion-safe:block absolute inset-0 pointer-events-none z-0 transition-all duration-700 ease-in-out"
        style={{
          backdropFilter: `blur(${blurAmount}px)`,
          WebkitBackdropFilter: `blur(${blurAmount}px)`,
        }}
      />
      <div className="absolute inset-0 pointer-events-none z-0 bg-gradient-to-b from-white/[0.03] via-transparent to-transparent md:motion-safe:hidden" />
      <div className="absolute inset-0 pointer-events-none z-0 bg-gradient-to-b from-transparent via-transparent to-background/60" />
      
      {/* Floating HUD Header */}
      <header
        inert={hudCollapsed && isMobile}
        className={`bg-[#0A0A0B]/80 backdrop-blur-md border-white/5 flex-none z-10 w-full transition-all duration-300 ${
          hudCollapsed && isMobile
            ? 'max-h-0 overflow-hidden -translate-y-1 pointer-events-none border-b-0'
            : 'max-h-[80vh] overflow-y-auto border-b'
        }`}
        style={{ opacity: hudCollapsed && isMobile ? 0 : textOpacity }}
      >
        <div className="max-w-[850px] mx-auto w-full px-md md:px-lg py-xs md:py-sm flex flex-col gap-1.5 md:gap-2">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-xs sm:gap-none">
            <div className="flex flex-col">
              <span className="hidden sm:block font-label-sm text-[11px] md:text-[9px] uppercase tracking-[0.25em] text-[#71717A]">
                ACTIVE NARRATIVE UNIT
              </span>
              <h1 className="font-sans text-base md:text-xl font-extrabold text-white tracking-tight leading-none mt-0.5">
                {activeChar?.name || 'Narrative Core'}
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 select-none mt-xs sm:mt-0">
              {activeChar?.state && (activeChar.state?.location || activeChar.state?.clothes) && (
                <span className="font-mono text-[11px] md:text-[9px] text-[#A1A1AA] bg-white/5 border border-white/10 px-2 py-0.5 rounded-full truncate max-w-[200px] sm:max-w-none">
                  {(activeChar.state?.location || '').toUpperCase()} • {(activeChar.state?.clothes || '').toUpperCase()}
                </span>
              )}
              {/* Session picker: switch between this character's independent chats */}
              {activeChar && onSelectChat && chats.length > 0 && (
                <select
                  value={activeChatId ?? ''}
                  onChange={(e) => onSelectChat(Number(e.target.value))}
                  title="Switch chat session"
                  className="font-mono text-[9.5px] text-zinc-200 bg-white/5 border border-white/10 rounded-full px-2 py-1 max-w-[160px] cursor-pointer focus:outline-none focus:border-white/25"
                >
                  {chats.map((c) => (
                    <option key={c.id} value={c.id} className="bg-[#0A0A0B]">
                      {c.title || 'Untitled'} · {c.message_count}
                    </option>
                  ))}
                </select>
              )}
              {/* Opening-greeting picker: only when the card has alternates */}
              {activeChar && onNewChat && greetings.length > 1 && (
                <select
                  value={greetingChoice}
                  onChange={(e) => setGreetingChoice(Number(e.target.value))}
                  title="Opening greeting for the next new chat"
                  className="font-mono text-[9.5px] text-zinc-200 bg-white/5 border border-white/10 rounded-full px-2 py-1 max-w-[150px] cursor-pointer focus:outline-none focus:border-white/25"
                >
                  {greetings.map((g, i) => (
                    <option key={i} value={i} className="bg-[#0A0A0B]">
                      Greeting {i + 1}: {g.slice(0, 24)}
                    </option>
                  ))}
                </select>
              )}
              {activeChar && onNewChat && (
                <button
                  type="button"
                  onClick={() => onNewChat(greetings.length > 1 ? greetingChoice : undefined)}
                  className="font-mono text-[11px] text-emerald-200 hover:text-emerald-100 bg-emerald-950/25 hover:bg-emerald-900/40 border border-emerald-800/40 px-2.5 py-1.5 min-h-9 rounded-full transition-all duration-300 flex items-center gap-1 cursor-pointer select-none shrink-0 touch-manipulation active:scale-95"
                  title="Start a new chat (keeps this one)"
                >
                  <Icon name="add" size="sm" />
                  <span className="hidden sm:inline">NEW CHAT</span>
                </button>
              )}
              {activeChar && onDeleteChat && activeChatId != null && chats.length > 1 && (
                <button
                  type="button"
                  onClick={() => onDeleteChat(activeChatId)}
                  className="font-mono text-[#FDA4AF] hover:text-red-400 bg-red-950/20 hover:bg-red-950/45 border border-red-900/40 rounded-full transition-all duration-300 flex items-center justify-center min-h-9 min-w-9 cursor-pointer select-none shrink-0 touch-manipulation active:scale-95"
                  title="Delete this chat session"
                  aria-label="Delete this chat session"
                >
                  <Icon name="delete" size="sm" />
                </button>
              )}
              {activeChar && (
                <button
                  type="button"
                  onClick={onClearChat}
                  className="font-mono text-[#A1A1AA] hover:text-red-400 bg-white/5 hover:bg-red-950/40 border border-white/10 hover:border-red-900/40 rounded-full transition-all duration-300 flex items-center justify-center min-h-9 min-w-9 cursor-pointer select-none shrink-0 touch-manipulation active:scale-95"
                  title="Reset: delete this character's entire history"
                  aria-label="Reset: delete this character's entire history"
                >
                  <Icon name="restart_alt" size="sm" />
                </button>
              )}
            </div>
          </div>

          {/* Stats Bar */}
          {activeChar?.state?.stats && (
            <>
            {/* Mobile: one-line summary; tap to expand the full grid. Desktop: always shown. */}
            <button
              type="button"
              onClick={() => setStatsExpanded((v) => !v)}
              className="md:hidden flex items-center justify-between gap-2 border-t border-white/5 pt-2 font-mono text-[11px] text-zinc-300 select-none"
              aria-expanded={statsExpanded}
            >
              <span className="flex items-center gap-3">
                <span>EN {activeChar?.state?.stats?.energy}</span>
                <span>HU {activeChar?.state?.stats?.hunger}</span>
                <span className="text-emerald-400">REL {activeChar?.state?.stats?.relationship?.score}</span>
              </span>
              <span className="flex items-center gap-0.5 text-zinc-500">
                {statsExpanded ? 'Hide' : 'Stats'}
                <Icon name={statsExpanded ? 'expand_less' : 'expand_more'} size="xs" />
              </span>
            </button>
            <div className={`${statsExpanded ? 'grid' : 'hidden'} md:grid grid-cols-1 md:grid-cols-5 gap-md border-t border-white/5 pt-2`}>
              <StatBar label="ENERGY" percent={activeChar?.state?.stats?.energy}>
                <span className="text-white">{activeChar?.state?.stats?.energy}%</span>
                <button
                  type="button"
                  onClick={() => activeChar && onUpdateState(activeChar.id, { stats: { is_sleeping: !activeChar.state?.stats?.is_sleeping } })}
                  className={`${STAT_CONTROL_CLASS} uppercase px-2`}
                >
                  {activeChar?.state?.stats?.is_sleeping ? 'Wake' : 'Sleep'}
                </button>
              </StatBar>

              <StatBar label="HUNGER" percent={activeChar?.state?.stats?.hunger}>
                <span className="text-white">{activeChar?.state?.stats?.hunger}%</span>
                <button
                  type="button"
                  onClick={() => adjustStat('hunger', activeChar?.state?.stats?.hunger ?? 0, -30)}
                  className={`${STAT_CONTROL_CLASS} uppercase px-2`}
                  disabled={activeChar?.state?.stats?.hunger === 0}
                >
                  Feed
                </button>
              </StatBar>

              <StatBar label="HAPPINESS" percent={activeChar?.state?.stats?.happiness ?? 100}>
                <span className="text-white">{activeChar?.state?.stats?.happiness ?? 100}%</span>
                <AdjustButtons
                  onDecrement={() => adjustStat('happiness', activeChar?.state?.stats?.happiness ?? 100, -10)}
                  onIncrement={() => adjustStat('happiness', activeChar?.state?.stats?.happiness ?? 100, 10)}
                />
              </StatBar>

              <StatBar label="SOCIAL" percent={activeChar?.state?.stats?.social ?? 100}>
                <span className="text-white">{activeChar?.state?.stats?.social ?? 100}%</span>
                <AdjustButtons
                  onDecrement={() => adjustStat('social', activeChar?.state?.stats?.social ?? 100, -10)}
                  onIncrement={() => adjustStat('social', activeChar?.state?.stats?.social ?? 100, 10)}
                />
              </StatBar>

              <StatBar label="RELATIONSHIP" percent={activeChar?.state?.stats?.relationship?.score} barClass="bg-emerald-400">
                <span className="text-white">{activeChar?.state?.stats?.relationship?.score}%</span>
                <AdjustButtons
                  onDecrement={() => adjustStat('relationship_score', activeChar?.state?.stats?.relationship?.score ?? 0, -10)}
                  onIncrement={() => adjustStat('relationship_score', activeChar?.state?.stats?.relationship?.score ?? 0, 10)}
                />
              </StatBar>
            </div>
            </>
          )}

          {/* Tab Selector */}
          <div className="flex border-t border-white/5 pt-1.5 mt-1.5 md:pt-2 md:mt-2 gap-4 select-none">
            <button
              type="button"
              onClick={() => setCurrentTab('chat')}
              className={`font-mono text-[11px] md:text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer ${
                currentTab === 'chat'
                  ? 'border-white text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Story Log
            </button>
            <button
              type="button"
              onClick={() => setCurrentTab('journal')}
              className={`font-mono text-[11px] md:text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer flex items-center gap-1.5 ${
                currentTab === 'journal'
                  ? 'border-white text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <span>Private Journal</span>
              {journalEntries.length > 0 && (
                <span className="bg-zinc-800 text-zinc-300 text-[10px] md:text-[8px] px-1.5 py-0.5 rounded font-sans font-bold leading-none">
                  {journalEntries.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Message Canvas */}
      <main
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto w-full flex flex-col items-center custom-scrollbar z-[1] transition-opacity duration-500"
        style={{ opacity: textOpacity }}
      >
        <div className="w-full max-w-[850px] px-md md:px-lg py-sm md:py-lg flex flex-col gap-md">
          {currentTab === 'chat' ? (
            <>
              {/* History divider. Hidden on mobile: it's decorative and the
                  transcript should own the phone viewport (~80%), so every
                  non-essential row of chrome above the first message is cut. */}
              <div className="hidden md:flex w-full items-center justify-center gap-sm py-2 opacity-30 select-none">
                <div className="h-px bg-white/10 flex-1" />
                <span className="font-mono text-[10px] md:text-[8px] uppercase tracking-[0.3em] text-[#71717A]">
                  Narrative Ingest
                </span>
                <div className="h-px bg-white/10 flex-1" />
              </div>

              {activePath.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 opacity-20">
                  <Icon name="menu_book" size="xl" className="mb-3" />
                  <p className="font-sans text-xs tracking-widest uppercase font-medium">Core Idle. Input prompt.</p>
                </div>
              )}

              {activePath.map((msg, i) => {
                const siblings = getSiblings(msg.id)
                const hasSiblings = siblings.length > 1
                const currentIndex = siblings.findIndex(s => s.id === msg.id)
                const isLastMessage = i === activePath.length - 1
                // Identity-scoped: only the node this stream actually belongs
                // to (see streamingMessageId) can ever render the live/typewriter
                // text, regardless of which node happens to be last.
                const isStreamTarget = streamingMessageId === undefined || streamingMessageId === msg.id
                const isStreaming = isLastMessage && msg.role === 'assistant' && isStreamTarget && (isLoading || isDraining)
                const isEditing = editingMessageId === msg.id
                const isCopied = !!msg.request_id && copiedId === msg.request_id

                return (
                  <MessageRow
                    key={msg.id}
                    msg={msg}
                    characterName={activeChar?.name || 'Narrator'}
                    isEditing={isEditing}
                    editContent={editContent}
                    isStreaming={isStreaming}
                    displayedContent={displayedContent}
                    isLoading={isLoading}
                    isCopied={isCopied}
                    hasSiblings={hasSiblings}
                    currentIndex={currentIndex}
                    siblingsLength={siblings.length}
                    onEditStart={() => {
                      setEditingMessageId(msg.id)
                      setEditContent(msg.content)
                    }}
                    onEditChange={setEditContent}
                    onEditCancel={() => setEditingMessageId(null)}
                    onEditSave={() => {
                      if (onEditMessage) onEditMessage(msg.id, editContent)
                      setEditingMessageId(null)
                    }}
                    onDelete={onDeleteMessage ? async () => {
                      const ok = await confirm({
                        title: 'Delete this message?',
                        message: 'This will also delete everything after it. This cannot be undone.',
                        confirmLabel: 'Delete',
                        danger: true,
                      })
                      if (ok) onDeleteMessage(msg.id)
                    } : undefined}
                    onRegenerate={() => handleRegenerate(msg)}
                    onCopyId={() => handleCopyID(msg.request_id || '')}
                    onPrevVariant={() => prevVariant(msg.id)}
                    onNextVariant={() => nextVariant(msg.id)}
                  />
                )
              })}

              {isLoading && !isDraining && (
                <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 pl-4 py-2 select-none">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                  <span>LOGGING RESPONSE STREAM...</span>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Journal Tab */}
              {isJournalLoading ? (
                <div className="flex items-center justify-center py-24 text-xs font-mono text-zinc-500 select-none animate-pulse">
                  <span>RETRIEVING PRIVATE JOURNAL ENTRIES...</span>
                </div>
              ) : journalEntries.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-24 opacity-20 select-none">
                  <Icon name="auto_stories" size="xl" className="mb-3" />
                  <p className="font-sans text-xs tracking-widest uppercase font-medium">No journal entries yet.</p>
                  <p className="font-sans text-[11px] md:text-[10px] text-center max-w-[280px] mt-2 leading-relaxed">
                    As you chat and interact, {activeChar?.name || 'the character'} will write down first-person reflections in this private log.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col gap-8 w-full max-w-[700px] mx-auto py-4">
                  {journalEntries.map((entry) => {
                    const date = new Date(entry.timestamp)
                    const formattedDate = date.toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })
                    
                    return (
                      <div key={entry.id} className="relative pl-6 border-l border-white/10 flex flex-col gap-2 transition-all duration-300">
                        {/* Circle bullet */}
                        <div className="absolute -left-[5.5px] top-[6px] w-2.5 h-2.5 rounded-full bg-zinc-700 border border-zinc-950" />
                        
                        {/* Header line */}
                        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] md:text-[10px] font-mono text-zinc-500 select-none">
                          <span>{formattedDate.toUpperCase()}</span>
                          <div className="flex gap-2">
                            <span>MOOD: {entry.mood_at_time ? entry.mood_at_time.toUpperCase() : 'NEUTRAL'}</span>
                            <span>•</span>
                            <span>AFFECTION: {entry.relationship_score}%</span>
                            <span>•</span>
                            <span>ENERGY: {entry.energy_level}%</span>
                          </div>
                        </div>
                        
                        {/* Content text */}
                        <div className="font-serif text-[16.5px] text-zinc-300 leading-relaxed italic bg-white/2 px-4 py-3 rounded-lg border border-white/5 select-text">
                          "{entry.content}"
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </>
          )}
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Floating Glass Input Container */}
      <div 
        className="bg-gradient-to-t from-[#050505] via-[#050505]/95 to-transparent w-full flex-none pb-[calc(1.5rem+env(safe-area-inset-bottom))] pt-sm px-md md:px-lg z-10 transition-opacity duration-500"
        style={{ opacity: textOpacity }}
      >
        <div className="max-w-[850px] mx-auto relative flex flex-col gap-2">
          {/* Tap-outside backdrop: standard bottom-sheet dismissal, consistent
              with the mobile sidebar's backdrop-click-to-close in App.tsx. */}
          {isDrawerOpen && activeChar && (
            <div
              onClick={() => setIsDrawerOpen(false)}
              aria-hidden="true"
              className="fixed inset-0 z-[15] bg-black/40"
            />
          )}
          {/* Interact Drawer Panel */}
          {isDrawerOpen && activeChar && (
            <div className="bg-[#0A0A0B]/90 backdrop-blur-md border border-white/10 rounded-2xl p-4 shadow-2xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-4 z-20 max-h-[70dvh] overflow-y-auto">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-3 select-none">
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setDrawerTab('actions')}
                    className={`font-mono text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer ${
                      drawerTab === 'actions'
                        ? 'border-white text-white font-bold'
                        : 'border-transparent text-zinc-500 hover:text-zinc-300'
                    }`}
                  >
                    Actions
                  </button>
                  <button
                    type="button"
                    onClick={() => setDrawerTab('gifts')}
                    className={`font-mono text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer ${
                      drawerTab === 'gifts'
                        ? 'border-white text-white font-bold'
                        : 'border-transparent text-zinc-500 hover:text-zinc-300'
                    }`}
                  >
                    Gifting
                  </button>
                </div>
                <IconButton
                  icon="close"
                  label="Close Drawer"
                  size="sm"
                  onClick={() => setIsDrawerOpen(false)}
                  className="text-zinc-500 hover:text-white"
                />
              </div>

              {/* Items Grid (actions and gifts share one layout) */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {(drawerTab === 'actions' ? ACTIONS : GIFTS).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleActionTrigger(item.id)}
                    disabled={isLoading}
                    className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/5 hover:border-white/20 transition-all duration-300 group cursor-pointer disabled:opacity-50"
                  >
                    <Icon name={item.icon} size="md" className="text-emerald-400 group-hover:scale-110 transition-transform duration-300" />
                    <span className="font-mono text-[11px] text-zinc-200 font-medium">
                      {item.name}
                    </span>
                    <span className="text-[9px] text-zinc-500 font-mono tracking-tighter">
                      {item.effect}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="bg-[#0A0A0B]/85 backdrop-blur-md border border-white/10 rounded-2xl flex items-end p-2 focus-within:border-white/30 transition-all duration-300">
            {/* Interact Drawer Toggle Button */}
            <button
              type="button"
              onClick={() => setIsDrawerOpen(!isDrawerOpen)}
              className={`rounded-xl transition-all duration-300 flex items-center justify-center shrink-0 cursor-pointer mr-1 mb-0.5 border min-h-11 min-w-11 md:min-h-9 md:min-w-9 touch-manipulation active:scale-95 ${
                isDrawerOpen
                  ? 'bg-white text-black border-white'
                  : 'bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-white border-white/10'
              }`}
              title="Interact & Gift"
              aria-label="Interact & Gift"
              aria-expanded={isDrawerOpen}
              disabled={isLoading || !activeChar}
            >
              <Icon name="bolt" size="sm" />
            </button>

            <textarea
              ref={composerRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              className="w-full bg-transparent border-none focus:outline-none text-white font-sans text-base md:text-sm resize-none min-h-[28px] max-h-[160px] py-1 px-2 overflow-y-auto"
              placeholder={`Write a prompt for ${activeChar?.name || 'Core'}...`}
              rows={1}
              disabled={isLoading || !activeChar}
            />
            <div className="flex gap-1 ml-2">
              {isLoading ? (
                <IconButton
                  icon="stop"
                  label="Stop generating"
                  size="sm"
                  onClick={onCancelStream}
                  className="bg-red-600 text-white hover:bg-red-500 shadow-lg self-end mb-0.5"
                />
              ) : (
                <IconButton
                  icon="arrow_upward"
                  label="Send"
                  size="sm"
                  onClick={handleSend}
                  disabled={!input.trim()}
                  className="bg-white text-black hover:bg-[#E4E4E7] disabled:opacity-30 shadow-lg self-end mb-0.5"
                />
              )}
            </div>
          </div>
          {/* Desktop-only helper: on a phone there's no Shift+Enter and the
              line just steals vertical space from the transcript. */}
          <div className="hidden md:block text-center">
            <span className="font-mono text-[11px] md:text-[9px] uppercase tracking-wider text-[#71717A]">
              Shift + Enter for multi-line. Direct stream enabled.
            </span>
          </div>
        </div>
      </div>

      {dialog}
    </div>
  )
}

export default ChatView
