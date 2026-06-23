import React, { useState } from 'react'

interface Tag {
  id: number
  label: string
}

interface Character {
  id: number
  name: string
  description: string
  tags: Tag[]
}

interface CharactersViewProps {
  characters: Character[]
  selectedCharId: number | null
  setSelectedCharId: (id: number) => void
  onNewCharacter: () => void
  onChat: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

const CharactersView: React.FC<CharactersViewProps> = ({
  characters,
  selectedCharId,
  setSelectedCharId,
  onNewCharacter,
  onChat,
  onEdit,
  onDelete
}) => {
  const [search, setSearch] = useState('')

  const filteredCharacters = characters.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase()) || 
    c.description.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#050505] text-[#F4F4F5] relative">
      {/* Background ambient orbs */}
      <div className="absolute top-20 right-20 w-96 h-96 bg-white/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-white/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-[1200px] mx-auto w-full h-full flex flex-col px-md md:px-lg py-lg relative z-10">
        
        {/* Header Section */}
        <header className="mb-lg flex flex-col gap-md">
          <div className="flex items-center justify-between gap-sm">
            <div className="flex flex-col gap-1">
              <span className="font-label-sm text-[10px] uppercase tracking-[0.2em] text-[#71717A]">
                NARRATIVE ENGINE
              </span>
              <h1 className="font-sans text-3xl font-extrabold tracking-tight text-white leading-none">
                Character Core
              </h1>
            </div>
            <button
              onClick={onNewCharacter}
              className="btn-premium-primary cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              Initialize Persona
            </button>
          </div>

          <div className="relative w-full">
            <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-[#71717A] text-[18px]">
              search
            </span>
            <input
              type="text"
              placeholder="Search library..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0A0A0B]/60 backdrop-blur border border-white/10 rounded-full pl-10 pr-sm py-2 text-sm text-white placeholder-[#71717A] focus:border-white/30 focus:outline-none transition-all duration-300"
            />
          </div>
        </header>

        {/* Grid Area */}
        <main className="flex-1 overflow-y-auto pr-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md pb-lg">
            {filteredCharacters.length > 0 ? (
              filteredCharacters.map((character) => {
                const isSelected = selectedCharId === character.id
                return (
                  <div
                    key={character.id}
                    onClick={() => setSelectedCharId(character.id)}
                    className={`bezel-outer group cursor-pointer ${
                      isSelected ? 'border-white/30 bg-white/5 shadow-2xl scale-[0.99]' : ''
                    }`}
                  >
                    <div className="bezel-inner min-h-[160px] flex flex-col justify-between">
                      {/* Top Row: Info & Controls */}
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-3">
                          {/* Avatar icon */}
                          <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center font-mono text-xs text-[#A1A1AA] font-bold shadow-inner relative">
                            {character.name.substring(0, 2).toUpperCase()}
                            {isSelected && (
                              <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border border-[#09090B] dot-glow animate-pulse" />
                            )}
                          </div>
                          <div>
                            <h2 className={`font-sans text-md font-bold tracking-tight transition-colors ${
                              isSelected ? 'text-white' : 'text-[#A1A1AA] group-hover:text-white'
                            }`}>
                              {character.name}
                            </h2>
                          </div>
                        </div>

                        {/* Actions menu (fades in on hover) */}
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                          <button
                            aria-label="Edit"
                            onClick={(e) => {
                              e.stopPropagation()
                              onEdit(character.id)
                            }}
                            className="p-1.5 text-[#71717A] hover:text-white bg-white/5 hover:bg-white/10 rounded-full border border-white/5 transition-all duration-300 flex items-center justify-center"
                          >
                            <span className="material-symbols-outlined text-[16px]">edit</span>
                          </button>
                          <button
                            aria-label="Delete"
                            onClick={(e) => {
                              e.stopPropagation()
                              onDelete(character.id)
                            }}
                            className="p-1.5 text-[#71717A] hover:text-red-400 bg-white/5 hover:bg-white/10 rounded-full border border-white/5 transition-all duration-300 flex items-center justify-center"
                          >
                            <span className="material-symbols-outlined text-[16px]">delete</span>
                          </button>
                          <button
                            aria-label="Chat"
                            onClick={(e) => {
                              e.stopPropagation()
                              onChat(character.id)
                            }}
                            className="p-1.5 text-[#71717A] hover:text-emerald-400 bg-white/5 hover:bg-white/10 rounded-full border border-white/5 transition-all duration-300 flex items-center justify-center"
                          >
                            <span className="material-symbols-outlined text-[16px]">chat</span>
                          </button>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="font-sans text-xs text-[#A1A1AA] line-clamp-2 leading-relaxed mb-4">
                        {character.description}
                      </p>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-1.5 mt-auto">
                        {character.tags.map((tag) => (
                          <span
                            key={tag.id}
                            className="rounded-full border border-white/5 bg-white/5 px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-[#A1A1AA]"
                          >
                            {tag.label}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="col-span-full border border-white/10 bg-[#09090B] rounded-[1rem] p-lg text-center text-[#71717A]">
                <p className="font-sans text-sm">No personalities found matching your query.</p>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-auto pt-md border-t border-white/5 flex justify-between items-center text-[#71717A] font-mono text-[9px] uppercase tracking-[0.2em] relative z-10">
          <span>{characters.length} Active Personas</span>
          <span>Core Sync: OK</span>
        </footer>
      </div>
    </div>
  )
}

export default CharactersView
