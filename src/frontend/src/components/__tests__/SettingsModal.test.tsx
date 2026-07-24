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
  restartAllServers: vi.fn(),
  fetchPresets: vi.fn(),
  updatePreset: vi.fn()
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

const mockPresets: api.SamplerPreset[] = [
  {
    id: 1,
    name: 'Default Preset',
    is_default: true,
    temperature: 0.7,
    min_p: 0.05,
    top_k: 40,
    top_p: 0.9,
    repeat_penalty: 1.1,
    dry_multiplier: 0.8,
    dry_base: 1.75,
    dry_range: 0,
    xtc_threshold: 0.1,
    xtc_probability: 0
  },
  {
    id: 2,
    name: 'Creative Preset',
    is_default: false,
    temperature: 1.0,
    min_p: 0.02,
    top_k: 50,
    top_p: 0.95,
    repeat_penalty: 1.05,
    dry_multiplier: 0.8,
    dry_base: 1.75,
    dry_range: 0,
    xtc_threshold: 0.1,
    xtc_probability: 0
  }
]

describe('SettingsModal', () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'alert').mockImplementation(() => {})
    vi.mocked(api.fetchRunnerStatus).mockResolvedValue(mockStatusResponse)
    vi.mocked(api.saveRunnerConfig).mockResolvedValue({ status: 'success' })
    vi.mocked(api.restartAllServers).mockResolvedValue({ status: 'success' })
    vi.mocked(api.fetchPresets).mockResolvedValue(mockPresets)
    vi.mocked(api.updatePreset).mockResolvedValue({ status: 'success' })
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

  it('sizes form inputs and selects to avoid iOS Safari focus-zoom', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    expect(screen.getByLabelText('Port').className).toContain('text-base md:text-sm')
    expect(screen.getByLabelText('Active GGUF Model').className).toContain('text-base md:text-sm')
  })

  it('gives the modal panel its own bounded height and scroll region', async () => {
    const { container } = render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const panel = container.querySelector('[class*="max-h-[90vh]"]')
    expect(panel).not.toBeNull()
    expect(panel?.className).toContain('overflow-y-auto')
  })

  it('keeps the footer pinned to the bottom of the scroll region', async () => {
    const { container } = render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const footer = container.querySelector('[class*="sticky"][class*="bottom-0"]')
    expect(footer).not.toBeNull()
    expect(footer?.className).toContain('sticky')
    expect(footer?.className).toContain('bottom-0')
  })

  it('lets the tab bar scroll horizontally instead of clipping on narrow viewports', async () => {
    const { container } = render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const tabBar = container.querySelector('[class*="overflow-x-auto"]')
    expect(tabBar).not.toBeNull()

    const samplersTab = screen.getByText('Samplers')
    expect(samplersTab.className).toContain('whitespace-nowrap')
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

    // Switch back to the Inference tab
    const inferenceTabButton = screen.getByText(/Inference Engine/i)
    fireEvent.click(inferenceTabButton)

    await waitFor(() => {
      expect(screen.getByLabelText('Context Size (tokens)')).toBeInTheDocument()
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
    // loadStatus() populates form fields from fetchRunnerStatus() *then* awaits
    // fetchPresets() before clearing the loading flag that disables START
    // SERVER (disabled={loading || !infModel}) -- wait for that second fetch
    // and the button's enabled state too, or a slower run can click while
    // it's still disabled and startServer never fires (same CI-only flake
    // class fixed for the Save buttons in 087bdd4/d4b789d).
    await waitFor(() => {
      expect(api.fetchPresets).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(screen.getByText('START SERVER')).not.toBeDisabled()
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

  it('shows an error message when the initial status fetch fails', async () => {
    vi.mocked(api.fetchRunnerStatus).mockRejectedValue(new Error('network error'))
    render(<SettingsModal onClose={mockOnClose} />)

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch AI runner status from backend.')).toBeInTheDocument()
    })
  })

  describe('GPU layers regression (clearing/invalid input resets to -1)', () => {
    it('resets the inference GPU layers field instead of leaking NaN', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      const gpuInput = screen.getByLabelText('GPU Layers (-1 to disable)') as HTMLInputElement
      expect(gpuInput).toHaveValue(-1)

      fireEvent.change(gpuInput, { target: { value: '12' } })
      expect(gpuInput).toHaveValue(12)

      fireEvent.change(gpuInput, { target: { value: '' } })
      expect(gpuInput).toHaveValue(-1)

      fireEvent.change(gpuInput, { target: { value: '20' } })
      expect(gpuInput).toHaveValue(20)

      fireEvent.change(gpuInput, { target: { value: 'not-a-number' } })
      expect(gpuInput).toHaveValue(-1)
    })

    it('resets the embedding GPU layers field instead of leaking NaN', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Embedding Vector/i))
      await waitFor(() => {
        expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
      })

      const gpuInput = screen.getByLabelText('GPU Layers (-1 to disable)') as HTMLInputElement
      expect(gpuInput).toHaveValue(-1)

      fireEvent.change(gpuInput, { target: { value: '6' } })
      expect(gpuInput).toHaveValue(6)

      fireEvent.change(gpuInput, { target: { value: '' } })
      expect(gpuInput).toHaveValue(-1)

      fireEvent.change(gpuInput, { target: { value: '9' } })
      expect(gpuInput).toHaveValue(9)

      fireEvent.change(gpuInput, { target: { value: 'nope' } })
      expect(gpuInput).toHaveValue(-1)
    })
  })

  it('updates and falls back on invalid inference context size input', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const contextInput = screen.getByLabelText('Context Size (tokens)') as HTMLInputElement
    expect(contextInput).toHaveValue(4096)

    fireEvent.change(contextInput, { target: { value: '8192' } })
    expect(contextInput).toHaveValue(8192)

    fireEvent.change(contextInput, { target: { value: '' } })
    expect(contextInput).toHaveValue(4096)
  })

  it('falls back to default port and thread values when the inference fields are cleared', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const portInput = screen.getByLabelText('Port') as HTMLInputElement
    fireEvent.change(portInput, { target: { value: '9090' } })
    expect(portInput).toHaveValue(9090)
    fireEvent.change(portInput, { target: { value: '' } })
    expect(portInput).toHaveValue(8080)

    const threadsInput = screen.getByLabelText('CPU Threads') as HTMLInputElement
    fireEvent.change(threadsInput, { target: { value: '16' } })
    expect(threadsInput).toHaveValue(16)
    fireEvent.change(threadsInput, { target: { value: '' } })
    expect(threadsInput).toHaveValue(4)
  })

  it('falls back to default port and thread values when the embedding fields are cleared', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText(/Embedding Vector/i))
    await waitFor(() => {
      expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
    })

    const portInput = screen.getByLabelText('Port') as HTMLInputElement
    fireEvent.change(portInput, { target: { value: '9091' } })
    expect(portInput).toHaveValue(9091)
    fireEvent.change(portInput, { target: { value: '' } })
    expect(portInput).toHaveValue(8081)

    const threadsInput = screen.getByLabelText('CPU Threads') as HTMLInputElement
    fireEvent.change(threadsInput, { target: { value: '2' } })
    expect(threadsInput).toHaveValue(2)
    fireEvent.change(threadsInput, { target: { value: '' } })
    expect(threadsInput).toHaveValue(4)
  })

  it('updates the inference additional CLI arguments field', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const argsInput = screen.getByLabelText('Additional CLI Arguments') as HTMLInputElement
    expect(argsInput).toHaveValue('--cache-type-k q8_0')
    fireEvent.change(argsInput, { target: { value: '--foo bar' } })
    expect(argsInput).toHaveValue('--foo bar')
  })

  it('updates the embedding additional CLI arguments field', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText(/Embedding Vector/i))
    await waitFor(() => {
      expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
    })

    const argsInput = screen.getByLabelText('Additional CLI Arguments') as HTMLInputElement
    expect(argsInput).toHaveValue('')
    fireEvent.change(argsInput, { target: { value: '--pooling cls' } })
    expect(argsInput).toHaveValue('--pooling cls')
  })

  it('updates inference binary and model selects, including clearing the model', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    const modelSelect = screen.getByLabelText('Active GGUF Model') as HTMLSelectElement
    expect(modelSelect).toHaveValue('qwen.gguf')

    fireEvent.change(modelSelect, { target: { value: '' } })
    expect(modelSelect).toHaveValue('')

    fireEvent.change(modelSelect, { target: { value: 'qwen-emb.gguf' } })
    expect(modelSelect).toHaveValue('qwen-emb.gguf')

    const binarySelect = screen.getByLabelText('Runner Binary') as HTMLSelectElement
    fireEvent.change(binarySelect, { target: { value: 'llama-server.exe' } })
    expect(binarySelect).toHaveValue('llama-server.exe')
  })

  it('updates embedding binary and model selects, including clearing the model', async () => {
    render(<SettingsModal onClose={mockOnClose} />)
    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText(/Embedding Vector/i))
    await waitFor(() => {
      expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
    })

    const modelSelect = screen.getByLabelText('Active GGUF Model') as HTMLSelectElement
    expect(modelSelect).toHaveValue('qwen-emb.gguf')

    fireEvent.change(modelSelect, { target: { value: '' } })
    expect(modelSelect).toHaveValue('')

    fireEvent.change(modelSelect, { target: { value: 'qwen.gguf' } })
    expect(modelSelect).toHaveValue('qwen.gguf')

    const binarySelect = screen.getByLabelText('Runner Binary') as HTMLSelectElement
    fireEvent.change(binarySelect, { target: { value: 'llama-server.exe' } })
    expect(binarySelect).toHaveValue('llama-server.exe')
  })

  it('shows fallback options when no models or binaries are available', async () => {
    vi.mocked(api.fetchRunnerStatus).mockResolvedValue({
      ...mockStatusResponse,
      available_models: [],
      available_binaries: []
    })
    render(<SettingsModal onClose={mockOnClose} />)

    await waitFor(() => {
      expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
    })

    expect(await screen.findByText('No models in ./models directory. Add GGUF files.')).toBeInTheDocument()
    expect(await screen.findByText('llama-server.exe (Default)')).toBeInTheDocument()
  })

  describe('Save & Restart flow', () => {
    it('saves a non-consolidated payload, restarts servers, reloads status and alerts success', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      // loadStatus() populates form fields from fetchRunnerStatus() *then* awaits
      // fetchPresets() before clearing the loading flag that disables Save --
      // wait for that second fetch too, or a slower CI run can click while the
      // button is still disabled/mid-load, and saveRunnerConfig never fires.
      await waitFor(() => {
        expect(api.fetchPresets).toHaveBeenCalled()
      })
      await waitFor(() => {
        expect(screen.getByText('Save & Restart AI')).not.toBeDisabled()
      })

      fireEvent.click(screen.getByText('Save & Restart AI'))

      await waitFor(() => {
        expect(api.saveRunnerConfig).toHaveBeenCalledWith({
          inference: {
            binary_path: 'llama_bin/llama-server.exe',
            model_path: 'models/qwen.gguf',
            port: 8080,
            threads: 4,
            gpu_layers: -1,
            context_size: 4096,
            additional_args: '--cache-type-k q8_0'
          },
          embedding: {
            binary_path: 'llama_bin/llama-server.exe',
            model_path: 'models/qwen-emb.gguf',
            port: 8081,
            threads: 4,
            gpu_layers: -1,
            context_size: 4096,
            additional_args: ''
          }
        })
        expect(api.restartAllServers).toHaveBeenCalled()
      })

      await waitFor(() => {
        expect(window.alert).toHaveBeenCalledWith('AI Configuration updated and servers restarted successfully!')
      })
      // Initial mount load + reload after save
      expect(api.fetchRunnerStatus).toHaveBeenCalledTimes(2)
    })

    it('saves a consolidated payload that mirrors inference settings into embedding', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Embedding Vector/i))
      await waitFor(() => {
        expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
      })

      const consolidatedToggle = screen.getByRole('checkbox')
      fireEvent.click(consolidatedToggle)

      await waitFor(() => {
        expect(screen.getByText('Managed by Inference')).toBeInTheDocument()
      })
      await waitFor(() => {
        expect(screen.getByText('Save & Restart AI')).not.toBeDisabled()
      })

      fireEvent.click(screen.getByText('Save & Restart AI'))

      await waitFor(() => {
        expect(api.saveRunnerConfig).toHaveBeenCalledWith(
          expect.objectContaining({
            embedding: expect.objectContaining({
              binary_path: 'llama_bin/llama-server.exe',
              model_path: 'models/qwen.gguf',
              port: 8080,
              threads: 4,
              gpu_layers: -1,
              context_size: 4096,
              additional_args: '--cache-type-k q8_0'
            })
          })
        )
      })
    })

    it('shows the backend error message when saving fails with an Error', async () => {
      vi.mocked(api.saveRunnerConfig).mockRejectedValue(new Error('Disk full'))
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      await waitFor(() => {
        expect(screen.getByText('Save & Restart AI')).not.toBeDisabled()
      })

      fireEvent.click(screen.getByText('Save & Restart AI'))

      await waitFor(() => {
        expect(screen.getByText('Disk full')).toBeInTheDocument()
      })
      expect(api.restartAllServers).not.toHaveBeenCalled()
    })

    it('shows a generic error message when saving fails with a non-Error rejection', async () => {
      vi.mocked(api.saveRunnerConfig).mockRejectedValue('network down')
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      await waitFor(() => {
        expect(screen.getByText('Save & Restart AI')).not.toBeDisabled()
      })

      fireEvent.click(screen.getByText('Save & Restart AI'))

      await waitFor(() => {
        expect(screen.getByText('Failed to save settings.')).toBeInTheDocument()
      })
    })

    it('does nothing when the form is submitted before the initial status has loaded', async () => {
      let resolveStatus: (value: typeof mockStatusResponse) => void = () => {}
      vi.mocked(api.fetchRunnerStatus).mockReturnValue(
        new Promise<typeof mockStatusResponse>(resolve => {
          resolveStatus = resolve
        })
      )

      const { container } = render(<SettingsModal onClose={mockOnClose} />)

      const form = container.querySelector('form') as HTMLFormElement
      fireEvent.submit(form)

      expect(api.saveRunnerConfig).not.toHaveBeenCalled()

      resolveStatus(mockStatusResponse)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
    })
  })

  describe('Start/Stop server error handling', () => {
    it('shows the backend error message when starting the inference server fails', async () => {
      vi.mocked(api.startServer).mockRejectedValue(new Error('port already bound'))
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('START SERVER'))

      await waitFor(() => {
        expect(screen.getByText('port already bound')).toBeInTheDocument()
      })
    })

    it('shows a generic error message when starting the inference server fails without an Error object', async () => {
      vi.mocked(api.startServer).mockRejectedValue('bad path')
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('START SERVER'))

      await waitFor(() => {
        expect(screen.getByText('Failed to start inference server. Check GGUF path.')).toBeInTheDocument()
      })
    })

    it('shows the backend error message when stopping the inference server fails', async () => {
      const runningStatusResponse = {
        ...mockStatusResponse,
        inference: { ...mockStatusResponse.inference, running: true }
      }
      vi.mocked(api.fetchRunnerStatus).mockResolvedValue(runningStatusResponse)
      vi.mocked(api.stopServer).mockRejectedValue(new Error('process pinned'))
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: ACTIVE')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('STOP SERVER'))

      await waitFor(() => {
        expect(screen.getByText('process pinned')).toBeInTheDocument()
      })
    })

    it('shows a generic error message when stopping the inference server fails without an Error object', async () => {
      const runningStatusResponse = {
        ...mockStatusResponse,
        inference: { ...mockStatusResponse.inference, running: true }
      }
      vi.mocked(api.fetchRunnerStatus).mockResolvedValue(runningStatusResponse)
      vi.mocked(api.stopServer).mockRejectedValue('boom')
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: ACTIVE')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('STOP SERVER'))

      await waitFor(() => {
        expect(screen.getByText('Failed to stop inference server.')).toBeInTheDocument()
      })
    })

    it('dismisses the error banner when the close (x) button is clicked', async () => {
      vi.mocked(api.startServer).mockRejectedValue(new Error('boom'))
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('START SERVER'))
      await waitFor(() => {
        expect(screen.getByText('boom')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('✕'))
      expect(screen.queryByText('boom')).not.toBeInTheDocument()
    })
  })

  describe('Embedding server start/stop', () => {
    it('calls startServer with "embedding" when the embedding START SERVER button is clicked', async () => {
      vi.mocked(api.startServer).mockResolvedValue({ status: 'success' })
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Embedding Vector/i))
      await waitFor(() => {
        expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('START SERVER'))

      await waitFor(() => {
        expect(api.startServer).toHaveBeenCalledWith('embedding')
      })
    })

    it('calls stopServer with "embedding" when a running embedding server is stopped', async () => {
      const runningEmbeddingResponse = {
        ...mockStatusResponse,
        embedding: { ...mockStatusResponse.embedding, running: true }
      }
      vi.mocked(api.fetchRunnerStatus).mockResolvedValue(runningEmbeddingResponse)
      vi.mocked(api.stopServer).mockResolvedValue({ status: 'success' })
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Embedding Vector/i))
      await waitFor(() => {
        expect(screen.getByText('Embedding Server: ACTIVE')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('STOP SERVER'))

      await waitFor(() => {
        expect(api.stopServer).toHaveBeenCalledWith('embedding')
      })
    })
  })

  describe('Consolidated server mode', () => {
    it('disables and syncs embedding fields when enabled, and resets the port when disabled', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Embedding Vector/i))
      await waitFor(() => {
        expect(screen.getByText('Embedding Server: STOPPED')).toBeInTheDocument()
      })

      const embPortInput = screen.getByLabelText('Port') as HTMLInputElement
      expect(embPortInput).toHaveValue(8081)
      expect(embPortInput).not.toBeDisabled()

      const consolidatedToggle = screen.getByRole('checkbox')
      fireEvent.click(consolidatedToggle)

      await waitFor(() => {
        expect(screen.getByText('Managed by Inference')).toBeInTheDocument()
      })

      expect(embPortInput).toHaveValue(8080)
      expect(embPortInput).toBeDisabled()
      expect(screen.getByLabelText('Runner Binary')).toBeDisabled()
      expect(screen.getByLabelText('Active GGUF Model')).toBeDisabled()
      expect(screen.getByLabelText('CPU Threads')).toBeDisabled()
      expect(screen.getByLabelText('GPU Layers (-1 to disable)')).toBeDisabled()
      expect(screen.getByLabelText('Additional CLI Arguments')).toBeDisabled()
      expect(screen.getByText(/Sharing port 8080 and model qwen\.gguf/)).toBeInTheDocument()

      fireEvent.click(consolidatedToggle)

      await waitFor(() => {
        expect(embPortInput).toHaveValue(8081)
      })
      expect(embPortInput).not.toBeDisabled()
    })
  })

  describe('Samplers tab', () => {
    it('renders preset options and the active default preset details', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Samplers'))

      await waitFor(() => {
        expect(screen.getByText('Global Sampler Preset')).toBeInTheDocument()
      })

      expect(screen.getByText('temperature')).toBeInTheDocument()
      expect(screen.getByText('0.7')).toBeInTheDocument()
    })

    it('updates the default preset when a different preset is selected', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      fireEvent.click(screen.getByText('Samplers'))
      await waitFor(() => {
        expect(screen.getByText('Global Sampler Preset')).toBeInTheDocument()
      })

      const presetSelect = screen.getByRole('combobox')
      fireEvent.change(presetSelect, { target: { value: '2' } })

      await waitFor(() => {
        expect(api.updatePreset).toHaveBeenCalledWith(2, expect.objectContaining({ id: 2, is_default: true }))
        expect(api.fetchPresets).toHaveBeenCalledTimes(2)
      })
    })

    it('does nothing when the preset selection resolves to an empty/falsy id', async () => {
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      fireEvent.click(screen.getByText('Samplers'))
      await waitFor(() => {
        expect(screen.getByText('Global Sampler Preset')).toBeInTheDocument()
      })

      const presetSelect = screen.getByRole('combobox')
      fireEvent.change(presetSelect, { target: { value: '' } })

      expect(api.updatePreset).not.toHaveBeenCalled()
    })

    it('shows an error message when updating the default preset fails', async () => {
      vi.mocked(api.updatePreset).mockRejectedValue(new Error('nope'))
      render(<SettingsModal onClose={mockOnClose} />)
      await waitFor(() => {
        expect(screen.getByText('Inference Engine: STOPPED')).toBeInTheDocument()
      })
      fireEvent.click(screen.getByText('Samplers'))
      await waitFor(() => {
        expect(screen.getByText('Global Sampler Preset')).toBeInTheDocument()
      })

      const presetSelect = screen.getByRole('combobox')
      fireEvent.change(presetSelect, { target: { value: '2' } })

      await waitFor(() => {
        expect(screen.getByText('Failed to update default preset.')).toBeInTheDocument()
      })
    })
  })
})
