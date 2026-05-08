import React from 'react'

interface Tag {
  id: number
  label: string
}

interface Character {
  id: number
  name: string
  description: string
  tags: Tag[]
  lust: number
}

interface CharactersViewProps {
  characters: Character[]
  selectedCharId: number | null
  setSelectedCharId: (id: number) => void
  onNewCharacter: () => void
  onChat: (id: number) => void
  onEdit: (id: number) => void
}

const CharactersView: React.FC<CharactersViewProps> = ({
  characters,
  selectedCharId,
  setSelectedCharId,
  onNewCharacter,
  onChat,
  onEdit
}) => {
  return (
    <div className="max-w-container-max mx-auto h-full flex flex-col p-sm md:p-lg">
      <header className="mb-lg flex justify-between items-end border-b border-surface-variant pb-md">
        <div>
          <h2 className="font-display text-display text-primary tracking-tight">Characters</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mt-2">Manage your AI personas and character profiles.</p>
        </div>
        <button
          onClick={onNewCharacter}
          className="px-4 py-2 border border-outline-variant text-primary rounded font-body-md text-body-md hover:border-outline hover:bg-surface-container transition-all flex items-center gap-xs"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Character
        </button>
      </header>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <div className="mb-md relative">
          <span className="material-symbols-outlined absolute left-0 bottom-2 text-on-surface-variant text-[20px]">search</span>
          <input
            className="w-full bg-transparent border-0 border-b border-surface-variant pl-8 pb-2 text-primary focus:ring-0 focus:border-outline-variant transition-colors font-body-md text-body-md placeholder:text-surface-variant"
            placeholder="Search characters..."
            type="text"
          />
        </div>

        <div className="flex flex-col gap-3">
          {characters.map((char) => (
            <div
              key={char.id}
              onClick={() => setSelectedCharId(char.id)}
              className={`group flex flex-col rounded-xl border p-sm transition-all cursor-pointer ${
                selectedCharId === char.id
                  ? 'border-outline-variant bg-surface-container'
                  : 'border-transparent hover:border-surface-variant hover:bg-surface-container-low'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-md">
                  <div className="w-12 h-12 rounded-full border border-surface-variant bg-surface-container-highest flex items-center justify-center overflow-hidden shrink-0">
                    <span className="font-label-sm text-label-sm text-on-surface-variant">
                      {char.name.substring(0, 2).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className={`font-body-lg text-body-lg font-medium ${selectedCharId === char.id ? 'text-primary' : 'text-on-surface group-hover:text-primary transition-colors'}`}>
                      {char.name}
                    </h3>
                    <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mt-1">
                      {char.description.substring(0, 40)}...
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-xs">
                  <button
                    aria-label="Edit"
                    onClick={(e) => {
                      e.stopPropagation()
                      onEdit(char.id)
                    }}
                    className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-bright"
                  >
                    <span className="material-symbols-outlined text-[20px]">edit</span>
                  </button>
                  <button
                    aria-label="Chat"
                    onClick={(e) => {
                      e.stopPropagation()
                      onChat(char.id)
                    }}
                    className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-bright"
                  >
                    <span className="material-symbols-outlined text-[20px]">chat</span>
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-4">
                {char.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {char.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded-full border border-outline-variant bg-surface-container-low px-3 py-1 text-label-sm text-on-surface-variant"
                      >
                        {tag.label}
                      </span>
                    ))}
                  </div>
                )}
                {char.lust !== undefined && (
                  <span className="ml-auto text-label-sm text-on-surface-variant/60">
                    Lust: {char.lust}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <footer className="mt-auto pt-md border-t border-surface-variant flex justify-between items-center text-surface-variant font-label-sm text-label-sm uppercase tracking-widest">
        <span>{characters.length} Characters</span>
        <span>Sync Active</span>
      </footer>
    </div>
  )
}

export default CharactersView
