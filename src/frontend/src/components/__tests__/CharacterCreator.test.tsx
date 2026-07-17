import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CharacterCreator from '../CharacterCreator';
import { describe, it, expect, vi, beforeEach } from 'vitest';

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

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock global fetch for tokenize endpoint query
    globalThis.fetch = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ tokens: 10 }),
      })
    ) as unknown as typeof fetch;
  });

  it('should render form for creating a new character', () => {
    render(<CharacterCreator {...defaultProps} />);
    
    expect(screen.getByText('Create Character')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('A unique title for your character')).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Provide a short description / bio summary...")).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Initialize' })).toBeInTheDocument();
  });

  it('should fill form, select tags, and submit new character data', async () => {
    render(<CharacterCreator {...defaultProps} />);

    const nameInput = screen.getByLabelText('Title / Name *');
    const descInput = screen.getByLabelText('Bio *');
    const braveTagButton = screen.getByText('Brave');
    const submitButton = screen.getByRole('button', { name: 'Initialize' });

    fireEvent.change(nameInput, { target: { value: 'Elara' } });
    fireEvent.change(descInput, { target: { value: 'A brave scholar' } });
    
    // Select brave tag
    fireEvent.click(braveTagButton);
    
    // Submit
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Elara',
          description: 'A brave scholar',
          tagIds: [10],
          content_rating: 'limited'
        })
      );
    });
  });

  it('defaults dynamic_persona to true and sends it toggled-off in the payload', async () => {
    render(<CharacterCreator {...defaultProps} />);
    fireEvent.change(screen.getByLabelText('Title / Name *'), { target: { value: 'Elara' } });
    fireEvent.change(screen.getByLabelText('Bio *'), { target: { value: 'A scholar' } });

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeChecked(); // dynamic by default

    fireEvent.click(checkbox); // make it static
    fireEvent.click(screen.getByRole('button', { name: 'Initialize' }));

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith(
        expect.objectContaining({ dynamic_persona: false })
      );
    });
  });

  it('prefills the dynamic_persona checkbox from an edited character', () => {
    render(
      <CharacterCreator
        {...defaultProps}
        editingCharacter={{ id: 1, name: 'X', description: 'd', dynamic_persona: false, is_active: true, tags: [] }}
      />
    );
    expect(screen.getByRole('checkbox')).not.toBeChecked();
  });

  it('edits Definition-tab fields and switches to the Preview tab', () => {
    render(<CharacterCreator {...defaultProps} />);
    fireEvent.click(screen.getByRole('button', { name: 'Definition' }));

    fireEvent.change(screen.getByLabelText('Personality *'), { target: { value: 'A sly rogue.' } });
    fireEvent.change(screen.getByLabelText('Scenario'), { target: { value: 'A dark tavern.' } });

    fireEvent.click(screen.getByRole('button', { name: 'Preview' }));
    expect(screen.getAllByText('Personality').length).toBeGreaterThan(0);
  });

  it('warns when the permanent card exceeds the recommended token ceiling', () => {
    render(<CharacterCreator {...defaultProps} />);
    fireEvent.click(screen.getByRole('button', { name: 'Definition' }));

    // ~5000 words -> well past the 4096-token soft ceiling (offline estimate).
    fireEvent.change(screen.getByLabelText('Personality *'), {
      target: { value: 'word '.repeat(5000) },
    });
    expect(screen.getByText(/above the recommended/i)).toBeInTheDocument();
  });

  it('re-enables the submit button when onCreate rejects', async () => {
    const failingCreate = vi.fn().mockRejectedValue(new Error('save failed'));
    render(<CharacterCreator {...defaultProps} onCreate={failingCreate} />);

    fireEvent.change(screen.getByLabelText('Title / Name *'), { target: { value: 'Elara' } });
    fireEvent.change(screen.getByLabelText('Bio *'), { target: { value: 'A brave scholar' } });
    fireEvent.click(screen.getByRole('button', { name: 'Initialize' }));

    await waitFor(() => expect(failingCreate).toHaveBeenCalled());
    // The button must return to its idle label, not stay stuck on "Saving...".
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Initialize' })).not.toBeDisabled()
    );
  });

  it('should toggle tags correctly when clicked multiple times', async () => {
    render(<CharacterCreator {...defaultProps} />);

    const nameInput = screen.getByLabelText('Title / Name *');
    const descInput = screen.getByLabelText('Bio *');
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
      expect(mockOnCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Kaelen',
          description: 'A tricky rogue',
          tagIds: [20]
        })
      );
    });
  });

  it('should navigate to definition tab and submit behavior fields', async () => {
    render(<CharacterCreator {...defaultProps} />);

    // Go to Definition Tab
    const defTabButton = screen.getByRole('button', { name: 'Definition' });
    fireEvent.click(defTabButton);

    // Write definitions
    const personaInput = screen.getByLabelText('Personality *');
    const scenarioInput = screen.getByLabelText('Scenario');
    const firstMesInput = screen.getByLabelText('Initial messages (first messages) *');
    const mesExampleInput = screen.getByLabelText('Example dialogs');

    fireEvent.change(personaInput, { target: { value: 'Sarcastic AI' } });
    fireEvent.change(scenarioInput, { target: { value: 'Locked inside a server room' } });
    fireEvent.change(firstMesInput, { target: { value: 'Welcome back. Or not.' } });
    fireEvent.change(mesExampleInput, { target: { value: '{{char}}: go away' } });

    // Switch back to General and submit
    const genTabButton = screen.getByRole('button', { name: 'General' });
    fireEvent.click(genTabButton);

    // Fill required general fields
    const nameInput = screen.getByLabelText('Title / Name *');
    const descInput = screen.getByLabelText('Bio *');
    fireEvent.change(nameInput, { target: { value: 'Glados' } });
    fireEvent.change(descInput, { target: { value: 'Server entity' } });

    const submitButton = screen.getByRole('button', { name: 'Initialize' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Glados',
          description: 'Server entity',
          persona_prompt: 'Sarcastic AI',
          scenario: 'Locked inside a server room',
          first_mes: 'Welcome back. Or not.',
          mes_example: '{{char}}: go away'
        })
      );
    });
  });

  it('should prepopulate fields when editing an existing character and save updates', async () => {
    const existingChar = {
      id: 5,
      name: 'Architect',
      description: 'Builder of worlds',
      nickname: 'Archy',
      persona_prompt: 'Creative intellect',
      scenario: 'Blank canvas grid',
      first_mes: 'Create anything.',
      mes_example: '{{char}}: let there be light',
      content_rating: 'limitless',
      is_active: true,
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
    expect(screen.getByDisplayValue('Archy')).toBeInTheDocument();
    
    // Toggle content rating radio to the General rating
    const sfwRadio = screen.getByLabelText('General');
    fireEvent.click(sfwRadio);

    const braveTagButton = screen.getByText('Brave');
    const saveButton = screen.getByRole('button', { name: 'Save Changes' });

    // Select Brave tag in addition to Smart
    fireEvent.click(braveTagButton);
    
    // Submit
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(
        5,
        expect.objectContaining({
          name: 'Architect',
          description: 'Builder of worlds',
          nickname: 'Archy',
          content_rating: 'limited',
          tagIds: [20, 10]
        })
      );
    });
  });

  it('adds an alternate greeting and includes it on submit', async () => {
    render(<CharacterCreator {...defaultProps} />);

    fireEvent.click(screen.getByRole('button', { name: 'Definition' }));
    fireEvent.change(screen.getByLabelText('Personality *'), { target: { value: 'Calm' } });
    fireEvent.change(screen.getByLabelText('Initial messages (first messages) *'), { target: { value: 'Primary hello.' } });

    fireEvent.click(screen.getByRole('button', { name: /Add alternate greeting/ }));
    const altBox = screen.getByPlaceholderText(/Another opening message/);
    fireEvent.change(altBox, { target: { value: '*door creaks* Hi {{user}}.' } });

    fireEvent.click(screen.getByRole('button', { name: 'General' }));
    fireEvent.change(screen.getByLabelText('Title / Name *'), { target: { value: 'Aria' } });
    fireEvent.change(screen.getByLabelText('Bio *'), { target: { value: 'Librarian' } });
    fireEvent.click(screen.getByRole('button', { name: 'Initialize' }));

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          first_mes: 'Primary hello.',
          alternate_greetings: ['*door creaks* Hi {{user}}.']
        })
      );
    });
  });

  it('preview tab resolves {{user}} / {{char}} macros', () => {
    render(<CharacterCreator {...defaultProps} />);

    fireEvent.change(screen.getByLabelText('Title / Name *'), { target: { value: 'Aria' } });
    fireEvent.click(screen.getByRole('button', { name: 'Definition' }));
    fireEvent.change(screen.getByLabelText('Initial messages (first messages) *'), { target: { value: 'Hello {{user}}, I am {{char}}.' } });

    fireEvent.click(screen.getByRole('button', { name: 'Preview' }));

    expect(screen.getByText('Hello User, I am Aria.')).toBeInTheDocument();
  });

  it('should display empty message when no tags are provided', () => {
    render(<CharacterCreator {...defaultProps} tags={[]} />);
    expect(screen.getByText('No tags available. Create tags in Archives.')).toBeInTheDocument();
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
