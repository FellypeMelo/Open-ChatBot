import React from 'react'
import Icon from './Icon'
import IconButton from './IconButton'
import MessageRenderer from './MessageRenderer'
import { arePropsEqual } from './messageRowEquality'
import type { MessageRowProps } from './messageRowEquality'
export type { MessageRowProps } from './messageRowEquality'

// Inline editor shared by the user-prompt and assistant-reply message editors --
// same textarea + Cancel/Save row, differing only in the textarea's type styling.
// Only used inside MessageRow's own edit states, so it lives here rather than
// in ChatView (which no longer renders per-message markup directly).
const MessageEditor: React.FC<{
  value: string
  onChange: (v: string) => void
  onCancel: () => void
  onSave: () => void
  textareaClassName: string
  wrapperClassName?: string
}> = ({ value, onChange, onCancel, onSave, textareaClassName, wrapperClassName = 'w-full flex flex-col gap-2' }) => (
  <div className={wrapperClassName}>
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={textareaClassName}
      autoFocus
    />
    <div className="flex gap-2 self-end">
      <button onClick={onCancel} className="px-3 py-1 text-xs font-mono text-zinc-400 hover:text-white">
        CANCEL
      </button>
      <button onClick={onSave} className="px-3 py-1 bg-white text-black text-xs font-bold rounded">
        SAVE
      </button>
    </div>
  </div>
)

// Renders exactly one node of the active message path -- the user-prompt
// branch or the assistant-reply branch. Extracted out of ChatView's
// `activePath.map(...)` (and wrapped in React.memo below with a custom
// comparator) so a streaming turn's per-token re-render only ever recomputes
// the JSX for the one row actually receiving new tokens, not all of them.
const MessageRowImpl: React.FC<MessageRowProps> = ({
  msg,
  characterName,
  isEditing,
  editContent,
  isStreaming,
  displayedContent,
  isCopied,
  hasSiblings,
  currentIndex,
  siblingsLength,
  onEditStart,
  onEditChange,
  onEditCancel,
  onEditSave,
  onDelete,
  onRegenerate,
  onCopyId,
  onPrevVariant,
  onNextVariant,
}) => {
  if (msg.role === 'user') {
    return (
      <div className="w-full flex flex-col items-start mt-6 mb-6 group">
        <div className="flex items-center justify-between w-full mb-2">
          <div className="flex items-center gap-2 select-none">
            <span className="w-1.5 h-1.5 rounded-full bg-[#34D399]/40" />
            <span className="font-mono text-[11px] md:text-[9px] uppercase tracking-[0.2em] text-[#34D399]/70">
              PROMPT ACTION
            </span>
          </div>

          {!isEditing && (
            <div className="flex items-center gap-0.5 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
              <IconButton
                icon="edit"
                label="Edit"
                size="sm"
                onClick={onEditStart}
                className="text-[#71717A] hover:text-white"
              />
              {onDelete && (
                <IconButton
                  icon="delete"
                  label="Delete"
                  size="sm"
                  onClick={onDelete}
                  className="text-[#71717A] hover:text-red-400"
                />
              )}
            </div>
          )}
        </div>

        {isEditing ? (
          <MessageEditor
            value={editContent}
            onChange={onEditChange}
            onCancel={onEditCancel}
            onSave={onEditSave}
            textareaClassName="w-full bg-[#09090B] border border-white/20 focus:border-white/40 outline-none rounded p-3 text-zinc-300 font-sans text-base md:text-sm resize-y min-h-[80px]"
          />
        ) : (
          <div className="w-full border-l-2 border-white/10 pl-5 py-1 text-zinc-400 font-sans text-sm leading-relaxed whitespace-pre-wrap">
            {msg.content}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2 w-full group mt-6 mb-8 relative border-t border-white/5 pt-6 first:border-t-0 first:pt-0">
      {/* Character Header Info */}
      <div className="flex items-center justify-between mb-1 select-none">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[11px] md:text-[10px] uppercase tracking-[0.25em] text-white/50">
            {characterName}
          </span>
          {isStreaming && (
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          )}
        </div>

        {/* Variant Navigation switcher */}
        {hasSiblings && (
          <div className="flex items-center gap-0.5 px-1 rounded-full bg-white/5 border border-white/10 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
            <IconButton
              icon="chevron_left"
              label="Previous variant"
              size="sm"
              onClick={onPrevVariant}
              disabled={currentIndex === 0}
              className="text-[#71717A] hover:text-white"
            />
            <span className="font-mono text-[11px] text-[#71717A] tabular-nums px-0.5">
              {currentIndex + 1} / {siblingsLength}
            </span>
            <IconButton
              icon="chevron_right"
              label="Next variant"
              size="sm"
              onClick={onNextVariant}
              disabled={currentIndex === siblingsLength - 1}
              className="text-[#71717A] hover:text-white"
            />
          </div>
        )}
      </div>

      {/* Message Body (No bubble, flows directly on background) */}
      {isEditing ? (
        <MessageEditor
          value={editContent}
          onChange={onEditChange}
          onCancel={onEditCancel}
          onSave={onEditSave}
          textareaClassName="w-full bg-[#09090B] border border-white/20 focus:border-white/40 outline-none rounded p-3 text-zinc-300 font-serif text-[17px] leading-[1.8] resize-y min-h-[120px]"
          wrapperClassName="w-full flex flex-col gap-2 mt-2"
        />
      ) : (
        <div className="font-serif text-[17px] text-zinc-200 leading-[1.8] antialiased select-text">
          <MessageRenderer content={isStreaming ? displayedContent : msg.content} />
        </div>
      )}

      {/* Controls Footer. Icon-only on mobile (labels hidden but
          kept in the DOM), icon + label from md up. */}
      <div className="flex flex-wrap gap-x-1 gap-y-1 mt-3 items-center opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
        <button
          onClick={onRegenerate}
          aria-label="Regenerate response"
          className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer min-h-11 md:min-h-0 px-1.5 touch-manipulation active:scale-95"
        >
          <Icon name="refresh" size="sm" />
          <span className="hidden md:inline">Regenerate</span>
        </button>
        <button
          onClick={onEditStart}
          aria-label="Edit response"
          className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer min-h-11 md:min-h-0 px-1.5 touch-manipulation active:scale-95"
        >
          <Icon name="edit" size="sm" />
          <span className="hidden md:inline">Edit</span>
        </button>
        {onDelete && (
          <button
            onClick={onDelete}
            aria-label="Delete response"
            className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-red-400 transition-colors cursor-pointer min-h-11 md:min-h-0 px-1.5 touch-manipulation active:scale-95"
          >
            <Icon name="delete" size="sm" />
            <span className="hidden md:inline">Delete</span>
          </button>
        )}
        <button
          onClick={onCopyId}
          disabled={!msg.request_id}
          className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#71717A] hover:text-white transition-colors cursor-pointer min-h-11 md:min-h-0 px-1.5 touch-manipulation active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:text-[#71717A]"
          title={msg.request_id ? 'Copy Request ID' : 'Request ID not available yet'}
        >
          <Icon name={msg.request_id && isCopied ? 'check' : 'content_copy'} size="sm" />
          <span className="hidden md:inline">
            {msg.request_id && isCopied ? 'Copied' : 'Copy ID'}
          </span>
        </button>
        {msg.request_id && (
          <span className="font-mono text-[11px] md:text-[9px] text-[#71717A]/30 uppercase tracking-wider select-none">
            REQ: {msg.request_id.split('-')[0]}
          </span>
        )}
      </div>
    </div>
  )
}

// arePropsEqual (the WHY behind each gated/ignored prop) lives in
// ./messageRowEquality -- imported above -- so it can be unit-tested in
// isolation without a component file needing to export a non-component value.
const MessageRow = React.memo(MessageRowImpl, arePropsEqual)

export default MessageRow
