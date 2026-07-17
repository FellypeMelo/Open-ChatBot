import React, { useRef, useEffect, useState, useCallback } from 'react'
import MessageRenderer from './MessageRenderer'
import { useMessageTree } from '../hooks/useMessageTree'
import type { MessageNode } from '../hooks/useMessageTree'
import { useTokenQueue } from '../hooks/useTokenQueue'
import { useAtmosphere } from '../hooks/useAtmosphere'
import { useAudio } from '../hooks/useAudio'
import { fetchJournal } from '../services/api'
import type { JournalEntry, Character, ChatSession } from '../services/api'

const ACTIONS = [
  { id: 'hug', name: 'Hug', icon: 'favorite', effect: 'HAPPINESS +5 • SOCIAL +10 • RELATION +2' },
  { id: 'pat_head', name: 'Pat Head', icon: 'emoji_emotions', effect: 'HAPPINESS +3 • SOCIAL +5 • RELATION +1' },
  { id: 'tease', name: 'Tease', icon: 'theater_comedy', effect: 'HAPPINESS +2 • SOCIAL +8 • RELATION +1' },
  { id: 'hold_hand', name: 'Hold Hand', icon: 'handshake', effect: 'HAPPINESS +4 • SOCIAL +8 • RELATION +2' }
]

const GIFTS = [
  { id: 'coffee', name: 'Hot Coffee', icon: 'local_cafe', effect: 'HUNGER -10 • ENERGY +15 • RELATION +2' },
  { id: 'croissant', name: 'Croissant', icon: 'bakery_dining', effect: 'HUNGER -35 • ENERGY +5 • RELATION +3' },
  { id: 'book', name: 'Book', icon: 'book', effect: 'HAPPINESS +8 • SOCIAL +5 • RELATION +4' },
  { id: 'necklace', name: 'Necklace', icon: 'diamond', effect: 'HAPPINESS +15 • SOCIAL +10 • RELATION +8' }
]

// Inline editor shared by the user-prompt and assistant-reply message editors --
// same textarea + Cancel/Save row, differing only in the textarea's type styling.
const MessageEditor: React.FC<{
  value: string
  onChange: (v: string) => void
  onCancel: () => void
  onSave: () => void
  textareaClassName: string
  wrapperClassName?: string
}> = ({ value, onChange, onCancel, onSave, textareaClassName, wrapperClassName = 'w-full flex flex-col gap-2' }) => (
  <div className={wrapperClassName}>
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={textareaClassName}
      autoFocus
    />
    <div className="flex gap-2 self-end">
      <button onClick={onCancel} className="px-3 py-1 text-xs font-mono text-zinc-400 hover:text-white">
        CANCEL
      </button>
      <button onClick={onSave} className="px-3 py-1 bg-white text-black text-xs font-bold rounded">
        SAVE
      </button>
    </div>
  </div>
)

// Stat gauge shell: label row + progress bar. The right-hand value and controls
// vary per stat, so each caller passes them as children.
const StatBar: React.FC<{
  label: string
  percent?: number
  barClass?: string
  children: React.ReactNode
}> = ({ label, percent, barClass = 'bg-white', children }) => (
  <div className="flex flex-col gap-1">
    <div className="flex items-center justify-between font-mono text-[9px] text-[#71717A]">
      <span>{label}</span>
      <div className="flex items-center gap-1.5">{children}</div>
    </div>
    <div className="h-1 bg-white/5 rounded-full overflow-hidden">
      <div className={`h-full ${barClass} transition-all duration-500`} style={{ width: `${percent}%` }} />
    </div>
  </div>
)

// The identical minus/plus pair used by happiness / social / relationship.
const AdjustButtons: React.FC<{ onDecrement: () => void; onIncrement: () => void }> = ({ onDecrement, onIncrement }) => (
  <div className="flex gap-0.5">
    <button
      type="button"
      onClick={onDecrement}
      className="text-[8px] bg-white/5 border border-white/10 px-1 py-0.5 rounded hover:bg-white/10 text-[#A1A1AA] hover:text-white transition-colors cursor-pointer select-none"
    >
      -
    </button>
    <button
      type="button"
      onClick={onIncrement}
      className="text-[8px] bg-white/5 border border-white/10 px-1 py-0.5 rounded hover:bg-white/10 text-[#A1A1AA] hover:text-white transition-colors cursor-pointer select-none"
    >
      +
    </button>
  </div>
)

interface ChatViewProps {
  activeChar: Character | null
  messages: MessageNode[]
  input: string
  setInput: (val: string) => void
  onSend: (parentId?: number) => void
  onRegenerate: (parentId: number) => void
  isLoading: boolean
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
}

const ChatView: React.FC<ChatViewProps> = ({
  activeChar,
  messages,
  input,
  setInput,
  onSend,
  onRegenerate,
  isLoading,
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
  onDeleteChat
}) => {
  // Which opening greeting seeds the next "New Chat" (only relevant when the
  // character has more than one greeting).
  const [greetingChoice, setGreetingChoice] = useState(0)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const { activePath, nextVariant, prevVariant, getSiblings } = useMessageTree(messages)
  const { playTypewriterClick, resumeAudio, playAmbient, stopAmbient } = useAudio()
  const { displayedContent, enqueue, reset, isDraining } = useTokenQueue(20, playTypewriterClick)
  const { blurAmount, textOpacity } = useAtmosphere(displayedContent)
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

  const scrollToBottom = useCallback((force = false) => {
    if (force || isAtBottom) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [isAtBottom])

  const handleScroll = (e: React.UIEvent<HTMLElement>) => {
    const el = e.currentTarget
    const offset = 100
    const atBottom = el.scrollHeight - el.scrollTop <= el.clientHeight + offset
    setIsAtBottom(atBottom)
  }

  useEffect(() => {
    scrollToBottom()
  }, [activePath, displayedContent, scrollToBottom])

  useEffect(() => {
    if (isLoading) {
      reset()
      prevContentLength.current = 0
    }
  }, [isLoading, reset])

  useEffect(() => {
    if (isLoading && activePath.length > 0) {
      const lastMsg = activePath[activePath.length - 1]
      if (lastMsg.role === 'assistant' && lastMsg.content.length > prevContentLength.current) {
        const delta = lastMsg.content.substring(prevContentLength.current)
        enqueue(delta)
        prevContentLength.current = lastMsg.content.length
      }
    }
  }, [activePath, isLoading, enqueue])

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
    navigator.clipboard.writeText(id)
    setCopiedId(id)
    setTimeout(() => setCopiedId((prev) => (prev === id ? null : prev)), 1500)
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] overflow-hidden relative">
      {/* Background vignette & blur gradients */}
      <div 
        className="absolute inset-0 pointer-events-none z-0 transition-all duration-700 ease-in-out"
        style={{ 
          backdropFilter: `blur(${blurAmount}px)`,
          WebkitBackdropFilter: `blur(${blurAmount}px)`,
        }}
      />
      <div className="absolute inset-0 pointer-events-none z-0 bg-gradient-to-b from-transparent via-transparent to-background/60" />
      
      {/* Floating HUD Header */}
      <header className="bg-[#0A0A0B]/80 backdrop-blur-md border-b border-white/5 flex-none z-10 w-full transition-opacity duration-500" style={{ opacity: textOpacity }}>
        <div className="max-w-[850px] mx-auto w-full px-md md:px-lg py-sm flex flex-col gap-2">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-xs sm:gap-none">
            <div className="flex flex-col">
              <span className="hidden sm:block font-label-sm text-[9px] uppercase tracking-[0.25em] text-[#71717A]">
                ACTIVE NARRATIVE UNIT
              </span>
              <h1 className="font-sans text-xl font-extrabold text-white tracking-tight leading-none mt-0.5">
                {activeChar?.name || 'Narrative Core'}
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 select-none mt-xs sm:mt-0">
              {activeChar?.state && (activeChar.state?.location || activeChar.state?.clothes) && (
                <span className="font-mono text-[9px] text-[#A1A1AA] bg-white/5 border border-white/10 px-2 py-0.5 rounded-full truncate max-w-[200px] sm:max-w-none">
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
                  className="font-mono text-[9.5px] text-emerald-200 hover:text-emerald-100 bg-emerald-950/25 hover:bg-emerald-900/40 border border-emerald-800/40 px-3 py-1 rounded-full transition-all duration-300 flex items-center gap-1 cursor-pointer select-none shrink-0"
                  title="Start a new chat (keeps this one)"
                >
                  <span className="material-symbols-outlined text-[11px] leading-none">add</span>
                  NEW CHAT
                </button>
              )}
              {activeChar && onDeleteChat && activeChatId != null && chats.length > 1 && (
                <button
                  type="button"
                  onClick={() => onDeleteChat(activeChatId)}
                  className="font-mono text-[9.5px] text-[#FDA4AF] hover:text-red-400 bg-red-950/20 hover:bg-red-950/45 border border-red-900/40 px-2.5 py-1 rounded-full transition-all duration-300 flex items-center gap-1 cursor-pointer select-none shrink-0"
                  title="Delete this chat session"
                >
                  <span className="material-symbols-outlined text-[11px] leading-none">delete</span>
                </button>
              )}
              {activeChar && (
                <button
                  type="button"
                  onClick={onClearChat}
                  className="font-mono text-[9.5px] text-[#A1A1AA] hover:text-red-400 bg-white/5 hover:bg-red-950/40 border border-white/10 hover:border-red-900/40 px-2.5 py-1 rounded-full transition-all duration-300 flex items-center gap-1 cursor-pointer select-none shrink-0"
                  title="Reset: delete this character's entire history"
                >
                  <span className="material-symbols-outlined text-[11px] leading-none">restart_alt</span>
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
                <span className="material-symbols-outlined text-[16px]">{statsExpanded ? 'expand_less' : 'expand_more'}</span>
              </span>
            </button>
            <div className={`${statsExpanded ? 'grid' : 'hidden'} md:grid grid-cols-2 md:grid-cols-5 gap-md border-t border-white/5 pt-2`}>
              <StatBar label="ENERGY" percent={activeChar?.state?.stats?.energy}>
                <span className="text-white">{activeChar?.state?.stats?.energy}%</span>
                <button
                  type="button"
                  onClick={() => activeChar && onUpdateState(activeChar.id, { stats: { is_sleeping: !activeChar.state?.stats?.is_sleeping } })}
                  className="text-[8px] bg-white/5 border border-white/10 px-1 py-0.5 rounded uppercase hover:bg-white/10 text-[#A1A1AA] hover:text-white transition-colors cursor-pointer select-none"
                >
                  {activeChar?.state?.stats?.is_sleeping ? 'Wake' : 'Sleep'}
                </button>
              </StatBar>

              <StatBar label="HUNGER" percent={activeChar?.state?.stats?.hunger}>
                <span className="text-white">{activeChar?.state?.stats?.hunger}%</span>
                <button
                  type="button"
                  onClick={() => activeChar && onUpdateState(activeChar.id, { stats: { hunger: Math.max(0, (activeChar.state?.stats?.hunger ?? 0) - 30) } })}
                  className="text-[8px] bg-white/5 border border-white/10 px-1 py-0.5 rounded uppercase hover:bg-white/10 text-[#A1A1AA] hover:text-white transition-colors cursor-pointer select-none disabled:opacity-20"
                  disabled={activeChar?.state?.stats?.hunger === 0}
                >
                  Feed
                </button>
              </StatBar>

              <StatBar label="HAPPINESS" percent={activeChar?.state?.stats?.happiness ?? 100}>
                <span className="text-white">{activeChar?.state?.stats?.happiness ?? 100}%</span>
                <AdjustButtons
                  onDecrement={() => activeChar && onUpdateState(activeChar.id, { stats: { happiness: Math.max(0, (activeChar.state?.stats?.happiness ?? 100) - 10) } })}
                  onIncrement={() => activeChar && onUpdateState(activeChar.id, { stats: { happiness: Math.min(100, (activeChar.state?.stats?.happiness ?? 100) + 10) } })}
                />
              </StatBar>

              <StatBar label="SOCIAL" percent={activeChar?.state?.stats?.social ?? 100}>
                <span className="text-white">{activeChar?.state?.stats?.social ?? 100}%</span>
                <AdjustButtons
                  onDecrement={() => activeChar && onUpdateState(activeChar.id, { stats: { social: Math.max(0, (activeChar.state?.stats?.social ?? 100) - 10) } })}
                  onIncrement={() => activeChar && onUpdateState(activeChar.id, { stats: { social: Math.min(100, (activeChar.state?.stats?.social ?? 100) + 10) } })}
                />
              </StatBar>

              <StatBar label="RELATIONSHIP" percent={activeChar?.state?.stats?.relationship?.score} barClass="bg-emerald-400">
                <span className="text-white">{activeChar?.state?.stats?.relationship?.score}%</span>
                <AdjustButtons
                  onDecrement={() => activeChar && onUpdateState(activeChar.id, { stats: { relationship_score: Math.max(0, (activeChar.state?.stats?.relationship?.score ?? 0) - 10) } })}
                  onIncrement={() => activeChar && onUpdateState(activeChar.id, { stats: { relationship_score: Math.min(100, (activeChar.state?.stats?.relationship?.score ?? 0) + 10) } })}
                />
              </StatBar>
            </div>
            </>
          )}

          {/* Tab Selector */}
          <div className="flex border-t border-white/5 pt-2 mt-2 gap-4 select-none">
            <button
              type="button"
              onClick={() => setCurrentTab('chat')}
              className={`font-mono text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer ${
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
              className={`font-mono text-[10px] uppercase tracking-wider py-1 px-2 border-b-2 transition-all cursor-pointer flex items-center gap-1.5 ${
                currentTab === 'journal'
                  ? 'border-white text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <span>Private Journal</span>
              {journalEntries.length > 0 && (
                <span className="bg-zinc-800 text-zinc-300 text-[8px] px-1.5 py-0.5 rounded font-sans font-bold leading-none">
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
        <div className="w-full max-w-[850px] px-md md:px-lg py-lg flex flex-col gap-md">
          {currentTab === 'chat' ? (
            <>
              {/* History divider */}
              <div className="w-full flex items-center justify-center gap-sm py-2 opacity-30 select-none">
                <div className="h-px bg-white/10 flex-1" />
                <span className="font-mono text-[8px] uppercase tracking-[0.3em] text-[#71717A]">
                  Narrative Ingest
                </span>
                <div className="h-px bg-white/10 flex-1" />
              </div>

              {activePath.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 opacity-20">
                  <span className="material-symbols-outlined text-[48px] mb-3">menu_book</span>
                  <p className="font-sans text-xs tracking-widest uppercase font-medium">Core Idle. Input prompt.</p>
                </div>
              )}

              {activePath.map((msg, i) => {
                const siblings = getSiblings(msg.id)
                const hasSiblings = siblings.length > 1
                const currentIndex = siblings.findIndex(s => s.id === msg.id)
                const isLastMessage = i === activePath.length - 1
                const isStreaming = isLastMessage && msg.role === 'assistant' && (isLoading || isDraining)

                if (msg.role === 'user') {
                  const isEditing = editingMessageId === msg.id
                  return (
                    <div key={msg.id} className="w-full flex flex-col items-start mt-6 mb-6 group">
                      <div className="flex items-center justify-between w-full mb-2">
                        <div className="flex items-center gap-2 select-none">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#34D399]/40" />
                          <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-[#34D399]/70">
                            PROMPT ACTION
                          </span>
                        </div>
                        
                        {!isEditing && (
                          <div className="flex items-center gap-1.5 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                            <button 
                              onClick={() => {
                                setEditingMessageId(msg.id)
                                setEditContent(msg.content)
                              }}
                              className="text-[#71717A] hover:text-white transition-colors cursor-pointer"
                              title="Edit"
                            >
                              <span className="material-symbols-outlined text-[14px]">edit</span>
                            </button>
                            {onDeleteMessage && (
                              <button 
                                onClick={() => {
                                  if(confirm('Delete this message and everything after it?')) onDeleteMessage(msg.id)
                                }}
                                className="text-[#71717A] hover:text-red-400 transition-colors cursor-pointer"
                                title="Delete"
                              >
                                <span className="material-symbols-outlined text-[14px]">delete</span>
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {isEditing ? (
                        <MessageEditor
                          value={editContent}
                          onChange={setEditContent}
                          onCancel={() => setEditingMessageId(null)}
                          onSave={() => {
                            if (onEditMessage) onEditMessage(msg.id, editContent)
                            setEditingMessageId(null)
                          }}
                          textareaClassName="w-full bg-[#09090B] border border-white/20 focus:border-white/40 outline-none rounded p-3 text-zinc-300 font-sans text-sm resize-y min-h-[80px]"
                        />
                      ) : (
                        <div className="w-full border-l-2 border-white/10 pl-5 py-1 text-zinc-400 font-sans text-sm leading-relaxed whitespace-pre-wrap">
                          {msg.content}
                        </div>
                      )}
                    </div>
                  )
                }

                return (
                  <div 
                    key={msg.id} 
                    className="flex flex-col gap-2 w-full group mt-6 mb-8 relative border-t border-white/5 pt-6 first:border-t-0 first:pt-0"
                  >
                    {/* Character Header Info */}
                    <div className="flex items-center justify-between mb-1 select-none">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/50">
                          {activeChar?.name || 'Narrator'}
                        </span>
                        {isStreaming && (
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                        )}
                      </div>

                      {/* Variant Navigation switcher */}
                      {hasSiblings && (
                        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-white/5 border border-white/10 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
                          <button 
                            onClick={() => prevVariant(msg.id)}
                            disabled={currentIndex === 0}
                            className="text-[#71717A] hover:text-white disabled:opacity-30 transition-colors flex items-center cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-[12px]">chevron_left</span>
                          </button>
                          <span className="font-mono text-[8px] text-[#71717A]">
                            {currentIndex + 1} / {siblings.length}
                          </span>
                          <button 
                            onClick={() => nextVariant(msg.id)}
                            disabled={currentIndex === siblings.length - 1}
                            className="text-[#71717A] hover:text-white disabled:opacity-30 transition-colors flex items-center cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-[12px]">chevron_right</span>
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Message Body (No bubble, flows directly on background) */}
                    {editingMessageId === msg.id ? (
                      <MessageEditor
                        value={editContent}
                        onChange={setEditContent}
                        onCancel={() => setEditingMessageId(null)}
                        onSave={() => {
                          if (onEditMessage) onEditMessage(msg.id, editContent)
                          setEditingMessageId(null)
                        }}
                        textareaClassName="w-full bg-[#09090B] border border-white/20 focus:border-white/40 outline-none rounded p-3 text-zinc-300 font-serif text-[17px] leading-[1.8] resize-y min-h-[120px]"
                        wrapperClassName="w-full flex flex-col gap-2 mt-2"
                      />
                    ) : (
                      <div className="font-serif text-[17px] text-zinc-200 leading-[1.8] antialiased select-text">
                        <MessageRenderer content={isStreaming ? displayedContent : msg.content} />
                      </div>
                    )}

                    {/* Controls Footer */}
                    <div className="flex gap-4 mt-3 items-center opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
                      <button 
                        onClick={() => handleRegenerate(msg)}
                        className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[12px]">refresh</span>
                        Regenerate
                      </button>
                      <button 
                        onClick={() => {
                          setEditingMessageId(msg.id)
                          setEditContent(msg.content)
                        }}
                        className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[12px]">edit</span>
                        Edit
                      </button>
                      {onDeleteMessage && (
                        <button 
                          onClick={() => {
                            if(confirm('Delete this message and everything after it?')) onDeleteMessage(msg.id)
                          }}
                          className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-red-400 transition-colors cursor-pointer"
                        >
                          <span className="material-symbols-outlined text-[12px]">delete</span>
                          Delete
                        </button>
                      )}
                      <button
                        onClick={() => handleCopyID(msg.request_id || '')}
                        disabled={!msg.request_id}
                        className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:text-[#71717A]"
                        title={msg.request_id ? 'Copy Request ID' : 'Request ID not available yet'}
                      >
                        <span className="material-symbols-outlined text-[11px]">
                          {msg.request_id && copiedId === msg.request_id ? 'check' : 'content_copy'}
                        </span>
                        {msg.request_id && copiedId === msg.request_id ? 'Copied' : 'Copy ID'}
                      </button>
                      {msg.request_id && (
                        <span className="font-mono text-[8px] text-[#71717A]/30 ml-auto uppercase tracking-wider select-none">
                          REQ: {msg.request_id.split('-')[0]}
                        </span>
                      )}
                    </div>
                  </div>
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
                  <span className="material-symbols-outlined text-[48px] mb-3">auto_stories</span>
                  <p className="font-sans text-xs tracking-widest uppercase font-medium">No journal entries yet.</p>
                  <p className="font-sans text-[10px] text-center max-w-[280px] mt-2 leading-relaxed">
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
                        <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-zinc-500 select-none">
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
          {/* Interact Drawer Panel */}
          {isDrawerOpen && activeChar && (
            <div className="bg-[#0A0A0B]/90 backdrop-blur-md border border-white/10 rounded-2xl p-4 shadow-2xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-4 z-20">
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
                <button
                  type="button"
                  onClick={() => setIsDrawerOpen(false)}
                  className="text-zinc-500 hover:text-white flex items-center cursor-pointer p-1"
                  title="Close Drawer"
                >
                  <span className="material-symbols-outlined text-[16px]">close</span>
                </button>
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
                    <span className="material-symbols-outlined text-[20px] text-emerald-400 group-hover:scale-110 transition-transform duration-300">
                      {item.icon}
                    </span>
                    <span className="font-mono text-[10px] text-zinc-200 font-medium">
                      {item.name}
                    </span>
                    <span className="text-[8px] text-zinc-500 font-mono tracking-tighter">
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
              className={`p-1.5 rounded-xl transition-all duration-300 flex items-center justify-center shrink-0 cursor-pointer mr-1 mb-0.5 border ${
                isDrawerOpen
                  ? 'bg-white text-black border-white'
                  : 'bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-white border-white/10'
              }`}
              title="Interact & Gift"
              disabled={isLoading || !activeChar}
            >
              <span className="material-symbols-outlined text-[18px]">bolt</span>
            </button>

            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              className="w-full bg-transparent border-none focus:outline-none text-white font-sans text-sm resize-none min-h-[28px] max-h-[160px] py-1 px-2 overflow-y-auto" 
              placeholder={`Write a prompt for ${activeChar?.name || 'Core'}...`}
              rows={1}
              disabled={isLoading || !activeChar}
            />
            <div className="flex gap-1 ml-2">
              <button 
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="bg-white text-black hover:bg-[#E4E4E7] disabled:opacity-30 transition-all duration-300 flex items-center justify-center h-8 w-8 rounded-full shadow-lg shrink-0 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[16px] font-bold">arrow_upward</span>
              </button>
            </div>
          </div>
          <div className="text-center">
            <span className="font-mono text-[9px] uppercase tracking-wider text-[#71717A]">
              Shift + Enter for multi-line. Direct stream enabled.
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatView
