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
    { id: 1, name: 'Luna', description: 'A calm bot', tags: [{ id: 1, label: 'calm' }] }
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
      if (String(url).startsWith('/history/')) {
        return Promise.resolve({
          json: () => Promise.resolve([]),
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
    expect(screen.getAllByText('Characters').length).toBeGreaterThan(0)
    expect(screen.getByText('Manage your AI personas and character profiles.')).toBeInTheDocument()

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

    const addBtn = screen.getByText('New Character')
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
    fireEvent.click(screen.getByText('New Character'))

    const nameInput = await screen.findByPlaceholderText(/e\.g\. Architect/)
    fireEvent.change(nameInput, { target: { value: 'Nova' } })
    fireEvent.change(screen.getByPlaceholderText(/secretly protective/), { target: { value: 'New AI' } })

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
      if (url === '/chat' && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve({
            reply: 'Hello user!',
            thought: 'I am thinking',
            actions: ['waves'],
            stats: { energy: 90, hunger: 10, relationship: { score: 60 } }
          }),
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

    // Click the Chat button on the character card
    const chatBtn = screen.getByRole('button', { name: 'Chat' })
    fireEvent.click(chatBtn)

    // Should now be in chat view
    const input = await screen.findByPlaceholderText(/Speak with Luna/)
    expect(input).toBeInTheDocument()

    fireEvent.change(input, { target: { value: 'Hi Luna' } })

    const sendButton = screen.getByText('arrow_upward').closest('button')!
    fireEvent.click(sendButton)

    expect(await screen.findByText('Hi Luna')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/Hello user/)).toBeInTheDocument())
  })

  it('handles chat error', async () => {
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/chat') return Promise.reject(new Error('Network error'))
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      if (url === '/tags/') return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      if (String(url).startsWith('/history/')) return Promise.resolve({ json: () => Promise.resolve([]), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')

    // Click the Chat button
    fireEvent.click(screen.getByRole('button', { name: 'Chat' }))
    await screen.findByPlaceholderText(/Speak with Luna/)

    fireEvent.change(screen.getByPlaceholderText(/Speak with Luna/), { target: { value: 'Hi' } })
    const sendButton = screen.getByText('arrow_upward').closest('button')!

    await act(async () => {
      fireEvent.click(sendButton)
    })

    expect(await screen.findByText(/Erro ao comunicar/)).toBeInTheDocument()
  })
})
