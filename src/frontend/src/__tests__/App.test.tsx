import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import App from '../App'

// Mock fetch
vi.stubGlobal('fetch', vi.fn())

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = vi.fn()

describe('App', () => {
  const mockUser = { id: 1, name: 'Test User', gender: 'Male', is_active: true }
  const mockCharacters = [
    { 
      id: 1, 
      name: 'Luna', 
      description: 'A calm bot', 
      tags: [{ id: 1, label: 'calm' }],
      state: {
        stats: { energy: 100, hunger: 0, relationship: { score: 50 } }
      }
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/users/me') {
        return Promise.resolve({
          json: () => Promise.resolve(mockUser),
          ok: true
        } as any)
      }
      if (url === '/characters/') {
        return Promise.resolve({
          json: () => Promise.resolve(mockCharacters),
          ok: true
        } as any)
      }
      if (url === '/tags/') {
        return Promise.resolve({
          json: () => Promise.resolve([]),
          ok: true
        } as any)
      }
      if (url === '/lore/') {
        return Promise.resolve({
          json: () => Promise.resolve([]),
          ok: true
        } as any)
      }
      if (String(url).startsWith('/history/')) {
        return Promise.resolve({
          json: () => Promise.resolve([]),
          ok: true
        } as any)
      }
      if (url === '/settings/status') {
        return Promise.resolve({
          json: () => Promise.resolve({
            inference: { running: false, config: { binary_path: 'llama-server.exe', model_path: '', port: 8080, threads: 4, gpu_layers: -1, context_size: 4096, additional_args: '' } },
            embedding: { running: false, config: { binary_path: 'llama-server.exe', model_path: '', port: 8081, threads: 4, gpu_layers: -1, context_size: 4096, additional_args: '' } },
            available_models: [],
            available_binaries: []
          }),
          ok: true
        } as any)
      }
      return Promise.resolve({
        json: () => Promise.resolve({}),
        ok: true
      } as any)
    })
  })

  it('renders the main application structure', async () => {
    render(<App />)
    expect(screen.getAllByText('Character Core').length).toBeGreaterThan(0)
    expect(screen.getByText('NARRATIVE ENGINE')).toBeInTheDocument()

    // Wait for initial data fetch
    await waitFor(() => {
      const lunaElements = screen.getAllByText('Luna')
      expect(lunaElements.length).toBeGreaterThan(0)
    })
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })

  it('opens and closes the character creator modal', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    const addBtn = screen.getByText('Initialize Persona')
    fireEvent.click(addBtn)

    expect(await screen.findByText('Create Character')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Cancel'))
    await waitFor(() => expect(screen.queryByText('Create Character')).not.toBeInTheDocument())
  })

  it('creates a new character', async () => {
    const updatedCharacters = [
      ...mockCharacters,
      { id: 2, name: 'Nova', description: 'New AI', tags: [] }
    ]
    vi.mocked(fetch).mockImplementation((url, options) => {
      if (url === '/characters/' && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve(updatedCharacters[1]),
          ok: true
        } as any)
      }
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(updatedCharacters), ok: true } as any)
      if (url === '/tags/') return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      if (String(url).startsWith('/history/')) return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Initialize Persona'))

    const nameInput = await screen.findByPlaceholderText(/e\.g\. Architect/)
    fireEvent.change(nameInput, { target: { value: 'Nova' } })
    fireEvent.change(screen.getByPlaceholderText(/Describe the character/), { target: { value: 'New AI' } })

    const submitBtn = screen.getByText('Initialize')
    await act(async () => {
      fireEvent.click(submitBtn)
    })

    expect(await screen.findByText('Nova')).toBeInTheDocument()
  })

  it('updates user profile', async () => {
    const updatedUser = { ...mockUser, name: 'New Name', gender: 'Female' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      if (url === '/users/me' && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve(updatedUser),
          ok: true
        } as any)
      }
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      if (url === '/tags/') return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      if (String(url).startsWith('/history/')) return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')

    const profileBtn = await screen.findByText('Test User')
    fireEvent.click(profileBtn)

    const nameInput = await screen.findByPlaceholderText(/How should the AI address/)
    fireEvent.change(nameInput, { target: { value: 'New Name' } })
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Female' } })

    fireEvent.click(screen.getByText('Update Profile'))

    expect(await screen.findByText('New Name')).toBeInTheDocument()
  })

  it('starts chat from character card', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      if (url === '/chat/stream' && options?.method === 'POST') {
        const encoder = new TextEncoder()
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(encoder.encode('data: {"token": "Hello user!"}\n\n'))
            controller.enqueue(encoder.encode('data: {"done": true}\n\n'))
            controller.close()
          }
        })
        return Promise.resolve({ body: stream, ok: true } as any)
      }
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      if (url === '/tags/') return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      if (String(url).startsWith('/history/')) {
          return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      }
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')

    // Click the Chat button
    const chatBtn = screen.getByRole('button', { name: 'Chat' })
    fireEvent.click(chatBtn)

    // Should now be in chat view
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    
    // Type and send
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Hi Luna' } })
    })
    
    const sendButton = screen.getByText('arrow_upward').closest('button')!
    await act(async () => {
      fireEvent.click(sendButton)
    })

    // Wait for user message to appear in the narrative list
    await waitFor(() => {
      expect(screen.queryByText('Hi Luna')).not.toBeNull()
    }, { timeout: 5000 })
    
    // Wait for assistant response
    await waitFor(() => {
      expect(screen.queryByText(/Hello user/)).not.toBeNull()
    }, { timeout: 8000 })
  })

  it('handles chat error', async () => {
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/chat/stream') return Promise.reject(new Error('Network error'))
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      if (url === '/tags/') return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      if (String(url).startsWith('/history/')) return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.change(screen.getByPlaceholderText(/Write a prompt for Luna/), { target: { value: 'Hi' } })
    const sendButton = screen.getByText('arrow_upward').closest('button')!

    await act(async () => {
      fireEvent.click(sendButton)
    })

    expect(await screen.findByText(/Lost connection/)).toBeInTheDocument()
  })

  it('navigates to Lorebook and Knowledge Tags views via sidebar buttons', async () => {
    render(<App />)
    
    // Wait for App to render
    await screen.findAllByText('Luna')

    // Click Lorebook link in sidebar
    const lorebookBtn = screen.getByText('Lorebook')
    fireEvent.click(lorebookBtn)
    
    // Should display Lorebook title
    expect(await screen.findByText('Lorebook & Knowledge')).toBeInTheDocument()

    // Click Knowledge Tags link in sidebar
    const tagsBtn = screen.getByText('Knowledge Tags')
    fireEvent.click(tagsBtn)
    
    // Should display Tag Management title
    expect(await screen.findByText('Tag Management')).toBeInTheDocument()
  })

  it('opens and closes the settings modal', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    const settingsBtn = screen.getByTitle('Settings')
    fireEvent.click(settingsBtn)

    expect(await screen.findByText('Local Narrative Core')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Cancel'))
    await waitFor(() => expect(screen.queryByText('Local Narrative Core')).not.toBeInTheDocument())
  })

  it('opens character creator in edit mode when Edit is clicked', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    // Find and click the edit button on the card (first we hover or hover isn't strictly required in JSDOM unless CSS hides it, click by aria-label)
    const editBtn = screen.getByRole('button', { name: 'Edit' })
    fireEvent.click(editBtn)

    expect(await screen.findByText('Edit Character')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Luna')).toBeInTheDocument()
  })
})
