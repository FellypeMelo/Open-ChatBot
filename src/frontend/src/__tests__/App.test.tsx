import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act, within } from '@testing-library/react'
import App from '../App'
import * as messageTreeModule from '../hooks/useMessageTree'

// Wraps the real useMessageTree with a spy so tests can assert on how many
// times its memoized `activePath` was actually recomputed (a NEW reference)
// versus how many times ChatView simply re-rendered -- the crux of the
// per-token streaming decoupling below. Delegates to the real implementation
// throughout, so this is transparent to every other test in this file.
vi.mock('../hooks/useMessageTree', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../hooks/useMessageTree')>()
  return { ...actual, useMessageTree: vi.fn(actual.useMessageTree) }
})

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

  const mockResponse = (data: unknown, ok = true) => {
    return Promise.resolve({
      ok,
      json: () => Promise.resolve(data),
    } as unknown as Response)
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/users/me') {
        return mockResponse(mockUser)
      }
      if (url === '/characters/') {
        return mockResponse(mockCharacters)
      }
      if (url === '/tags/') {
        return mockResponse([])
      }
      if (url === '/lore/') {
        return mockResponse([])
      }
      if (String(url).startsWith('/history/')) {
        return mockResponse([])
      }
      if (url === '/settings/status') {
        return mockResponse({
          inference: { running: false, config: { binary_path: 'llama-server.exe', model_path: '', port: 8080, threads: 4, gpu_layers: -1, context_size: 4096, additional_args: '' } },
          embedding: { running: false, config: { binary_path: 'llama-server.exe', model_path: '', port: 8081, threads: 4, gpu_layers: -1, context_size: 4096, additional_args: '' } },
          available_models: [],
          available_binaries: []
        })
      }
      return mockResponse({})
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
    const newCharacter = { id: 2, name: 'Nova', description: 'New AI', tags: [] }
    vi.mocked(fetch).mockImplementation((url, options) => {
      // NOTE: the initial GET must keep returning only the original roster
      // (not the post-creation roster) -- App appends the POST response to
      // whatever it already has in state, so seeding the GET with the new
      // character too would double it up (and break on duplicate React keys).
      if (url === '/characters/' && options?.method === 'POST') {
        return mockResponse(newCharacter)
      }
      if (url === '/users/me') return mockResponse(mockUser)
      if (url === '/characters/') return mockResponse(mockCharacters)
      if (url === '/tags/') return mockResponse([])
      if (String(url).startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Initialize Persona'))

    const nameInput = await screen.findByPlaceholderText(/A unique title/)
    fireEvent.change(nameInput, { target: { value: 'Nova' } })
    fireEvent.change(screen.getByPlaceholderText(/Provide a short description/), { target: { value: 'New AI' } })

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
        return mockResponse(updatedUser)
      }
      if (url === '/users/me') return mockResponse(mockUser)
      if (url === '/characters/') return mockResponse(mockCharacters)
      if (url === '/tags/') return mockResponse([])
      if (String(url).startsWith('/history/')) return mockResponse([])
      return mockResponse({})
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
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (url === '/users/me') return mockResponse(mockUser)
      if (url === '/characters/') return mockResponse(mockCharacters)
      if (url === '/tags/') return mockResponse([])
      if (String(url).startsWith('/history/')) {
          return mockResponse([])
      }
      return mockResponse({})
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
      if (url === '/users/me') return mockResponse(mockUser)
      if (url === '/characters/') return mockResponse(mockCharacters)
      if (url === '/tags/') return mockResponse([])
      if (String(url).startsWith('/history/')) return mockResponse([])
      return mockResponse({})
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

  // Regression test for the bug fix described in the App.tsx comment: fetchCharacters
  // used to depend on selectedCharId, which meant the mount effect's dependency array
  // ([fetchCharacters, fetchUser, fetchTags, fetchActions]) recreated fetchCharacters
  // (and thus re-ran the whole mount effect) every time the selected character changed.
  // With the functional state update fix, each mount-time fetch should fire exactly
  // once, even after the user switches the active character.
  it('fetches characters, user, tags, and actions exactly once on mount, even after switching the selected character', async () => {
    const charA = mockCharacters[0]
    const charB = { id: 2, name: 'Nova', description: 'Another AI', tags: [] }
    const counts = { user: 0, characters: 0, tags: 0, actions: 0 }

    vi.mocked(fetch).mockImplementation((url) => {
      const u = String(url)
      if (u === '/users/me') {
        counts.user += 1
        return mockResponse(mockUser)
      }
      if (u === '/characters/') {
        counts.characters += 1
        return mockResponse([charA, charB])
      }
      if (u === '/tags/') {
        counts.tags += 1
        return mockResponse([])
      }
      if (u === '/chat/actions') {
        counts.actions += 1
        return mockResponse({ hug: 'Gives a warm hug.' })
      }
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    await screen.findAllByText('Nova')

    expect(counts.user).toBe(1)
    expect(counts.characters).toBe(1)
    expect(counts.tags).toBe(1)
    expect(counts.actions).toBe(1)

    // Switch selected character by starting a chat with Luna, then going back
    // and starting a chat with Nova instead.
    const chatButtons = screen.getAllByRole('button', { name: 'Chat' })
    fireEvent.click(chatButtons[0])
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.click(screen.getByRole('button', { name: /Characters/ }))
    await screen.findAllByText('Luna')

    const chatButtonsAgain = screen.getAllByRole('button', { name: 'Chat' })
    fireEvent.click(chatButtonsAgain[1])
    await screen.findByPlaceholderText(/Write a prompt for Nova/)

    // The mount-time fetches must not have re-fired after the character switch.
    expect(counts.user).toBe(1)
    expect(counts.characters).toBe(1)
    expect(counts.tags).toBe(1)
    expect(counts.actions).toBe(1)
  })

  it('sends a known action using the fetched action message, and a gift id missing from the fetched map renders no button', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        const encoder = new TextEncoder()
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(encoder.encode('data: {"done": true}\n\n'))
            controller.close()
          }
        })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u === '/chat/actions') {
        return mockResponse({
          hug: { id: 'hug', name: 'Hug', icon: 'favorite', message: 'Gives Luna a warm hug.', deltas: { happiness: 5 } }
        })
      }
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    // Known action id ('hug') should use the message resolved from fetchActions.
    fireEvent.click(screen.getByTitle('Interact & Gift'))
    await act(async () => {
      fireEvent.click(screen.getByText('Hug'))
    })
    expect(await screen.findByText('Gives Luna a warm hug.')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByTitle('Interact & Gift')).not.toBeDisabled())

    // A gift id absent from the fetched actions map renders no button for it.
    fireEvent.click(screen.getByTitle('Interact & Gift'))
    fireEvent.click(screen.getByText('Gifting'))
    expect(screen.queryByText('Hot Coffee')).not.toBeInTheDocument()
  })

  it('creates a tag successfully', async () => {
    const newTag = { id: 5, label: 'Witty', instruction: 'Be witty' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/' && options?.method === 'POST') return mockResponse(newTag)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Tag Management')

    fireEvent.click(screen.getByText('Create New Tag'))
    const labelInput = await screen.findByPlaceholderText(/e\.g\. Sarcastic, Tactical/)
    fireEvent.change(labelInput, { target: { value: 'Witty' } })
    fireEvent.change(screen.getByPlaceholderText(/Detailed instructions/), { target: { value: 'Be witty' } })

    await act(async () => {
      fireEvent.click(screen.getByText('Create Tag'))
    })

    expect(await screen.findByText('Tag created.')).toBeInTheDocument()
    expect(screen.getByText('Witty')).toBeInTheDocument()
  })

  it('shows an error toast when tag creation fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/' && options?.method === 'POST') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Tag Management')

    fireEvent.click(screen.getByText('Create New Tag'))
    const labelInput = await screen.findByPlaceholderText(/e\.g\. Sarcastic, Tactical/)
    fireEvent.change(labelInput, { target: { value: 'Witty' } })
    fireEvent.change(screen.getByPlaceholderText(/Detailed instructions/), { target: { value: 'Be witty' } })

    await act(async () => {
      fireEvent.click(screen.getByText('Create Tag'))
    })

    expect(await screen.findByText('Failed to create tag.')).toBeInTheDocument()
  })

  it('updates a tag successfully', async () => {
    const existingTag = { id: 9, label: 'Calm', instruction: 'Stay calm' }
    const updatedTag = { id: 9, label: 'Serene', instruction: 'Stay serene' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/9' && options?.method === 'PUT') return mockResponse(updatedTag)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([existingTag])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Calm')

    fireEvent.click(screen.getByRole('button', { name: /edit/i }))
    const labelInput = await screen.findByDisplayValue('Calm')
    fireEvent.change(labelInput, { target: { value: 'Serene' } })

    await act(async () => {
      fireEvent.click(screen.getByText('Save Changes'))
    })

    expect(await screen.findByText('Tag updated.')).toBeInTheDocument()
    expect(screen.getByText('Serene')).toBeInTheDocument()
  })

  it('shows an error toast when tag update fails', async () => {
    const existingTag = { id: 9, label: 'Calm', instruction: 'Stay calm' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/9' && options?.method === 'PUT') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([existingTag])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Calm')

    fireEvent.click(screen.getByRole('button', { name: /edit/i }))
    await screen.findByDisplayValue('Calm')

    await act(async () => {
      fireEvent.click(screen.getByText('Save Changes'))
    })

    expect(await screen.findByText('Failed to update tag.')).toBeInTheDocument()
  })

  it('deletes a tag successfully', async () => {
    const existingTag = { id: 9, label: 'Calm', instruction: 'Stay calm' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/9' && options?.method === 'DELETE') return mockResponse({})
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([existingTag])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Calm')

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /delete/i }))
    })

    expect(await screen.findByText('Tag deleted.')).toBeInTheDocument()
    expect(screen.queryByText('Calm')).not.toBeInTheDocument()
  })

  it('shows an error toast when tag deletion fails', async () => {
    const existingTag = { id: 9, label: 'Calm', instruction: 'Stay calm' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/tags/9' && options?.method === 'DELETE') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([existingTag])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Calm')

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /delete/i }))
    })

    expect(await screen.findByText('Failed to delete tag.')).toBeInTheDocument()
  })

  it('updates a character successfully', async () => {
    const updatedChar = { ...mockCharacters[0], name: 'Luna Prime' }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'PUT') return mockResponse(updatedChar)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }))
    const nameInput = await screen.findByDisplayValue('Luna')
    fireEvent.change(nameInput, { target: { value: 'Luna Prime' } })

    await act(async () => {
      fireEvent.click(screen.getByText('Save Changes'))
    })

    expect(await screen.findByText('Changes saved.')).toBeInTheDocument()
    expect(await screen.findAllByText('Luna Prime')).not.toHaveLength(0)
  })

  it('shows an error toast when character update fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'PUT') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }))
    await screen.findByDisplayValue('Luna')

    await act(async () => {
      fireEvent.click(screen.getByText('Save Changes'))
    })

    expect(await screen.findByText('Failed to update character.')).toBeInTheDocument()
  })

  it('deletes a character successfully after confirming', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'DELETE') return mockResponse({})
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText('Delete character?')).toBeInTheDocument()
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
    })

    expect(await screen.findByText('Character deleted.')).toBeInTheDocument()
    expect(screen.queryByText('Luna')).not.toBeInTheDocument()
  })

  it('does not delete a character when the confirmation dialog is dismissed', async () => {
    const deleteSpy = vi.fn()
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'DELETE') {
        deleteSpy()
        return mockResponse({})
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Cancel' }))

    expect(deleteSpy).not.toHaveBeenCalled()
    expect(screen.getAllByText('Luna').length).toBeGreaterThan(0)
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('shows an error toast when character deletion fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'DELETE') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    const dialog = await screen.findByRole('alertdialog')
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
    })

    expect(await screen.findByText('Failed to delete character.')).toBeInTheDocument()
  })

  const streamResponse = (chunks: string[]) => {
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        chunks.forEach((c) => controller.enqueue(encoder.encode(c)))
        controller.close()
      }
    })
    return Promise.resolve({ body: stream, ok: true } as unknown as Response)
  }

  it('applies server-provided state and request id from the stream response', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse([
          'data: {"token": "Hi!"}\n\n',
          'data: {"done": true, "state": {"stats": {"energy": 42, "hunger": 0, "relationship": {"score": 50}}}, "request_id": "req-123"}\n\n'
        ])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      // Also reflect the post-stream energy value here: handleStreamResponse
      // re-fetches characters after the stream completes ("Refresh stats"),
      // so the mock must stay consistent with the state pushed via the SSE
      // "state" field or that refetch would clobber it in this test.
      if (u === '/characters/') {
        return mockResponse([
          { ...mockCharacters[0], state: { stats: { energy: 42, hunger: 0, relationship: { score: 50 } } } }
        ])
      }
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    await waitFor(() => expect(screen.queryByText(/Hi!/)).not.toBeNull())
    // The stats bar reflects the new energy value pushed via the "state" field.
    await waitFor(() => expect(screen.getByText('42%')).toBeInTheDocument())
    // The Copy ID control becomes enabled once a request id is attached.
    await waitFor(() => expect(screen.getByTitle('Copy Request ID')).toBeInTheDocument())
  })

  it('reassembles a data frame split across two stream chunks', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // The token frame is deliberately split mid-JSON across two reads.
        return streamResponse([
          'data: {"token": "Split ',
          'works"}\n\n',
          'data: {"done": true}\n\n'
        ])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    await waitFor(() => expect(screen.queryByText(/Split works/)).not.toBeNull())
  })

  it('regenerates an assistant response', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "First reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/First reply/)).not.toBeNull())

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "Second reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    await act(async () => {
      fireEvent.click(screen.getByText('Regenerate'))
    })

    expect(await screen.findByText(/Second reply/)).toBeInTheDocument()
  })

  it('edits a user message successfully and reloads history', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "Reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/chat/message/') && options?.method === 'PUT') return mockResponse({})
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Reply/)).not.toBeNull())

    // After the edit is submitted, App re-fetches history -- reflect the edit there.
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u.startsWith('/chat/message/') && options?.method === 'PUT') return mockResponse({})
      if (u.startsWith('/history/')) {
        return mockResponse([
          { id: 1, parent_id: null, role: 'user', content: 'Edited message', variant_index: 0 }
        ])
      }
      return mockResponse({})
    })

    fireEvent.click(screen.getByTitle('Edit'))
    const textarea = screen.getByDisplayValue('Hi Luna')
    fireEvent.change(textarea, { target: { value: 'Edited message' } })

    await act(async () => {
      fireEvent.click(screen.getByText('SAVE'))
    })

    expect(await screen.findByText('Edited message')).toBeInTheDocument()
  })

  it('shows an error toast when editing a message fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "Reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Reply/)).not.toBeNull())

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u.startsWith('/chat/message/') && options?.method === 'PUT') return mockResponse({}, false)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    fireEvent.click(screen.getByTitle('Edit'))
    await act(async () => {
      fireEvent.click(screen.getByText('SAVE'))
    })

    expect(await screen.findByText('Failed to edit message.')).toBeInTheDocument()
  })

  it('deletes a user message successfully after confirming', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "Reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Reply/)).not.toBeNull())

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u.startsWith('/chat/message/') && options?.method === 'DELETE') return mockResponse({})
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    fireEvent.click(screen.getByTitle('Delete'))
    const dialog = await screen.findByRole('alertdialog')
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
    })

    await waitFor(() => expect(screen.queryByText('Hi Luna')).not.toBeInTheDocument())
  })

  it('shows an error toast when deleting a message fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"token": "Reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Reply/)).not.toBeNull())

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u.startsWith('/chat/message/') && options?.method === 'DELETE') return mockResponse({}, false)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    fireEvent.click(screen.getByTitle('Delete'))
    const dialog = await screen.findByRole('alertdialog')
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
    })

    expect(await screen.findByText('Failed to delete message.')).toBeInTheDocument()
  })

  it('updates character state via the sleep toggle', async () => {
    const napping = { ...mockCharacters[0], state: { ...mockCharacters[0].state, stats: { ...mockCharacters[0].state.stats, is_sleeping: true } } }
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1/state' && options?.method === 'PUT') return mockResponse(napping)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    await act(async () => {
      fireEvent.click(screen.getByText('Sleep'))
    })

    expect(await screen.findByText('Wake')).toBeInTheDocument()
  })

  it('shows an error toast when updating character state fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1/state' && options?.method === 'PUT') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    await act(async () => {
      fireEvent.click(screen.getByText('Sleep'))
    })

    expect(await screen.findByText('Failed to update character state.')).toBeInTheDocument()
  })

  it('clears the chat history after confirming', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/clear/1' && options?.method === 'POST') return mockResponse({})
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))
    const dialog = await screen.findByRole('alertdialog')
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Clear' }))
    })

    expect(await screen.findByText('Conversation cleared.')).toBeInTheDocument()
  })

  it('does not clear the chat when the confirmation dialog is dismissed', async () => {
    const clearSpy = vi.fn()
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/clear/1' && options?.method === 'POST') {
        clearSpy()
        return mockResponse({})
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Cancel' }))

    expect(clearSpy).not.toHaveBeenCalled()
  })

  it('shows an error toast when clearing chat history fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/clear/1' && options?.method === 'POST') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))
    const dialog = await screen.findByRole('alertdialog')
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Clear' }))
    })

    expect(await screen.findByText('Failed to clear conversation history.')).toBeInTheDocument()
  })

  it('starts a new chat non-destructively (no confirm, calls /chat/new)', async () => {
    const newChatSpy = vi.fn()
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/new/1' && options?.method === 'POST') {
        newChatSpy()
        return mockResponse({ chat_id: 99, title: 'New Chat' })
      }
      if (u === '/chat/clear/1') return mockResponse({}, false) // must NOT be called
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/chats/')) return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    await act(async () => {
      fireEvent.click(screen.getByTitle('Start a new chat (keeps this one)'))
    })

    expect(newChatSpy).toHaveBeenCalled()
    // Non-destructive: no confirmation dialog for starting a new chat.
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
    expect(await screen.findByText('Started a new chat.')).toBeInTheDocument()
  })

  it('opens and closes the mobile sidebar drawer', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    // The mobile backdrop overlay only renders once the sidebar drawer is open.
    expect(document.querySelector('.bg-black\\/60')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('menu').closest('button')!)

    const backdrop = document.querySelector('.bg-black\\/60') as HTMLElement
    expect(backdrop).toBeTruthy()
    fireEvent.click(backdrop)

    expect(document.querySelector('.bg-black\\/60')).not.toBeInTheDocument()
  })

  it('opens the user profile modal from the mobile header avatar button', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    const header = document.querySelector('header')!
    fireEvent.click(within(header).getByText('person').closest('button')!)

    expect(await screen.findByPlaceholderText(/How should the AI address/)).toBeInTheDocument()
  })

  it('shows an error toast when character creation fails', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/' && options?.method === 'POST') return mockResponse({}, false)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Initialize Persona'))

    const nameInput = await screen.findByPlaceholderText(/A unique title/)
    fireEvent.change(nameInput, { target: { value: 'Nova' } })
    fireEvent.change(screen.getByPlaceholderText(/Provide a short description/), { target: { value: 'New AI' } })

    await act(async () => {
      fireEvent.click(screen.getByText('Initialize'))
    })

    expect(await screen.findByText('Failed to create character.')).toBeInTheDocument()
    // The modal should stay open on failure so the user can correct and retry.
    expect(screen.getByText('Create Character')).toBeInTheDocument()
  })

  it('shows failure toasts and logs an error when the mount-time fetches fail', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.mocked(fetch).mockImplementation((url) => {
      const u = String(url)
      if (u === '/users/me') return mockResponse({}, false)
      if (u === '/characters/') return mockResponse({}, false)
      if (u === '/tags/') return mockResponse({}, false)
      if (u === '/chat/actions') return mockResponse({}, false)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)

    await waitFor(() => expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch actions'))
    await waitFor(() => expect(screen.queryByText(/Failed to fetch/)).toBeInTheDocument())
  })

  it('opens and closes the tag creator modal in create mode without submitting', async () => {
    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByText('Knowledge Tags'))
    await screen.findByText('Tag Management')

    fireEvent.click(screen.getByText('Create New Tag'))
    const labelInput = await screen.findByPlaceholderText(/e\.g\. Sarcastic, Tactical/)
    expect(labelInput).toBeInTheDocument()

    fireEvent.click(screen.getByText('Cancel'))
    await waitFor(() => expect(screen.queryByPlaceholderText(/e\.g\. Sarcastic, Tactical/)).not.toBeInTheDocument())
  })

  it('opens and closes the user profile modal without submitting', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByText('Test User'))
    expect(await screen.findByText('User Profile')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Cancel'))
    await waitFor(() => expect(screen.queryByText('User Profile')).not.toBeInTheDocument())
  })

  it('deletes a chat session after confirming via the dialog', async () => {
    const deleteChatSpy = vi.fn()
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/1' && options?.method === 'DELETE') {
        deleteChatSpy()
        return mockResponse({})
      }
      if (u === '/chats/1') {
        return mockResponse([
          { id: 1, title: 'Chat A', is_archived: false, is_active: true, message_count: 2 },
          { id: 2, title: 'Chat B', is_archived: false, is_active: false, message_count: 0 }
        ])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.click(screen.getByRole('button', { name: 'Delete this chat session' }))
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText('Delete chat session?')).toBeInTheDocument()
    await act(async () => {
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
    })

    expect(deleteChatSpy).toHaveBeenCalled()
    expect(await screen.findByText('Chat deleted.')).toBeInTheDocument()
  })

  it('shows a toast when the browser goes offline and comes back online', async () => {
    render(<App />)
    await screen.findAllByText('Luna')

    await act(async () => {
      window.dispatchEvent(new Event('offline'))
    })
    expect(await screen.findByText('You are offline. Reconnect to continue chatting.')).toBeInTheDocument()

    // The offline toast is persistent -- confirm it survives well past the
    // normal auto-dismiss window instead of vanishing on its own.
    vi.useFakeTimers()
    try {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000)
      })
    } finally {
      vi.useRealTimers()
    }
    expect(screen.getByText('You are offline. Reconnect to continue chatting.')).toBeInTheDocument()

    await act(async () => {
      window.dispatchEvent(new Event('online'))
    })
    expect(await screen.findByText('Back online.')).toBeInTheDocument()
    // The single-toast state means the online toast replaces the persistent
    // offline one outright -- no orphaned toast left stacked behind it.
    expect(screen.queryByText('You are offline. Reconnect to continue chatting.')).not.toBeInTheDocument()
  })

  it('keeps the connection-lost toast visible past the normal auto-dismiss window (persistent), and Dismiss clears it', async () => {
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/chat/stream') return Promise.reject(new Error('Network error'))
      if (url === '/users/me') return mockResponse(mockUser)
      if (url === '/characters/') return mockResponse(mockCharacters)
      if (url === '/tags/') return mockResponse([])
      if (String(url).startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi' } })

    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    expect(await screen.findByText('Lost connection to AI.')).toBeInTheDocument()

    // Matches App.tsx's TOAST_DURATION_MS -- a persistent toast must not
    // auto-dismiss even after this much time elapses.
    vi.useFakeTimers()
    try {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })
    } finally {
      vi.useRealTimers()
    }
    expect(screen.getByText('Lost connection to AI.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Dismiss' }))
    expect(screen.queryByText('Lost connection to AI.')).not.toBeInTheDocument()
  })

  it('still auto-dismisses a normal (non-persistent) toast after TOAST_DURATION_MS elapses (regression)', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/characters/1' && options?.method === 'DELETE') return mockResponse({})
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    const dialog = await screen.findByRole('alertdialog')

    // Fake timers must be active before the confirm click so the toast's own
    // setTimeout (registered synchronously once the delete call resolves) is
    // captured by them -- see the idle-timeout test above for the same
    // constraint.
    vi.useFakeTimers()
    try {
      await act(async () => {
        fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))
      })
      expect(screen.getByText('Character deleted.')).toBeInTheDocument()

      // Matches App.tsx's TOAST_DURATION_MS.
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })
    } finally {
      vi.useRealTimers()
    }

    expect(screen.queryByText('Character deleted.')).not.toBeInTheDocument()
  })

  it('clicking Retry on the connection-lost toast re-attempts the same turn (no duplicate send) and dismisses the toast', async () => {
    let attempts = 0
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        attempts += 1
        if (attempts === 1) return Promise.reject(new Error('Network error'))
        return streamResponse(['data: {"token": "Recovered"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    expect(await screen.findByText('Lost connection to AI.')).toBeInTheDocument()
    expect(attempts).toBe(1)

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    })

    expect(await screen.findByText(/Recovered/)).toBeInTheDocument()
    expect(screen.queryByText('Lost connection to AI.')).not.toBeInTheDocument()
    expect(attempts).toBe(2)
    // The retry re-sent the failed request, not the user's turn -- exactly
    // one "Hi Luna" bubble, never two.
    expect(screen.getAllByText('Hi Luna')).toHaveLength(1)
  })

  it('a mid-body connection drop (after headers) does NOT offer a full-resend retry, to avoid duplicating the already-committed user turn', async () => {
    // Regression: past the response headers the backend has already committed
    // the user message, so replaying the whole send would create a second user
    // turn under the same parent. This path must reconcile + prompt Regenerate
    // instead of showing the resend-Retry toast.
    let streamAttempts = 0
    const persistedTurn = [
      { id: 50, parent_id: null, role: 'user', content: 'Hi Luna', variant_index: 0 },
      { id: 51, parent_id: 50, role: 'assistant', content: 'half a repl', variant_index: 0 },
    ]
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        streamAttempts += 1
        // Headers arrive (resolves), one token is actually DELIVERED (enqueued
        // on the first pull so it isn't discarded), then the body errors on the
        // next pull -- a dropped connection AFTER the server accepted the turn.
        let pulls = 0
        const stream = new ReadableStream<Uint8Array>({
          pull(controller) {
            pulls += 1
            if (pulls === 1) {
              controller.enqueue(new TextEncoder().encode('data: {"token": "half a repl"}\n\n'))
            } else {
              controller.error(new Error('network drop mid-body'))
            }
          },
        })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      // The backend persisted the user turn + partial reply before/during the
      // drop, so the reconcile finds a real-id turn to adopt.
      if (u.startsWith('/history/')) return mockResponse(streamAttempts >= 1 ? persistedTurn : [])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    // Mid-reply message, NOT the resend-Retry toast, and no Retry control.
    expect(await screen.findByText(/Connection lost mid-reply/)).toBeInTheDocument()
    expect(screen.queryByText('Lost connection to AI.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Retry' })).not.toBeInTheDocument()
    // Exactly one stream attempt (no auto-replay) and one user bubble (no dup).
    expect(streamAttempts).toBe(1)
    expect(screen.getAllByText('Hi Luna')).toHaveLength(1)
  })

  it('surfaces a mid-stream data.error SSE event as a toast and stops the stream', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse(['data: {"error": "Model crashed"}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    expect(await screen.findByText('Model crashed')).toBeInTheDocument()
    // isLoading cleared -- the Stop control reverts back to Send (now
    // disabled only because the composer was optimistically emptied on send).
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Stop generating' })).not.toBeInTheDocument())
    expect(screen.getByText('arrow_upward')).toBeInTheDocument()
  })

  it('cancels an in-flight stream via the Stop button and shows a stopped toast', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // A stream that never enqueues or closes -- simulates a hung connection.
        const stream = new ReadableStream<Uint8Array>({ start() {} })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    const stopBtn = await screen.findByRole('button', { name: 'Stop generating' })
    await act(async () => {
      fireEvent.click(stopBtn)
    })

    expect(await screen.findByText('Generation stopped.')).toBeInTheDocument()
    expect(await screen.findByText('arrow_upward')).toBeInTheDocument()
  })

  it('refetches history after a stopped stream so optimistic temp ids reconcile to the real persisted turn', async () => {
    // Regression: stopping mid-stream used to leave the turn's optimistic
    // user+assistant nodes carrying temporary client ids while the backend
    // persisted the partial reply under REAL ids. A later edit/delete/
    // regenerate then 404'd on the temp id, wedging the chat. The Stop path
    // must refetch history to swap the temp nodes for the real persisted turn.
    let historyCalls = 0
    const persistedTurn = [
      { id: 33, parent_id: null, role: 'user', content: 'Hi Luna', variant_index: 0 },
      { id: 34, parent_id: 33, role: 'assistant', content: 'Persisted partial reply', variant_index: 0 },
    ]
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        const stream = new ReadableStream<Uint8Array>({ start() {} }) // hung
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) {
        historyCalls += 1
        // Empty on the initial load; the backend's real persisted turn once
        // the stopped stream triggers the reconciling refetch.
        return mockResponse(historyCalls === 1 ? [] : persistedTurn)
      }
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    const stopBtn = await screen.findByRole('button', { name: 'Stop generating' })
    await act(async () => {
      fireEvent.click(stopBtn)
    })

    // The stopped turn triggers a second /history/ read whose real-id nodes
    // replace the optimistic temp-id placeholders.
    await waitFor(() => expect(historyCalls).toBeGreaterThanOrEqual(2))
    expect(await screen.findByText('Persisted partial reply')).toBeInTheDocument()
  })

  it('never wipes a streamed partial on Stop while the backend is still persisting it (race-safe reconcile)', async () => {
    // Regression for the "cancel is broken" report: an immediate refetch on
    // Stop could win the race against the backend's teardown partial-save and
    // briefly REPLACE the turn with a history missing the assistant reply --
    // the partial the user just watched stream visibly vanished. The reconcile
    // must wait for the server to catch up before adopting it.
    let historyCalls = 0
    const persisted = [
      { id: 40, parent_id: null, role: 'user', content: 'Hi Luna', variant_index: 0 },
      { id: 41, parent_id: 40, role: 'assistant', content: 'Streamed partial', variant_index: 0 },
    ]
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // Emit one token, then stay open (never close) so Stop lands mid-stream
        // with a non-empty partial already on screen.
        const stream = new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('data: {"token": "Streamed partial"}\n\n'))
          },
        })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) {
        historyCalls += 1
        // 1 = initial load (empty). 2 = first reconcile poll: backend has only
        // the user turn so far (assistant not persisted yet -> "short"). 3+ =
        // caught up with the persisted partial.
        if (historyCalls === 1) return mockResponse([])
        if (historyCalls === 2) return mockResponse([persisted[0]])
        return mockResponse(persisted)
      }
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    const stopBtn = await screen.findByRole('button', { name: 'Stop generating' })
    await act(async () => {
      fireEvent.click(stopBtn)
    })

    // Partial stays visible the whole time, and the reconcile keeps polling
    // past the "short" intermediate history until the backend has caught up.
    await waitFor(() => expect(screen.getByText('Streamed partial')).toBeInTheDocument())
    await waitFor(() => expect(historyCalls).toBeGreaterThanOrEqual(3), { timeout: 3000 })
    expect(screen.getByText('Streamed partial')).toBeInTheDocument()
  })

  it('aborts a stalled stream after the idle timeout and shows a timeout toast', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // A stream that never enqueues or closes -- simulates a hung connection.
        const stream = new ReadableStream<Uint8Array>({ start() {} })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })

    // Fake timers must be installed before the send so the idle-timeout's
    // setTimeout (registered synchronously inside runStream) is captured by
    // them -- testing-library's findBy*/waitFor helpers poll via real timers
    // in this project's setup, so they're avoided entirely from here on.
    vi.useFakeTimers()
    try {
      await act(async () => {
        fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
      })

      // Matches App.tsx's STREAM_IDLE_TIMEOUT_MS -- no token for this long
      // aborts the stream automatically. The timer is (re)armed the moment the
      // response headers arrive, which the mocked fetch resolves immediately.
      await act(async () => {
        await vi.advanceTimersByTimeAsync(120000)
      })
    } finally {
      vi.useRealTimers()
    }

    expect(await screen.findByText('Response timed out. Check your connection.')).toBeInTheDocument()
  })

  it('keeps the message tree referentially stable across every SSE token, rebuilding it only at turn boundaries', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // Five separate token frames -- streamed one at a time, exactly like
        // a real backend would emit them.
        return streamResponse([
          'data: {"token": "H"}\n\n',
          'data: {"token": "e"}\n\n',
          'data: {"token": "l"}\n\n',
          'data: {"token": "l"}\n\n',
          'data: {"token": "o"}\n\n',
          'data: {"done": true}\n\n'
        ])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })

    const spy = vi.mocked(messageTreeModule.useMessageTree)
    spy.mockClear()

    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Hello/)).not.toBeNull())

    // Sanity: the spy is actually wired up and useMessageTree really ran.
    expect(spy.mock.calls.length).toBeGreaterThanOrEqual(1)

    const activePathRefs = new Set(spy.mock.results.map((r) => r.value.activePath))
    // The turn touches `messages` at most twice (the optimistic append, then
    // the single commit on `done`) regardless of how many tokens streamed --
    // never once per token. Before this fix, every token produced a new
    // `messages` reference, so this would have scaled with the 5 tokens above.
    expect(activePathRefs.size).toBeLessThanOrEqual(2)
  })

  it('persists partial assistant content when the stream errors mid-generation, instead of leaving the bubble empty', async () => {
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return streamResponse([
          'data: {"token": "Partial reply before the crash"}\n\n',
          'data: {"error": "Model crashed"}\n\n'
        ])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    expect(await screen.findByText('Model crashed')).toBeInTheDocument()
    await waitFor(() => expect(screen.queryByText(/Partial reply before the crash/)).not.toBeNull())
  })

  it('does not leak an abandoned stream into a different character switched to mid-stream (regression)', async () => {
    const charA = mockCharacters[0] // Luna
    const charB = { id: 2, name: 'Nova', description: 'Another AI', tags: [] }
    const novaHistory = [
      { id: 201, parent_id: null, role: 'user', content: 'Hi Nova', variant_index: 0 },
      { id: 202, parent_id: 201, role: 'assistant', content: 'Hello there, I am Nova.', variant_index: 0 }
    ]

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        // A stream that emits one token then hangs forever -- simulates
        // Luna's generation being abandoned mid-turn by the character switch.
        const stream = new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('data: {"token": "Hello "}\n\n'))
          }
        })
        return Promise.resolve({ body: stream, ok: true } as unknown as Response)
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse([charA, charB])
      if (u === '/tags/') return mockResponse([])
      if (u === '/history/2') return mockResponse(novaHistory)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    await screen.findAllByText('Nova')

    // Start a turn with Luna and let its first token stream in.
    const chatButtons = screen.getAllByRole('button', { name: 'Chat' })
    fireEvent.click(chatButtons[0])
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    await waitFor(() => expect(screen.queryByText(/Hello/)).not.toBeNull(), { timeout: 5000 })

    // Switch to Nova, who already has her own finished conversation, while
    // Luna's stream is still open (never sent `done`).
    fireEvent.click(screen.getByRole('button', { name: /Characters/ }))
    await screen.findAllByText('Luna')
    const chatButtonsAgain = screen.getAllByRole('button', { name: 'Chat' })
    await act(async () => {
      fireEvent.click(chatButtonsAgain[1]) // Nova
    })
    await screen.findByPlaceholderText(/Write a prompt for Nova/)

    // Nova's own, already-persisted reply must be shown -- never Luna's
    // leaked/abandoned stream text.
    expect(await screen.findByText('Hello there, I am Nova.')).toBeInTheDocument()

    // The composer must not be stuck in the loading/"Stop" state for Nova --
    // the switch aborts Luna's orphaned stream instead of waiting out its
    // idle timeout.
    expect(screen.queryByRole('button', { name: 'Stop generating' })).not.toBeInTheDocument()
    expect(screen.getByText('arrow_upward')).toBeInTheDocument()
  })

  it('clears the persistent connection-lost/Retry toast when switching to a different character (regression: a stale Retry could otherwise overwrite the newly-viewed character\'s history)', async () => {
    const charA = mockCharacters[0] // Luna
    const charB = { id: 2, name: 'Nova', description: 'Another AI', tags: [] }
    const novaHistory = [
      { id: 301, parent_id: null, role: 'user', content: 'Hi Nova', variant_index: 0 },
      { id: 302, parent_id: 301, role: 'assistant', content: 'Hello there, I am Nova.', variant_index: 0 }
    ]

    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        return Promise.reject(new Error('Network error'))
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse([charA, charB])
      if (u === '/tags/') return mockResponse([])
      if (u === '/history/2') return mockResponse(novaHistory)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    await screen.findAllByText('Nova')

    // Fail a turn with Luna -> persistent "Lost connection" toast with Retry.
    const chatButtons = screen.getAllByRole('button', { name: 'Chat' })
    fireEvent.click(chatButtons[0])
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    expect(await screen.findByText('Lost connection to AI.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()

    // Switch to Nova, who has her own already-persisted conversation.
    fireEvent.click(screen.getByRole('button', { name: /Characters/ }))
    await screen.findAllByText('Luna')
    const chatButtonsAgain = screen.getAllByRole('button', { name: 'Chat' })
    await act(async () => {
      fireEvent.click(chatButtonsAgain[1]) // Nova
    })
    await screen.findByPlaceholderText(/Write a prompt for Nova/)
    expect(await screen.findByText('Hello there, I am Nova.')).toBeInTheDocument()

    // The stale toast -- and, crucially, its Retry control bound to Luna's
    // failed turn -- must not survive the switch. Left alive, clicking it
    // would (pre-fix) silently overwrite Nova's just-rendered history with
    // Luna's once the retried stream completed, violating the
    // per-(character_id, chat_id) scoping invariant.
    expect(screen.queryByText('Lost connection to AI.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Retry' })).not.toBeInTheDocument()
  })

  it('does not let a slower, earlier chat-history fetch clobber a newer chat switch once it finally resolves (regression: fetchHistory applied setMessages unconditionally, without re-checking the character/chat is still the one on screen)', async () => {
    const charA = mockCharacters[0] // Luna, id 1
    const chatSessions = [
      { id: 10, title: 'Chat A', is_archived: false, is_active: true, message_count: 1 },
      { id: 20, title: 'Chat B', is_archived: false, is_active: false, message_count: 1 }
    ]
    const chatAHistory = [
      { id: 401, parent_id: null, role: 'user', content: 'Message in chat A', variant_index: 0 }
    ]
    const chatBHistory = [
      { id: 501, parent_id: null, role: 'user', content: 'Message in chat B', variant_index: 0 }
    ]

    // Chat A's history is deliberately held open so it resolves AFTER chat B's,
    // even though it was requested first (the exact ordering a fast double
    // chat-switch, or plain network jitter, can produce).
    let resolveChatAHistory: () => void = () => {}
    const chatAGate = new Promise<void>((resolve) => { resolveChatAHistory = resolve })

    vi.mocked(fetch).mockImplementation((url) => {
      const u = String(url)
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse([charA])
      if (u === '/tags/') return mockResponse([])
      if (u === '/chats/1') return mockResponse(chatSessions)
      if (u === '/history/1?chat_id=10') {
        return chatAGate.then(() => ({ ok: true, json: () => Promise.resolve(chatAHistory) } as unknown as Response))
      }
      if (u === '/history/1?chat_id=20') return mockResponse(chatBHistory)
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')

    // Enter the chat view for Luna -- this fires the character-switch effect,
    // which loads her chats (active = chat A, id 10) and kicks off chat A's
    // (deliberately slow) history fetch.
    const chatButtons = screen.getAllByRole('button', { name: 'Chat' })
    fireEvent.click(chatButtons[0])

    // The session picker is populated by loadChats, independent of the still-
    // pending history fetch, so it's available immediately.
    const picker = await screen.findByTitle('Switch chat session')

    // Switch to chat B before chat A's history has resolved. Chat B's own
    // history fetch resolves immediately.
    await act(async () => {
      fireEvent.change(picker, { target: { value: '20' } })
    })
    expect(await screen.findByText('Message in chat B')).toBeInTheDocument()

    // Now let chat A's slow, now-stale fetch finally resolve.
    await act(async () => {
      resolveChatAHistory()
      await chatAGate
    })

    // Chat A's history must not have clobbered chat B's -- the user is still
    // looking at chat B, per the per-(character_id, chat_id) scoping invariant.
    expect(screen.queryByText('Message in chat A')).not.toBeInTheDocument()
    expect(screen.getByText('Message in chat B')).toBeInTheDocument()
  })

  it('clears a leftover persistent connection-lost toast when a new turn is started (regression: a stale Retry could otherwise fire concurrently with a later, unrelated send)', async () => {
    let attempts = 0
    vi.mocked(fetch).mockImplementation((url, options) => {
      const u = String(url)
      if (u === '/chat/stream' && options?.method === 'POST') {
        attempts += 1
        if (attempts === 1) return Promise.reject(new Error('Network error'))
        return streamResponse(['data: {"token": "Second reply"}\n\n', 'data: {"done": true}\n\n'])
      }
      if (u === '/users/me') return mockResponse(mockUser)
      if (u === '/characters/') return mockResponse(mockCharacters)
      if (u === '/tags/') return mockResponse([])
      if (u.startsWith('/history/')) return mockResponse([])
      return mockResponse({})
    })

    render(<App />)
    await screen.findAllByText('Luna')
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    const input = await screen.findByPlaceholderText(/Write a prompt for Luna/)

    fireEvent.change(input, { target: { value: 'First' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })
    expect(await screen.findByText('Lost connection to AI.')).toBeInTheDocument()

    // Without dismissing or retrying, send a second, unrelated message --
    // allowed because isLoading was reset to false in the failed attempt's
    // `finally`.
    fireEvent.change(input, { target: { value: 'Second' } })
    await act(async () => {
      fireEvent.click(screen.getByText('arrow_upward').closest('button')!)
    })

    // The leftover toast from the first failure -- and its now-superseded
    // Retry control -- must not survive into the new turn: left alive, it
    // could fire concurrently with the second (real) stream and clobber the
    // shared streamAbortRef/streamingContent/isLoading state.
    expect(screen.queryByText('Lost connection to AI.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Retry' })).not.toBeInTheDocument()
    expect(await screen.findByText(/Second reply/)).toBeInTheDocument()
  })
})
