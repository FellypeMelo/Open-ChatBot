import React, { useState } from 'react'

interface Tag {
  id: number
  label: string
  instruction: string
}

interface TagCreatorProps {
  onClose: () => void
  onSubmit: (label: string, instruction: string) => Promise<void> | void
  tag?: Tag | null
}

const TagCreator: React.FC<TagCreatorProps> = ({ onClose, onSubmit, tag }) => {
  const [label, setLabel] = useState(tag?.label ?? '')
  const [instruction, setInstruction] = useState(tag?.instruction ?? '')
  const [isSaving, setIsSaving] = useState(false)

  const [prevTag, setPrevTag] = useState(tag)
  if (tag !== prevTag) {
    setPrevTag(tag)
    setLabel(tag?.label ?? '')
    setInstruction(tag?.instruction ?? '')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    await onSubmit(label, instruction)
    setIsSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md">
      <div className="w-full max-w-[500px] bg-[#111111] border border-[#1A1A1A] p-lg md:p-xl flex flex-col gap-lg z-50 animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-start w-full">
          <div className="flex flex-col gap-xs">
            <h2 className="font-headline-lg text-headline-lg text-primary tracking-tight">
              {tag ? 'Edit Tag' : 'Create New Tag'}
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {tag ? 'Update visibility and behavior for this tag.' : 'Define a modular behavioral modifier.'}
            </p>
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
          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="tag_label">Tag Label</label>
            <input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30"
              id="tag_label"
              placeholder="e.g. Sarcastic, Tactical..."
              type="text"
              required
            />
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="tag_instruction">Prompt Instruction</label>
            <textarea
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
              id="tag_instruction"
              placeholder="Detailed instructions for the AI on how to embody this tag..."
              rows={4}
              required
            />
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
              className="font-body-md text-body-md font-medium bg-primary text-surface-container-lowest px-lg py-xs hover:bg-on-surface transition-colors disabled:opacity-50 min-w-[120px]"
              type="submit"
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : (tag ? 'Save Changes' : 'Create Tag')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TagCreator
