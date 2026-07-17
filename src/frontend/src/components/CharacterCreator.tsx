import React, { useState, useEffect, useRef } from 'react'
import type { Character, Tag } from '../services/api'

interface CharacterFormData {
  name: string
  description: string
  nickname: string
  short_description: string
  persona_prompt: string
  scenario: string
  first_mes: string
  alternate_greetings: string[]
  mes_example: string
  content_rating: string
  tagIds: number[]
  avatarFile: File | null
}

interface CharacterCreatorProps {
  onClose: () => void
  onCreate: (data: CharacterFormData) => Promise<void> | void
  onUpdate: (id: number, data: CharacterFormData) => Promise<void> | void
  tags: Tag[]
  editingCharacter?: Character | null
}

const MAX_GREETINGS = 10
// Offline token estimate: English averages ~1.3 tokens per word.
const WORDS_TO_TOKENS_RATIO = 1.3

// Resolve {{char}}/{{user}} for the Preview tab (mirrors the backend macro pass).
const renderMacros = (text: string, charName: string): string =>
  (text || '')
    .replace(/\{\{\s*char\s*\}\}/gi, charName || 'Character')
    .replace(/\{\{\s*user\s*\}\}/gi, 'User')

const CharacterCreator: React.FC<CharacterCreatorProps> = ({
  onClose,
  onCreate,
  onUpdate,
  tags,
  editingCharacter
}) => {
  const isEditing = !!editingCharacter

  // Core Fields
  const [name, setName] = useState(editingCharacter?.name ?? '')
  const [nickname, setNickname] = useState(editingCharacter?.nickname ?? '')
  const [description, setDescription] = useState(editingCharacter?.description ?? '')
  const [shortDescription, setShortDescription] = useState(editingCharacter?.short_description ?? '')
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>(
    editingCharacter?.tags.map((t) => t.id) ?? []
  )
  const [contentRating, setContentRating] = useState(editingCharacter?.content_rating ?? 'limited')

  // Behaviors & Definitions
  const [personaPrompt, setPersonaPrompt] = useState(editingCharacter?.persona_prompt ?? '')
  const [scenario, setScenario] = useState(editingCharacter?.scenario ?? '')
  const [firstMes, setFirstMes] = useState(editingCharacter?.first_mes ?? '')
  const [altGreetings, setAltGreetings] = useState<string[]>(
    editingCharacter?.alternate_greetings ?? []
  )
  const [mesExample, setMesExample] = useState(editingCharacter?.mes_example ?? '')

  // UI States
  const [activeTab, setActiveTab] = useState<'general' | 'definition' | 'preview'>('general')
  const [isSaving, setIsSaving] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(
    editingCharacter?.avatar_url ?? null
  )
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [importStatus, setImportStatus] = useState<string | null>(null)
  const [importError, setImportError] = useState<string | null>(null)

  // Token counters
  const [tokens, setTokens] = useState({
    personality: 0,
    scenario: 0,
    first_mes: 0,
    mes_example: 0
  })

  // Macro insertion: track the last-focused definition field so the {{char}} /
  // {{user}} buttons insert at the caret of whichever field the user was in.
  const activeFieldRef = useRef<HTMLTextAreaElement | null>(null)
  const activeFieldKeyRef = useRef<string | null>(null)

  const setFieldValue = (key: string, value: string) => {
    if (key === 'persona') setPersonaPrompt(value)
    else if (key === 'scenario') setScenario(value)
    else if (key === 'firstMes') setFirstMes(value)
    else if (key === 'mesExample') setMesExample(value)
    else if (key.startsWith('alt-')) {
      const i = Number(key.slice(4))
      setAltGreetings((prev) => prev.map((g, idx) => (idx === i ? value : g)))
    }
  }

  const registerField = (key: string) => ({
    onFocus: (e: React.FocusEvent<HTMLTextAreaElement>) => {
      activeFieldRef.current = e.target
      activeFieldKeyRef.current = key
    }
  })

  const insertMacro = (macro: string) => {
    const el = activeFieldRef.current
    const key = activeFieldKeyRef.current
    if (!el || !key) return
    const start = el.selectionStart ?? el.value.length
    const end = el.selectionEnd ?? el.value.length
    const next = el.value.slice(0, start) + macro + el.value.slice(end)
    setFieldValue(key, next)
    requestAnimationFrame(() => {
      el.focus()
      const pos = start + macro.length
      el.setSelectionRange(pos, pos)
    })
  }

  // Debounced token calculation helper
  const estimateTokens = (text: string): number => {
    if (!text) return 0
    return Math.ceil(text.trim().split(/\s+/).filter(Boolean).length * WORDS_TO_TOKENS_RATIO)
  }

  const queryTokenCount = async (text: string): Promise<number> => {
    if (!text.trim()) return 0
    try {
      const resp = await fetch('/settings/tokenize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      if (resp.ok) {
        const data = await resp.json()
        return data.tokens
      }
    } catch {
      // ignore
    }
    return estimateTokens(text)
  }

  useEffect(() => {
    const handler = setTimeout(async () => {
      const pTokens = await queryTokenCount(personaPrompt)
      const sTokens = await queryTokenCount(scenario)
      const fTokens = await queryTokenCount(firstMes)
      const mTokens = await queryTokenCount(mesExample)
      setTokens({
        personality: pTokens,
        scenario: sTokens,
        first_mes: fTokens,
        mes_example: mTokens
      })
    }, 500)

    // Set estimates immediately
    setTokens({
      personality: estimateTokens(personaPrompt),
      scenario: estimateTokens(scenario),
      first_mes: estimateTokens(firstMes),
      mes_example: estimateTokens(mesExample)
    })

    return () => clearTimeout(handler)
  }, [personaPrompt, scenario, firstMes, mesExample])

  const totalTokens = tokens.personality + tokens.scenario + tokens.first_mes + tokens.mes_example
  const permanentTokens = tokens.personality + tokens.scenario + tokens.mes_example

  const greetingCount = (firstMes.trim() ? 1 : 0) + altGreetings.length

  const addGreeting = () => {
    if (greetingCount >= MAX_GREETINGS) return
    setAltGreetings((prev) => [...prev, ''])
  }
  const removeGreeting = (i: number) => setAltGreetings((prev) => prev.filter((_, idx) => idx !== i))
  const moveGreeting = (i: number, dir: -1 | 1) => {
    setAltGreetings((prev) => {
      const j = i + dir
      if (j < 0 || j >= prev.length) return prev
      const next = [...prev]
      ;[next[i], next[j]] = [next[j], next[i]]
      return next
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    const payload: CharacterFormData = {
      name,
      description: description || shortDescription,
      nickname,
      short_description: shortDescription || description,
      persona_prompt: personaPrompt,
      scenario,
      first_mes: firstMes,
      alternate_greetings: altGreetings.map((g) => g.trim()).filter(Boolean),
      mes_example: mesExample,
      content_rating: contentRating,
      tagIds: selectedTagIds,
      avatarFile
    }

    if (isEditing && editingCharacter) {
      await onUpdate(editingCharacter.id, payload)
    } else {
      await onCreate(payload)
    }
    setIsSaving(false)
  }

  const handleFileChange = async (file: File) => {
    setAvatarFile(file)
    setAvatarPreview(URL.createObjectURL(file))
    setImportStatus(null)
    setImportError(null)

    // Attempt to parse Tavern PNG V2/V3 card metadata
    if (file.type === 'image/png') {
      setImportStatus('Analyzing character card...')
      try {
        const formData = new FormData()
        formData.append('file', file)
        const resp = await fetch('/characters/parse-png', {
          method: 'POST',
          body: formData
        })
        if (resp.ok) {
          const card = await resp.json()
          setName(card.name || '')
          setNickname(card.name || '')
          setDescription(card.description || '')
          setShortDescription(card.description || '')
          setPersonaPrompt(card.personality || '')
          setScenario(card.scenario || '')
          setFirstMes(card.first_mes || '')
          setAltGreetings(Array.isArray(card.alternate_greetings) ? card.alternate_greetings : [])
          setMesExample(card.mes_example || '')
          setImportStatus('Imported character card.')
        } else {
          // No embedded card (a plain image) is fine -- it's just the avatar.
          setImportStatus(null)
          if (resp.status !== 422) {
            setImportError('Could not read card metadata; using the image as the avatar only.')
          }
        }
      } catch {
        setImportStatus(null)
        setImportError('Failed to read the character card from this image.')
      }
    }
  }

  const toggleTag = (tagId: number) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    )
  }

  const displayName = nickname || name || 'Character'
  const previewGreetings = [firstMes, ...altGreetings].filter((g) => g.trim())

  const MacroToolbar = () => (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="font-label-sm text-body-xs text-[#71717A]">Insert macro:</span>
      <button
        type="button"
        onClick={() => insertMacro('{{char}}')}
        className="font-mono text-body-xs text-primary bg-white/5 border border-white/10 rounded px-2 py-0.5 hover:bg-white/10 transition-colors"
      >
        {'{{char}}'}
      </button>
      <button
        type="button"
        onClick={() => insertMacro('{{user}}')}
        className="font-mono text-body-xs text-primary bg-white/5 border border-white/10 rounded px-2 py-0.5 hover:bg-white/10 transition-colors"
      >
        {'{{user}}'}
      </button>
      <span className="font-body-sm text-body-xs text-on-surface-variant/60">
        resolved to the character &amp; your name at chat time
      </span>
    </div>
  )

  return (
    <div className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md">
      <div className="w-full max-w-[800px] rounded-[1.5rem] bg-[#111111] border border-[#1A1A1A] p-lg md:p-xl flex flex-col gap-md z-50 animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">

        {/* Modal Header */}
        <div className="flex justify-between items-start w-full border-b border-[#1A1A1A] pb-md">
          <div className="flex flex-col gap-xs">
            <h2 className="font-heading-lg text-heading-lg text-primary tracking-tight">
              {isEditing ? 'Edit Character' : 'Create Character'}
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Set up how your character looks, speaks, and behaves in chat.</p>
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

        {/* Tabs Controller */}
        <div className="flex gap-md border-b border-[#1A1A1A]">
          {(['general', 'definition', 'preview'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`pb-xs px-xs font-heading-sm text-body-lg transition-colors border-b-2 ${
                activeTab === tab
                  ? 'text-primary border-primary'
                  : 'text-on-surface-variant border-transparent hover:text-primary'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tabs Content */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-lg w-full">
          {activeTab === 'general' && (
            <div className="grid md:grid-cols-[200px_1fr] gap-lg">

              {/* Image / Card upload area */}
              <div className="flex flex-col gap-xs">
                <label className="font-label-sm text-label-sm text-[#71717A] uppercase">Image Avatar *</label>
                <div
                  onDragOver={(e) => {
                    e.preventDefault()
                    setIsDragging(true)
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault()
                    setIsDragging(false)
                    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                      handleFileChange(e.dataTransfer.files[0])
                    }
                  }}
                  className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-[1rem] aspect-square overflow-hidden cursor-pointer transition-all ${
                    isDragging
                      ? 'border-primary bg-primary/5'
                      : 'border-[#1A1A1A] hover:border-primary/55 bg-transparent'
                  }`}
                  onClick={() => document.getElementById('avatar-input')?.click()}
                >
                  {avatarPreview ? (
                    <img src={avatarPreview} alt="Avatar Preview" className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex flex-col items-center gap-xs p-xs text-center">
                      <span className="material-symbols-outlined text-[32px] text-[#71717A]">image</span>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">Drag image here or click</p>
                    </div>
                  )}
                  <input
                    id="avatar-input"
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileChange(e.target.files[0])
                      }
                    }}
                    className="hidden"
                  />
                </div>
                <p className="font-body-sm text-body-xs text-[#71717A] leading-tight pt-xs">
                  Supports Tavern PNG character cards, parsing specifications automatically.
                </p>
                {importStatus && (
                  <p className="font-body-sm text-body-xs text-primary font-medium mt-xs">{importStatus}</p>
                )}
                {importError && (
                  <p className="font-body-sm text-body-xs text-red-400 font-medium mt-xs">{importError}</p>
                )}
              </div>

              {/* General Fields */}
              <div className="flex flex-col gap-md">
                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_name">Title / Name *</label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="input-premium w-full font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30"
                    id="char_name"
                    placeholder="A unique title for your character"
                    type="text"
                    required
                  />
                </div>

                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_nickname">Chat Name</label>
                  <input
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30"
                    id="char_nickname"
                    placeholder="Optional display name shown in chats"
                    type="text"
                  />
                </div>

                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_description">Bio *</label>
                  <textarea
                    value={description}
                    onChange={(e) => {
                      setDescription(e.target.value)
                      setShortDescription(e.target.value)
                    }}
                    className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                    id="char_description"
                    placeholder="Provide a short description / bio summary..."
                    rows={3}
                    required
                  />
                </div>

                {/* Content Rating toggler (neutral labels, not consumer SFW/NSFW gating) */}
                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase">Content Rating</label>
                  <div className="flex gap-md pt-xs">
                    <label className="flex items-center gap-xs cursor-pointer">
                      <input
                        type="radio"
                        name="rating"
                        value="limited"
                        checked={contentRating === 'limited'}
                        onChange={() => setContentRating('limited')}
                        className="accent-primary"
                      />
                      <span className="font-body-md text-body-md text-primary">General</span>
                    </label>
                    <label className="flex items-center gap-xs cursor-pointer">
                      <input
                        type="radio"
                        name="rating"
                        value="limitless"
                        checked={contentRating === 'limitless'}
                        onChange={() => setContentRating('limitless')}
                        className="accent-primary"
                      />
                      <span className="font-body-md text-body-md text-primary">Mature</span>
                    </label>
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-col gap-xs pt-xs">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase">Tags</label>
                  {tags.length === 0 ? (
                    <p className="font-body-sm text-body-sm text-on-surface-variant/50">No tags available. Create tags in Archives.</p>
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
                              : 'bg-transparent text-on-surface-variant border-outline hover:border-primary hover:text-primary'
                          }`}
                        >
                          {tag.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            </div>
          )}

          {activeTab === 'definition' && (
            <div className="flex flex-col gap-md">

              {/* Macro helper toolbar */}
              <div className="bg-[#151515] border border-[#252525] rounded-[0.5rem] p-sm">
                <MacroToolbar />
              </div>

              {/* Definition block fields */}
              <div className="flex flex-col gap-xs">
                <div className="flex justify-between items-center">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_personality">Personality *</label>
                  <span className="font-label-sm text-label-sm text-[#71717A]">{tokens.personality} tokens</span>
                </div>
                <textarea
                  value={personaPrompt}
                  onChange={(e) => setPersonaPrompt(e.target.value)}
                  {...registerField('persona')}
                  className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                  id="char_personality"
                  placeholder="Describe your character's persona. This will define how they interact with others..."
                  rows={4}
                  required
                />
              </div>

              <div className="flex flex-col gap-xs">
                <div className="flex justify-between items-center">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_scenario">Scenario</label>
                  <span className="font-label-sm text-label-sm text-[#71717A]">{tokens.scenario} tokens</span>
                </div>
                <textarea
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  {...registerField('scenario')}
                  className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                  id="char_scenario"
                  placeholder="Outline the context, conversation setting and circumstances..."
                  rows={2}
                />
              </div>

              {/* Greetings: primary first message + alternates (chat-start picker) */}
              <div className="flex flex-col gap-xs">
                <div className="flex justify-between items-center">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_first_mes">Initial messages (first messages) *</label>
                  <span className="font-label-sm text-label-sm text-[#71717A]">{greetingCount}/{MAX_GREETINGS} · {tokens.first_mes} tokens</span>
                </div>
                <textarea
                  value={firstMes}
                  onChange={(e) => setFirstMes(e.target.value)}
                  {...registerField('firstMes')}
                  className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                  id="char_first_mes"
                  placeholder="The first message from your character. Make it lengthy to prime long replies..."
                  rows={3}
                  required
                />

                {/* Alternate greetings */}
                {altGreetings.map((g, i) => (
                  <div key={i} className="flex flex-col gap-1 border-l-2 border-[#252525] pl-sm mt-1">
                    <div className="flex justify-between items-center">
                      <span className="font-label-sm text-body-xs text-[#71717A] uppercase">Alternate greeting {i + 2}</span>
                      <div className="flex items-center gap-1">
                        <button type="button" onClick={() => moveGreeting(i, -1)} disabled={i === 0} title="Move up"
                          className="text-[#71717A] hover:text-primary disabled:opacity-30 transition-colors">
                          <span className="material-symbols-outlined text-[16px]">arrow_upward</span>
                        </button>
                        <button type="button" onClick={() => moveGreeting(i, 1)} disabled={i === altGreetings.length - 1} title="Move down"
                          className="text-[#71717A] hover:text-primary disabled:opacity-30 transition-colors">
                          <span className="material-symbols-outlined text-[16px]">arrow_downward</span>
                        </button>
                        <button type="button" onClick={() => removeGreeting(i)} title="Remove greeting"
                          className="text-[#71717A] hover:text-red-400 transition-colors">
                          <span className="material-symbols-outlined text-[16px]">delete</span>
                        </button>
                      </div>
                    </div>
                    <textarea
                      value={g}
                      onChange={(e) => setFieldValue(`alt-${i}`, e.target.value)}
                      {...registerField(`alt-${i}`)}
                      className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
                      placeholder="Another opening message the user can pick when starting a chat..."
                      rows={2}
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addGreeting}
                  disabled={greetingCount >= MAX_GREETINGS}
                  className="self-start mt-1 font-body-sm text-body-xs text-primary hover:text-on-surface flex items-center gap-1 disabled:opacity-40 transition-colors"
                >
                  <span className="material-symbols-outlined text-[16px]">add</span>
                  Add alternate greeting
                </button>
              </div>

              <div className="flex flex-col gap-xs">
                <div className="flex justify-between items-center">
                  <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="char_mes_example">Example dialogs</label>
                  <span className="font-label-sm text-label-sm text-[#71717A]">{tokens.mes_example} tokens</span>
                </div>
                <textarea
                  value={mesExample}
                  onChange={(e) => setMesExample(e.target.value)}
                  {...registerField('mesExample')}
                  className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 font-mono resize-none"
                  id="char_mes_example"
                  placeholder={`Provide example conversations:\n{{char}}: Hey, im Mark\n{{user}}: hello Mark\n{{char}}: nice to meet you :)`}
                  rows={4}
                />
              </div>

              {/* Combined Token budget alerts */}
              <div className="bg-[#151515] border border-[#252525] rounded-[0.5rem] p-md flex gap-md justify-between items-center mt-xs">
                <div className="flex flex-col">
                  <span className="font-label-sm text-body-md text-[#71717A] uppercase">Prompt token statistics</span>
                  <p className="font-body-sm text-body-xs text-on-surface-variant leading-tight">Estimates based on current active model context window.</p>
                </div>
                <div className="flex gap-lg">
                  <div className="flex flex-col text-right">
                    <span className="font-heading-sm text-[#71717A] uppercase text-body-xs">Total Tokens</span>
                    <span className="font-body-md text-body-lg text-primary font-bold">{totalTokens}</span>
                  </div>
                  <div className="flex flex-col text-right">
                    <span className="font-heading-sm text-[#71717A] uppercase text-body-xs">Permanent</span>
                    <span className="font-body-md text-body-lg text-primary font-bold">{permanentTokens}</span>
                  </div>
                </div>
              </div>

            </div>
          )}

          {activeTab === 'preview' && (
            <div className="flex flex-col gap-md">
              <p className="font-body-sm text-body-xs text-on-surface-variant">
                Live preview of the assembled card. Macros are resolved with a sample user named "User".
              </p>
              <div className="bg-[#0D0D0D] border border-[#1A1A1A] rounded-[0.75rem] p-md flex flex-col gap-md">
                <div className="flex items-center gap-md">
                  {avatarPreview && (
                    <img src={avatarPreview} alt="" className="w-14 h-14 rounded-full object-cover border border-[#1A1A1A]" />
                  )}
                  <div className="flex flex-col">
                    <span className="font-heading-md text-body-lg text-primary font-bold">{displayName || 'Untitled'}</span>
                    <span className="font-body-sm text-body-xs text-on-surface-variant">{description || 'No bio yet.'}</span>
                  </div>
                </div>

                {personaPrompt && (
                  <div className="flex flex-col gap-1">
                    <span className="font-label-sm text-body-xs text-[#71717A] uppercase">Personality</span>
                    <p className="font-body-sm text-body-sm text-on-surface whitespace-pre-wrap">{renderMacros(personaPrompt, displayName)}</p>
                  </div>
                )}
                {scenario && (
                  <div className="flex flex-col gap-1">
                    <span className="font-label-sm text-body-xs text-[#71717A] uppercase">Scenario</span>
                    <p className="font-body-sm text-body-sm text-on-surface whitespace-pre-wrap">{renderMacros(scenario, displayName)}</p>
                  </div>
                )}

                <div className="flex flex-col gap-1">
                  <span className="font-label-sm text-body-xs text-[#71717A] uppercase">Greetings ({previewGreetings.length})</span>
                  {previewGreetings.length === 0 ? (
                    <p className="font-body-sm text-body-xs text-on-surface-variant/50">No greeting yet.</p>
                  ) : (
                    previewGreetings.map((g, i) => (
                      <div key={i} className="border-l-2 border-[#252525] pl-sm py-1">
                        <span className="font-label-sm text-[10px] text-[#71717A] uppercase">#{i + 1}</span>
                        <p className="font-body-sm text-body-sm text-on-surface whitespace-pre-wrap">{renderMacros(g, displayName)}</p>
                      </div>
                    ))
                  )}
                </div>

                {mesExample && (
                  <div className="flex flex-col gap-1">
                    <span className="font-label-sm text-body-xs text-[#71717A] uppercase">Example dialogs</span>
                    <pre className="font-mono text-body-xs text-on-surface whitespace-pre-wrap">{renderMacros(mesExample, displayName)}</pre>
                  </div>
                )}

                {selectedTagIds.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {tags.filter((t) => selectedTagIds.includes(t.id)).map((t) => (
                      <span key={t.id} className="px-2 py-0.5 rounded-sm border border-outline text-label-sm text-on-surface-variant">{t.label}</span>
                    ))}
                  </div>
                )}

                <div className="flex gap-lg border-t border-[#1A1A1A] pt-sm">
                  <span className="font-body-sm text-body-xs text-[#71717A]">Total: <span className="text-primary font-bold">{totalTokens}</span> tokens</span>
                  <span className="font-body-sm text-body-xs text-[#71717A]">Permanent: <span className="text-primary font-bold">{permanentTokens}</span> tokens</span>
                </div>
              </div>
            </div>
          )}

          {/* Footer controllers */}
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
