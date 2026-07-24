import { render, screen, fireEvent } from '@testing-library/react';
import TagManagementView from '../TagManagementView';
import { describe, it, expect, vi } from 'vitest';

describe('TagManagementView', () => {
  const mockTags = [
    { id: 1, label: 'Sarcastic', instruction: 'Make sarcastic remarks.' },
    { id: 2, label: 'Tactical', instruction: 'Speak only about tactics.' },
  ];
  const mockUsage = { 1: 5, 2: 0 };
  const mockOnCreateTag = vi.fn();
  const mockOnEditTag = vi.fn();
  const mockOnDeleteTag = vi.fn();

  const defaultProps = {
    tags: mockTags,
    onCreateTag: mockOnCreateTag,
    onEditTag: mockOnEditTag,
    onDeleteTag: mockOnDeleteTag,
    usage: mockUsage,
  };

  it('should render tags and usage information', () => {
    render(<TagManagementView {...defaultProps} />);
    
    expect(screen.getByText('Tag Management')).toBeInTheDocument();
    expect(screen.getByText('Sarcastic')).toBeInTheDocument();
    expect(screen.getByText('Make sarcastic remarks.')).toBeInTheDocument();
    expect(screen.getByText('Used: 5x')).toBeInTheDocument();

    expect(screen.getByText('Tactical')).toBeInTheDocument();
    expect(screen.getByText('Speak only about tactics.')).toBeInTheDocument();
    expect(screen.getByText('Used: 0x')).toBeInTheDocument();
  });

  it('should filter tags based on search input', () => {
    render(<TagManagementView {...defaultProps} />);
    
    const filterInput = screen.getByPlaceholderText('Filter tags...');
    fireEvent.change(filterInput, { target: { value: 'Tactical' } });

    expect(screen.getByText('Tactical')).toBeInTheDocument();
    expect(screen.queryByText('Sarcastic')).not.toBeInTheDocument();
  });

  it('should keep the tag filter input visible (not `hidden`) so it works on mobile', () => {
    render(<TagManagementView {...defaultProps} />);

    const filterInput = screen.getByPlaceholderText('Filter tags...');
    const wrapper = filterInput.parentElement as HTMLElement;
    expect(wrapper.className).not.toMatch(/\bhidden\b/);
    expect(wrapper.className).toContain('w-full');
  });

  it('should trigger onCreateTag when Create button is clicked', () => {
    render(<TagManagementView {...defaultProps} />);
    
    const createButton = screen.getByRole('button', { name: /Create New Tag/i });
    fireEvent.click(createButton);

    expect(mockOnCreateTag).toHaveBeenCalled();
  });

  it('should show edit and delete actions and trigger them when clicked', () => {
    render(<TagManagementView {...defaultProps} />);
    
    const editButtons = screen.getAllByRole('button');
    
    const editButton = editButtons.find(btn => btn.querySelector('span')?.textContent === 'edit');
    if (editButton) {
      fireEvent.click(editButton);
      expect(mockOnEditTag).toHaveBeenCalledWith(mockTags[0]);
    }

    const deleteButton = editButtons.find(btn => btn.querySelector('span')?.textContent === 'delete');
    if (deleteButton) {
      fireEvent.click(deleteButton);
      expect(mockOnDeleteTag).toHaveBeenCalledWith(mockTags[0].id);
    }
  });

  it('should render empty state when no tags match filter', () => {
    render(<TagManagementView {...defaultProps} />);
    
    const filterInput = screen.getByPlaceholderText('Filter tags...');
    fireEvent.change(filterInput, { target: { value: 'nonexistent' } });

    expect(screen.getByText('No tags match your filter. Use the "Create New Tag" button to add more taxonomy entries.')).toBeInTheDocument();
  });
});
