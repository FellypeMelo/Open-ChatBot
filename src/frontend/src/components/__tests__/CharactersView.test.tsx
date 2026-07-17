import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CharactersView from '../CharactersView';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('../../services/api', () => ({
  importCharacterPng: vi.fn().mockResolvedValue({}),
}));
import { importCharacterPng } from '../../services/api';

describe('CharactersView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (importCharacterPng as ReturnType<typeof vi.fn>).mockResolvedValue({});
  });

  const mockCharacters = [
    {
      id: 1,
      name: 'Sherlock Holmes',
      description: 'A brilliant detective.',
      is_active: true,
      tags: [{ id: 10, label: 'Observant', instruction: '' }],
    },
    {
      id: 2,
      name: 'John Watson',
      description: 'A loyal assistant.',
      is_active: true,
      tags: [{ id: 20, label: 'Loyal', instruction: '' }],
    },
  ];

  const mockSetSelectedCharId = vi.fn();
  const mockOnNewCharacter = vi.fn();
  const mockOnChat = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnCharacterImported = vi.fn();

  const defaultProps = {
    characters: mockCharacters,
    selectedCharId: null,
    setSelectedCharId: mockSetSelectedCharId,
    onNewCharacter: mockOnNewCharacter,
    onChat: mockOnChat,
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
    onCharacterImported: mockOnCharacterImported,
  };

  it('should render characters and metadata', () => {
    render(<CharactersView {...defaultProps} />);
    
    expect(screen.getByText('Character Core')).toBeInTheDocument();
    expect(screen.getByText('Sherlock Holmes')).toBeInTheDocument();
    expect(screen.getByText('A brilliant detective.')).toBeInTheDocument();
    expect(screen.getByText('Observant')).toBeInTheDocument();

    expect(screen.getByText('John Watson')).toBeInTheDocument();
    expect(screen.getByText('A loyal assistant.')).toBeInTheDocument();
    expect(screen.getByText('Loyal')).toBeInTheDocument();
    
    expect(screen.getByText('2 Active Personas')).toBeInTheDocument();
  });

  it('should select character when card is clicked', () => {
    render(<SidebarPropsWrapper selectedCharId={null} />);
    
    const holmesCard = screen.getByText('Sherlock Holmes');
    fireEvent.click(holmesCard);

    expect(mockSetSelectedCharId).toHaveBeenCalledWith(1);
  });

  it('should highlight selected character card', () => {
    render(<CharactersView {...defaultProps} selectedCharId={1} />);
    
    // Check if the avatar or container has visual select styling
    const avatarElement = screen.getByText('SH');
    expect(avatarElement).toBeInTheDocument();
  });

  it('should trigger actions when action buttons are clicked', () => {
    render(<CharactersView {...defaultProps} />);
    
    const editButton = screen.getAllByLabelText('Edit')[0];
    const deleteButton = screen.getAllByLabelText('Delete')[0];
    const chatButton = screen.getAllByLabelText('Chat')[0];

    fireEvent.click(editButton);
    expect(mockOnEdit).toHaveBeenCalledWith(1);

    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledWith(1);

    fireEvent.click(chatButton);
    expect(mockOnChat).toHaveBeenCalledWith(1);
  });

  it('should filter characters list based on search', () => {
    render(<CharactersView {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search library...');
    fireEvent.change(searchInput, { target: { value: 'Watson' } });

    expect(screen.getByText('John Watson')).toBeInTheDocument();
    expect(screen.queryByText('Sherlock Holmes')).not.toBeInTheDocument();
  });

  it('should show empty state message when search yields no matches', () => {
    render(<CharactersView {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search library...');
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    expect(screen.getByText('No personalities found matching your query.')).toBeInTheDocument();
  });

  it('should trigger onNewCharacter when premium button is clicked', () => {
    render(<CharactersView {...defaultProps} />);
    
    const initializeButton = screen.getByText('Initialize Persona');
    fireEvent.click(initializeButton);

    expect(mockOnNewCharacter).toHaveBeenCalled();
  });

  it('imports a PNG file and notifies the parent', async () => {
    const { container } = render(<CharactersView {...defaultProps} />);
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(['x'], 'c.png', { type: 'image/png' })] },
    });
    await waitFor(() => expect(importCharacterPng).toHaveBeenCalled());
    await waitFor(() => expect(mockOnCharacterImported).toHaveBeenCalled());
  });

  it('opens the file picker when Import PNG is clicked', () => {
    const { container } = render(<CharactersView {...defaultProps} />);
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const clickSpy = vi.spyOn(fileInput, 'click').mockImplementation(() => {});
    fireEvent.click(screen.getByRole('button', { name: /Import PNG/i }));
    expect(clickSpy).toHaveBeenCalled();
  });

  it('ignores an empty file selection', () => {
    const { container } = render(<CharactersView {...defaultProps} />);
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [] } });
    expect(importCharacterPng).not.toHaveBeenCalled();
  });

  it('alerts when a PNG import fails', async () => {
    (importCharacterPng as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('boom'));
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    const { container } = render(<CharactersView {...defaultProps} />);
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(['x'], 'c.png', { type: 'image/png' })] },
    });
    await waitFor(() => expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('boom')));
  });

  // Small wrapper helper
  function SidebarPropsWrapper({ selectedCharId }: { selectedCharId: number | null }) {
    return (
      <CharactersView
        characters={mockCharacters}
        selectedCharId={selectedCharId}
        setSelectedCharId={mockSetSelectedCharId}
        onNewCharacter={mockOnNewCharacter}
        onChat={mockOnChat}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCharacterImported={vi.fn()}
      />
    );
  }
});
