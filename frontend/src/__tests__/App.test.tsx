import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import App from '../App'
import MessageRenderer from '../components/MessageRenderer'

// Mock fetch
global.fetch = vi.fn()

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
      return Promise.resolve({
        json: () => Promise.resolve({}),
        ok: true
      } as any)
    })
  })

  it('renders the main application structure', async () => {
    render(<App />)
    expect(screen.getByText('Entidades')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Falar com/)).toBeInTheDocument()
    
    // Wait for initial data fetch
    await waitFor(() => {
      const lunaElements = screen.getAllByText('Luna')
      expect(lunaElements.length).toBeGreaterThan(0)
    })
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })

  it('displays the empty state when no messages', () => {
    render(<App />)
    expect(screen.getByText('Pronto para o Roleplay?')).toBeInTheDocument()
  })

  it('handles sending a message and receiving a reply', async () => {
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
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    
    await screen.findAllByText('Luna')
    
    const input = screen.getByPlaceholderText(/Falar com Luna/)
    fireEvent.change(input, { target: { value: 'Hi Luna' } })
    
    const buttons = screen.getAllByRole('button')
    const sendButton = buttons.find(b => b.querySelector('.lucide-send'))!
    fireEvent.click(sendButton)
    
    expect(await screen.findByText('Hi Luna')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/Hello user/)).toBeInTheDocument())
    expect(screen.getByText(/I am thinking/)).toBeInTheDocument()
    expect(screen.getByText(/\*\*waves\*\*/)).toBeInTheDocument()
  })

  it('opens and closes the character creator modal', async () => {
    render(<App />)
    await screen.findAllByText('Luna')
    const addBtn = screen.getAllByRole('button').find(b => b.querySelector('.lucide-plus'))!
    fireEvent.click(addBtn)
    
    expect(await screen.findByText('Criar Nova Entidade')).toBeInTheDocument()
    
    fireEvent.click(screen.getByText('Cancelar'))
    await waitFor(() => expect(screen.queryByText('Criar Nova Entidade')).not.toBeInTheDocument())
  })

  it('creates a new character', async () => {
    const newChar = { id: 2, name: 'Nova', description: 'New AI', tags: [] }
    vi.mocked(fetch).mockImplementation((url, options) => {
      if (url === '/characters/' && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve(newChar),
          ok: true
        } as any)
      }
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')
    const addBtn = screen.getAllByRole('button').find(b => b.querySelector('.lucide-plus'))!
    fireEvent.click(addBtn)
    
    const nameInput = await screen.findByPlaceholderText(/Ex: Luna/)
    fireEvent.change(nameInput, { target: { value: 'Nova' } })
    fireEvent.change(screen.getByPlaceholderText(/Descreva a história/), { target: { value: 'New AI' } })
    
    const submitBtn = screen.getByText('Criar Entidade')
    await act(async () => {
      fireEvent.click(submitBtn)
    })
    
    await waitFor(() => {
      const novaElements = screen.getAllByText('Nova')
      expect(novaElements.length).toBeGreaterThan(0)
    })
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
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')
    
    const profileBtn = await screen.findByText('Test User')
    fireEvent.click(profileBtn)
    
    const nameInput = await screen.findByPlaceholderText(/Como a entidade/)
    fireEvent.change(nameInput, { target: { value: 'New Name' } })
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Female' } })
    
    fireEvent.click(screen.getByText('Salvar Perfil'))
    
    expect(await screen.findByText('New Name')).toBeInTheDocument()
  })

  it('triggers immersion logic after inactivity', async () => {
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      if (url === '/chat') return Promise.resolve({ json: () => Promise.resolve({ reply: 'Hello' }), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    vi.useFakeTimers()
    render(<App />)
    
    await act(async () => {
      vi.runOnlyPendingTimers()
    })

    const input = screen.getByPlaceholderText(/Falar com Luna/)
    fireEvent.change(input, { target: { value: 'Hi' } })
    
    const buttons = screen.getAllByRole('button')
    const sendButton = buttons.find(b => b.querySelector('.lucide-send'))!
    fireEvent.click(sendButton)
    
    await act(async () => {
      vi.runOnlyPendingTimers()
    })

    act(() => {
      vi.advanceTimersByTime(3500)
    })

    const aside = screen.getByRole('complementary')
    expect(aside).toHaveClass('w-0')

    act(() => {
      fireEvent.mouseMove(window)
    })

    expect(aside).toHaveClass('w-64')
    vi.useRealTimers()
  })

  it('handles chat error', async () => {
    vi.mocked(fetch).mockImplementation((url) => {
      if (url === '/chat') return Promise.reject(new Error('Network error'))
      if (url === '/users/me') return Promise.resolve({ json: () => Promise.resolve(mockUser), ok: true } as any)
      if (url === '/characters/') return Promise.resolve({ json: () => Promise.resolve(mockCharacters), ok: true } as any)
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true } as any)
    })

    render(<App />)
    await screen.findAllByText('Luna')
    
    fireEvent.change(screen.getByPlaceholderText(/Falar com Luna/), { target: { value: 'Hi' } })
    const buttons = screen.getAllByRole('button')
    const sendButton = buttons.find(b => b.querySelector('.lucide-send'))!
    
    await act(async () => {
      fireEvent.click(sendButton)
    })
    
    expect(await screen.findByText(/Erro ao comunicar/)).toBeInTheDocument()
  })
})

describe('MessageRenderer Extra', () => {
  it('handles small word clusters at the end', () => {
    const fallback = { content: 'one two three four five' }
    const { container } = render(<MessageRenderer fallback={fallback} isLatest={true} />)
    const spans = container.querySelectorAll('.animate-word-reveal')
    expect(spans.length).toBe(2)
  })
})
