import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import LibraryView from './components/LibraryView'
import CharactersView from './components/CharactersView'
import ChatView from './components/ChatView'
import TagManagementView from './components/TagManagementView'
import CharacterCreator from './components/CharacterCreator'
import UserProfileModal from './components/UserProfileModal'
import TagCreator from './components/TagCreator'

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
  lust: number
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

interface Stats {
  energy: number
  hunger: number
  relationship: {
    score: number
  }
}

type View = 'library' | 'chat' | 'characters' | 'archives'

function App() {
  const [currentView, setCurrentView] = useState<View>('characters')
  const [characters, setCharacters] = useState<Character[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showCharModal, setShowCharModal] = useState(false)
  const [showUserModal, setShowUserModal] = useState(false)
  const [showTagModal, setShowTagModal] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [, setStats] = useState<Stats | null>(null)

  const fetchUser = useCallback(async () => {
    try {
      const response = await fetch('/users/me')
      const data = await response.json()
      setUser(data)
    } catch (err) {
      console.error('Failed to fetch user', err)
    }
  }, [])

  const fetchCharacters = useCallback(async () => {
    try {
      const response = await fetch('/characters/')
      const data = await response.json()
      setCharacters(data)
      if (data.length > 0 && !selectedCharId) {
        setSelectedCharId(data[0].id)
      }
    } catch (err) {
      console.error('Failed to fetch characters', err)
    }
  }, [selectedCharId])

  const fetchTags = useCallback(async () => {
    try {
      const response = await fetch('/tags/')
      const data = await response.json()
      setTags(data)
    } catch (err) {
      console.error('Failed to fetch tags', err)
    }
  }, [])

  useEffect(() => {
    fetchCharacters()
    fetchUser()
    fetchTags()
  }, [fetchCharacters, fetchUser, fetchTags])

  const fetchHistory = useCallback(async (charId: number) => {
    try {
      const response = await fetch(`/history/${charId}`)
      const data = await response.json()
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
      const response = await fetch('/users/me', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, gender })
      })
      const data = await response.json()
      setUser(data)
      setShowUserModal(false)
    } catch (err) {
      console.error('Failed to update user', err)
    }
  }

  const createTag = async (label: string, instruction: string) => {
    try {
      const response = await fetch('/tags/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, instruction })
      })
      const data = await response.json()
      setTags(prev => [...prev, data])
      setShowTagModal(false)
      setEditingTag(null)
      return data
    } catch (err) {
      console.error('Failed to create tag', err)
      return null
    }
  }

  const updateTag = async (id: number, label: string, instruction: string) => {
    try {
      const response = await fetch(`/tags/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, instruction })
      })
      const data = await response.json()
      setTags((prev) => prev.map((tag) => (tag.id === id ? data : tag)))
      setShowTagModal(false)
      setEditingTag(null)
    } catch (err) {
      console.error('Failed to update tag', err)
    }
  }

  const deleteTag = async (id: number) => {
    try {
      await fetch(`/tags/${id}`, { method: 'DELETE' })
      setTags((prev) => prev.filter((tag) => tag.id !== id))
    } catch (err) {
      console.error('Failed to delete tag', err)
    }
  }

  const createCharacter = async (
    name: string,
    description: string,
    tagIds: number[]
  ) => {
    try {
      const response = await fetch('/characters/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          tag_ids: tagIds
        })
      })
      const data = await response.json()
      setCharacters((prev) => [...prev, data])
      setSelectedCharId(data.id)
      setShowCharModal(false)
    } catch (err) {
      console.error('Failed to create character', err)
    }
  }

  const updateCharacter = async (
    id: number,
    name: string,
    description: string,
    tagIds: number[],
    lust: number
  ) => {
    try {
      const response = await fetch(`/characters/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          tag_ids: tagIds,
          lust
        })
      })
      const data = await response.json()
      setCharacters((prev) => prev.map((c) => (c.id === id ? data : c)))
      setShowCharModal(false)
      setEditingCharacter(null)
    } catch (err) {
      console.error('Failed to update character', err)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || !selectedCharId) return

    const userMessage: Message = { role: 'user', content: input, timestamp: new Date() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          character_id: selectedCharId
        })
      })

      const data = await response.json()
      console.log('API Response:', data);
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.reply,
        timestamp: new Date()
      }
      setMessages((prev) => [...prev, assistantMessage])
      if (data.stats) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Erro ao comunicar com IA.', timestamp: new Date() }])
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
    <div className="flex h-screen w-screen bg-background text-on-surface font-body-md overflow-hidden antialiased">
      <Sidebar
        currentView={currentView}
        setView={(v) => setCurrentView(v as View)}
        userName={user?.name}
        onProfileClick={() => setShowUserModal(true)}
      />

      <main className="flex-1 md:ml-64 h-screen overflow-hidden flex flex-col">
        {currentView === 'library' && (
          <LibraryView
            characters={characters}
            onOpenStory={handleStartChat}
            onNewStory={() => setShowCharModal(true)}
          />
        )}

        {currentView === 'characters' && (
          <CharactersView
            characters={characters}
            selectedCharId={selectedCharId}
            setSelectedCharId={setSelectedCharId}
            onNewCharacter={() => setShowCharModal(true)}
            onChat={handleStartChat}
            onEdit={(id) => {
              const char = characters.find((c) => c.id === id)
              if (char) setEditingCharacter(char)
            }}
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
              setShowTagModal(true)
            }}
            onEditTag={(tag) => {
              setEditingTag(tag)
              setShowTagModal(true)
            }}
            onDeleteTag={deleteTag}
            usage={tagUsage}
          />
        )}
      </main>

      {/* Modals */}
      {(showCharModal || editingCharacter) && (
        <CharacterCreator
          tags={tags}
          onClose={() => {
            setShowCharModal(false)
            setEditingCharacter(null)
          }}
          onCreate={createCharacter}
          onUpdate={updateCharacter}
          editingCharacter={editingCharacter}
        />
      )}
      {showUserModal && (
        <UserProfileModal
          user={user}
          onClose={() => setShowUserModal(false)}
          onUpdate={updateUser}
        />
      )}
      {showTagModal && (
        <TagCreator
          onClose={() => {
            setShowTagModal(false)
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

      <button
        onClick={() => setShowUserModal(true)}
        className="fixed bottom-4 right-4 p-2 bg-surface-container border border-outline-variant rounded-full text-on-surface-variant hover:text-primary transition-colors z-30"
      >
        <span className="material-symbols-outlined">settings</span>
      </button>
    </div>
  )
}

export default App
