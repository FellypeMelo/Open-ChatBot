import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import CharactersView from './components/CharactersView'
import ChatView from './components/ChatView'
import TagManagementView from './components/TagManagementView'
import CharacterCreator from './components/CharacterCreator'
import UserProfileModal from './components/UserProfileModal'
import TagCreator from './components/TagCreator'
import ErrorBoundary from './components/ErrorBoundary'
import * as api from './services/api'

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

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

type View = 'chat' | 'characters' | 'archives'
type ModalType = 'character' | 'user' | 'tag' | null

interface Toast {
  message: string
  type: 'success' | 'error'
}

function App() {
  const [currentView, setCurrentView] = useState<View>('characters')
  const [activeModal, setActiveModal] = useState<ModalType>(null)
  const [toast, setToast] = useState<Toast | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
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
      setMessages(data.map((m: any) => ({
        ...m,
        timestamp: new Date(m.timestamp)
      })))
    } catch (err) {
      console.error('Failed to fetch history', err)
    }
  }, [])

  useEffect(() => {
    if (selectedCharId) {
      fetchHistory(selectedCharId)
    }
  }, [selectedCharId, fetchHistory])

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

  const handleSend = async () => {
    if (!input.trim() || isLoading || !selectedCharId) return

    const userMsg: Message = { role: 'user', content: input, timestamp: new Date() }
    const assistantMsg: Message = { role: 'assistant', content: '', timestamp: new Date() }
    
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, character_id: selectedCharId })
      })

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
            if (data.done && data.stats) {
              setCharacters(prev => prev.map(c => 
                c.id === selectedCharId ? { ...c, state: { ...c.state, stats: data.stats } } : c
              ))
            }
          } catch (e) {
            console.error('SSE Error', e)
          }
        }
      }
      fetchCharacters() // Refresh stats
    } catch (error) {
      showToast('Lost connection to AI.', 'error')
      setMessages(prev => [...prev.slice(0, -1), { role: 'assistant', content: 'Connection error.', timestamp: new Date() }])
    } finally {
      setIsLoading(false)
    }
  }

  const activeChar = characters.find((c) => c.id === selectedCharId) || null

  const handleStartChat = (id: number) => {
    setSelectedCharId(id)
    setCurrentView('chat')
  }

  const tagUsage = characters.reduce<Record<number, number>>((acc, character) => {
    character.tags.forEach((tag) => {
      acc[tag.id] = (acc[tag.id] ?? 0) + 1
    })
    return acc
  }, {})

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-screen bg-background text-on-surface font-body-md overflow-hidden antialiased">
        <Sidebar
          currentView={currentView}
          setView={(v) => setCurrentView(v as View)}
          userName={user?.name}
          onProfileClick={() => setActiveModal('user')}
        />

        <main className="flex-1 md:ml-64 h-screen overflow-hidden flex flex-col">
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
              isLoading={isLoading}
            />
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

        <button
          onClick={() => setActiveModal('user')}
          className="fixed bottom-4 right-4 p-2 bg-surface-container border border-outline-variant rounded-full text-on-surface-variant hover:text-primary transition-colors z-30"
        >
          <span className="material-symbols-outlined">settings</span>
        </button>
      </div>
    </ErrorBoundary>
  )
}

export default App
