import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CharacterCreator from '../CharacterCreator';
import { describe, it, expect, vi } from 'vitest';

describe('CharacterCreator', () => {
  const mockOnClose = vi.fn();
  const mockOnCreate = vi.fn();
  const mockOnUpdate = vi.fn();
  
  const mockTags = [
    { id: 10, label: 'Brave', instruction: 'Act brave' },
    { id: 20, label: 'Smart', instruction: 'Act smart' },
  ];

  const defaultProps = {
    onClose: mockOnClose,
    onCreate: mockOnCreate,
    onUpdate: mockOnUpdate,
    tags: mockTags,
    editingCharacter: null,
  };

  it('should render form for creating a new character', () => {
    render(<CharacterCreator {...defaultProps} />);
    
    expect(screen.getByText('Create Character')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g. Architect, Elara, Kaelen')).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Describe the character's personality, backstory, and behavior...")).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Initialize' })).toBeInTheDocument();
  });

  it('should fill form, select tags, and submit new character data', async () => {
    render(<CharacterCreator {...defaultProps} />);

    const nameInput = screen.getByLabelText('Name');
    const descInput = screen.getByLabelText('Description');
    const braveTagButton = screen.getByText('Brave');
    const submitButton = screen.getByRole('button', { name: 'Initialize' });

    fireEvent.change(nameInput, { target: { value: 'Elara' } });
    fireEvent.change(descInput, { target: { value: 'A brave scholar' } });
    
    // Select brave tag
    fireEvent.click(braveTagButton);
    
    // Submit
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith('Elara', 'A brave scholar', [10]);
    });
  });

  it('should toggle tags correctly when clicked multiple times', async () => {
    render(<CharacterCreator {...defaultProps} />);

    const nameInput = screen.getByLabelText('Name');
    const descInput = screen.getByLabelText('Description');
    const braveTagButton = screen.getByText('Brave');
    const smartTagButton = screen.getByText('Smart');
    const submitButton = screen.getByRole('button', { name: 'Initialize' });

    fireEvent.change(nameInput, { target: { value: 'Kaelen' } });
    fireEvent.change(descInput, { target: { value: 'A tricky rogue' } });
    
    // Select both tags
    fireEvent.click(braveTagButton);
    fireEvent.click(smartTagButton);
    
    // Deselect brave tag
    fireEvent.click(braveTagButton);
    
    // Submit
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith('Kaelen', 'A tricky rogue', [20]);
    });
  });

  it('should prepopulate fields when editing an existing character and save updates', async () => {
    const existingChar = {
      id: 5,
      name: 'Architect',
      description: 'Builder of worlds',
      tags: [mockTags[1]], // Smart
    };

    render(
      <CharacterCreator
        {...defaultProps}
        editingCharacter={existingChar}
      />
    );

    expect(screen.getByText('Edit Character')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Architect')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Builder of worlds')).toBeInTheDocument();
    
    const braveTagButton = screen.getByText('Brave');
    const saveButton = screen.getByRole('button', { name: 'Save Changes' });

    // Select Brave tag in addition to Smart
    fireEvent.click(braveTagButton);
    
    // Submit
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(5, 'Architect', 'Builder of worlds', [20, 10]);
    });
  });

  it('should display empty message when no tags are provided', () => {
    render(<CharacterCreator {...defaultProps} tags={[]} />);
    expect(screen.getByText('No tags available. Create some in the Archives view.')).toBeInTheDocument();
  });

  it('should call onClose when close buttons are clicked', () => {
    render(<CharacterCreator {...defaultProps} />);
    
    const closeIconButton = screen.getByRole('button', { name: 'Close modal' });
    fireEvent.click(closeIconButton);
    expect(mockOnClose).toHaveBeenCalled();

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalled();
  });
});
