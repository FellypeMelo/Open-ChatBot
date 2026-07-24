import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ConfirmDialog from '../ConfirmDialog'

describe('ConfirmDialog', () => {
  const baseProps = {
    title: 'Delete this chat?',
    message: 'This cannot be undone.',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
  }

  it('renders nothing when closed', () => {
    const { container } = render(<ConfirmDialog {...baseProps} open={false} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders with an accessible alertdialog role and name when open', () => {
    render(<ConfirmDialog {...baseProps} open />)
    const dialog = screen.getByRole('alertdialog', { name: 'Delete this chat?' })
    expect(dialog).toBeInTheDocument()
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument()
  })

  it('fires onConfirm when the confirm button is clicked', () => {
    const onConfirm = vi.fn()
    render(<ConfirmDialog {...baseProps} open onConfirm={onConfirm} />)
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('fires onCancel when the cancel button is clicked', () => {
    const onCancel = vi.fn()
    render(<ConfirmDialog {...baseProps} open onCancel={onCancel} />)
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('supports custom confirm/cancel labels', () => {
    render(<ConfirmDialog {...baseProps} open confirmLabel="Delete" cancelLabel="Keep it" />)
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Keep it' })).toBeInTheDocument()
  })

  it('fires onCancel on Escape', () => {
    const onCancel = vi.fn()
    render(<ConfirmDialog {...baseProps} open onCancel={onCancel} />)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('fires onCancel when clicking the backdrop, but not when clicking inside the panel', () => {
    const onCancel = vi.fn()
    render(<ConfirmDialog {...baseProps} open onCancel={onCancel} />)
    fireEvent.click(screen.getByText('This cannot be undone.'))
    expect(onCancel).not.toHaveBeenCalled()

    const backdrop = screen.getByRole('alertdialog').parentElement as HTMLElement
    fireEvent.click(backdrop)
    expect(onCancel).toHaveBeenCalledOnce()
  })
})
