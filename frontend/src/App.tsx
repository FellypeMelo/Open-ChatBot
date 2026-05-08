import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Smile, MoreVertical } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const formatTime = (date?: Date) => {
    if (!date) return ''
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  const formatDate = (date?: Date) => {
    if (!date) return ''
    return date.toLocaleDateString('pt-BR', { weekday: 'short', day: 'numeric', month: 'short' })
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
      
      const data = await response.json()
      const assistantMessage: Message = { role: 'assistant', content: data.reply, timestamp: new Date() }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { role: 'assistant', content: 'Erro ao comunicar com IA.', timestamp: new Date() }])
    } finally {
      setIsLoading(false)
    }
  }

  // Agrupar mensagens por data
  const groupedMessages = messages.reduce((acc, msg, idx) => {
    const today = new Date()
    const msgDate = msg.timestamp || new Date()
    const isToday = msgDate.toDateString() === today.toDateString()
    
    const dateKey = isToday ? 'Hoje' : formatDate(msgDate)
    
    if (!acc[dateKey]) {
      acc[dateKey] = []
    }
    acc[dateKey].push({ ...msg, index: idx })
    return acc
  }, {} as Record<string, (Message & { index: number })[]>)

  return (
    <div className="flex flex-col h-screen w-screen bg-stone-100 text-stone-900 font-sans">
      {/* Header */}
      <header className="bg-teal-700 px-4 py-3 shadow-md flex justify-between items-center">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-full bg-teal-500 flex items-center justify-center shadow-md">
            <span className="text-white font-bold">🤖</span>
          </div>
          <div>
            <h1 className="text-white font-medium">Open-ChatBot</h1>
            <p className="text-xs text-teal-100">Clique para exibir informações</p>
          </div>
        </div>
        <button className="p-2 hover:bg-teal-600 rounded-full transition-colors text-white">
          <MoreVertical size={20} />
        </button>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto px-3 py-4 space-y-3 bg-stone-50">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-stone-400">
            <div className="text-6xl mb-4">💬</div>
            <p className="text-lg font-medium">Comece uma conversa</p>
            <p className="text-sm text-stone-500">Digite uma mensagem para começar</p>
          </div>
        )}
        
        {Object.entries(groupedMessages).map(([date, msgs]) => (
          <div key={date}>
            {/* Separador de data */}
            <div className="flex justify-center my-4">
              <div className="bg-stone-300 text-stone-600 text-xs px-3 py-1 rounded-full">
                {date}
              </div>
            </div>

            {/* Mensagens do dia */}
            {msgs.map((msg) => (
              <div 
                key={msg.index}
                className={`flex gap-2 mb-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex flex-col gap-0.5 max-w-xs ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div 
                    className={`px-4 py-2 rounded-lg break-words text-sm leading-relaxed shadow-sm ${
                      msg.role === 'user' 
                        ? 'bg-teal-500 text-white rounded-br-none' 
                        : 'bg-white text-stone-900 rounded-bl-none border border-stone-200'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  <span className={`text-xs text-stone-500 px-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-2 justify-start">
            <div className="flex flex-col gap-0.5">
              <div className="bg-white px-4 py-3 rounded-lg rounded-bl-none border border-stone-200 shadow-sm flex gap-2">
                <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-xs text-stone-500 px-2">Digitando...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-stone-100 border-t border-stone-200 px-3 py-3 shadow-lg">
        <div className="flex gap-2 items-end">
          <button className="p-2 hover:bg-stone-200 rounded-full transition-colors text-teal-600 hover:text-teal-700 flex-shrink-0">
            <Smile size={24} />
          </button>
          
          <button className="p-2 hover:bg-stone-200 rounded-full transition-colors text-teal-600 hover:text-teal-700 flex-shrink-0">
            <Paperclip size={24} />
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Mensagem"
            className="flex-1 bg-white border border-stone-300 rounded-full px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all text-stone-900 placeholder-stone-400 text-sm"
            disabled={isLoading}
          />
          
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="p-2 bg-teal-500 hover:bg-teal-600 disabled:bg-stone-300 rounded-full transition-colors text-white shadow-md flex items-center justify-center flex-shrink-0"
          >
            <Send size={20} />
          </button>
        </div>
      </footer>
    </div>
  )
}

export default App
