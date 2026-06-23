import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TagCreator from '../TagCreator';
import { describe, it, expect, vi } from 'vitest';

describe('TagCreator', () => {
  const mockOnClose = vi.fn();
  const mockOnSubmit = vi.fn();
  
  const defaultProps = {
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
    tag: null,
  };

  it('should render form for creating a new tag', () => {
    render(<TagCreator {...defaultProps} />);
    
    expect(screen.getByText('Create New Tag')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g. Sarcastic, Tactical...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Detailed instructions for the AI on how to embody this tag...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Tag' })).toBeInTheDocument();
  });

  it('should fill form and trigger submit when fields are populated and saved', async () => {
    render(<TagCreator {...defaultProps} />);

    const labelInput = screen.getByLabelText('Tag Label');
    const instructionInput = screen.getByLabelText('Prompt Instruction');
    const submitButton = screen.getByRole('button', { name: 'Create Tag' });

    fireEvent.change(labelInput, { target: { value: 'Sarcastic' } });
    fireEvent.change(instructionInput, { target: { value: 'Be very sarcastic and mocking.' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Sarcastic', 'Be very sarcastic and mocking.');
    });
  });

  it('should prepopulate fields when editing an existing tag', () => {
    const existingTag = {
      id: 1,
      label: 'Gentle',
      instruction: 'Always speak softly and kindly.',
    };

    render(<TagCreator {...defaultProps} tag={existingTag} />);

    expect(screen.getByText('Edit Tag')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Gentle')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Always speak softly and kindly.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save Changes' })).toBeInTheDocument();
  });

  it('should trigger onClose when cancel button is clicked', () => {
    render(<TagCreator {...defaultProps} />);
    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should trigger onClose when close icon button is clicked', () => {
    render(<TagCreator {...defaultProps} />);
    const closeIconButton = screen.getByRole('button', { name: 'Close modal' });
    fireEvent.click(closeIconButton);
    expect(mockOnClose).toHaveBeenCalled();
  });
});
