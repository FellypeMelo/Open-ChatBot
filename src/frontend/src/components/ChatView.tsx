import React, { useRef, useEffect, useCallback } from 'react'
import MessageRenderer from './MessageRenderer'
import { useMessageTree, MessageNode } from '../hooks/useMessageTree'

interface Character {
  id: number
  name: string
  description: string
  tags: { id: number; label: string }[]
  state?: {
    stats: {
      energy: number
      hunger: number
      relationship: {
        score: number
      }
    }
  }
}

interface ChatViewProps {
  activeChar: Character | null
  messages: MessageNode[]
  input: string
  setInput: (val: string) => void
  onSend: (parentId?: number) => void
  onRegenerate: (parentId: number) => void
  isLoading: boolean
}

const ChatView: React.FC<ChatViewProps> = ({
  activeChar,
  messages,
  input,
  setInput,
  onSend,
  onRegenerate,
  isLoading
}) => {
  const chatEndRef = useRef<HTMLDivElement>(null)
  const { activePath, nextVariant, prevVariant, getSiblings } = useMessageTree(messages)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [activePath])

  const handleRegenerate = (node: MessageNode) => {
    if (isLoading || node.parent_id === null) return
    onRegenerate(node.parent_id)
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      {/* TopAppBar */}
      <header className="bg-background border-b border-outline-variant/10 flex-none z-10 w-full">
        <div className="flex justify-between items-center w-full px-md h-16 max-w-container-max mx-auto">
          <div className="flex items-center gap-sm">
            <div className="flex flex-col">
              <h1 className="font-display text-headline-lg font-semibold text-primary">
                {activeChar?.name || 'Open Chat'}
              </h1>
              {activeChar?.state?.stats ? (
                <div className="flex items-center gap-3 mt-1">
                  <div className="flex items-center gap-1" title="Energy">
                    <span className="material-symbols-outlined text-[14px] text-on-surface-variant">bolt</span>
                    <div className="w-12 h-1 bg-surface-container-highest rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${activeChar.state.stats.energy}%` }}></div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1" title="Hunger">
                    <span className="material-symbols-outlined text-[14px] text-on-surface-variant">restaurant</span>
                    <div className="w-12 h-1 bg-surface-container-highest rounded-full overflow-hidden">
                      <div className="h-full bg-surface-tint" style={{ width: `${activeChar.state.stats.hunger}%` }}></div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1" title="Relationship Score">
                    <span className="material-symbols-outlined text-[14px] text-on-surface-variant">favorite</span>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">{activeChar.state.stats.relationship.score}%</span>
                  </div>
                </div>
              ) : (
                <span className="font-label-sm text-label-sm text-on-surface-variant">
                  {activeChar?.description.substring(0, 40) || 'Narrative Session'}...
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-sm">
            <button className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center h-10 w-10">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <button className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center h-10 w-10">
              <span className="material-symbols-outlined">history</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Canvas */}
      <main className="flex-1 overflow-y-auto w-full flex flex-col items-center custom-scrollbar">
        <div className="w-full max-w-container-max px-sm md:px-md py-xl flex flex-col gap-lg">
          {/* Context Divider */}
          <div className="w-full flex items-center justify-center gap-md py-sm opacity-50">
            <div className="h-px bg-outline-variant flex-1"></div>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest">
              The Archives - Midnight
            </span>
            <div className="h-px bg-outline-variant flex-1"></div>
          </div>

          {activePath.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 opacity-30">
              <span className="material-symbols-outlined text-[64px] mb-4">menu_book</span>
              <p className="font-display text-body-lg italic">Begin the narrative...</p>
            </div>
          )}

          {activePath.map((msg, i) => {
            const siblings = getSiblings(msg.id);
            const hasSiblings = siblings.length > 1;
            const currentIndex = siblings.findIndex(s => s.id === msg.id);

            return (
              <div key={msg.id} className={`flex flex-col gap-xs w-full group ${msg.role === 'user' ? 'items-end pl-xl pr-0 mt-md' : 'pl-0 pr-xl mt-md'}`}>
                <div className="flex items-center gap-xs mb-1">
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-surface-container overflow-hidden flex items-center justify-center border border-outline-variant">
                      <span className="material-symbols-outlined text-sm text-on-surface-variant">person</span>
                    </div>
                  )}
                  <span className={`font-display text-body-md font-semibold ${msg.role === 'user' ? 'text-on-surface-variant' : 'text-primary'}`}>
                    {msg.role === 'user' ? 'You' : activeChar?.name}
                  </span>
                  
                  {msg.role === 'assistant' && hasSiblings && (
                    <div className="flex items-center gap-1 ml-2 px-2 py-0.5 rounded-full bg-surface-container-high border border-outline-variant/30 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={() => prevVariant(msg.id)}
                        disabled={currentIndex === 0}
                        className="text-on-surface-variant hover:text-primary disabled:opacity-30 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[16px]">chevron_left</span>
                      </button>
                      <span className="font-label-sm text-label-xs text-on-surface-variant select-none">
                        {currentIndex + 1} / {siblings.length}
                      </span>
                      <button 
                        onClick={() => nextVariant(msg.id)}
                        disabled={currentIndex === siblings.length - 1}
                        className="text-on-surface-variant hover:text-primary disabled:opacity-30 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                      </button>
                    </div>
                  )}
                </div>

                <div className="relative w-full">
                  <div className={`font-body-lg text-body-lg leading-relaxed ${msg.role === 'user' ? 'text-primary' : 'text-on-surface'}`}>
                    {msg.role === 'user' ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <MessageRenderer content={msg.content} />
                    )}
                  </div>

                  {msg.role === 'assistant' && i === activePath.length - 1 && !isLoading && (
                    <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={() => handleRegenerate(msg)}
                        className="flex items-center gap-1 px-3 py-1 rounded-md bg-surface-container-high border border-outline-variant text-on-surface-variant hover:text-primary transition-all text-[12px] font-medium"
                      >
                        <span className="material-symbols-outlined text-[14px]">refresh</span>
                        Regenerate
                      </button>
                      <button className="flex items-center justify-center h-7 w-7 rounded-md bg-surface-container-high border border-outline-variant text-on-surface-variant hover:text-primary transition-all">
                        <span className="material-symbols-outlined text-[14px]">content_copy</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex flex-col gap-xs w-full pl-0 pr-xl mt-md opacity-50">
              <div className="font-label-sm text-label-sm text-on-surface-variant animate-pulse">
                {activeChar?.name} is writing...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Bottom Input Area */}
      <div className="bg-background w-full flex-none pb-lg pt-sm px-sm md:px-md border-t border-outline-variant/10">
        <div className="max-w-container-max mx-auto relative">
          <div className="bg-surface-container-low border border-outline-variant rounded-xl flex items-end p-sm focus-within:border-outline focus-within:bg-surface-container transition-all">
            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  onSend()
                }
              }}
              className="w-full bg-transparent border-none focus:ring-0 text-on-surface font-body-md text-body-md resize-none min-h-[24px] max-h-[200px] py-0 overflow-y-auto" 
              placeholder={`Speak with ${activeChar?.name || 'Entity'}...`}
              rows={1}
              disabled={isLoading || !activeChar}
            />
            <div className="flex gap-xs ml-sm">
              <button 
                className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center h-8 w-8"
                disabled={isLoading}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>add_circle</span>
              </button>
              <button 
                onClick={() => onSend()}
                disabled={isLoading || !input.trim()}
                className="bg-on-surface text-background hover:bg-primary disabled:opacity-50 transition-colors flex items-center justify-center h-8 w-8 rounded-full shadow-sm"
              >
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>arrow_upward</span>
              </button>
            </div>
          </div>
          <div className="text-center mt-xs">
            <span className="font-label-sm text-label-sm text-on-surface-variant/30">
              Shift + Enter for new line. AI can make mistakes.
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatView
