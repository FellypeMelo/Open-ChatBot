import type { MessageNode } from '../hooks/useMessageTree'

// --- Shared request helpers -------------------------------------------------
// Every endpoint below is the same shape: fetch, throw a labelled Error on a
// non-OK response, then return the parsed body. These three helpers hold that
// shape in one place so each endpoint is a single line.

// A dropped/dead LAN socket otherwise hangs a plain fetch() until the OS TCP
// timeout (can be minutes); every REST call below gets this default so a
// spinner fails fast into a retryable error instead. Streaming (/chat/stream)
// is intentionally excluded -- it manages its own idle timeout in App.tsx
// since a generation can legitimately run far longer than this.
const DEFAULT_TIMEOUT_MS = 15000

const jsonInit = (method: string, data: unknown): RequestInit => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})

// Merge in a default timeout signal unless the caller already supplied one.
const withTimeout = (init?: RequestInit): RequestInit => ({
  ...init,
  signal: init?.signal ?? AbortSignal.timeout(DEFAULT_TIMEOUT_MS)
})

const request = async <T = unknown>(url: string, errorMessage: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(url, withTimeout(init))
  if (!response.ok) throw new Error(errorMessage)
  return response.json() as Promise<T>
}

// For endpoints that only signal success/failure (DELETEs) rather than a body.
const requestOk = async (url: string, errorMessage: string, init: RequestInit): Promise<boolean> => {
  const response = await fetch(url, withTimeout(init))
  if (!response.ok) throw new Error(errorMessage)
  return response.ok
}

export const fetchUser = async () => request<User>('/users/me', 'Failed to fetch user')

export const fetchCharacters = async () => request<Character[]>('/characters/', 'Failed to fetch characters')

export const fetchTags = async () => request<Tag[]>('/tags/', 'Failed to fetch tags')

export const fetchHistory = async (charId: number, chatId?: number) => {
  const qs = chatId != null ? `?chat_id=${chatId}` : ''
  return request<MessageNode[]>(`/history/${charId}${qs}`, 'Failed to fetch history')
}

export interface ChatSession {
  id: number
  title: string
  is_archived: boolean
  is_active: boolean
  message_count: number
  created_at?: string
  updated_at?: string
}

export const fetchChats = async (charId: number): Promise<ChatSession[]> => {
  const data = await request<ChatSession[]>(`/chats/${charId}`, 'Failed to fetch chats')
  return Array.isArray(data) ? data : []
}

export const newChat = async (charId: number, greetingIndex?: number): Promise<{ chat_id: number; title: string }> => {
  const init = greetingIndex != null
    ? jsonInit('POST', { greeting_index: greetingIndex })
    : { method: 'POST' }
  return request(`/chat/new/${charId}`, 'Failed to start a new chat', init)
}

export const updateChat = async (chatId: number, data: { title?: string; is_archived?: boolean }) =>
  request(`/chat/${chatId}`, 'Failed to update chat', jsonInit('PUT', data))

export const deleteChat = async (chatId: number) =>
  request(`/chat/${chatId}`, 'Failed to delete chat', { method: 'DELETE' })

export interface ActionInfo {
  id: string
  name: string
  icon: string
  message: string
  deltas: Record<string, number>
}

// Single-sourced from the backend's ACTIONS_CONFIG (src/backend/api/chat.py)
// so neither the optimistic-UI placeholder text nor a quick-action button's
// name/icon/effect label can ever drift from what the server actually applies.
export const fetchActions = async (): Promise<Record<string, ActionInfo>> =>
  request('/chat/actions', 'Failed to fetch actions')

export const updateUser = async (name: string, gender: string, persona_description?: string, appearance?: string) =>
  request<User>('/users/me', 'Failed to update user', jsonInit('POST', { name, gender, persona_description, appearance }))

export const createTag = async (label: string, instruction: string) =>
  request<Tag>('/tags/', 'Failed to create tag', jsonInit('POST', { label, instruction }))

export const updateTag = async (id: number, label: string, instruction: string) =>
  request<Tag>(`/tags/${id}`, 'Failed to update tag', jsonInit('PUT', { label, instruction }))

export const deleteTag = async (id: number) =>
  requestOk(`/tags/${id}`, 'Failed to delete tag', { method: 'DELETE' })

export interface CharacterInput {
  name: string
  description: string
  nickname?: string
  short_description?: string
  persona_prompt?: string
  scenario?: string
  first_mes?: string
  alternate_greetings?: string[]
  mes_example?: string
  content_rating?: string
  dynamic_persona?: boolean
  tag_ids: number[]
  compress_backstory: boolean
}

export const createCharacter = async (data: CharacterInput): Promise<Character> =>
  request<Character>('/characters/', 'Failed to create character', jsonInit('POST', data))

export const importCharacterPng = async (file: File): Promise<Character> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/characters/import-png', {
    method: 'POST',
    body: formData,
    signal: AbortSignal.timeout(DEFAULT_TIMEOUT_MS)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to import character');
  }
  return response.json();
};

export const updateCharacter = async (id: number, data: CharacterInput): Promise<Character> =>
  request<Character>(`/characters/${id}`, 'Failed to update character', jsonInit('PUT', data))

export const deleteCharacter = async (id: number) =>
  requestOk(`/characters/${id}`, 'Failed to delete character', { method: 'DELETE' })

export interface LLMConfig {
  base_url?: string;
  model_name?: string;
  preset_id?: number;
}

export interface Tag {
  id: number;
  label: string;
  instruction: string;
}

export interface User {
  id: number;
  name: string;
  gender: string;
  is_active: boolean;
  persona_description?: string;
  appearance?: string;
}

export interface CharacterStats {
  energy: number;
  hunger: number;
  happiness?: number;
  social?: number;
  is_sleeping?: boolean;
  relationship: {
    score: number;
  };
}

export interface CharacterState {
  location: string;
  mood: string;
  clothes: string;
  interaction_count: number;
  stats: CharacterStats;
}

export interface Character {
  id: number;
  name: string;
  description: string;
  nickname?: string;
  short_description?: string;
  persona_prompt?: string;
  scenario?: string;
  first_mes?: string;
  alternate_greetings?: string[];
  mes_example?: string;
  content_rating?: string;
  dynamic_persona?: boolean;
  is_active: boolean;
  tags: Tag[];
  state?: CharacterState;
  avatar_url?: string;
}

export interface SamplerPreset {
  id: number;
  name: string;
  is_default: boolean;
  temperature: number;
  min_p: number;
  top_k: number;
  top_p: number;
  repeat_penalty: number;
  dry_multiplier: number;
  dry_base: number;
  dry_range: number;
  xtc_threshold: number;
  xtc_probability: number;
}

export const fetchPresets = async (): Promise<SamplerPreset[]> =>
  request<SamplerPreset[]>('/presets/', 'Failed to fetch presets')

export const createPreset = async (preset: Omit<SamplerPreset, 'id'>) =>
  request('/presets/', 'Failed to create preset', jsonInit('POST', preset))

export const updatePreset = async (id: number, preset: Omit<SamplerPreset, 'id'>) =>
  request(`/presets/${id}`, 'Failed to update preset', jsonInit('PUT', preset))

export const deletePreset = async (id: number) =>
  requestOk(`/presets/${id}`, 'Failed to delete preset', { method: 'DELETE' })

// No default timeout here -- a generation can legitimately run far longer
// than the 15s REST default. Callers that want to abort a hung/slow stream
// (App.tsx's idle-timeout + Stop button) pass their own AbortSignal instead.
export const sendMessageStream = async (message: string | null, characterId: number, parentId: number | null, config?: LLMConfig, actionId?: string, chatId?: number, signal?: AbortSignal) => {
  const response = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, character_id: characterId, parent_id: parentId, chat_id: chatId, config, action_id: actionId }),
    signal
  })
  if (!response.ok) throw new Error('Failed to start stream')
  return response
}

export const fetchLore = async () => request('/lore/', 'Failed to fetch lore')

export const createLore = async (keyword: string, content: string, characterId?: number, isGlobal: boolean = false) =>
  request('/lore/', 'Failed to create lore', jsonInit('POST', { keyword, content, character_id: characterId, is_global: isGlobal }))

export const deleteLore = async (id: number) =>
  requestOk(`/lore/${id}`, 'Failed to delete lore', { method: 'DELETE' })

export interface LlamaServerConfig {
  binary_path: string;
  model_path: string;
  port: number;
  threads: number;
  gpu_layers: number;
  context_size: number;
  additional_args: string;
}

export interface RunnerStatus {
  inference: {
    running: boolean;
    config: LlamaServerConfig;
  };
  embedding: {
    running: boolean;
    config: LlamaServerConfig;
  };
  available_models: string[];
  available_binaries: string[];
}

export const fetchRunnerStatus = async (): Promise<RunnerStatus> =>
  request<RunnerStatus>('/settings/status', 'Failed to fetch runner status')

export const saveRunnerConfig = async (config: { inference: LlamaServerConfig; embedding: LlamaServerConfig }) =>
  request('/settings/save', 'Failed to save runner configuration', jsonInit('POST', config))

export const startServer = async (type: 'inference' | 'embedding') =>
  request(`/settings/start/${type}`, `Failed to start ${type} server`, { method: 'POST' })

export const stopServer = async (type: 'inference' | 'embedding') =>
  request(`/settings/stop/${type}`, `Failed to stop ${type} server`, { method: 'POST' })

export const restartAllServers = async () =>
  request('/settings/restart-all', 'Failed to restart servers', { method: 'POST' })

export const updateCharacterState = async (charId: number, stateUpdate: Record<string, unknown>) =>
  request<Character>(`/characters/${charId}/state`, 'Failed to update character state', jsonInit('PUT', stateUpdate))

export const clearChatHistory = async (characterId: number) =>
  request(`/chat/clear/${characterId}`, 'Failed to clear chat history', { method: 'POST' })

export const editMessage = async (messageId: number, content: string) =>
  request(`/chat/message/${messageId}`, 'Failed to edit message', jsonInit('PUT', { content }))

export const deleteMessage = async (messageId: number) =>
  request(`/chat/message/${messageId}`, 'Failed to delete message', { method: 'DELETE' })

export interface JournalEntry {
  id: number;
  timestamp: string;
  content: string;
  summary: string;
  mood_at_time: string;
  relationship_score: number;
  energy_level: number;
}

export const fetchJournal = async (characterId: number): Promise<JournalEntry[]> =>
  request<JournalEntry[]>(`/characters/${characterId}/journal`, 'Failed to fetch journal entries')
