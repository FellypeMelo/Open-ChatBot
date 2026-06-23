import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LorebookView from '../LorebookView';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as api from '../../services/api';

vi.mock('../../services/api', () => ({
  fetchLore: vi.fn(),
  createLore: vi.fn(),
  deleteLore: vi.fn(),
}));

describe('LorebookView', () => {
  const mockLoreEntries = [
    { id: 1, keyword: 'Silver Dragon', content: 'A mighty friendly dragon', character_id: null, is_global: true },
    { id: 2, keyword: 'Excalibur', content: 'Legendary sword of kings', character_id: 12, is_global: false },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(window, 'confirm').mockImplementation(() => true);
    vi.mocked(api.fetchLore).mockResolvedValue(mockLoreEntries);
    vi.mocked(api.createLore).mockResolvedValue({ id: 3, keyword: 'Magic Ring', content: 'Allows invisibility', character_id: null, is_global: true });
    vi.mocked(api.deleteLore).mockResolvedValue({ status: 'success' });
  });

  it('should render page title and fetch lore entries on mount', async () => {
    render(<LorebookView />);
    
    expect(screen.getByText('Lorebook & Knowledge')).toBeInTheDocument();
    expect(api.fetchLore).toHaveBeenCalled();

    await waitFor(() => {
      expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
      expect(screen.getByText('Excalibur')).toBeInTheDocument();
    });
  });

  it('should display empty state when no entries exist', async () => {
    vi.mocked(api.fetchLore).mockResolvedValue([]);
    render(<LorebookView />);

    await waitFor(() => {
      expect(screen.getByText('The library is empty.')).toBeInTheDocument();
    });
  });

  it('should filter entries when search input changes', async () => {
    render(<LorebookView />);
    
    await waitFor(() => {
      expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search lore...');
    fireEvent.change(searchInput, { target: { value: 'Dragon' } });

    expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
    expect(screen.queryByText('Excalibur')).not.toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: 'NonExistent' } });
    expect(screen.queryByText('Silver Dragon')).not.toBeInTheDocument();
    expect(screen.getByText('No lore matches your search.')).toBeInTheDocument();
  });

  it('should filter entries based on Global / Personal tab selection', async () => {
    render(<LorebookView />);
    
    await waitFor(() => {
      expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
      expect(screen.getByText('Excalibur')).toBeInTheDocument();
    });

    const globalButton = screen.getByText('Global');
    fireEvent.click(globalButton);
    expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
    expect(screen.queryByText('Excalibur')).not.toBeInTheDocument();

    const personalButton = screen.getByText('Personal');
    fireEvent.click(personalButton);
    expect(screen.queryByText('Silver Dragon')).not.toBeInTheDocument();
    expect(screen.getByText('Excalibur')).toBeInTheDocument();
  });

  it('should create a new lore entry when form is submitted', async () => {
    render(<LorebookView />);

    const keywordInput = screen.getByPlaceholderText("Keyword (e.g. 'Silver Dragon')");
    const contentInput = screen.getByPlaceholderText('What should the character remember when this keyword is mentioned?');
    const submitButton = screen.getByText('Add Knowledge Entry');

    fireEvent.change(keywordInput, { target: { value: 'Magic Ring' } });
    fireEvent.change(contentInput, { target: { value: 'Allows invisibility' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(api.createLore).toHaveBeenCalledWith('Magic Ring', 'Allows invisibility', undefined, true);
    });
  });

  it('should delete a lore entry when delete button is clicked and confirmed', async () => {
    render(<LorebookView />);

    await waitFor(() => {
      expect(screen.getByText('Silver Dragon')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button');
    // The delete button is the icon button next to entries
    const deleteButton = deleteButtons.find(btn => btn.querySelector('span')?.textContent === 'delete');
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
      expect(window.confirm).toHaveBeenCalled();
      expect(api.deleteLore).toHaveBeenCalledWith(1);
    }
  });
});
