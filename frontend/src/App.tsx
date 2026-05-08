import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Plus, Users, Tag as TagIcon, Brain as BrainIcon, Heart, Zap, Pizza } from 'lucide-react'
import MessageRenderer, { SequenceBlock } from './components/MessageRenderer'

interface Tag {
  id: number
  label: string
  instruction: string
}

interface Character {
  id: number
  name: string
  description: string
  short_description?: string
  tags: Tag[]
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
  thought?: string
  actions?: string[]
  sequence?: SequenceBlock[]
  timestamp?: Date
}

interface Stats {
  energy: number
  hunger: number
  relationship: {
    score: number
  }
}

function App() {
  const [characters, setCharacters] = useState<Character[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showCharModal, setShowCharModal] = useState(false)
  const [showUserModal, setShowUserModal] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [isImmersed, setIsImmersed] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Character Form State
  const [newCharName, setNewCharName] = useState('')
  const [newCharDesc, setNewCharDesc] = useState('')
  const [newCharShortDesc, setNewCharShortDesc] = useState('')

  // User Form State
  const [userName, setUserName] = useState('')
  const [userGender, setUserGender] = useState('Male')

  const fetchUser = useCallback(async () => {
    try {
      const response = await fetch('/users/me')
      const data = await response.json()
      setUser(data)
      setUserName(data.name)
      setUserGender(data.gender)
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

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCharacters()
      fetchUser()
    }, 0)
    return () => clearTimeout(timer)
  }, [fetchCharacters, fetchUser])

  // Immersion logic
  const resetImmersion = useCallback(() => {
    setIsImmersed(false)
    if (timerRef.current) clearTimeout(timerRef.current)
    
    // Only start timer if there are messages and we aren't loading
    if (messages.length > 0 && !isLoading) {
      timerRef.current = setTimeout(() => {
        setIsImmersed(true)
      }, 3000)
    }
  }, [messages.length, isLoading])

  useEffect(() => {
    const handleActivity = () => resetImmersion()
    window.addEventListener('mousemove', handleActivity)
    window.addEventListener('keydown', handleActivity)
    window.addEventListener('mousedown', handleActivity)
    window.addEventListener('touchstart', handleActivity)

    return () => {
      window.removeEventListener('mousemove', handleActivity)
      window.removeEventListener('keydown', handleActivity)
      window.removeEventListener('mousedown', handleActivity)
      window.removeEventListener('touchstart', handleActivity)
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [resetImmersion])

  // Trigger immersion when messages change or loading finishes
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsImmersed(false)
      if (timerRef.current) clearTimeout(timerRef.current)
      
      if (messages.length > 0 && !isLoading) {
        timerRef.current = setTimeout(() => {
          setIsImmersed(true)
        }, 3000)
      }
    }, 0)
    return () => clearTimeout(timer)
  }, [messages.length, isLoading])

  const updateUser = async () => {
    try {
      const response = await fetch('/users/me', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: userName, gender: userGender })
      })
      const data = await response.json()
      setUser(data)
      setShowUserModal(false)
    } catch (err) {
      console.error('Failed to update user', err)
    }
  }

  const createCharacter = async () => {
    if (!newCharName || !newCharDesc) return
    try {
      const response = await fetch('/characters/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: newCharName, 
          description: newCharDesc,
          short_description: newCharShortDesc
        })
      })
      const data = await response.json()
      setCharacters(prev => [...prev, data])
      setSelectedCharId(data.id)
      setShowCharModal(false)
      setNewCharName('')
      setNewCharDesc('')
      setNewCharShortDesc('')
    } catch (err) {
      console.error('Failed to create character', err)
    }
  }

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading || !selectedCharId) return

    const userMessage: Message = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
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
      const assistantMessage: Message = { 
        role: 'assistant', 
        content: data.reply, 
        thought: data.thought,
        actions: data.actions,
        sequence: data.sequence,
        timestamp: new Date() 
      }
      setMessages(prev => [...prev, assistantMessage])
      if (data.stats) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { role: 'assistant', content: 'Erro ao comunicar com IA.', timestamp: new Date() }])
    } finally {
      setIsLoading(false)
    }
  }

  const activeChar = characters.find(c => c.id === selectedCharId)

  return (
    <div className="flex h-screen w-screen bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
      {/* Sidebar: Character List */}
      <aside className={`border-r border-zinc-800 flex flex-col bg-zinc-900 shadow-xl transition-all duration-700 ease-in-out overflow-hidden ${
        isImmersed ? 'w-0 opacity-0 -translate-x-full border-none' : 'w-64 opacity-100 translate-x-0'
      }`}>
        <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50 min-w-[16rem]">
          <h2 className="font-bold text-emerald-500 flex items-center gap-2">
            <Users size={18} /> Entidades
          </h2>
          <button 
            onClick={() => setShowCharModal(true)}
            className="p-1.5 hover:bg-emerald-500/10 text-emerald-500 rounded-lg transition-colors border border-emerald-500/20"
          >
            <Plus size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1 min-w-[16rem]">
          {characters.map(char => (
            <button
              key={char.id}
              onClick={() => setSelectedCharId(char.id)}
              className={`w-full text-left p-3 rounded-xl transition-all duration-200 flex flex-col gap-1 ${
                selectedCharId === char.id 
                  ? 'bg-emerald-600 shadow-lg shadow-emerald-900/20 scale-[1.02]' 
                  : 'hover:bg-zinc-800 text-zinc-400 hover:text-zinc-100'
              }`}
            >
              <span className="font-semibold">{char.name}</span>
              <span className={`text-xs truncate ${selectedCharId === char.id ? 'text-emerald-100' : 'text-zinc-500'}`}>
                {char.short_description || char.description}
              </span>
            </button>
          ))}
        </div>
        
        {/* Global Systems Link */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/80 backdrop-blur space-y-2 min-w-[16rem]">
          <button 
            onClick={() => setShowUserModal(true)}
            className="w-full flex items-center justify-between p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 text-sm transition-colors border border-transparent hover:border-zinc-700"
          >
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] font-bold text-emerald-500">
                {user?.name?.[0] || 'U'}
              </div>
              <span>{user?.name || 'Perfil'}</span>
            </div>
            <span className="text-[10px] opacity-50">{user?.gender}</span>
          </button>
          <button className="w-full flex items-center gap-2 p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 text-sm transition-colors">
            <TagIcon size={16} /> Gerenciar Tags
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative bg-zinc-950">
        {/* Header / HUD */}
        <header className={`px-6 py-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-950/50 backdrop-blur-md sticky top-0 z-10 transition-all duration-700 ease-in-out ${
          isImmersed ? '-translate-y-full opacity-0 h-0 py-0 border-none' : 'translate-y-0 opacity-100 h-auto'
        }`}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
              <span className="text-xl">✨</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">
                {activeChar?.name || 'Open-ChatBot'}
              </h1>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-[10px] uppercase tracking-wider font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  Online
                </span>
                {activeChar?.tags.slice(0, 2).map(t => (
                  <span key={t.id} className="text-[10px] text-zinc-500 font-medium lowercase">#{t.label}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Quick HUD */}
          <div className="flex gap-4">
            <div className="flex flex-col items-center" title={`Energy: ${stats?.energy ?? 100}%`}>
              <Zap size={16} className="text-amber-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-amber-500 transition-all duration-500" style={{ width: `${stats?.energy ?? 100}%` }} />
              </div>
            </div>
            <div className="flex flex-col items-center" title={`Hunger: ${stats?.hunger ?? 0}%`}>
              <Pizza size={16} className="text-rose-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-rose-500 transition-all duration-500" style={{ width: `${stats?.hunger ?? 0}%` }} />
              </div>
            </div>
            <div className="flex flex-col items-center" title={`Relationship: ${stats?.relationship?.score ?? 50}%`}>
              <Heart size={16} className="text-emerald-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${stats?.relationship?.score ?? 50}%` }} />
              </div>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-12">
          <div className="max-w-[680px] mx-auto space-y-12">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center text-zinc-600 mx-auto text-center space-y-4">
                <div className="p-12 spatial-field rounded-3xl border border-zinc-800/50">
                  <BrainIcon size={48} className="mx-auto mb-6 text-emerald-500/40" />
                  <p className="text-xl font-serif italic text-zinc-400">Pronto para o Roleplay?</p>
                  <p className="text-sm mt-4 font-sans text-zinc-500 max-w-xs mx-auto">A entidade vai responder com pensamentos internos, ações físicas e diálogos.</p>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                <div className={`flex flex-col gap-3 w-full ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="p-6 rounded-3xl shadow-2xl bg-emerald-600/90 text-white max-w-[90%] font-sans text-lg leading-relaxed transition-all duration-500 hover:scale-[1.01]">
                      <p className="whitespace-pre-wrap">
                        {msg.content}
                      </p>
                    </div>
                  ) : (
                    <div className="w-full">
                      <MessageRenderer 
                        sequence={msg.sequence} 
                        fallback={{ 
                          content: msg.content, 
                          thought: msg.thought, 
                          actions: msg.actions 
                        }}
                        isLatest={i === messages.length - 1}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                 <div className="spatial-field p-6 rounded-3xl flex gap-2 items-center">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                 </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </div>
        {/* Input */}
        <footer className="p-6 bg-zinc-950/80 backdrop-blur-xl border-t border-zinc-800">
          <div className="max-w-5xl mx-auto relative flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Falar com ${activeChar?.name || 'Entidade'}...`}
              className="flex-1 bg-zinc-900 border border-zinc-800 rounded-2xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-white placeholder-zinc-600"
              disabled={isLoading || !selectedCharId}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !selectedCharId}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-800 text-white w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-900/20 transition-all hover:scale-105 active:scale-95"
            >
              <Send size={24} />
            </button>
          </div>
        </footer>
      </main>

      {/* Character Creator Modal */}
      {showCharModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 w-full max-w-md rounded-3xl p-8 shadow-2xl animate-in zoom-in-95 duration-200">
            <h2 className="text-2xl font-bold mb-6 text-white">Criar Nova Entidade</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Nome</label>
                <input 
                  type="text" 
                  value={newCharName}
                  onChange={e => setNewCharName(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="Ex: Luna, Dr. Kaos..."
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Descrição Curta</label>
                <input 
                  type="text" 
                  value={newCharShortDesc}
                  onChange={e => setNewCharShortDesc(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="Ex: Uma assistente calma e prestativa."
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">História / Personalidade (Backstory)</label>
                <textarea 
                  rows={4}
                  value={newCharDesc}
                  onChange={e => setNewCharDesc(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors resize-none"
                  placeholder="Descreva a história e personalidade dela em detalhes..."
                />
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button 
                onClick={() => setShowCharModal(false)}
                className="flex-1 px-4 py-3 rounded-xl bg-zinc-800 hover:bg-zinc-700 font-bold transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={createCharacter}
                className="flex-1 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold transition-all"
              >
                Criar Entidade
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Profile Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 w-full max-w-md rounded-3xl p-8 shadow-2xl animate-in zoom-in-95 duration-200">
            <h2 className="text-2xl font-bold mb-6 text-white text-center">Seu Perfil</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Seu Nome</label>
                <input 
                  type="text" 
                  value={userName}
                  onChange={e => setUserName(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="Como a entidade deve te chamar?"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Gênero</label>
                <select 
                  value={userGender}
                  onChange={e => setUserGender(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors appearance-none"
                >
                  <option value="Male">Masculino</option>
                  <option value="Female">Feminino</option>
                  <option value="Non-binary">Não-binário</option>
                  <option value="Unknown">Prefiro não dizer</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button 
                onClick={() => setShowUserModal(false)}
                className="flex-1 px-4 py-3 rounded-xl bg-zinc-800 hover:bg-zinc-700 font-bold transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={updateUser}
                className="flex-1 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold transition-all"
              >
                Salvar Perfil
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
