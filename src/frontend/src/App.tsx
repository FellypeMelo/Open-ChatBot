import { useState, useEffect, useCallback, useRef } from 'react'
import Icon from './components/Icon'
import IconButton from './components/IconButton'
import Sidebar from './components/Sidebar'
import MobileTabBar from './components/MobileTabBar'
import CharactersView from './components/CharactersView'
import ChatView from './components/ChatView'
import TagManagementView from './components/TagManagementView'
import LorebookView from './components/LorebookView'
import CharacterCreator from './components/CharacterCreator'
import UserProfileModal from './components/UserProfileModal'
import SettingsModal from './components/SettingsModal'
import TagCreator from './components/TagCreator'
import ErrorBoundary from './components/ErrorBoundary'
import * as api from './services/api'
import type { MessageNode } from './hooks/useMessageTree'
import type { Character, CharacterInput, CharacterState, Tag, User } from './services/api'
import type { CharacterFormData } from './components/CharacterCreator'
import { useSettings } from './hooks/useSettings'
import { useIsMobile } from './hooks/useIsMobile'
import { useConfirm } from './hooks/useConfirm'

type View = 'chat' | 'characters' | 'archives' | 'library'
type ModalType = 'character' | 'user' | 'tag' | 'settings' | null

interface Toast {
  message: string
  type: 'success' | 'error'
  // Skips the auto-dismiss timer -- for connection-class errors the user
  // must act on (dismiss or retry), not glance past in 3s.
  persistent?: boolean
  // Present only on toasts offering a real retry of the action that failed.
  // Re-invoked (then the toast is dismissed) by the toast's Retry control.
  onRetry?: () => void
}

// Optimistic client-side message ids: a large random offset plus the epoch ms
// keeps them unique and above any server id until the real history reloads.
const TEMP_ID_RANGE = 1000000
const TOAST_DURATION_MS = 3000

// No token for this long during a stream -> treat the connection as dead and
// abort. Generous and reset on every token (not a hard total cap) so a slow
// first-token on a cold/loaded model isn't mistaken for a dropped Wi-Fi link.
// Sized for a slow self-hosted llama-server on modest hardware (CPU/iGPU),
// where the first token after a cold prompt can legitimately take well over a
// minute. The timer is ALSO reset the moment the response headers arrive (see
// runStream), so slow backend pre-work -- RAG embedding, prompt assembly --
// never eats into this first-token budget.
const STREAM_IDLE_TIMEOUT_MS = 120000

// Thrown from inside the SSE event handler when the backend's `error_stream`/
// mid-generation error event fires, so runStream's catch can distinguish a
// server-reported failure from a dropped connection or a client-side abort.
class StreamError extends Error {}

const generateMessageId = () => Math.floor(Math.random() * TEMP_ID_RANGE) + Date.now();

// Map the creator form shape to the API payload (tagIds -> tag_ids, drop the file).
const toCharacterPayload = (data: CharacterFormData): CharacterInput => ({
  name: data.name,
  description: data.description,
  nickname: data.nickname,
  short_description: data.short_description,
  persona_prompt: data.persona_prompt,
  scenario: data.scenario,
  first_mes: data.first_mes,
  alternate_greetings: data.alternate_greetings,
  mes_example: data.mes_example,
  content_rating: data.content_rating,
  dynamic_persona: data.dynamic_persona,
  tag_ids: data.tagIds,
  compress_backstory: false
})

// Upload an avatar for a saved character; returns the new URL or null on failure.
const uploadAvatar = async (characterId: number, file: File): Promise<string | null> => {
  const formData = new FormData()
  formData.append('file', file)
  const resp = await fetch(`/characters/${characterId}/avatar`, { method: 'POST', body: formData })
  if (!resp.ok) return null
  const result = await resp.json()
  return result.avatar_url ?? null
}

function App() {
  const { config } = useSettings()
  const [currentView, setCurrentView] = useState<View>('characters')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const isMobile = useIsMobile()
  // Mobile immersive reading: driven by ChatView's scroll direction. When true
  // the app top bar and bottom tab bar collapse so the transcript owns nearly
  // the whole phone screen; restored on a deliberate upward scroll.
  const [immersive, setImmersive] = useState(false)
  const [activeModal, setActiveModal] = useState<ModalType>(null)
  const [toast, setToast] = useState<Toast | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null)
  const [chats, setChats] = useState<api.ChatSession[]>([])
  const [activeChatId, setActiveChatId] = useState<number | null>(null)
  const [messages, setMessages] = useState<MessageNode[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [actionsConfig, setActionsConfig] = useState<Record<string, api.ActionInfo>>({})
  const { confirm, dialog } = useConfirm()
  // Holds the in-flight stream's AbortController so a Stop action or an idle
  // timeout can cancel it; cleared once the stream settles.
  const streamAbortRef = useRef<AbortController | null>(null)
  // Length of the assistant reply streamed so far this turn, updated
  // synchronously per token. Read by reconcileInterruptedStream (which runs in
  // the abort path, before React has flushed the committed partial into
  // `messages`) to know whether the interrupted turn left a non-empty partial
  // that the server must have persisted before we swap its history in.
  const streamedLenRef = useRef(0)
  // The in-flight assistant reply's accumulated text, updated once per SSE
  // token. Kept OUTSIDE `messages` so a token never triggers a new `messages`
  // array reference -- ChatView's useMessageTree would otherwise rebuild its
  // childrenMap/activePath (and re-render every message row) on every single
  // token. Committed into `messages` exactly once (on done/error/cancel).
  const [streamingContent, setStreamingContent] = useState<string | null>(null)
  // The id of the assistant placeholder `streamingContent` belongs to. This
  // is the load-bearing piece that scopes the single global streaming buffer
  // to a specific node: ChatView only ever renders `streamingContent` for
  // the message whose id matches this, so swiping to a different (already
  // finished) sibling variant mid-stream -- or switching character/chat,
  // which swaps `messages` out from under an in-flight stream -- can no
  // longer make an unrelated, static message display the live/abandoned
  // stream text. Deliberately NOT cleared when a stream finishes normally
  // (see runStream) so the typewriter can keep draining its buffered tail
  // after `isLoading` flips back to false; it's only reset by
  // cancelActiveStream, and immediately overwritten at the start of the
  // next turn.
  const [streamingMessageId, setStreamingMessageId] = useState<number | null>(null)

  // Mirrors selectedCharId/activeChatId for reads from callbacks that were
  // created in an earlier render and may still fire long after -- most
  // notably a retried turn's `done` handler (see runStream/onRetry, whose
  // closure freezes the character/chat it originally targeted). Reading a
  // ref instead of the closed-over state answers "is this stream's target
  // still what's on screen" with the CURRENT selection, never a stale one.
  const selectedCharIdRef = useRef<number | null>(null)
  const activeChatIdRef = useRef<number | null>(null)
  useEffect(() => { selectedCharIdRef.current = selectedCharId }, [selectedCharId])
  useEffect(() => { activeChatIdRef.current = activeChatId }, [activeChatId])

  // Aborts any in-flight stream and immediately resets its state. Called
  // whenever the app is about to swap out `messages` for a different
  // character/chat's history, so an orphaned stream can never keep writing
  // into (or appearing to belong to) a context it no longer applies to --
  // without this, isLoading could stay stuck true for the newly selected
  // character until the abandoned stream's idle timeout eventually fires.
  const cancelActiveStream = useCallback(() => {
    streamAbortRef.current?.abort()
    streamAbortRef.current = null
    setIsLoading(false)
    setStreamingContent(null)
    setStreamingMessageId(null)
    // A persistent "Lost connection" toast's Retry replays the turn against
    // whatever character/chat was active when it failed. Once that context
    // is being left, the retry closure's frozen ids would otherwise still
    // be clickable and -- on completion -- silently overwrite whatever is
    // now on screen (see runStream/onRetry and fetchHistory). Leave other
    // toasts (e.g. a still-true offline notice) alone.
    setToast(prev => (prev?.onRetry ? null : prev))
  }, [])

  // Switches the active character. This is the only path by which
  // `selectedCharId` changes as a result of a deliberate user action
  // (starting a chat, creating/deleting a character, picking one from the
  // roster) -- routing every such change through here aborts any in-flight
  // stream for the character being left BEFORE `selectedCharId` updates,
  // rather than reactively inside the character-switch effect (a setState
  // call made synchronously in an effect body triggers avoidable cascading
  // renders -- see react-hooks/set-state-in-effect).
  const selectCharacter = useCallback((id: number | null) => {
    cancelActiveStream()
    setSelectedCharId(id)
  }, [cancelActiveStream])

  const showToast = (
    message: string,
    type: 'success' | 'error' = 'success',
    opts?: { persistent?: boolean; onRetry?: () => void }
  ) => {
    setToast({ message, type, persistent: opts?.persistent, onRetry: opts?.onRetry })
    if (!opts?.persistent) {
      setTimeout(() => setToast(null), TOAST_DURATION_MS)
    }
  }

  // Surface connectivity changes with the existing toast mechanism. Defined
  // with only `setToast` in scope (not `showToast`, which is recreated every
  // render) so the effect can register its listeners once on mount.
  useEffect(() => {
    const notify = (message: string, type: Toast['type'], opts?: { persistent?: boolean }) => {
      setToast({ message, type, persistent: opts?.persistent })
      if (!opts?.persistent) {
        setTimeout(() => setToast(null), TOAST_DURATION_MS)
      }
    }
    // Persistent: the user is offline until the 'online' handler below fires
    // its own (transient) toast, which -- since `toast` holds a single value
    // -- replaces this one outright rather than stacking alongside it.
    const handleOffline = () => notify('You are offline. Reconnect to continue chatting.', 'error', { persistent: true })
    const handleOnline = () => notify('Back online.', 'success')
    window.addEventListener('offline', handleOffline)
    window.addEventListener('online', handleOnline)
    return () => {
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('online', handleOnline)
    }
  }, [])

  const fetchUser = useCallback(async () => {
    try {
      const data = await api.fetchUser()
      setUser(data)
    } catch {
      showToast('Failed to fetch user.', 'error')
    }
  }, [])

  const fetchCharacters = useCallback(async () => {
    try {
      const data = await api.fetchCharacters()
      setCharacters(data)
      // Functional update reads the latest selectedCharId without needing it
      // in this callback's dependencies -- keeps fetchCharacters' identity
      // stable so the mount effect below doesn't re-fire on every character
      // switch (selectedCharId changing would otherwise recreate this
      // callback and re-trigger the effect that depends on it).
      setSelectedCharId((prev) => (prev === null && data.length > 0 ? data[0].id : prev))
    } catch {
      showToast('Failed to fetch characters.', 'error')
    }
  }, [])

  const fetchTags = useCallback(async () => {
    try {
      const data = await api.fetchTags()
      setTags(data)
    } catch {
      showToast('Failed to fetch tags.', 'error')
    }
  }, [])

  const fetchActions = useCallback(async () => {
    try {
      const data = await api.fetchActions()
      setActionsConfig(data)
    } catch {
      // Non-critical: handleSendAction falls back to a generic placeholder.
      console.error('Failed to fetch actions')
    }
  }, [])

  useEffect(() => {
    let active = true
    const init = async () => {
      await Promise.resolve()
      if (active) {
        fetchCharacters()
        fetchUser()
        fetchTags()
        fetchActions()
      }
    }
    init()
    return () => {
      active = false
    }
  }, [fetchCharacters, fetchUser, fetchTags, fetchActions])

  // Every caller fires this with the character/chat it wants history FOR at
  // call time, but `await api.fetchHistory(...)` is a network round-trip --
  // the user can switch character/chat (or delete the one being fetched)
  // before it resolves. Re-checking the target against the CURRENT selection
  // (via the refs, not a closed-over value) only at the call site is not
  // enough: a later, faster call can still finish first and then get
  // clobbered when this earlier, slower call finally resolves and applies
  // its now-stale result. So the guard has to live here, at the point the
  // result is actually applied, not at each call site -- this is the single
  // choke point every caller (character switch, chat switch, chat delete,
  // edit/delete-message refresh, SSE done-handler) goes through.
  const fetchHistory = useCallback(async (charId: number, chatId?: number) => {
    try {
      const data = await api.fetchHistory(charId, chatId)
      const chatIdOrNull = chatId ?? null
      if (charId !== selectedCharIdRef.current || chatIdOrNull !== activeChatIdRef.current) {
        return
      }
      // Only update if we are not currently loading a new response to avoid race conditions
      setMessages(prev => {
        // Simple heuristic: if we have local unsaved messages, don't overwrite with empty history
        if (prev.length > 0 && data.length === 0) return prev;
        return data;
      })
    } catch (err) {
      console.error('Failed to fetch history', err)
    }
  }, [])

  const loadChats = useCallback(async (charId: number): Promise<number | null> => {
    try {
      const list = await api.fetchChats(charId)
      setChats(list)
      const active = list.find((c) => c.is_active) ?? list[0] ?? null
      setActiveChatId(active ? active.id : null)
      return active ? active.id : null
    } catch (err) {
      console.error('Failed to fetch chats', err)
      setChats([])
      setActiveChatId(null)
      return null
    }
  }, [])

  useEffect(() => {
    let active = true
    const init = async () => {
      if (selectedCharId) {
        setMessages([]) // Clear stale messages from previous character to avoid tree mismatch
        const chatId = await loadChats(selectedCharId)
        if (active) {
          await fetchHistory(selectedCharId, chatId ?? undefined)
        }
      }
    }
    init()
    return () => {
      active = false
    }
  }, [selectedCharId, fetchHistory, loadChats]) // Re-run when character changes

  // Immersive mode is a chat-only, mobile-only affordance; never let it stay
  // latched after navigating away or resizing up to desktop. Reset during
  // render (not an effect) so the bars are already restored on that frame.
  if (immersive && (currentView !== 'chat' || !isMobile)) {
    setImmersive(false)
  }

  const updateUser = async (name: string, gender: string, persona: string, appearance: string) => {
    try {
      const data = await api.updateUser(name, gender, persona, appearance)
      setUser(data)
      setActiveModal(null)
      showToast('Profile updated.')
    } catch {
      showToast('Failed to update profile.', 'error')
    }
  }

  const createTag = async (label: string, instruction: string) => {
    try {
      const data = await api.createTag(label, instruction)
      setTags(prev => [...prev, data])
      setActiveModal(null)
      setEditingTag(null)
      showToast('Tag created.')
      return data
    } catch {
      showToast('Failed to create tag.', 'error')
      return null
    }
  }

  const updateTag = async (id: number, label: string, instruction: string) => {
    try {
      const data = await api.updateTag(id, label, instruction)
      setTags((prev) => prev.map((tag) => (tag.id === id ? data : tag)))
      setActiveModal(null)
      setEditingTag(null)
      showToast('Tag updated.')
    } catch {
      showToast('Failed to update tag.', 'error')
    }
  }

  const deleteTag = async (id: number) => {
    try {
      await api.deleteTag(id)
      setTags((prev) => prev.filter((tag) => tag.id !== id))
      showToast('Tag deleted.')
    } catch {
      showToast('Failed to delete tag.', 'error')
    }
  }

  const deleteCharacter = async (id: number) => {
    const ok = await confirm({
      title: 'Delete character?',
      message: 'This action is permanent.',
      confirmLabel: 'Delete',
      danger: true,
    })
    if (!ok) return
    try {
      await api.deleteCharacter(id)
      setCharacters(prev => prev.filter(c => c.id !== id))
      if (selectedCharId === id) selectCharacter(null)
      showToast('Character deleted.')
    } catch {
      showToast('Failed to delete character.', 'error')
    }
  }

  const createCharacter = async (data: CharacterFormData) => {
    try {
      const characterData = await api.createCharacter(toCharacterPayload(data))

      if (data.avatarFile) {
        const url = await uploadAvatar(characterData.id, data.avatarFile)
        if (url) characterData.avatar_url = url
      }

      setCharacters((prev) => [...prev, characterData])
      selectCharacter(characterData.id)
      setActiveModal(null)
      showToast('Character initialized.')
    } catch {
      showToast('Failed to create character.', 'error')
    }
  }

  const updateCharacter = async (id: number, data: CharacterFormData) => {
    try {
      const characterData = await api.updateCharacter(id, toCharacterPayload(data))

      if (data.avatarFile) {
        const url = await uploadAvatar(characterData.id, data.avatarFile)
        if (url) characterData.avatar_url = url
      }

      setCharacters((prev) => prev.map((c) => (c.id === id ? characterData : c)))
      setActiveModal(null)
      setEditingCharacter(null)
      showToast('Changes saved.')
    } catch {
      showToast('Failed to update character.', 'error')
    }
  }

  // Parent of the next message: an explicit id (branching) else the newest node.
  const resolveParentId = (explicitParentId?: number) =>
    explicitParentId ?? (messages.length > 0 ? messages[messages.length - 1].id : null)

  // Optimistically append a user turn + its empty assistant placeholder. The
  // robust temporary id avoids collisions and keeps test ordering stable.
  // Returns the assistant placeholder's id so the caller can tell runStream
  // exactly which node the stream it's about to start belongs to.
  const appendExchange = (content: string, parentId: number | null): number => {
    const userMsgId = generateMessageId()
    const assistantMsgId = userMsgId + 1
    const assistantMsg: MessageNode = { id: assistantMsgId, parent_id: userMsgId, role: 'assistant', content: '', variant_index: 0 }
    const userMsg: MessageNode = { id: userMsgId, parent_id: parentId, role: 'user', content, variant_index: 0 }
    setMessages(prev => [...prev, userMsg, assistantMsg])
    return assistantMsgId
  }

  // Drive one streaming turn: flip the loading flag, stream the response, and
  // surface a connection-error toast. Shared by send / action / regenerate so
  // the try/catch/finally lives in exactly one place. `start` receives an
  // AbortSignal wired to a per-turn AbortController, which a Stop button or
  // an idle timeout can trigger to recover a hung stream (dropped Wi-Fi mid
  // generation used to leave isLoading stuck true forever). `messageId` is
  // the assistant placeholder this stream's tokens belong to -- threaded
  // through to streamingMessageId/commitStreamedContent so a sibling-variant
  // swap or a character/chat switch mid-stream can never make an unrelated
  // message display or absorb this stream's text (see streamingMessageId).
  const runStream = async (
    messageId: number,
    charId: number,
    chatId: number | undefined,
    start: (signal: AbortSignal) => Promise<Response>
  ) => {
    if (streamAbortRef.current) {
      // A stream is already active -- refuse to start a second one rather
      // than let two concurrent streams clobber the single shared
      // streamAbortRef/streamingContent/streamingMessageId/isLoading state.
      // Reachable via a stale toast's Retry (a frozen closure with no
      // isLoading guard of its own) firing while a newer, unrelated send is
      // still in flight.
      showToast('A response is already in progress.', 'error')
      return
    }
    const controller = new AbortController()
    streamAbortRef.current = controller
    let timedOut = false
    // True once the response headers arrive. Past that point the backend has
    // already run _prepare_chat_turn and COMMITTED the user message, so a later
    // failure must NOT offer a full-resend retry (it would create a duplicate
    // user turn under the same parent). Only a pre-header failure is safe to
    // replay wholesale.
    let headersReceived = false
    let idleTimer: ReturnType<typeof setTimeout> | undefined
    const resetIdleTimer = () => {
      clearTimeout(idleTimer)
      idleTimer = setTimeout(() => {
        timedOut = true
        controller.abort()
      }, STREAM_IDLE_TIMEOUT_MS)
    }

    // Starting a new turn (including this very call being a retry)
    // supersedes any leftover "Lost connection" toast from a previous
    // failed turn -- it would otherwise stay visible pointing at a
    // now-superseded retry. Other toasts (e.g. a still-true offline notice)
    // are left alone.
    setToast(prev => (prev?.onRetry ? null : prev))
    setIsLoading(true)
    setStreamingContent('')
    setStreamingMessageId(messageId)
    streamedLenRef.current = 0
    resetIdleTimer()
    try {
      const response = await start(controller.signal)
      headersReceived = true
      // Headers are here -> the backend's pre-stream work (RAG embedding,
      // prompt build) is done. Give the FIRST token its own full idle budget
      // rather than whatever was left after that work, so a slow local model
      // isn't falsely timed out before it emits anything.
      resetIdleTimer()
      await handleStreamResponse(messageId, charId, chatId, response, controller.signal, resetIdleTimer)
    } catch (err) {
      if (err instanceof StreamError) {
        showToast(err.message || 'The AI reported an error.', 'error')
        // Terminal interrupt: reconcile temp ids -> real ids without wiping the
        // partial the user just saw. Fire-and-forget so the Stop->Send button
        // reverts immediately (isLoading clears in `finally`); it self-guards
        // against a new turn started meanwhile (see reconcileInterruptedStream).
        void reconcileInterruptedStream(charId, chatId)
      } else if (controller.signal.aborted) {
        showToast(
          timedOut ? 'Response timed out. Check your connection.' : 'Generation stopped.',
          timedOut ? 'error' : 'success'
        )
        // Stop button / idle timeout: both terminal (no retry). Reconcile the
        // real ids in, race-safe against the backend's teardown partial-save.
        // NOT done for the retryable connection-lost branch below, which must
        // keep the temp placeholder so its onRetry can re-drive this same turn.
        void reconcileInterruptedStream(charId, chatId)
      } else if (headersReceived) {
        // Connection dropped AFTER headers, i.e. mid-body. The backend already
        // committed the user turn (and persists whatever partial streamed on
        // teardown), so a full-resend retry would duplicate the user turn under
        // the same parent (a "2/2" swiper on the user bubble + an orphaned
        // partial). Instead reconcile the real ids in and let the user hit
        // Regenerate on the now-persisted turn to finish the reply.
        showToast('Connection lost mid-reply. Reconnect, then Regenerate to continue.', 'error')
        void reconcileInterruptedStream(charId, chatId)
      } else {
        // Dropped BEFORE headers -> the backend never accepted this turn (no
        // user message committed), so replaying the whole send is safe and
        // won't duplicate anything. `start` is the same signal-taking closure
        // runStream was originally called with, so Retry re-issues the
        // identical request for the same `messageId` placeholder. `charId`/
        // `chatId` are threaded through unchanged so a late completion after
        // the user switched away is recognized as stale (see
        // handleStreamResponse) instead of overwriting the current view.
        showToast('Lost connection to AI.', 'error', {
          persistent: true,
          onRetry: () => { void runStream(messageId, charId, chatId, start) }
        })
      }
    } finally {
      clearTimeout(idleTimer)
      setIsLoading(false)
      if (streamAbortRef.current === controller) streamAbortRef.current = null
    }
  }

  // Wired to the composer's Stop control while a response is streaming.
  const handleCancelStream = () => {
    streamAbortRef.current?.abort()
  }

  // Writes the streamed assistant reply into `messages` exactly once -- on
  // stream completion, or with whatever partial text has accumulated so far
  // on error/abort/cancel, so a dropped connection doesn't leave the bubble
  // permanently empty. Never called per-token.
  //
  // Targets `messageId` by id, NOT by array position. A positional
  // "last element of `messages`" write is only safe as long as nothing else
  // could be last -- but switching character/chat mid-stream swaps `messages`
  // out for a completely unrelated array, so a late-arriving `done` from an
  // abandoned stream would silently overwrite whatever real, already-
  // persisted message now happens to sit last. Looking the node up by id
  // instead makes that a safe no-op (the id simply isn't found).
  const commitStreamedContent = (messageId: number | null, content: string, requestId?: string | null) => {
    if (messageId === null) return
    setMessages(prev => {
      const idx = prev.findIndex(m => m.id === messageId)
      if (idx === -1 || prev[idx].role !== 'assistant') return prev
      const target = prev[idx]
      const updated: MessageNode = requestId ? { ...target, content, request_id: requestId } : { ...target, content }
      const next = prev.slice()
      next[idx] = updated
      return next
    })
  }

  const refreshHistory = async () => {
    if (!selectedCharId) return
    const charId = selectedCharId
    const chatId = activeChatId ?? undefined
    const history = await api.fetchHistory(charId, chatId)
    // Re-check identity now that the round-trip has resolved -- an edit/
    // delete whose refresh resolves after the user has since switched
    // character/chat must not clobber the newly-viewed conversation. Deliberately
    // NOT routed through fetchHistory: that helper also skips an empty result
    // when there are local unsaved messages, which is wrong here -- an edit/
    // delete's own empty result (e.g. deleting the last message) is real and
    // must be applied, not treated as a stale/incomplete background read.
    if (charId !== selectedCharIdRef.current || (chatId ?? null) !== activeChatIdRef.current) return
    setMessages(history)
  }

  // Reconcile the optimistic temp-id nodes to the backend's real ids after an
  // INTERRUPTED stream (Stop / idle-timeout / mid-stream error). The backend
  // persists the user turn + whatever partial reply streamed, but that partial
  // save happens during the server's request teardown, which can land just
  // AFTER our first refetch would. A naive immediate refetch therefore races
  // it and briefly REPLACES the on-screen turn with a server history that
  // doesn't have the assistant reply yet -- i.e. the partial the user just
  // watched stream visibly vanishes. That was the "cancel is broken" bug.
  //
  // So: if we're showing a non-empty partial, poll until the server history has
  // caught up to (>=) what we're showing before swapping it in; otherwise apply
  // immediately (nothing to protect). Identity-guarded on every await so a
  // character/chat switch mid-reconcile can't clobber the new view.
  const reconcileInterruptedStream = async (charId: number, chatId: number | undefined) => {
    const chatIdOrNull = chatId ?? null
    // Node COUNT is reliable here even though message CONTENT isn't yet flushed
    // to `messages`: the optimistic user+assistant nodes were appended (and the
    // ref updated) before the stream started; the partial only MUTATED an
    // existing node's content, never changed the count. If we streamed a
    // non-empty partial, the server must include that assistant node before we
    // adopt its history (`target` = full local count); if nothing streamed, the
    // server legitimately has no assistant node, so adopt one node short.
    const hadPartial = streamedLenRef.current > 0
    for (let attempt = 0; attempt < 5; attempt++) {
      let data: MessageNode[]
      try {
        data = await api.fetchHistory(charId, chatId)
      } catch {
        return
      }
      // Bail if the view moved on OR a fresh turn is already streaming --
      // applying this now-stale server history would clobber the new turn's
      // optimistic nodes (runs fire-and-forget, so a new send can race it).
      if (charId !== selectedCharIdRef.current || chatIdOrNull !== activeChatIdRef.current) return
      if (streamAbortRef.current) return
      // Decide against the LATEST committed messages via the functional updater
      // (a ref would lag one commit behind the optimistic append). Nothing
      // streamed -> nothing to protect, adopt immediately. Otherwise only adopt
      // once the server history has caught up to (>=) the on-screen node count,
      // so we never briefly wipe the partial the user just watched stream.
      let adopted = false
      setMessages((prev) => {
        if (!hadPartial || data.length >= prev.length) {
          adopted = true
          return data
        }
        return prev
      })
      if (adopted) return
      await new Promise((resolve) => setTimeout(resolve, 250))
    }
    // Backend never caught up within the window (partial persist genuinely
    // failed or was skipped): keep the local partial on screen rather than
    // wiping it to an empty server history. Its temp id self-heals on the next
    // successful turn's reconcile -- losing the visible partial is worse.
  }

  const handleSend = async (explicitParentId?: number) => {
    if (!input.trim() || isLoading || !selectedCharId) return
    const parentId = resolveParentId(explicitParentId)
    const assistantMsgId = appendExchange(input, parentId)
    const currentInput = input
    const chatId = activeChatId ?? undefined
    setInput('')
    await runStream(assistantMsgId, selectedCharId, chatId, (signal) => api.sendMessageStream(currentInput, selectedCharId, parentId, config, undefined, chatId, signal))
  }

  const handleEditMessage = async (messageId: number, content: string) => {
    try {
      await api.editMessage(messageId, content)
      await refreshHistory()
    } catch {
      showToast('Failed to edit message.', 'error')
    }
  }

  const handleDeleteMessage = async (messageId: number) => {
    try {
      await api.deleteMessage(messageId)
      await refreshHistory()
    } catch {
      showToast('Failed to delete message.', 'error')
    }
  }

  const handleSendAction = async (actionId: string, explicitParentId?: number) => {
    if (isLoading || !selectedCharId) return
    const parentId = resolveParentId(explicitParentId)
    const actionMessage = actionsConfig[actionId]?.message || `*Performs action: ${actionId}*`
    const assistantMsgId = appendExchange(actionMessage, parentId)
    const chatId = activeChatId ?? undefined
    await runStream(assistantMsgId, selectedCharId, chatId, (signal) => api.sendMessageStream(null, selectedCharId, parentId, config, actionId, chatId, signal))
  }

  const handleRegenerate = async (parentId: number) => {
    if (isLoading || !selectedCharId) return
    const assistantMsgId = generateMessageId()
    const assistantMsg: MessageNode = {
      id: assistantMsgId,
      parent_id: parentId,
      role: 'assistant',
      content: '',
      variant_index: 0 // Will be corrected by fetchHistory
    }
    setMessages(prev => [...prev, assistantMsg])
    const chatId = activeChatId ?? undefined
    await runStream(assistantMsgId, selectedCharId, chatId, (signal) => api.sendMessageStream(null, selectedCharId, parentId, config, undefined, chatId, signal))
  }

  // `onToken` resets the caller's idle timeout on every token so a stalled
  // connection (no token for N seconds) is distinguishable from a merely slow
  // one -- see runStream/STREAM_IDLE_TIMEOUT_MS. `messageId` identifies which
  // assistant placeholder this stream's tokens belong to (see runStream).
  // `charId`/`chatId` are the character/chat this specific turn was actually
  // sent to -- pinned at the call site (handleSend et al.), NOT read from
  // `selectedCharId`/`activeChatId` here, precisely because a retried turn's
  // `done` handler can still fire long after the user has switched to a
  // different character/chat (see the `data.done` branch below).
  const handleStreamResponse = async (
    messageId: number,
    charId: number,
    chatId: number | undefined,
    response: Response,
    signal: AbortSignal,
    onToken?: () => void
  ) => {
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let fullContent = ''

    if (!reader) throw new Error('Reader unavailable')

    // Rejects as soon as `signal` aborts, racing the in-flight read so a Stop
    // click or an idle timeout interrupts it immediately. Doesn't rely on the
    // runtime auto-rejecting a pending body read on abort -- true for a real
    // fetch(), but a wider net (and easier to test) done explicitly here.
    const readChunk = (): Promise<ReadableStreamReadResult<Uint8Array>> => {
      if (signal.aborted) return Promise.reject(new DOMException('Aborted', 'AbortError'))
      return new Promise((resolve, reject) => {
        const onAbort = () => reject(new DOMException('Aborted', 'AbortError'))
        signal.addEventListener('abort', onAbort, { once: true })
        reader.read().then(
          (result) => {
            signal.removeEventListener('abort', onAbort)
            resolve(result)
          },
          (err) => {
            signal.removeEventListener('abort', onAbort)
            reject(err)
          }
        )
      })
    }

    // Apply one parsed SSE payload. Kept local so it closes over fullContent.
    const applyEvent = async (data: {
      token?: string
      done?: boolean
      error?: string
      state?: CharacterState
      request_id?: string
    }) => {
      // The backend's error_stream/mid-generation error event (chat.py) has
      // no `done` flag of its own -- surface it and stop instead of silently
      // finishing with an empty/partial reply and no feedback.
      if (data.error) {
        throw new StreamError(data.error)
      }
      if (data.token) {
        onToken?.()
        fullContent += data.token
        streamedLenRef.current = fullContent.length
        // Dedicated streaming state, NOT the messages array -- see
        // streamingContent's declaration for why.
        setStreamingContent(fullContent)
      }
      if (data.done) {
        if (data.state) {
          // Keyed on `charId` (this turn's actual target), not the possibly
          // stale `selectedCharId` -- the returned state belongs to `charId`
          // regardless of which character is currently on screen.
          setCharacters(prev => prev.map(c =>
            c.id === charId ? { ...c, state: data.state as CharacterState } : c
          ))
        }
        commitStreamedContent(messageId, fullContent, data.request_id)
        setStreamingContent(null)
        // Only refresh if we haven't been aborted AND this turn's target
        // character/chat is still the one currently on screen (compared
        // against the ref, i.e. the CURRENT selection, not this closure's
        // own possibly-stale one). A retried turn (see runStream/onRetry)
        // can complete long after the user switched away. This is a fast-path
        // that skips firing a pointless request outright -- fetchHistory
        // itself re-checks the same refs once ITS OWN result comes back, so
        // a switch that happens while that follow-up request is in flight
        // still can't clobber the newly-viewed character/chat's history.
        const chatIdOrNull = chatId ?? null
        if (
          !signal.aborted &&
          charId === selectedCharIdRef.current &&
          chatIdOrNull === activeChatIdRef.current
        ) {
          await fetchHistory(charId, chatId)
        }
      }
    }

    // Parse whole `data: ...` lines out of `buffer`, leaving any partial trailing
    // line in place so a frame split across reads is reassembled, not dropped.
    // Only a JSON.parse failure is swallowed here -- applyEvent's own errors
    // (e.g. StreamError from a `data.error` event) propagate to the caller.
    const drainBuffer = async (buffer: string): Promise<string> => {
      let newlineIndex: number
      while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newlineIndex)
        buffer = buffer.slice(newlineIndex + 1)
        if (!line.startsWith('data: ')) continue
        let payload: Parameters<typeof applyEvent>[0]
        try {
          payload = JSON.parse(line.slice(6))
        } catch (e) {
          console.error('SSE Error', e)
          continue
        }
        await applyEvent(payload)
      }
      return buffer
    }

    try {
      let buffer = ''
      while (true) {
        const { done, value } = await readChunk()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        buffer = await drainBuffer(buffer)
      }
      // Flush a trailing frame that arrived without a closing newline.
      await drainBuffer(buffer + '\n')
    } catch (err) {
      // Abort (Stop/idle-timeout/character-switch) or a mid-stream
      // StreamError: persist whatever text streamed in before the failure
      // instead of leaving the assistant bubble empty forever, then let
      // runStream's catch toast it. Safe even if `messageId` no longer
      // exists in `messages` (e.g. the user has since switched character) --
      // commitStreamedContent looks it up by id and no-ops if it's gone.
      commitStreamedContent(messageId, fullContent)
      setStreamingContent(null)
      throw err
    } finally {
      reader.cancel().catch(() => {})
    }

    fetchCharacters() // Refresh stats
  }

  const handleStartChat = (id: number) => {
    selectCharacter(id)
    setCurrentView('chat')
  }

  const handleUpdateState = async (charId: number, stateUpdate: Record<string, unknown>) => {
    try {
      const updatedChar = await api.updateCharacterState(charId, stateUpdate)
      setCharacters((prev) => prev.map((c) => c.id === charId ? updatedChar : c))
    } catch {
      showToast('Failed to update character state.', 'error')
    }
  }

  const handleClearChat = async () => {
    if (!selectedCharId) return
    const ok = await confirm({
      title: 'Clear conversation history?',
      message: 'This cannot be undone.',
      confirmLabel: 'Clear',
      danger: true,
    })
    if (!ok) return
    cancelActiveStream()
    try {
      await api.clearChatHistory(selectedCharId)
      setMessages([])
      await loadChats(selectedCharId)
      fetchCharacters()
      showToast('Conversation cleared.')
    } catch {
      showToast('Failed to clear conversation history.', 'error')
    }
  }

  // Non-destructive "New Chat": starts a fresh session and keeps the old ones.
  // An optional greetingIndex selects which opening greeting seeds the session.
  const handleNewChat = async (greetingIndex?: number) => {
    if (!selectedCharId) return
    cancelActiveStream()
    try {
      const res = await api.newChat(selectedCharId, greetingIndex)
      setMessages([])
      await loadChats(selectedCharId)
      if (res?.chat_id != null) setActiveChatId(res.chat_id)
      fetchCharacters()
      showToast('Started a new chat.')
    } catch {
      showToast('Failed to start a new chat.', 'error')
    }
  }

  const handleSelectChat = async (chatId: number) => {
    if (!selectedCharId || chatId === activeChatId) return
    // A stream targeting the chat we're leaving must not keep running -- see
    // cancelActiveStream.
    cancelActiveStream()
    setActiveChatId(chatId)
    setMessages([])
    await fetchHistory(selectedCharId, chatId)
  }

  const handleDeleteChat = async (chatId: number) => {
    if (!selectedCharId) return
    const ok = await confirm({
      title: 'Delete chat session?',
      message: 'This cannot be undone.',
      confirmLabel: 'Delete',
      danger: true,
    })
    if (!ok) return
    cancelActiveStream()
    try {
      await api.deleteChat(chatId)
      setMessages([])
      const nextActive = await loadChats(selectedCharId)
      await fetchHistory(selectedCharId, nextActive ?? undefined)
      fetchCharacters()
      showToast('Chat deleted.')
    } catch {
      showToast('Failed to delete chat.', 'error')
    }
  }

  const activeChar = characters.find((c) => c.id === selectedCharId) || null

  const tagUsage = characters.reduce<Record<number, number>>((acc, character) => {
    character.tags.forEach((tag) => {
      acc[tag.id] = (acc[tag.id] ?? 0) + 1
    })
    return acc
  }, {})

  return (
    <ErrorBoundary>
      <div className="flex h-full w-full bg-background text-on-surface font-body-md overflow-hidden antialiased relative">
        {/* Mobile Backdrop Overlay */}
        {isSidebarOpen && (
          <div 
            onClick={() => setIsSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
          />
        )}

        <Sidebar
          currentView={currentView}
          setView={(v) => setCurrentView(v as View)}
          userName={user?.name}
          onProfileClick={() => setActiveModal('user')}
          onSettingsClick={() => setActiveModal('settings')}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main
          className="flex-1 h-full overflow-hidden flex flex-col min-w-0 transition-[padding] duration-300"
          style={isMobile ? { paddingBottom: immersive ? 'env(safe-area-inset-bottom)' : 'calc(3.5rem + env(safe-area-inset-bottom))' } : undefined}
        >
          {/* Mobile Top Header. Collapses to zero height in immersive reading
              mode (scrolled down into a chat) so the transcript owns the screen;
              restored on a deliberate upward scroll. */}
          <header
            inert={immersive}
            className={`md:hidden flex items-center justify-between px-md bg-[#0A0A0B]/90 backdrop-blur z-30 shrink-0 overflow-hidden transition-all duration-300 ${
              immersive ? 'max-h-0 py-0 opacity-0 pointer-events-none border-b-0' : 'max-h-16 py-sm border-b border-white/5'
            }`}
          >
            <button
              onClick={() => setIsSidebarOpen(true)}
              aria-label="Open menu"
              className="flex items-center justify-center min-h-11 min-w-11 -ml-2 text-[#A1A1AA] hover:text-white touch-manipulation active:scale-95"
            >
              <Icon name="menu" size="md" />
            </button>
            <h2 className="font-sans text-xs font-bold text-white uppercase tracking-[0.2em]">
              {currentView === 'characters' && 'Characters'}
              {currentView === 'chat' && 'Direct Chat'}
              {currentView === 'library' && 'Lorebook'}
              {currentView === 'archives' && 'Knowledge Tags'}
            </h2>
            <button
              onClick={() => setActiveModal('user')}
              aria-label="Open profile"
              className="w-9 h-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0 touch-manipulation active:scale-95"
            >
              <Icon name="person" size="sm" className="text-[#A1A1AA]" />
            </button>
          </header>

          {currentView === 'characters' && (
            <CharactersView
              characters={characters}
              selectedCharId={selectedCharId}
              setSelectedCharId={selectCharacter}
              onNewCharacter={() => setActiveModal('character')}
              onCharacterImported={() => fetchCharacters()}
              onChat={handleStartChat}
              onEdit={(id) => {
                const char = characters.find((c) => c.id === id)
                if (char) {
                  setEditingCharacter(char)
                  setActiveModal('character')
                }
              }}
              onDelete={deleteCharacter}
            />
          )}

          {currentView === 'chat' && (
            <ChatView
              activeChar={activeChar}
              messages={messages}
              streamingContent={streamingContent}
              streamingMessageId={streamingMessageId}
              input={input}
              setInput={setInput}
              onSend={handleSend}
              onRegenerate={handleRegenerate}
              isLoading={isLoading}
              onCancelStream={handleCancelStream}
              onUpdateState={handleUpdateState}
              onClearChat={handleClearChat}
              onSendAction={handleSendAction}
              onEditMessage={handleEditMessage}
              onDeleteMessage={handleDeleteMessage}
              actions={actionsConfig}
              chats={chats}
              activeChatId={activeChatId}
              greetings={[activeChar?.first_mes ?? '', ...(activeChar?.alternate_greetings ?? [])].filter((g) => g.trim())}
              onNewChat={handleNewChat}
              onSelectChat={handleSelectChat}
              onDeleteChat={handleDeleteChat}
              onImmersiveChange={setImmersive}
            />
          )}

          {currentView === 'library' && (
            <LorebookView />
          )}

          {currentView === 'archives' && (
            <TagManagementView
              tags={tags}
              onCreateTag={() => {
                setEditingTag(null)
                setActiveModal('tag')
              }}
              onEditTag={(tag) => {
                setEditingTag(tag)
                setActiveModal('tag')
              }}
              onDeleteTag={deleteTag}
              usage={tagUsage}
            />
          )}
        </main>

        {/* Mobile primary navigation: thumb-reachable bottom tab bar (replaces
            the hamburger drawer for switching views on phones). */}
        {isMobile && (
          <MobileTabBar
            currentView={currentView}
            setView={(v) => setCurrentView(v as View)}
            hidden={immersive}
          />
        )}

        {/* Modals */}
        {(activeModal === 'character' || editingCharacter) && (
          <CharacterCreator
            tags={tags}
            onClose={() => {
              setActiveModal(null)
              setEditingCharacter(null)
            }}
            onCreate={createCharacter}
            onUpdate={updateCharacter}
            editingCharacter={editingCharacter}
          />
        )}
        {activeModal === 'user' && (
          <UserProfileModal
            user={user}
            onClose={() => setActiveModal(null)}
            onUpdate={updateUser}
          />
        )}
        {activeModal === 'tag' && (
          <TagCreator
            onClose={() => {
              setActiveModal(null)
              setEditingTag(null)
            }}
            onSubmit={async (label, instruction) => {
              if (editingTag) {
                await updateTag(editingTag.id, label, instruction)
              } else {
                await createTag(label, instruction)
              }
            }}
            tag={editingTag}
          />
        )}
        {activeModal === 'settings' && (
          <SettingsModal
            onClose={() => setActiveModal(null)}
          />
        )}

        {/* Toast. Offset clears the fixed glass composer bar STACKED ON TOP
            of the fixed MobileTabBar on mobile: composer (pt-sm + p-2 inner
            box + pb-[1.5rem+safe-area] works out to roughly 92px + 1x
            safe-area) sits directly above the tab bar (min-h-14 buttons +
            pb-[safe-area], ~56px + 1x safe-area, reserved via `main`'s own
            paddingBottom above) -- combined clearance from the viewport
            bottom is ~148px + 2x safe-area. md: reverts to the original
            bottom-20 since neither the composer nor the tab bar is
            full-bleed/fixed at that width. */}
        {toast && (
          <div className={`fixed bottom-[calc(9.25rem+2*env(safe-area-inset-bottom))] md:bottom-20 left-1/2 -translate-x-1/2 flex items-center gap-sm max-w-[min(26rem,calc(100vw-2rem))] px-lg py-sm rounded border shadow-xl z-[60] animate-in fade-in slide-in-from-bottom-4 duration-300 ${
            toast.type === 'error'
              ? 'bg-error-container text-error border-error/20'
              : 'bg-surface-container-high text-primary border-primary/20'
          }`}>
            <p className="font-label-md text-label-md font-medium break-words">{toast.message}</p>
            {toast.onRetry && (
              <button
                type="button"
                onClick={() => {
                  const retry = toast.onRetry
                  setToast(null)
                  retry?.()
                }}
                className="shrink-0 font-label-md text-label-md font-bold underline underline-offset-2 cursor-pointer touch-manipulation"
              >
                Retry
              </button>
            )}
            <IconButton
              icon="close"
              label="Dismiss"
              size="sm"
              onClick={() => setToast(null)}
              className="shrink-0 text-current opacity-70 hover:opacity-100"
            />
          </div>
        )}

        {dialog}
      </div>
    </ErrorBoundary>
  )
}

export default App
