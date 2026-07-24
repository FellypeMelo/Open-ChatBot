import React, { useEffect } from 'react'

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
  onConfirm: () => void
  onCancel: () => void
}

/**
 * In-app replacement for `window.confirm()`. Matches the dark modal visual
 * language established by UserProfileModal/SettingsModal so confirmations
 * don't jar the user with an unstyled native dialog.
 */
const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}) => {
  useEffect(() => {
    if (!open) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, onCancel])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md"
      onClick={onCancel}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-message"
        className="w-full max-w-[420px] rounded-[1.5rem] bg-[#111111] border border-[#1A1A1A] p-lg flex flex-col gap-lg z-50 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col gap-xs">
          <h2 id="confirm-dialog-title" className="font-heading-lg text-heading-lg text-primary tracking-tight">
            {title}
          </h2>
          <p id="confirm-dialog-message" className="font-body-md text-body-md text-on-surface-variant">
            {message}
          </p>
        </div>

        <div className="flex justify-end items-center gap-md pt-md border-t border-[#1A1A1A]">
          <button
            onClick={onCancel}
            className="font-body-md text-body-md text-on-surface px-md min-h-11 md:min-h-9 border border-transparent hover:border-[#1A1A1A] transition-colors"
            type="button"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`font-body-md text-body-md font-medium px-lg min-h-11 md:min-h-9 min-w-[120px] transition-colors ${
              danger
                ? 'bg-red-600 text-white hover:bg-red-500'
                : 'bg-primary text-surface-container-lowest hover:bg-on-surface'
            }`}
            type="button"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDialog
