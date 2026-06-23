import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import CharactersView from './components/CharactersView'
import ChatView from './components/ChatView'
import TagManagementView from './components/TagManagementView'
import LorebookView from './components/LorebookView'
import CharacterCreator from './components/CharacterCreator'
import UserProfileModal from './components/UserProfileModal'
import SettingsModal from './components/SettingsModal'
import TagCreator from './components/TagCreator'
import ErrorBoundary from './components/ErrorBoundary'
import * as api from './services/api'
import type { MessageNode } from './hooks/useMessageTree'
import { useSettings } from './hooks/useSettings'

interface Tag {
  id: number
  label: string
  instruction: string
}

interface Character {
  id: number
  name: string
  description: string
  tags: Tag[]
  state?: {
    location: string
    clothes: string
    mood: string
    interaction_count: number
    stats: {
      energy: number
      hunger: number
      relationship: {
        score: number
      }
    }
  }
}

interface User {
  id: number
  name: string
  gender: string
  is_active: boolean
}

type View = 'chat' | 'characters' | 'archives' | 'library'
type ModalType = 'character' | 'user' | 'tag' | 'settings' | null

interface Toast {
  message: string
  type: 'success' | 'error'
}

function App() {
  const { config } = useSettings()
  const [currentView, setCurrentView] = useState<View>('characters')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [activeModal, setActiveModal] = useState<ModalType>(null)
  const [toast, setToast] = useState<Toast | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [messages, setMessages] = useState<MessageNode[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [user, setUser] = useState<User | null>(null)

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const fetchUser = useCallback(async () => {
    try {
      const data = await api.fetchUser()
      setUser(data)
    } catch (err) {
      showToast('Failed to fetch user.', 'error')
    }
  }, [])

  const fetchCharacters = useCallback(async () => {
    try {
      const data = await api.fetchCharacters()
      setCharacters(data)
      if (data.length > 0 && !selectedCharId) {
        setSelectedCharId(data[0].id)
      }
    } catch (err) {
      showToast('Failed to fetch characters.', 'error')
    }
  }, [selectedCharId])

  const fetchTags = useCallback(async () => {
    try {
      const data = await api.fetchTags()
      setTags(data)
    } catch (err) {
      showToast('Failed to fetch tags.', 'error')
    }
  }, [])

  useEffect(() => {
    fetchCharacters()
    fetchUser()
    fetchTags()
  }, [fetchCharacters, fetchUser, fetchTags])

  const fetchHistory = useCallback(async (charId: number) => {
    try {
      const data = await api.fetchHistory(charId)
      // Only update if we are not currently loading a new response to avoid race conditions
      setMessages(prev => {
        // Simple heuristic: if we have local unsaved messages, don't overwrite with empty history
        if (prev.length > 0 && data.length === 0) return prev;
        return data;
      })
    } catch (err) {
      console.error('Failed to fetch history', err)
    }
  }, [])

  useEffect(() => {
    if (selectedCharId) {
      fetchHistory(selectedCharId)
    }
  }, [selectedCharId]) // Only re-run when character changes

  const updateUser = async (name: string, gender: string) => {
    try {
      const data = await api.updateUser(name, gender)
      setUser(data)
      setActiveModal(null)
      showToast('Profile updated.')
    } catch (err) {
      showToast('Failed to update profile.', 'error')
    }
  }

  const createTag = async (label: string, instruction: string) => {
    try {
      const data = await api.createTag(label, instruction)
      setTags(prev => [...prev, data])
      setActiveModal(null)
      setEditingTag(null)
      showToast('Tag created.')
      return data
    } catch (err) {
      showToast('Failed to create tag.', 'error')
      return null
    }
  }

  const updateTag = async (id: number, label: string, instruction: string) => {
    try {
      const data = await api.updateTag(id, label, instruction)
      setTags((prev) => prev.map((tag) => (tag.id === id ? data : tag)))
      setActiveModal(null)
      setEditingTag(null)
      showToast('Tag updated.')
    } catch (err) {
      showToast('Failed to update tag.', 'error')
    }
  }

  const deleteTag = async (id: number) => {
    try {
      await api.deleteTag(id)
      setTags((prev) => prev.filter((tag) => tag.id !== id))
      showToast('Tag deleted.')
    } catch (err) {
      showToast('Failed to delete tag.', 'error')
    }
  }

  const deleteCharacter = async (id: number) => {
    if (!window.confirm('Delete this character? This action is permanent.')) return
    try {
      await api.deleteCharacter(id)
      setCharacters(prev => prev.filter(c => c.id !== id))
      if (selectedCharId === id) setSelectedCharId(null)
      showToast('Character deleted.')
    } catch (err) {
      showToast('Failed to delete character.', 'error')
    }
  }

  const createCharacter = async (
    name: string,
    description: string,
    tagIds: number[]
  ) => {
    try {
      const data = await api.createCharacter(name, description, tagIds)
      setCharacters((prev) => [...prev, data])
      setSelectedCharId(data.id)
      setActiveModal(null)
      showToast('Character initialized.')
    } catch (err) {
      showToast('Failed to create character.', 'error')
    }
  }

  const updateCharacter = async (
    id: number,
    name: string,
    description: string,
    tagIds: number[]
  ) => {
    try {
      const data = await api.updateCharacter(id, name, description, tagIds)
      setCharacters((prev) => prev.map((c) => (c.id === id ? data : c)))
      setActiveModal(null)
      setEditingCharacter(null)
      showToast('Changes saved.')
    } catch (err) {
      showToast('Failed to update character.', 'error')
    }
  }

  const handleSend = async (explicitParentId?: number) => {
    if (!input.trim() || isLoading || !selectedCharId) return

    const parentId = explicitParentId ?? (messages.length > 0 ? messages[messages.length - 1].id : null)

    // Use a more robust temporary ID to avoid collisions and ensure stability in tests
    const userMsgId = Math.floor(Math.random() * 1000000) + Date.now()
    const assistantMsgId = userMsgId + 1

    const userMsg: MessageNode = { 
      id: userMsgId,
      parent_id: parentId,
      role: 'user', 
      content: input, 
      variant_index: 0 
    }
    const assistantMsg: MessageNode = { 
      id: assistantMsgId,
      parent_id: userMsgId,
      role: 'assistant', 
      content: '', 
      variant_index: 0 
    }
    
    setMessages(prev => [...prev, userMsg, assistantMsg])
    const currentInput = input
    setInput('')
    setIsLoading(true)

    try {
      const response = await api.sendMessageStream(currentInput, selectedCharId, parentId, config)
      await handleStreamResponse(response)
    } catch (error) {
      showToast('Lost connection to AI.', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendAction = async (actionId: string, explicitParentId?: number) => {
    if (isLoading || !selectedCharId) return

    const parentId = explicitParentId ?? (messages.length > 0 ? messages[messages.length - 1].id : null)

    const actionsMessages: Record<string, string> = {
      "hug": "*I step forward and wrap my arms around you in a warm, gentle hug.*",
      "pat_head": "*I reach out and pat your head gently, smiling softly.*",
      "tease": "*I look at you with a playful smirk, teasing you lightly.*",
      "hold_hand": "*I slide my hand into yours, holding it gently.*",
      "coffee": "*I hand you a hot, freshly brewed cup of black coffee.*",
      "croissant": "*I offer you a warm, freshly baked chocolate croissant.*",
      "book": "*I present you with a beautifully bound, vintage book.*",
      "necklace": "*I hand you a small velvet box containing a delicate silver necklace.*"
    }

    const actionMessage = actionsMessages[actionId] || `*Performs action: ${actionId}*`
    const userMsgId = Math.floor(Math.random() * 1000000) + Date.now()
    const assistantMsgId = userMsgId + 1

    const userMsg: MessageNode = { 
      id: userMsgId,
      parent_id: parentId,
      role: 'user', 
      content: actionMessage, 
      variant_index: 0 
    }
    const assistantMsg: MessageNode = { 
      id: assistantMsgId,
      parent_id: userMsgId,
      role: 'assistant', 
      content: '', 
      variant_index: 0 
    }
    
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setIsLoading(true)

    try {
      const response = await api.sendMessageStream(null, selectedCharId, parentId, config, actionId)
      await handleStreamResponse(response)
    } catch (error) {
      showToast('Lost connection to AI.', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegenerate = async (parentId: number) => {
    if (isLoading || !selectedCharId) return

    const assistantMsgId = Date.now()
    const assistantMsg: MessageNode = { 
      id: assistantMsgId,
      parent_id: parentId,
      role: 'assistant', 
      content: '', 
      variant_index: 0 // Will be corrected by fetchHistory
    }
    
    setMessages(prev => [...prev, assistantMsg])
    setIsLoading(true)

    try {
      const response = await api.sendMessageStream(null, selectedCharId, parentId, config)
      await handleStreamResponse(response)
    } catch (error) {
      showToast('Lost connection to AI.', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStreamResponse = async (response: Response) => {
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let fullContent = ''

    if (!reader) throw new Error('Reader unavailable')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const data = JSON.parse(line.slice(6))
          if (data.token) {
            fullContent += data.token
            setMessages(prev => {
              const next = [...prev]
              const last = next[next.length - 1]
              if (last && last.role === 'assistant') {
                last.content = fullContent
              }
              return next
            })
          }
          if (data.done) {
            if (data.state) {
              setCharacters(prev => prev.map(c => 
                c.id === selectedCharId ? { ...c, state: data.state } : c
              ))
            }
            if (data.request_id) {
              setMessages(prev => {
                const next = [...prev]
                const last = next[next.length - 1]
                if (last && last.role === 'assistant') {
                  last.request_id = data.request_id
                }
                return next
              })
            }
            if (selectedCharId) fetchHistory(selectedCharId)
          }
        } catch (e) {
          console.error('SSE Error', e)
        }
      }
    }
    fetchCharacters() // Refresh stats
  }

  const handleStartChat = (id: number) => {
    setSelectedCharId(id)
    setCurrentView('chat')
  }

  const handleUpdateState = async (charId: number, stateUpdate: any) => {
    try {
      const updatedChar = await api.updateCharacterState(charId, stateUpdate)
      setCharacters((prev) => prev.map((c) => c.id === charId ? updatedChar : c))
    } catch (err) {
      setToast({ message: 'Failed to update character state.', type: 'error' })
    }
  }

  const handleClearChat = async () => {
    if (!selectedCharId) return
    if (window.confirm("Are you sure you want to clear this conversation history? This cannot be undone.")) {
      try {
        await api.clearChatHistory(selectedCharId)
        setMessages([])
        fetchCharacters()
        setToast({ message: 'Conversation cleared.', type: 'success' })
      } catch (err) {
        setToast({ message: 'Failed to clear conversation.', type: 'error' })
      }
    }
  }

  const activeChar = characters.find((c) => c.id === selectedCharId) || null

  const tagUsage = characters.reduce<Record<number, number>>((acc, character) => {
    character.tags.forEach((tag) => {
      acc[tag.id] = (acc[tag.id] ?? 0) + 1
    })
    return acc
  }, {})

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-screen bg-background text-on-surface font-body-md overflow-hidden antialiased relative">
        {/* Mobile Backdrop Overlay */}
        {isSidebarOpen && (
          <div 
            onClick={() => setIsSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
          />
        )}

        <Sidebar
          currentView={currentView}
          setView={(v) => setCurrentView(v as View)}
          userName={user?.name}
          onProfileClick={() => setActiveModal('user')}
          onSettingsClick={() => setActiveModal('settings')}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main className="flex-1 h-screen overflow-hidden flex flex-col min-w-0">
          {/* Mobile Top Header */}
          <header className="md:hidden flex items-center justify-between px-md py-sm bg-[#0A0A0B]/90 backdrop-blur border-b border-white/5 z-30 shrink-0">
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="p-1 text-[#A1A1AA] hover:text-white flex items-center"
            >
              <span className="material-symbols-outlined text-[20px]">menu</span>
            </button>
            <h2 className="font-sans text-xs font-bold text-white uppercase tracking-[0.2em]">
              {currentView === 'characters' && 'Characters'}
              {currentView === 'chat' && 'Direct Chat'}
              {currentView === 'library' && 'Lorebook'}
              {currentView === 'archives' && 'Knowledge Tags'}
            </h2>
            <button 
              onClick={() => setActiveModal('user')}
              className="w-7 h-7 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0"
            >
              <span className="material-symbols-outlined text-xs text-[#A1A1AA]">person</span>
            </button>
          </header>

          {currentView === 'characters' && (
            <CharactersView
              characters={characters}
              selectedCharId={selectedCharId}
              setSelectedCharId={setSelectedCharId}
              onNewCharacter={() => setActiveModal('character')}
              onChat={handleStartChat}
              onEdit={(id) => {
                const char = characters.find((c) => c.id === id)
                if (char) {
                  setEditingCharacter(char)
                  setActiveModal('character')
                }
              }}
              onDelete={deleteCharacter}
            />
          )}

          {currentView === 'chat' && (
            <ChatView
              activeChar={activeChar}
              messages={messages}
              input={input}
              setInput={setInput}
              onSend={handleSend}
              onRegenerate={handleRegenerate}
              isLoading={isLoading}
              onUpdateState={handleUpdateState}
              onClearChat={handleClearChat}
              onSendAction={handleSendAction}
            />
          )}

          {currentView === 'library' && (
            <LorebookView />
          )}

          {currentView === 'archives' && (
            <TagManagementView
              tags={tags}
              onCreateTag={() => {
                setEditingTag(null)
                setActiveModal('tag')
              }}
              onEditTag={(tag) => {
                setEditingTag(tag)
                setActiveModal('tag')
              }}
              onDeleteTag={deleteTag}
              usage={tagUsage}
            />
          )}
        </main>

        {/* Modals */}
        {(activeModal === 'character' || editingCharacter) && (
          <CharacterCreator
            tags={tags}
            onClose={() => {
              setActiveModal(null)
              setEditingCharacter(null)
            }}
            onCreate={createCharacter}
            onUpdate={updateCharacter}
            editingCharacter={editingCharacter}
          />
        )}
        {activeModal === 'user' && (
          <UserProfileModal
            user={user}
            onClose={() => setActiveModal(null)}
            onUpdate={updateUser}
          />
        )}
        {activeModal === 'tag' && (
          <TagCreator
            onClose={() => {
              setActiveModal(null)
              setEditingTag(null)
            }}
            onSubmit={(label, instruction) => {
              if (editingTag) {
                return updateTag(editingTag.id, label, instruction)
              }
              return createTag(label, instruction)
            }}
            tag={editingTag}
          />
        )}
        {activeModal === 'settings' && (
          <SettingsModal
            onClose={() => setActiveModal(null)}
          />
        )}

        {/* Toast */}
        {toast && (
          <div className={`fixed bottom-20 left-1/2 -translate-x-1/2 px-lg py-sm rounded border shadow-xl z-[60] animate-in fade-in slide-in-from-bottom-4 duration-300 ${
            toast.type === 'error' 
              ? 'bg-error-container text-error border-error/20' 
              : 'bg-surface-container-high text-primary border-primary/20'
          }`}>
            <p className="font-label-md text-label-md font-medium">{toast.message}</p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  )
}

export default App
