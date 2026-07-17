import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act, within } from '@testing-library/react'
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

  const mockResponse = (data: unknown, ok = true) => {
    return Promise.resolve({
      ok,
      json: () => Promise.resolve(data),
    } as unknown as Response)
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
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

  it('sends a known action using the fetched action message, and falls back to a placeholder for unknown action ids', async () => {
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
      if (u === '/chat/actions') return mockResponse({ hug: 'Gives Luna a warm hug.' })
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

    // Unknown action id (a gift id not present in the fetched actions map) should
    // fall back to the generic placeholder message.
    fireEvent.click(screen.getByTitle('Interact & Gift'))
    fireEvent.click(screen.getByText('Gifting'))
    await act(async () => {
      fireEvent.click(screen.getByText('Hot Coffee'))
    })
    expect(await screen.findByText('*Performs action: coffee*')).toBeInTheDocument()
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

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
    })

    expect(window.confirm).toHaveBeenCalled()
    expect(await screen.findByText('Character deleted.')).toBeInTheDocument()
    expect(screen.queryByText('Luna')).not.toBeInTheDocument()
  })

  it('does not delete a character when the confirmation dialog is dismissed', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
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

    expect(deleteSpy).not.toHaveBeenCalled()
    expect(screen.getAllByText('Luna').length).toBeGreaterThan(0)
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

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }))
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

    await act(async () => {
      fireEvent.click(screen.getByTitle('Delete'))
    })

    expect(window.confirm).toHaveBeenCalled()
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

    await act(async () => {
      fireEvent.click(screen.getByTitle('Delete'))
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

    await act(async () => {
      fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))
    })

    expect(window.confirm).toHaveBeenCalled()
    expect(await screen.findByText('Conversation cleared.')).toBeInTheDocument()
  })

  it('does not clear the chat when the confirmation dialog is dismissed', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
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

    await act(async () => {
      fireEvent.click(screen.getByTitle("Reset: delete this character's entire history"))
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
    expect(window.confirm).not.toHaveBeenCalled()
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
})
