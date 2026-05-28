export const fetchUser = async () => {
  const response = await fetch('/users/me')
  if (!response.ok) throw new Error('Failed to fetch user')
  return response.json()
}

export const fetchCharacters = async () => {
  const response = await fetch('/characters/')
  if (!response.ok) throw new Error('Failed to fetch characters')
  return response.json()
}

export const fetchTags = async () => {
  const response = await fetch('/tags/')
  if (!response.ok) throw new Error('Failed to fetch tags')
  return response.json()
}

export const fetchHistory = async (charId: number) => {
  const response = await fetch(`/history/${charId}`)
  if (!response.ok) throw new Error('Failed to fetch history')
  return response.json()
}

export const updateUser = async (name: string, gender: string) => {
  const response = await fetch('/users/me', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, gender })
  })
  if (!response.ok) throw new Error('Failed to update user')
  return response.json()
}

export const createTag = async (label: string, instruction: string) => {
  const response = await fetch('/tags/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label, instruction })
  })
  if (!response.ok) throw new Error('Failed to create tag')
  return response.json()
}

export const updateTag = async (id: number, label: string, instruction: string) => {
  const response = await fetch(`/tags/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label, instruction })
  })
  if (!response.ok) throw new Error('Failed to update tag')
  return response.json()
}

export const deleteTag = async (id: number) => {
  const response = await fetch(`/tags/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete tag')
  return response.ok
}

export const createCharacter = async (name: string, description: string, tagIds: number[]) => {
  const response = await fetch('/characters/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, tag_ids: tagIds })
  })
  if (!response.ok) throw new Error('Failed to create character')
  return response.json()
}

export const updateCharacter = async (id: number, name: string, description: string, tagIds: number[]) => {
  const response = await fetch(`/characters/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, tag_ids: tagIds })
  })
  if (!response.ok) throw new Error('Failed to update character')
  return response.json()
}

export const deleteCharacter = async (id: number) => {
  const response = await fetch(`/characters/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete character')
  return response.ok
}

export interface LLMConfig {
  base_url?: string;
  model_name?: string;
}

export const sendMessage = async (message: string | null, characterId: number, parentId: number | null, config?: LLMConfig) => {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, character_id: characterId, parent_id: parentId, config })
  })
  if (!response.ok) throw new Error('Failed to send message')
  return response.json()
}

export const sendMessageStream = async (message: string | null, characterId: number, parentId: number | null, config?: LLMConfig) => {
  const response = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, character_id: characterId, parent_id: parentId, config })
  })
  if (!response.ok) throw new Error('Failed to start stream')
  return response
}

export const fetchLore = async () => {
  const response = await fetch('/lore/')
  if (!response.ok) throw new Error('Failed to fetch lore')
  return response.json()
}

export const createLore = async (keyword: string, content: string, characterId?: number, isGlobal: boolean = false) => {
  const response = await fetch('/lore/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, content, character_id: characterId, is_global: isGlobal })
  })
  if (!response.ok) throw new Error('Failed to create lore')
  return response.json()
}

export const deleteLore = async (id: number) => {
  const response = await fetch(`/lore/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete lore')
  return response.ok
}
