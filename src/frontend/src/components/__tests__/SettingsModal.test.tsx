import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SettingsModal from '../SettingsModal'

// Mock useSettings hook
const mockSetConfig = vi.fn()
vi.mock('../../hooks/useSettings', () => ({
  useSettings: () => ({
    config: { base_url: 'http://localhost:8080', model_name: 'test-model' },
    setConfig: mockSetConfig
  })
}))

describe('SettingsModal', () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with initial values from config', () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    expect(screen.getByLabelText(/Server URL/i)).toHaveValue('http://localhost:8080')
    expect(screen.getByLabelText(/Model Identifier/i)).toHaveValue('test-model')
  })

  it('calls setConfig and onClose when form is submitted', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    const urlInput = screen.getByLabelText(/Server URL/i)
    const modelInput = screen.getByLabelText(/Model Identifier/i)
    const saveButton = screen.getByText('Save Settings')

    fireEvent.change(urlInput, { target: { value: 'http://127.0.0.1:9090' } })
    fireEvent.change(modelInput, { target: { value: 'new-model' } })
    fireEvent.click(saveButton)

    expect(mockSetConfig).toHaveBeenCalledWith({
      base_url: 'http://127.0.0.1:9090',
      model_name: 'new-model'
    })
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when Cancel button is clicked', () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when Close icon is clicked', () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    const closeIcon = screen.getByLabelText('Close modal')
    fireEvent.click(closeIcon)

    expect(mockOnClose).toHaveBeenCalled()
  })
})
