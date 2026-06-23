import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SettingsModal from '../SettingsModal'
import * as api from '../../services/api'

// Mock the API service
vi.mock('../../services/api', () => ({
  fetchRunnerStatus: vi.fn(),
  saveRunnerConfig: vi.fn(),
  startServer: vi.fn(),
  stopServer: vi.fn(),
  restartAllServers: vi.fn()
}))

const mockStatusResponse = {
  inference: {
    running: false,
    config: {
      binary_path: 'llama_bin/llama-server.exe',
      model_path: 'models/qwen.gguf',
      port: 8080,
      threads: 4,
      gpu_layers: -1,
      context_size: 4096,
      additional_args: '--cache-type-k q8_0'
    }
  },
  embedding: {
    running: false,
    config: {
      binary_path: 'llama_bin/llama-server.exe',
      model_path: 'models/qwen-emb.gguf',
      port: 8081,
      threads: 4,
      gpu_layers: -1,
      context_size: 4096,
      additional_args: ''
    }
  },
  available_models: ['qwen.gguf', 'qwen-emb.gguf'],
  available_binaries: ['llama-server.exe']
}

describe('SettingsModal', () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.fetchRunnerStatus).mockResolvedValue(mockStatusResponse)
    vi.mocked(api.saveRunnerConfig).mockResolvedValue({ status: 'success' })
    vi.mocked(api.restartAllServers).mockResolvedValue({ status: 'success' })
  })

  it('renders and displays loaded config values', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    // Wait for the status to load and loading state to end
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Local Narrative Core')).toBeInTheDocument()
    
    // Check ports
    const portInputs = screen.getAllByLabelText('Port')
    expect(portInputs[0]).toHaveValue(8080)
  })

  it('allows switching between Inference and Embedding tabs', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    // Inference tab is active by default, check for inference specific fields
    expect(screen.getByLabelText('Context Size (tokens)')).toBeInTheDocument()

    // Switch to Embedding tab
    const embeddingTabButton = screen.getByText(/Embedding Vector/i)
    fireEvent.click(embeddingTabButton)

    // Check embedding status title
    await waitFor(() => {
      expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
    })
  })

  it('calls saveRunnerConfig and restartAllServers when form is submitted', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    // Modify a field (e.g. CPU Threads)
    const threadsInput = screen.getByLabelText('CPU Threads')
    fireEvent.change(threadsInput, { target: { value: '8' } })

    // Save & Restart AI
    const saveButton = screen.getByText('Save & Restart AI')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(api.saveRunnerConfig).toHaveBeenCalled()
      expect(api.restartAllServers).toHaveBeenCalled()
    })
  })

  it('calls onClose when Cancel button is clicked', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when Close icon button is clicked', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const closeIconButton = screen.getByLabelText('Close modal')
    fireEvent.click(closeIconButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls startServer when START SERVER is clicked', async () => {
    vi.mocked(api.startServer).mockResolvedValue({ status: 'success' })
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const startButton = screen.getByText('START SERVER')
    fireEvent.click(startButton)

    await waitFor(() => {
      expect(api.startServer).toHaveBeenCalledWith('inference')
    })
  })

  it('calls stopServer when STOP SERVER is clicked', async () => {
    const runningStatusResponse = {
      ...mockStatusResponse,
      inference: {
        ...mockStatusResponse.inference,
        running: true
      }
    }
    vi.mocked(api.fetchRunnerStatus).mockResolvedValue(runningStatusResponse)
    vi.mocked(api.stopServer).mockResolvedValue({ status: 'success' })
    
    render(<SettingsModal onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: ACTIVE')).toBeInTheDocument()
    })

    const stopButton = screen.getByText('STOP SERVER')
    fireEvent.click(stopButton)

    await waitFor(() => {
      expect(api.stopServer).toHaveBeenCalledWith('inference')
    })
  })
})
