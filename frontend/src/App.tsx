import { useState, useRef, useEffect } from 'react'
import { Send, Plus, Users, Tag as TagIcon, Brain as BrainIcon, Heart, Zap, Pizza } from 'lucide-react'

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
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  thought?: string
  actions?: string[]
  timestamp?: Date
}

function App() {
  const [characters, setCharacters] = useState<Character[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showCharModal, setShowCharModal] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Character Form State
  const [newCharName, setNewCharName] = useState('')
  const [newCharDesc, setNewCharDesc] = useState('')

  useEffect(() => {
    fetchCharacters()
  }, [])

  const fetchCharacters = async () => {
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
  }

  const createCharacter = async () => {
    if (!newCharName || !newCharDesc) return
    try {
      const response = await fetch('/characters/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCharName, description: newCharDesc })
      })
      const data = await response.json()
      setCharacters(prev => [...prev, data])
      setSelectedCharId(data.id)
      setShowCharModal(false)
      setNewCharName('')
      setNewCharDesc('')
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
        timestamp: new Date() 
      }
      setMessages(prev => [...prev, assistantMessage])
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
      <aside className="w-64 border-r border-zinc-800 flex flex-col bg-zinc-900 shadow-xl">
        <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
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
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
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
                {char.description}
              </span>
            </button>
          ))}
        </div>
        
        {/* Global Systems Link */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/80 backdrop-blur">
          <button className="w-full flex items-center gap-2 p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 text-sm transition-colors">
            <TagIcon size={16} /> Gerenciar Tags
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative bg-zinc-950">
        {/* Header / HUD */}
        <header className="px-6 py-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-950/50 backdrop-blur-md sticky top-0 z-10">
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
            <div className="flex flex-col items-center">
              <Zap size={16} className="text-amber-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-amber-500 w-full" />
              </div>
            </div>
            <div className="flex flex-col items-center">
              <Pizza size={16} className="text-rose-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-rose-500 w-1/4" />
              </div>
            </div>
            <div className="flex flex-col items-center">
              <Heart size={16} className="text-emerald-500" />
              <div className="h-1 w-12 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                <div className="h-full bg-emerald-500 w-1/2" />
              </div>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-zinc-600 max-w-sm mx-auto text-center space-y-4">
              <div className="p-6 bg-zinc-900 rounded-3xl border border-zinc-800">
                <BrainIcon size={48} className="mx-auto mb-4 text-emerald-500/40" />
                <p className="text-lg font-medium text-zinc-400">Pronto para o Roleplay?</p>
                <p className="text-sm">A entidade vai responder com pensamentos internos, ações físicas e diálogos.</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
              <div className={`flex flex-col gap-1.5 max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                {/* Actions (Bold) */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="px-2 text-xs font-bold text-emerald-500/80 uppercase tracking-widest">
                    {msg.actions.map(a => `**${a}**`).join(' ')}
                  </div>
                )}

                <div className={`p-4 rounded-2xl shadow-lg border ${
                  msg.role === 'user' 
                    ? 'bg-emerald-600 border-emerald-500 text-white rounded-tr-none' 
                    : 'bg-zinc-900 border-zinc-800 text-zinc-100 rounded-tl-none'
                }`}>
                  {/* Internal Thought (Italic) */}
                  {msg.thought && (
                    <div className="text-sm italic text-zinc-400 mb-2 border-l-2 border-emerald-500/30 pl-3 py-0.5">
                      {msg.thought}
                    </div>
                  )}
                  
                  {/* Dialogue */}
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {msg.content}
                  </p>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
               <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-2xl rounded-tl-none flex gap-1.5 items-center">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" />
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.4s]" />
               </div>
            </div>
          )}
          <div ref={chatEndRef} />
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
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Descrição / Backstory</label>
                <textarea 
                  rows={4}
                  value={newCharDesc}
                  onChange={e => setNewCharDesc(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors resize-none"
                  placeholder="Descreva a história e personalidade dela..."
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
    </div>
  )
}

export default App
