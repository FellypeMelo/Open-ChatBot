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
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data),
    } as Response);
  };

  const mockErrorResponse = (status = 500) => {
    return Promise.resolve({
      ok: false,
      status,
    } as Response);
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

  it('fetchTags should make GET call to /tags/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchTags();
    expect(fetch).toHaveBeenCalledWith('/tags/');
  });

  it('fetchHistory should make GET call with character id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchHistory(42);
    expect(fetch).toHaveBeenCalledWith('/history/42');
  });

  it('updateUser should make POST call with body', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateUser('Bob', 'Male');
    expect(fetch).toHaveBeenCalledWith('/users/me', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ name: 'Bob', gender: 'Male' }),
    }));
  });

  it('createTag should make POST call to /tags/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createTag('Test', 'Do test');
    expect(fetch).toHaveBeenCalledWith('/tags/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ label: 'Test', instruction: 'Do test' }),
    }));
  });

  it('updateTag should make PUT call to /tags/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateTag(12, 'Test', 'Do test');
    expect(fetch).toHaveBeenCalledWith('/tags/12', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ label: 'Test', instruction: 'Do test' }),
    }));
  });

  it('deleteTag should make DELETE call to /tags/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    const result = await api.deleteTag(12);
    expect(fetch).toHaveBeenCalledWith('/tags/12', { method: 'DELETE' });
    expect(result).toBe(true);
  });

  it('createCharacter should make POST call to /characters/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createCharacter('Heros', 'A hero', [1, 2]);
    expect(fetch).toHaveBeenCalledWith('/characters/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ name: 'Heros', description: 'A hero', tag_ids: [1, 2] }),
    }));
  });

  it('updateCharacter should make PUT call to /characters/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateCharacter(3, 'Heros', 'A hero', [1, 2]);
    expect(fetch).toHaveBeenCalledWith('/characters/3', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ name: 'Heros', description: 'A hero', tag_ids: [1, 2] }),
    }));
  });

  it('deleteCharacter should make DELETE call to /characters/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    await api.deleteCharacter(3);
    expect(fetch).toHaveBeenCalledWith('/characters/3', { method: 'DELETE' });
  });

  it('sendMessage should make POST call to /chat', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.sendMessage('hello', 1, null, { base_url: 'http://localhost:8080' });
    expect(fetch).toHaveBeenCalledWith('/chat', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ message: 'hello', character_id: 1, parent_id: null, config: { base_url: 'http://localhost:8080' } }),
    }));
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

  it('fetchLore should make GET call to /lore/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchLore();
    expect(fetch).toHaveBeenCalledWith('/lore/');
  });

  it('createLore should make POST call to /lore/', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.createLore('Key', 'Val', 5, true);
    expect(fetch).toHaveBeenCalledWith('/lore/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ keyword: 'Key', content: 'Val', character_id: 5, is_global: true }),
    }));
  });

  it('deleteLore should make DELETE call to /lore/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse(true));
    await api.deleteLore(42);
    expect(fetch).toHaveBeenCalledWith('/lore/42', { method: 'DELETE' });
  });

  it('fetchRunnerStatus should make GET call to /settings/status', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.fetchRunnerStatus();
    expect(fetch).toHaveBeenCalledWith('/settings/status');
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

  it('startServer should make POST call to /settings/start/:type', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.startServer('inference');
    expect(fetch).toHaveBeenCalledWith('/settings/start/inference', { method: 'POST' });
  });

  it('stopServer should make POST call to /settings/stop/:type', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.stopServer('embedding');
    expect(fetch).toHaveBeenCalledWith('/settings/stop/embedding', { method: 'POST' });
  });

  it('restartAllServers should make POST call to /settings/restart-all', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.restartAllServers();
    expect(fetch).toHaveBeenCalledWith('/settings/restart-all', { method: 'POST' });
  });

  it('updateCharacterState should make PUT call to /characters/:id/state', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.updateCharacterState(5, { mood: 'happy' });
    expect(fetch).toHaveBeenCalledWith('/characters/5/state', expect.objectContaining({
      method: 'PUT',
      body: JSON.stringify({ mood: 'happy' }),
    }));
  });

  it('clearChatHistory should make POST call to /chat/clear/:id', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse({}));
    await api.clearChatHistory(5);
    expect(fetch).toHaveBeenCalledWith('/chat/clear/5', { method: 'POST' });
  });

  it('fetchJournal should make GET call to /characters/:id/journal', async () => {
    vi.mocked(fetch).mockResolvedValue(mockSuccessResponse([]));
    await api.fetchJournal(5);
    expect(fetch).toHaveBeenCalledWith('/characters/5/journal');
  });
});
