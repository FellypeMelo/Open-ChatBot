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
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <div className="max-w-container-max mx-auto w-full h-full flex flex-col px-sm md:px-lg py-lg">
        <header className="mb-lg flex flex-col gap-sm">
          <div className="flex items-center justify-between gap-sm">
            <div>
              <h1 className="font-display text-display text-primary tracking-tight">Character Library</h1>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mt-1">Manage and select your AI personas</p>
            </div>
            <button
              onClick={onNewCharacter}
              className="inline-flex items-center gap-xs rounded border border-outline-variant bg-surface-container px-4 py-2 text-body-md font-body-md text-on-surface transition-colors hover:border-outline hover:text-primary hover:bg-surface-container-high"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Character
            </button>
          </div>
          <div className="border-b border-outline-variant pb-sm">
            <input
              type="text"
              placeholder="Search library..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-transparent border-none text-body-md font-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none"
            />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg pb-lg">
            {filteredCharacters.length > 0 ? (
              filteredCharacters.map((character) => (
                <div
                  key={character.id}
                  onClick={() => setSelectedCharId(character.id)}
                  className={`group relative flex flex-col rounded-xl border p-lg transition-all cursor-pointer ${
                    selectedCharId === character.id
                      ? 'border-primary bg-surface-container-high'
                      : 'border-surface-container-high bg-surface-container hover:border-outline-variant hover:bg-surface-container-low'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex items-center gap-sm">
                      <div className="w-12 h-12 rounded-full bg-surface-container-highest border border-outline-variant flex items-center justify-center text-body-lg font-body-lg text-on-surface-variant">
                        {character.name.substring(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <h2 className={`font-display text-headline-lg transition-colors ${selectedCharId === character.id ? 'text-primary' : 'text-on-surface group-hover:text-primary'}`}>
                          {character.name}
                        </h2>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        aria-label="Edit"
                        onClick={(e) => {
                          e.stopPropagation()
                          onEdit(character.id)
                        }}
                        className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-bright"
                      >
                        <span className="material-symbols-outlined text-[22px]">edit</span>
                      </button>
                      <button
                        aria-label="Delete"
                        onClick={(e) => {
                          e.stopPropagation()
                          onDelete(character.id)
                        }}
                        className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-bright"
                      >
                        <span className="material-symbols-outlined text-[22px]">delete</span>
                      </button>
                      <button
                        aria-label="Chat"
                        onClick={(e) => {
                          e.stopPropagation()
                          onChat(character.id)
                        }}
                        className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-bright"
                      >
                        <span className="material-symbols-outlined text-[22px]">chat</span>
                      </button>
                    </div>
                  </div>

                  <p className="font-body-md text-body-md text-on-surface-variant mb-4 line-clamp-2">
                    {character.description}
                  </p>

                  <div className="mt-auto flex flex-wrap gap-2">
                    {character.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded-full border border-outline-variant bg-surface-container-low px-2 py-0.5 text-label-sm text-on-surface-variant"
                      >
                        {tag.label}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full rounded-xl border border-surface-container-high p-lg text-on-surface-variant">
                <p className="font-body-lg text-body-lg">No characters found matching your search.</p>
              </div>
            )}
          </div>
        </main>

        <footer className="mt-auto pt-md border-t border-surface-variant flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm uppercase tracking-widest">
          <span>{characters.length} Personalities</span>
          <span>Library Synchronized</span>
        </footer>
      </div>
    </div>
  )
}

export default CharactersView
