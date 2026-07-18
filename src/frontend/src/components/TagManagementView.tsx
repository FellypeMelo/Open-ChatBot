import React, { useMemo, useState } from 'react'
import type { Tag } from '../services/api'

interface TagManagementViewProps {
  tags: Tag[]
  onCreateTag: () => void
  onEditTag: (tag: Tag) => void
  onDeleteTag: (tagId: number) => void
  usage: Record<number, number>
}

const TagManagementView: React.FC<TagManagementViewProps> = ({ tags, onCreateTag, onEditTag, onDeleteTag, usage }) => {
  const [filter, setFilter] = useState('')

  const filteredTags = useMemo(() => {
    const search = filter.trim().toLowerCase()
    return tags.filter((tag) =>
      tag.label.toLowerCase().includes(search) || tag.instruction.toLowerCase().includes(search)
    )
  }, [filter, tags])

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-background custom-scrollbar">
      <header className="w-full px-md h-16 max-w-[1200px] mx-auto flex justify-between items-center shrink-0 mt-md">
        <div>
          <h2 className="font-heading-md text-heading-md font-semibold text-primary">Tag Management</h2>
          <p className="font-label-sm text-label-sm text-on-surface-variant mt-1 uppercase tracking-wider">System Taxonomy</p>
        </div>
        <div className="flex gap-sm items-center">
          <div className="relative hidden sm:block">
            <span className="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
            <input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-transparent border-b border-outline focus:border-primary focus:outline-none text-on-surface pl-8 pr-3 py-xs font-body-md text-body-md w-48 placeholder-on-surface-variant transition-colors bg-transparent h-full pb-1 focus:ring-0"
              placeholder="Filter tags..."
              type="text"
            />
          </div>
          <button
            onClick={onCreateTag}
            className="bg-transparent border border-outline text-on-surface rounded px-sm py-xs font-body-md text-body-md hover:border-primary hover:text-primary transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Create New Tag
          </button>
        </div>
      </header>

      <div className="flex-1 w-full max-w-[1200px] mx-auto px-md py-lg space-y-xl">
        <section>
          <div className="mb-sm border-b border-surface-container-high pb-xs flex justify-between items-end">
            <h3 className="font-body-lg text-body-lg text-on-surface">Personality Traits</h3>
            <span className="font-label-sm text-label-sm text-on-surface-variant">{filteredTags.length} items</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-sm">
            {filteredTags.map((tag) => (
              <div
                key={tag.id}
                className="group border border-surface-container-high hover:border-outline rounded p-sm transition-colors flex flex-col gap-3 bg-background"
              >
                <div className="flex justify-between items-start gap-2">
                  <span className="font-label-sm text-label-sm text-on-surface border border-outline rounded px-2 py-0.5 inline-block bg-surface-container-low group-hover:border-primary transition-colors">
                    {tag.label}
                  </span>
                  <div className="flex items-center gap-xs opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onEditTag(tag)}
                      className="text-on-surface-variant hover:text-primary transition-colors"
                      type="button"
                    >
                      <span className="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    <button
                      onClick={() => onDeleteTag(tag.id)}
                      className="text-on-surface-variant hover:text-primary transition-colors"
                      type="button"
                    >
                      <span className="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                  </div>
                </div>
                <p className="font-body-md text-body-md text-on-surface-variant pt-2">
                  {tag.instruction}
                </p>
                <div className="flex gap-2 mt-auto pt-3 border-t border-surface-container-lowest text-on-surface-variant text-label-sm">
                  <span className="flex items-center gap-1">
                    Used: {usage[tag.id] ?? 0}x
                  </span>
                  <span className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-secondary"></div>
                    Global
                  </span>
                </div>
              </div>
            ))}
          </div>
          {filteredTags.length === 0 && (
            <div className="rounded-xl border border-surface-container-high p-lg bg-surface-container-lowest text-on-surface-variant">
              <p className="font-body-lg text-body-lg">No tags match your filter. Use the "Create New Tag" button to add more taxonomy entries.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default TagManagementView
