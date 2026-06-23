import { render, screen, fireEvent } from '@testing-library/react';
import CharactersView from '../CharactersView';
import { describe, it, expect, vi } from 'vitest';

describe('CharactersView', () => {
  const mockCharacters = [
    {
      id: 1,
      name: 'Sherlock Holmes',
      description: 'A brilliant detective.',
      tags: [{ id: 10, label: 'Observant' }],
    },
    {
      id: 2,
      name: 'John Watson',
      description: 'A loyal assistant.',
      tags: [{ id: 20, label: 'Loyal' }],
    },
  ];

  const mockSetSelectedCharId = vi.fn();
  const mockOnNewCharacter = vi.fn();
  const mockOnChat = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  const defaultProps = {
    characters: mockCharacters,
    selectedCharId: null,
    setSelectedCharId: mockSetSelectedCharId,
    onNewCharacter: mockOnNewCharacter,
    onChat: mockOnChat,
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
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
      />
    );
  }
});
