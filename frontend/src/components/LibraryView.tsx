import React from 'react'

interface Tag {
  id: number
  label: string
}

interface Character {
  id: number
  name: string
  description: string
  short_description?: string
  tags: Tag[]
}

interface LibraryViewProps {
  characters: Character[]
  onOpenStory: (id: number) => void
  onNewStory: () => void
}

const LibraryView: React.FC<LibraryViewProps> = ({ characters, onOpenStory, onNewStory }) => {
  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <div className="max-w-container-max mx-auto h-full flex flex-col px-sm md:px-lg py-lg">
        <header className="mb-lg flex flex-col gap-sm">
          <div className="flex items-center justify-between gap-sm">
            <div>
              <h1 className="font-display text-display text-primary tracking-tight">Open Chat</h1>
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mt-1">Archivist of the Lost Library</p>
            </div>
            <button
              onClick={onNewStory}
              className="inline-flex items-center gap-xs rounded border border-outline-variant bg-surface-container px-4 py-2 text-body-md font-body-md text-on-surface transition-colors hover:border-outline hover:text-primary hover:bg-surface-container-high"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Story
            </button>
          </div>
          <div className="border-b border-outline-variant pb-sm">
            <input
              type="text"
              placeholder="Search stories..."
              className="w-full bg-transparent border-none border-b border-outline-variant pb-2 text-body-md font-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary"
            />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg">
            {characters.length > 0 ? (
              characters.map((character) => (
                <button
                  key={character.id}
                  onClick={() => onOpenStory(character.id)}
                  className="group text-left rounded-xl border border-surface-container-high hover:border-outline-variant bg-surface-container p-lg transition-all"
                >
                  <div className="flex items-center gap-sm mb-md">
                    <div className="w-12 h-12 rounded-full bg-surface-container-highest border border-outline-variant flex items-center justify-center text-body-lg font-body-lg text-on-surface-variant">
                      {character.name.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <h2 className="font-display text-headline-lg text-primary">{character.name}</h2>
                      <p className="font-body-md text-body-md text-on-surface-variant mt-1">{character.short_description || character.description.substring(0, 80) + '...'}</p>
                    </div>
                  </div>
                  <div className="mb-4 flex flex-wrap gap-2">
                    {character.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded-full border border-outline-variant bg-surface-container-low px-2 py-1 text-label-sm text-on-surface-variant"
                      >
                        {tag.label}
                      </span>
                    ))}
                  </div>
                  <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest flex items-center gap-2">
                    <span>Open story</span>
                    <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                  </div>
                </button>
              ))
            ) : (
              <div className="rounded-xl border border-surface-container-high p-lg text-on-surface-variant">
                <p className="font-body-lg text-body-lg">No stories found. Start by creating a new character or importing one from an existing prompt.</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default LibraryView
