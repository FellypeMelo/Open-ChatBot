import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useConfirm } from '../useConfirm'

const Harness = ({ onResult }: { onResult: (v: boolean) => void }) => {
  const { confirm, dialog } = useConfirm()
  return (
    <div>
      <button
        onClick={async () => {
          const result = await confirm({ title: 'Delete entry?', message: 'Permanent.' })
          onResult(result)
        }}
      >
        Trigger
      </button>
      {dialog}
    </div>
  )
}

describe('useConfirm', () => {
  it('does not render the dialog until confirm() is called', () => {
    render(<Harness onResult={() => {}} />)
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('resolves true when the user confirms', async () => {
    let result: boolean | undefined
    render(<Harness onResult={(v) => { result = v }} />)

    fireEvent.click(screen.getByRole('button', { name: 'Trigger' }))
    expect(await screen.findByRole('alertdialog', { name: 'Delete entry?' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))

    await waitFor(() => expect(result).toBe(true))
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('resolves false when the user cancels', async () => {
    let result: boolean | undefined
    render(<Harness onResult={(v) => { result = v }} />)

    fireEvent.click(screen.getByRole('button', { name: 'Trigger' }))
    await screen.findByRole('alertdialog')

    act(() => {
      fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    })

    await waitFor(() => expect(result).toBe(false))
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })
})
