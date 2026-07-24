import type { MessageNode } from '../hooks/useMessageTree'

export interface MessageRowProps {
  msg: MessageNode
  characterName: string
  isEditing: boolean
  editContent: string
  // True only when THIS row is the one actively streaming/typewriting right
  // now (see ChatView's isStreamTarget/isStreaming computation).
  isStreaming: boolean
  // The typewriter's current buffer. Only meaningful (and only read) while
  // isStreaming is true for this row -- see arePropsEqual below.
  displayedContent: string
  isLoading: boolean
  isCopied: boolean
  hasSiblings: boolean
  currentIndex: number
  siblingsLength: number
  onEditStart: () => void
  onEditChange: (value: string) => void
  onEditCancel: () => void
  onEditSave: () => void
  onDelete?: () => void
  onRegenerate: () => void
  onCopyId: () => void
  onPrevVariant: () => void
  onNextVariant: () => void
}

// Deliberately hand-rolled instead of the default shallow-props compare so
// each prop's gating behavior is explicit and auditable -- see the WHY notes
// inline. Returning true means "props are equivalent, skip re-render". Lives
// in its own module (rather than MessageRow.tsx) purely so it -- a plain
// function, not a component -- can be unit-tested directly without tripping
// the react-refresh/only-export-components lint rule on the component file.
export function arePropsEqual(prev: MessageRowProps, next: MessageRowProps): boolean {
  // The message itself: only the fields this row actually renders matter.
  // Covers both a genuinely new node (regenerate/variant swap) and an
  // in-place edit (content change) or the request_id arriving after the
  // stream's `done` event.
  const msgChanged =
    prev.msg !== next.msg &&
    (prev.msg.id !== next.msg.id ||
      prev.msg.content !== next.msg.content ||
      prev.msg.role !== next.msg.role ||
      prev.msg.request_id !== next.msg.request_id)
  if (msgChanged) return false

  if (prev.characterName !== next.characterName) return false
  if (prev.isEditing !== next.isEditing) return false
  if (prev.isStreaming !== next.isStreaming) return false

  // displayedContent changes on every SSE token, but it only ever feeds the
  // JSX of the one row currently streaming (see the ternary in the assistant
  // branch above). Gating on it unconditionally would force every historical
  // row to re-render on every token again -- exactly the cost this component
  // exists to eliminate. A non-streaming row's text always comes from
  // msg.content instead, which is already covered by msgChanged.
  if (next.isStreaming && prev.displayedContent !== next.displayedContent) return false

  // isLoading is not read anywhere in this row's own JSX, but every callback
  // prop below (onRegenerate in particular) is a fresh closure ChatView
  // creates on each of ITS renders, closing over the CURRENT isLoading value
  // (handleRegenerate's `if (isLoading || ...) return` guard). Callback props
  // are deliberately excluded from this comparator (see the note below) --
  // which means a row that bails out keeps whatever closures it received on
  // its last actual render, guard included. Without gating on isLoading here,
  // a row could go stale across an isLoading flip and let a click fire
  // against a guard evaluating a value that's no longer current -- a real
  // correctness bug, not a cosmetic one, so this is included even though it
  // changes at most twice per turn (send-start, stream-end).
  if (prev.isLoading !== next.isLoading) return false

  // Only differs for the 1-2 rows whose request_id matches copiedId.
  if (prev.isCopied !== next.isCopied) return false

  // Sibling/variant info for the swipe UI.
  if (prev.hasSiblings !== next.hasSiblings) return false
  if (prev.currentIndex !== next.currentIndex) return false
  if (prev.siblingsLength !== next.siblingsLength) return false

  // editContent only feeds the textarea while this row is actually being
  // edited -- ignored otherwise so typing in one row's editor never forces
  // every other (non-editing) row to re-render.
  if (next.isEditing && prev.editContent !== next.editContent) return false

  // Callback props (onEditStart, onEditChange, onEditCancel, onEditSave,
  // onDelete, onRegenerate, onCopyId, onPrevVariant, onNextVariant) are
  // deliberately NOT compared here. ChatView is not itself memoized, so it
  // hands down a brand-new closure for every one of these on every single
  // render; treating any of them as significant would make this comparator
  // (and therefore the whole point of memoizing this component) a no-op.
  // This is safe specifically because every prop that could make an OLD
  // closure behave incorrectly if invoked later -- isLoading, isStreaming,
  // and the message's own identity -- is already gated above. By the time
  // any of those meaningfully change, this row re-renders anyway and picks
  // up the current render's fresh callbacks along with it.
  return true
}
