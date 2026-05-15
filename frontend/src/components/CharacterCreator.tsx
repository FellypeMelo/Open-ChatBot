import React, { useState } from 'react'

interface Tag {
  id: number
  label: string
  instruction: string
}

interface CharacterData {
  id: number
  name: string
  description: string
  tags: Tag[]
}

interface CharacterCreatorProps {
  onClose: () => void
  onCreate: (name: string, description: string, tagIds: number[]) => Promise<void> | void
  onUpdate: (id: number, name: string, description: string, tagIds: number[]) => Promise<void> | void
  tags: Tag[]
  editingCharacter?: CharacterData | null
}

const CharacterCreator: React.FC<CharacterCreatorProps> = ({
  onClose,
  onCreate,
  onUpdate,
  tags,
  editingCharacter
}) => {
  const [name, setName] = useState(editingCharacter?.name ?? '')
  const [description, setDescription] = useState(editingCharacter?.description ?? '')
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>(
    editingCharacter?.tags.map((t) => t.id) ?? []
  )
  const [isSaving, setIsSaving] = useState(false)

  const isEditing = !!editingCharacter

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    if (isEditing && editingCharacter) {
      await onUpdate(editingCharacter.id, name, description, selectedTagIds)
    } else {
      await onCreate(name, description, selectedTagIds)
    }
    setIsSaving(false)
  }

  const toggleTag = (tagId: number) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    )
  }

  return (
    <div className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md">
      <div className="w-full max-w-[620px] bg-[#111111] border border-[#1A1A1A] p-lg md:p-xl flex flex-col gap-lg z-50 animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-start w-full">
          <div className="flex flex-col gap-xs">
            <h2 className="font-headline-lg text-headline-lg text-primary tracking-tight">
              {isEditing ? 'Edit Character' : 'Create Character'}
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Define the core attributes and narrative stance.</p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="text-on-surface-variant hover:text-primary transition-colors p-xs"
            type="button"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-lg w-full">
          <div className="grid gap-lg">
            <div className="flex flex-col gap-xs">
              <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_name">Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30"
                id="char_name"
                placeholder="e.g. Architect, Elara, Kaelen"
                type="text"
                required
              />
            </div>

            <div className="flex flex-col gap-xs">
              <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_description">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                id="char_description"
                placeholder="Describe the character's personality, backstory, and behavior..."
                rows={4}
                required
              />
            </div>

            <div className="flex flex-col gap-xs">
              <label className="font-label-sm text-label-sm text-[#71717A] uppercase">Tags</label>
              <p className="font-label-sm text-label-sm text-on-surface-variant -mt-1">Select traits or categories</p>
              {tags.length === 0 ? (
                <p className="font-body-sm text-body-sm text-on-surface-variant/50">No tags available. Create some in the Archives view.</p>
              ) : (
                <div className="flex flex-wrap gap-2 pt-xs">
                  {tags.map((tag) => (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => toggleTag(tag.id)}
                      className={`px-3 py-1.5 rounded-sm border text-label-sm transition-colors ${
                        selectedTagIds.includes(tag.id)
                          ? 'bg-primary text-surface-container-lowest border-primary'
                          : 'bg-transparent text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
                      }`}
                    >
                      {tag.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end items-center gap-md pt-md border-t border-[#1A1A1A] mt-sm">
            <button
              onClick={onClose}
              disabled={isSaving}
              className="font-body-md text-body-md text-on-surface px-md py-xs border border-transparent hover:border-[#1A1A1A] transition-colors disabled:opacity-50"
              type="button"
            >
              Cancel
            </button>
            <button
              disabled={isSaving}
              className="font-body-md text-body-md font-medium bg-primary text-surface-container-lowest px-lg py-xs hover:bg-on-surface transition-colors disabled:opacity-50 min-w-[120px]"
              type="submit"
            >
              {isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Initialize')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CharacterCreator
