import { render, screen, fireEvent } from '@testing-library/react';
import Sidebar from '../Sidebar';
import { describe, it, expect, vi } from 'vitest';

describe('Sidebar', () => {
  const mockSetView = vi.fn();
  const mockOnProfileClick = vi.fn();
  const mockOnSettingsClick = vi.fn();
  const mockOnClose = vi.fn();

  const defaultProps = {
    currentView: 'characters',
    setView: mockSetView,
    userName: 'John Doe',
    onProfileClick: mockOnProfileClick,
    onSettingsClick: mockOnSettingsClick,
    isOpen: true,
    onClose: mockOnClose,
  };

  it('should render brand header and navigation links', () => {
    render(<Sidebar {...defaultProps} />);
    
    expect(screen.getByText('Open-ChatBot')).toBeInTheDocument();
    expect(screen.getByText('Writers Room')).toBeInTheDocument();
    
    expect(screen.getByText('Characters')).toBeInTheDocument();
    expect(screen.getByText('Direct Chat')).toBeInTheDocument();
    expect(screen.getByText('Lorebook')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Tags')).toBeInTheDocument();
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('should highlight the active navigation item', () => {
    render(<Sidebar {...defaultProps} currentView="library" />);
    
    const lorebookButton = screen.getByRole('button', { name: /Lorebook/i });
    expect(lorebookButton).toHaveClass('bg-white');
    expect(lorebookButton).toHaveClass('text-black');
  });

  it('should trigger setView and onClose when a navigation button is clicked', () => {
    render(<Sidebar {...defaultProps} />);
    
    const chatButton = screen.getByRole('button', { name: /Direct Chat/i });
    fireEvent.click(chatButton);

    expect(mockSetView).toHaveBeenCalledWith('chat');
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should trigger onProfileClick and onClose when user profile is clicked', () => {
    render(<Sidebar {...defaultProps} />);
    
    const profileDiv = screen.getByText('John Doe');
    fireEvent.click(profileDiv);

    expect(mockOnProfileClick).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should trigger onSettingsClick and onClose when settings button is clicked', () => {
    render(<Sidebar {...defaultProps} />);
    
    const settingsButton = screen.getByTitle('Settings');
    fireEvent.click(settingsButton);

    expect(mockOnSettingsClick).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should trigger onClose when mobile close button is clicked', () => {
    render(<Sidebar {...defaultProps} />);
    
    const closeButton = screen.getByRole('button', { name: 'Close menu' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });
});
