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
import type { Character, Tag } from './services/api'
import { useSettings } from './hooks/useSettings'

interface User {
  id: number
  name: string
  gender: string
  is_active: boolean
  persona_description?: string
  appearance?: string
}

type View = 'chat' | 'characters' | 'archives' | 'library'
type ModalType = 'character' | 'user' | 'tag' | 'settings' | null

interface Toast {
  message: string
  type: 'success' | 'error'
}

// Optimistic client-side message ids: a large random offset plus the epoch ms
// keeps them unique and above any server id until the real history reloads.
const TEMP_ID_RANGE = 1000000
const TOAST_DURATION_MS = 3000

const generateMessageId = () => Math.floor(Math.random() * TEMP_ID_RANGE) + Date.now();

function App() {
  const { config } = useSettings()
  const [currentView, setCurrentView] = useState<View>('characters')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [activeModal, setActiveModal] = useState<ModalType>(null)
  const [toast, setToast] = useState<Toast | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [chats, setChats] = useState<api.ChatSession[]>([])
  const [activeChatId, setActiveChatId] = useState<number | null>(null)
  const [messages, setMessages] = useState<MessageNode[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [actionsMessages, setActionsMessages] = useState<Record<string, string>>({})

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), TOAST_DURATION_MS)
  }

  const fetchUser = useCallback(async () => {
    try {
      const data = await api.fetchUser()
      setUser(data)
    } catch {
      showToast('Failed to fetch user.', 'error')
    }
  }, [])

  const fetchCharacters = useCallback(async () => {
    try {
      const data = await api.fetchCharacters()
      setCharacters(data)
      // Functional update reads the latest selectedCharId without needing it
      // in this callback's dependencies -- keeps fetchCharacters' identity
      // stable so the mount effect below doesn't re-fire on every character
      // switch (selectedCharId changing would otherwise recreate this
      // callback and re-trigger the effect that depends on it).
      setSelectedCharId((prev) => (prev === null && data.length > 0 ? data[0].id : prev))
    } catch {
      showToast('Failed to fetch characters.', 'error')
    }
  }, [])

  const fetchTags = useCallback(async () => {
    try {
      const data = await api.fetchTags()
      setTags(data)
    } catch {
      showToast('Failed to fetch tags.', 'error')
    }
  }, [])

  const fetchActions = useCallback(async () => {
    try {
      const data = await api.fetchActions()
      setActionsMessages(data)
    } catch {
      // Non-critical: handleSendAction falls back to a generic placeholder.
      console.error('Failed to fetch actions')
    }
  }, [])

  useEffect(() => {
    let active = true
    const init = async () => {
      await Promise.resolve()
      if (active) {
        fetchCharacters()
        fetchUser()
        fetchTags()
        fetchActions()
      }
    }
    init()
    return () => {
      active = false
    }
  }, [fetchCharacters, fetchUser, fetchTags, fetchActions])

  const fetchHistory = useCallback(async (charId: number, chatId?: number) => {
    try {
      const data = await api.fetchHistory(charId, chatId)
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

  const loadChats = useCallback(async (charId: number): Promise<number | null> => {
    try {
      const list = await api.fetchChats(charId)
      setChats(list)
      const active = list.find((c) => c.is_active) ?? list[0] ?? null
      setActiveChatId(active ? active.id : null)
      return active ? active.id : null
    } catch (err) {
      console.error('Failed to fetch chats', err)
      setChats([])
      setActiveChatId(null)
      return null
    }
  }, [])

  useEffect(() => {
    let active = true
    const init = async () => {
      if (selectedCharId) {
        setMessages([]) // Clear stale messages from previous character to avoid tree mismatch
        const chatId = await loadChats(selectedCharId)
        if (active) {
          await fetchHistory(selectedCharId, chatId ?? undefined)
        }
      }
    }
    init()
    return () => {
      active = false
    }
  }, [selectedCharId, fetchHistory, loadChats]) // Re-run when character changes

  const updateUser = async (name: string, gender: string, persona: string, appearance: string) => {
    try {
      const data = await api.updateUser(name, gender, persona, appearance)
      setUser(data)
      setActiveModal(null)
      showToast('Profile updated.')
    } catch {
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
    } catch {
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
    } catch {
      showToast('Failed to update tag.', 'error')
    }
  }

  const deleteTag = async (id: number) => {
    try {
      await api.deleteTag(id)
      setTags((prev) => prev.filter((tag) => tag.id !== id))
      showToast('Tag deleted.')
    } catch {
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
    } catch {
      showToast('Failed to delete character.', 'error')
    }
  }

  const createCharacter = async (data: {
    name: string
    description: string
    nickname: string
    short_description: string
    persona_prompt: string
    scenario: string
    first_mes: string
    alternate_greetings: string[]
    mes_example: string
    content_rating: string
    tagIds: number[]
    avatarFile: File | null
  }) => {
    try {
      const characterData = await api.createCharacter({
        name: data.name,
        description: data.description,
        nickname: data.nickname,
        short_description: data.short_description,
        persona_prompt: data.persona_prompt,
        scenario: data.scenario,
        first_mes: data.first_mes,
        alternate_greetings: data.alternate_greetings,
        mes_example: data.mes_example,
        content_rating: data.content_rating,
        tag_ids: data.tagIds,
        compress_backstory: false
      })

      if (data.avatarFile) {
        const formData = new FormData()
        formData.append('file', data.avatarFile)
        const uploadResponse = await fetch(`/characters/${characterData.id}/avatar`, {
          method: 'POST',
          body: formData
        })
        if (uploadResponse.ok) {
          const uploadResult = await uploadResponse.json()
          characterData.avatar_url = uploadResult.avatar_url
        }
      }

      setCharacters((prev) => [...prev, characterData])
      setSelectedCharId(characterData.id)
      setActiveModal(null)
      showToast('Character initialized.')
    } catch {
      showToast('Failed to create character.', 'error')
    }
  }

  const updateCharacter = async (
    id: number,
    data: {
      name: string
      description: string
      nickname: string
      short_description: string
      persona_prompt: string
      scenario: string
      first_mes: string
      alternate_greetings: string[]
      mes_example: string
      content_rating: string
      tagIds: number[]
      avatarFile: File | null
    }
  ) => {
    try {
      const characterData = await api.updateCharacter(id, {
        name: data.name,
        description: data.description,
        nickname: data.nickname,
        short_description: data.short_description,
        persona_prompt: data.persona_prompt,
        scenario: data.scenario,
        first_mes: data.first_mes,
        alternate_greetings: data.alternate_greetings,
        mes_example: data.mes_example,
        content_rating: data.content_rating,
        tag_ids: data.tagIds,
        compress_backstory: false
      })

      if (data.avatarFile) {
        const formData = new FormData()
        formData.append('file', data.avatarFile)
        const uploadResponse = await fetch(`/characters/${characterData.id}/avatar`, {
          method: 'POST',
          body: formData
        })
        if (uploadResponse.ok) {
          const uploadResult = await uploadResponse.json()
          characterData.avatar_url = uploadResult.avatar_url
        }
      }

      setCharacters((prev) => prev.map((c) => (c.id === id ? characterData : c)))
      setActiveModal(null)
      setEditingCharacter(null)
      showToast('Changes saved.')
    } catch {
      showToast('Failed to update character.', 'error')
    }
  }

  // Parent of the next message: an explicit id (branching) else the newest node.
  const resolveParentId = (explicitParentId?: number) =>
    explicitParentId ?? (messages.length > 0 ? messages[messages.length - 1].id : null)

  // Optimistically append a user turn + its empty assistant placeholder. The
  // robust temporary id avoids collisions and keeps test ordering stable.
  const appendExchange = (content: string, parentId: number | null) => {
    const userMsgId = generateMessageId()
    const assistantMsg: MessageNode = { id: userMsgId + 1, parent_id: userMsgId, role: 'assistant', content: '', variant_index: 0 }
    const userMsg: MessageNode = { id: userMsgId, parent_id: parentId, role: 'user', content, variant_index: 0 }
    setMessages(prev => [...prev, userMsg, assistantMsg])
  }

  // Drive one streaming turn: flip the loading flag, stream the response, and
  // surface a connection-error toast. Shared by send / action / regenerate so
  // the try/catch/finally lives in exactly one place.
  const runStream = async (start: () => Promise<Response>) => {
    setIsLoading(true)
    try {
      await handleStreamResponse(await start())
    } catch {
      showToast('Lost connection to AI.', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const refreshHistory = async () => {
    if (!selectedCharId) return
    const history = await api.fetchHistory(selectedCharId, activeChatId ?? undefined)
    setMessages(history)
  }

  const handleSend = async (explicitParentId?: number) => {
    if (!input.trim() || isLoading || !selectedCharId) return
    const parentId = resolveParentId(explicitParentId)
    appendExchange(input, parentId)
    const currentInput = input
    setInput('')
    await runStream(() => api.sendMessageStream(currentInput, selectedCharId, parentId, config, undefined, activeChatId ?? undefined))
  }

  const handleEditMessage = async (messageId: number, content: string) => {
    try {
      await api.editMessage(messageId, content)
      await refreshHistory()
    } catch {
      showToast('Failed to edit message.', 'error')
    }
  }

  const handleDeleteMessage = async (messageId: number) => {
    try {
      await api.deleteMessage(messageId)
      await refreshHistory()
    } catch {
      showToast('Failed to delete message.', 'error')
    }
  }

  const handleSendAction = async (actionId: string, explicitParentId?: number) => {
    if (isLoading || !selectedCharId) return
    const parentId = resolveParentId(explicitParentId)
    const actionMessage = actionsMessages[actionId] || `*Performs action: ${actionId}*`
    appendExchange(actionMessage, parentId)
    await runStream(() => api.sendMessageStream(null, selectedCharId, parentId, config, actionId, activeChatId ?? undefined))
  }

  const handleRegenerate = async (parentId: number) => {
    if (isLoading || !selectedCharId) return
    const assistantMsg: MessageNode = {
      id: generateMessageId(),
      parent_id: parentId,
      role: 'assistant',
      content: '',
      variant_index: 0 // Will be corrected by fetchHistory
    }
    setMessages(prev => [...prev, assistantMsg])
    await runStream(() => api.sendMessageStream(null, selectedCharId, parentId, config, undefined, activeChatId ?? undefined))
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
            if (selectedCharId) await fetchHistory(selectedCharId, activeChatId ?? undefined)
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

  const handleUpdateState = async (charId: number, stateUpdate: Record<string, unknown>) => {
    try {
      const updatedChar = await api.updateCharacterState(charId, stateUpdate)
      setCharacters((prev) => prev.map((c) => c.id === charId ? updatedChar : c))
    } catch {
      showToast('Failed to update character state.', 'error')
    }
  }

  const handleClearChat = async () => {
    if (!selectedCharId) return
    if (window.confirm("Are you sure you want to clear this conversation history? This cannot be undone.")) {
      try {
        await api.clearChatHistory(selectedCharId)
        setMessages([])
        await loadChats(selectedCharId)
        fetchCharacters()
        showToast('Conversation cleared.')
      } catch {
        showToast('Failed to clear conversation history.', 'error')
      }
    }
  }

  // Non-destructive "New Chat": starts a fresh session and keeps the old ones.
  // An optional greetingIndex selects which opening greeting seeds the session.
  const handleNewChat = async (greetingIndex?: number) => {
    if (!selectedCharId) return
    try {
      const res = await api.newChat(selectedCharId, greetingIndex)
      setMessages([])
      await loadChats(selectedCharId)
      if (res?.chat_id != null) setActiveChatId(res.chat_id)
      fetchCharacters()
      showToast('Started a new chat.')
    } catch {
      showToast('Failed to start a new chat.', 'error')
    }
  }

  const handleSelectChat = async (chatId: number) => {
    if (!selectedCharId || chatId === activeChatId) return
    setActiveChatId(chatId)
    setMessages([])
    await fetchHistory(selectedCharId, chatId)
  }

  const handleDeleteChat = async (chatId: number) => {
    if (!selectedCharId) return
    if (!window.confirm("Delete this chat session permanently? This cannot be undone.")) return
    try {
      await api.deleteChat(chatId)
      setMessages([])
      const nextActive = await loadChats(selectedCharId)
      await fetchHistory(selectedCharId, nextActive ?? undefined)
      fetchCharacters()
      showToast('Chat deleted.')
    } catch {
      showToast('Failed to delete chat.', 'error')
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
      <div className="flex h-full w-full bg-background text-on-surface font-body-md overflow-hidden antialiased relative">
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

        <main className="flex-1 h-full overflow-hidden flex flex-col min-w-0">
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
              onCharacterImported={() => fetchCharacters()}
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
              onEditMessage={handleEditMessage}
              onDeleteMessage={handleDeleteMessage}
              chats={chats}
              activeChatId={activeChatId}
              greetings={[activeChar?.first_mes ?? '', ...(activeChar?.alternate_greetings ?? [])].filter((g) => g.trim())}
              onNewChat={handleNewChat}
              onSelectChat={handleSelectChat}
              onDeleteChat={handleDeleteChat}
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
