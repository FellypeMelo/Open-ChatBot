import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as api from '../api';

describe('api service tests', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  const mockSuccessResponse = (data: unknown) => {
    return {
      ok: true,
      json: () => Promise.resolve(data),
    } as Response;
  };

  const mockErrorResponse = (status = 500) => {
    return {
      ok: false,
      status,
    } as Response;
  };

  it('fetchUser should make GET call to /users/me', async () => {
    const mockUser = { id: 1, name: 'Alice' };
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(mockUser));

    const result = await api.fetchUser();
    expect(fetch).toHaveBeenCalledWith('/users/me');
    expect(result).toEqual(mockUser);
  });

  it('fetchUser should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchUser()).rejects.toThrow('Failed to fetch user');
  });

  it('fetchCharacters should make GET call to /characters/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchCharacters();
    expect(fetch).toHaveBeenCalledWith('/characters/');
  });

  it('fetchCharacters should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchCharacters()).rejects.toThrow('Failed to fetch characters');
  });

  it('fetchTags should make GET call to /tags/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchTags();
    expect(fetch).toHaveBeenCalledWith('/tags/');
  });

  it('fetchTags should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchTags()).rejects.toThrow('Failed to fetch tags');
  });

  it('fetchHistory should make GET call with character id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchHistory(42);
    expect(fetch).toHaveBeenCalledWith('/history/42');
  });

  it('fetchHistory should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchHistory(42)).rejects.toThrow('Failed to fetch history');
  });

  it('fetchActions should make GET call to /chat/actions', async () => {
    const mockActions = { chat: 'is typing...', hug: 'is hugging...' };
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(mockActions));

    const result = await api.fetchActions();
    expect(fetch).toHaveBeenCalledWith('/chat/actions');
    expect(result).toEqual(mockActions);
  });

  it('fetchActions should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchActions()).rejects.toThrow('Failed to fetch actions');
  });

  it('updateUser should make POST call with body', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateUser('Bob', 'Male');
    expect(fetch).toHaveBeenCalledWith('/users/me', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ name: 'Bob', gender: 'Male' }),
    }));
  });

  it('updateUser should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.updateUser('Bob', 'Male')).rejects.toThrow('Failed to update user');
  });

  it('createTag should make POST call to /tags/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createTag('Test', 'Do test');
    expect(fetch).toHaveBeenCalledWith('/tags/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ label: 'Test', instruction: 'Do test' }),
    }));
  });

  it('createTag should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.createTag('Test', 'Do test')).rejects.toThrow('Failed to create tag');
  });

  it('updateTag should make PUT call to /tags/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateTag(12, 'Test', 'Do test');
    expect(fetch).toHaveBeenCalledWith('/tags/12', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ label: 'Test', instruction: 'Do test' }),
    }));
  });

  it('updateTag should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.updateTag(12, 'Test', 'Do test')).rejects.toThrow('Failed to update tag');
  });

  it('deleteTag should make DELETE call to /tags/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    const result = await api.deleteTag(12);
    expect(fetch).toHaveBeenCalledWith('/tags/12', { method: 'DELETE' });
    expect(result).toBe(true);
  });

  it('deleteTag should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.deleteTag(12)).rejects.toThrow('Failed to delete tag');
  });

  it('createCharacter should make POST call to /characters/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createCharacter({ name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false });
    expect(fetch).toHaveBeenCalledWith('/characters/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false }),
    }));
  });

  it('createCharacter should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.createCharacter({ name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false })).rejects.toThrow('Failed to create character');
  });

  it('importCharacterPng should make POST call with form data', async () => {
    const mockCharacter = { id: 1, name: 'Imported' };
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(mockCharacter));
    const file = new File(['binary-content'], 'avatar.png', { type: 'image/png' });

    const result = await api.importCharacterPng(file);

    expect(fetch).toHaveBeenCalledWith('/characters/import-png', expect.objectContaining({
      method: 'POST',
      body: expect.any(FormData),
    }));
    expect(result).toEqual(mockCharacter);
  });

  it('importCharacterPng should throw the server-provided detail message on error response', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Unsupported PNG metadata' }),
    } as Response);
    const file = new File(['binary-content'], 'avatar.png', { type: 'image/png' });

    await expect(api.importCharacterPng(file)).rejects.toThrow('Unsupported PNG metadata');
  });

  it('importCharacterPng should fall back to a default message when error body has no detail', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      json: () => Promise.reject(new Error('invalid json')),
    } as Response);
    const file = new File(['binary-content'], 'avatar.png', { type: 'image/png' });

    await expect(api.importCharacterPng(file)).rejects.toThrow('Failed to import character');
  });

  it('updateCharacter should make PUT call to /characters/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateCharacter(3, { name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false });
    expect(fetch).toHaveBeenCalledWith('/characters/3', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false }),
    }));
  });

  it('updateCharacter should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.updateCharacter(3, { name: 'Heros', description: 'A hero', tag_ids: [1, 2], compress_backstory: false })).rejects.toThrow('Failed to update character');
  });

  it('deleteCharacter should make DELETE call to /characters/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    await api.deleteCharacter(3);
    expect(fetch).toHaveBeenCalledWith('/characters/3', { method: 'DELETE' });
  });

  it('deleteCharacter should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.deleteCharacter(3)).rejects.toThrow('Failed to delete character');
  });

  const mockPreset = {
    id: 1,
    name: 'Default',
    is_default: true,
    temperature: 0.8,
    min_p: 0.05,
    top_k: 40,
    top_p: 0.95,
    repeat_penalty: 1.1,
    dry_multiplier: 0,
    dry_base: 1.75,
    dry_range: 0,
    xtc_threshold: 0.1,
    xtc_probability: 0,
  };

  it('fetchPresets should make GET call to /presets/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([mockPreset]));
    const result = await api.fetchPresets();
    expect(fetch).toHaveBeenCalledWith('/presets/');
    expect(result).toEqual([mockPreset]);
  });

  it('fetchPresets should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchPresets()).rejects.toThrow('Failed to fetch presets');
  });

  it('createPreset should make POST call to /presets/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(mockPreset));
    const { id, ...presetPayload } = mockPreset;
    void id;
    await api.createPreset(presetPayload);
    expect(fetch).toHaveBeenCalledWith('/presets/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify(presetPayload),
    }));
  });

  it('createPreset should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    const { id, ...presetPayload } = mockPreset;
    void id;
    await expect(api.createPreset(presetPayload)).rejects.toThrow('Failed to create preset');
  });

  it('updatePreset should make PUT call to /presets/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(mockPreset));
    const { id, ...presetPayload } = mockPreset;
    await api.updatePreset(id, presetPayload);
    expect(fetch).toHaveBeenCalledWith('/presets/1', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify(presetPayload),
    }));
  });

  it('updatePreset should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    const { id, ...presetPayload } = mockPreset;
    await expect(api.updatePreset(id, presetPayload)).rejects.toThrow('Failed to update preset');
  });

  it('deletePreset should make DELETE call to /presets/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    const result = await api.deletePreset(1);
    expect(fetch).toHaveBeenCalledWith('/presets/1', { method: 'DELETE' });
    expect(result).toBe(true);
  });

  it('deletePreset should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.deletePreset(1)).rejects.toThrow('Failed to delete preset');
  });

  it('sendMessage should make POST call to /chat', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.sendMessage('hello', 1, null, { base_url: 'http://localhost:8080' });
    expect(fetch).toHaveBeenCalledWith('/chat', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ message: 'hello', character_id: 1, parent_id: null, config: { base_url: 'http://localhost:8080' } }),
    }));
  });

  it('sendMessage should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.sendMessage('hello', 1, null)).rejects.toThrow('Failed to send message');
  });

  it('sendMessageStream should make POST call to /chat/stream', async () => {
    const mockRes = { ok: true } as Response;
    vi.mocked(fetch).mockResolvedValue(mockRes);
    const result = await api.sendMessageStream('hello', 1, null, undefined, 'action-1');
    expect(fetch).toHaveBeenCalledWith('/chat/stream', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ message: 'hello', character_id: 1, parent_id: null, config: undefined, action_id: 'action-1' }),
    }));
    expect(result).toBe(mockRes);
  });

  it('sendMessageStream should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.sendMessageStream('hello', 1, null)).rejects.toThrow('Failed to start stream');
  });

  it('fetchLore should make GET call to /lore/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchLore();
    expect(fetch).toHaveBeenCalledWith('/lore/');
  });

  it('fetchLore should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchLore()).rejects.toThrow('Failed to fetch lore');
  });

  it('createLore should make POST call to /lore/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createLore('Key', 'Val', 5, true);
    expect(fetch).toHaveBeenCalledWith('/lore/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ keyword: 'Key', content: 'Val', character_id: 5, is_global: true }),
    }));
  });

  it('createLore should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.createLore('Key', 'Val', 5, true)).rejects.toThrow('Failed to create lore');
  });

  it('deleteLore should make DELETE call to /lore/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    await api.deleteLore(42);
    expect(fetch).toHaveBeenCalledWith('/lore/42', { method: 'DELETE' });
  });

  it('deleteLore should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.deleteLore(42)).rejects.toThrow('Failed to delete lore');
  });

  it('fetchRunnerStatus should make GET call to /settings/status', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.fetchRunnerStatus();
    expect(fetch).toHaveBeenCalledWith('/settings/status');
  });

  it('fetchRunnerStatus should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchRunnerStatus()).rejects.toThrow('Failed to fetch runner status');
  });

  it('saveRunnerConfig should make POST call to /settings/save', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    const cfg = { inference: {}, embedding: {} } as unknown as Parameters<typeof api.saveRunnerConfig>[0];
    await api.saveRunnerConfig(cfg);
    expect(fetch).toHaveBeenCalledWith('/settings/save', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify(cfg),
    }));
  });

  it('saveRunnerConfig should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    const cfg = { inference: {}, embedding: {} } as unknown as Parameters<typeof api.saveRunnerConfig>[0];
    await expect(api.saveRunnerConfig(cfg)).rejects.toThrow('Failed to save runner configuration');
  });

  it('startServer should make POST call to /settings/start/:type', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.startServer('inference');
    expect(fetch).toHaveBeenCalledWith('/settings/start/inference', { method: 'POST' });
  });

  it('startServer should throw a type-specific error message on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.startServer('inference')).rejects.toThrow('Failed to start inference server');
  });

  it('stopServer should make POST call to /settings/stop/:type', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.stopServer('embedding');
    expect(fetch).toHaveBeenCalledWith('/settings/stop/embedding', { method: 'POST' });
  });

  it('stopServer should throw a type-specific error message on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.stopServer('embedding')).rejects.toThrow('Failed to stop embedding server');
  });

  it('restartAllServers should make POST call to /settings/restart-all', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.restartAllServers();
    expect(fetch).toHaveBeenCalledWith('/settings/restart-all', { method: 'POST' });
  });

  it('restartAllServers should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.restartAllServers()).rejects.toThrow('Failed to restart servers');
  });

  it('updateCharacterState should make PUT call to /characters/:id/state', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateCharacterState(5, { mood: 'happy' });
    expect(fetch).toHaveBeenCalledWith('/characters/5/state', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ mood: 'happy' }),
    }));
  });

  it('updateCharacterState should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.updateCharacterState(5, { mood: 'happy' })).rejects.toThrow('Failed to update character state');
  });

  it('clearChatHistory should make POST call to /chat/clear/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.clearChatHistory(5);
    expect(fetch).toHaveBeenCalledWith('/chat/clear/5', { method: 'POST' });
  });

  it('clearChatHistory should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.clearChatHistory(5)).rejects.toThrow('Failed to clear chat history');
  });

  it('editMessage should make PUT call to /chat/message/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({ id: 9, content: 'edited' }));
    const result = await api.editMessage(9, 'edited');
    expect(fetch).toHaveBeenCalledWith('/chat/message/9', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ content: 'edited' }),
    }));
    expect(result).toEqual({ id: 9, content: 'edited' });
  });

  it('editMessage should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.editMessage(9, 'edited')).rejects.toThrow('Failed to edit message');
  });

  it('deleteMessage should make DELETE call to /chat/message/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({ success: true }));
    const result = await api.deleteMessage(9);
    expect(fetch).toHaveBeenCalledWith('/chat/message/9', { method: 'DELETE' });
    expect(result).toEqual({ success: true });
  });

  it('deleteMessage should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.deleteMessage(9)).rejects.toThrow('Failed to delete message');
  });

  it('fetchJournal should make GET call to /characters/:id/journal', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchJournal(5);
    expect(fetch).toHaveBeenCalledWith('/characters/5/journal');
  });

  it('fetchJournal should throw on error response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockErrorResponse());
    await expect(api.fetchJournal(5)).rejects.toThrow('Failed to fetch journal entries');
  });
});
