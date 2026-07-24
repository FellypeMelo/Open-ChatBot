import { createElement, useCallback, useState } from 'react'
import ConfirmDialog from '../components/ConfirmDialog'

export interface ConfirmOptions {
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
}

type Resolver = (value: boolean) => void

/**
 * Imperative-style replacement for `window.confirm()`. `confirm(opts)`
 * resolves `true`/`false` once the user answers; render `dialog` once near
 * the component root so it has somewhere to mount.
 */
export function useConfirm() {
  const [options, setOptions] = useState<ConfirmOptions | null>(null)
  const [resolver, setResolver] = useState<Resolver | null>(null)

  const confirm = useCallback((opts: ConfirmOptions) => {
    setOptions(opts)
    return new Promise<boolean>((resolve) => {
      setResolver(() => resolve)
    })
  }, [])

  const settle = useCallback((value: boolean) => {
    resolver?.(value)
    setResolver(null)
    setOptions(null)
  }, [resolver])

  const dialog = createElement(ConfirmDialog, {
    open: options !== null,
    title: options?.title ?? '',
    message: options?.message ?? '',
    confirmLabel: options?.confirmLabel,
    cancelLabel: options?.cancelLabel,
    danger: options?.danger,
    onConfirm: () => settle(true),
    onCancel: () => settle(false),
  })

  return { confirm, dialog }
}
