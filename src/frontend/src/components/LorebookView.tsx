import React, { useState, useEffect } from 'react';
import Icon from './Icon';
import IconButton from './IconButton';
import * as api from '../services/api';

interface LoreEntry {
  id: number;
  keyword: string;
  content: string;
  character_id: number | null;
  is_global: boolean;
}

const LorebookView: React.FC = () => {
  const [entries, setLore] = useState<LoreEntry[]>([]);
  const [keyword, setKeyword] = useState('');
  const [content, setContent] = useState('');
  const [isGlobal, setIsGlobal] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'global' | 'personal'>('all');

  const fetchLore = async () => {
    try {
      const data = (await api.fetchLore()) as LoreEntry[];
      setLore(data);
    } catch (err) {
      console.error('Failed to fetch lore', err);
    }
  };

  useEffect(() => {
    let active = true;
    const init = async () => {
      await Promise.resolve();
      if (active) {
        await fetchLore();
      }
    };
    init();
    return () => {
      active = false;
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim() || !content.trim()) return;

    setIsLoading(true);
    try {
      await api.createLore(keyword, content, undefined, isGlobal);
      setKeyword('');
      setContent('');
      fetchLore();
    } catch (err) {
      console.error('Failed to create lore', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this entry?')) return;
    try {
      await api.deleteLore(id);
      fetchLore();
    } catch (err) {
      console.error('Failed to delete lore', err);
    }
  };

  const filteredEntries = entries.filter(e => {
    const matchesSearch = e.keyword.toLowerCase().includes(search.toLowerCase()) || 
                          e.content.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || 
                          (filter === 'global' && e.is_global) || 
                          (filter === 'personal' && !e.is_global);
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="flex-1 flex flex-col h-full bg-background overflow-hidden p-md">
      <div className="max-w-[1200px] mx-auto w-full flex flex-col h-full gap-md">
        <header className="flex-none flex justify-between items-end">
          <div>
            <h1 className="font-heading-md text-heading-md font-semibold text-primary">Lorebook & Knowledge</h1>
            <p className="text-on-surface-variant text-body-md mt-1">
              Define keywords that trigger character memories.
            </p>
          </div>
          <div className="flex flex-col items-end gap-xs">
            <div className="flex bg-surface-container-high rounded-full p-1 border border-outline/30">
              <button 
                onClick={() => setFilter('all')}
                className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all ${filter === 'all' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-primary'}`}
              >
                All
              </button>
              <button 
                onClick={() => setFilter('global')}
                className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all ${filter === 'global' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-primary'}`}
              >
                Global
              </button>
              <button 
                onClick={() => setFilter('personal')}
                className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all ${filter === 'personal' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-primary'}`}
              >
                Personal
              </button>
            </div>
            <div className="relative">
              <Icon name="search" size="sm" className="absolute left-2 top-1/2 -translate-y-1/2 text-on-surface-variant/50" />
              <input 
                type="text"
                placeholder="Search lore..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-surface-container-low border border-outline rounded-full pl-8 pr-md py-1 text-label-sm focus:border-primary outline-none w-48 transition-all focus:w-64"
              />
            </div>
          </div>
        </header>

        <section className="bg-surface-container-low border border-outline rounded-xl p-md">
          <form onSubmit={handleSubmit} className="flex flex-col gap-sm">
            <div className="flex gap-sm">
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Keyword (e.g. 'Silver Dragon')"
                className="flex-1 bg-surface-container border border-outline rounded-lg px-md py-sm focus:border-primary outline-none text-on-surface"
              />
              <label className="flex items-center gap-xs cursor-pointer select-none px-md">
                <input
                  type="checkbox"
                  checked={isGlobal}
                  onChange={(e) => setIsGlobal(e.target.checked)}
                  className="accent-primary"
                />
                <span className="text-label-md text-on-surface-variant">Global Lore</span>
              </label>
            </div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What should the character remember when this keyword is mentioned?"
              rows={3}
              className="bg-surface-container border border-outline rounded-lg px-md py-sm focus:border-primary outline-none text-on-surface resize-none"
            />
            <button
              type="submit"
              disabled={isLoading || !keyword.trim() || !content.trim()}
              className="bg-primary text-on-primary font-label-md py-sm rounded-lg hover:brightness-110 disabled:opacity-50 transition-all"
            >
              {isLoading ? 'Storing...' : 'Add Knowledge Entry'}
            </button>
          </form>
        </section>

        <main className="flex-1 overflow-y-auto custom-scrollbar pr-xs">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-sm">
            {filteredEntries.map((entry) => (
              <div key={entry.id} className="bg-surface-container border border-outline rounded-xl p-md flex flex-col group animate-in">
                <div className="flex justify-between items-start">
                  <span className="bg-surface-container-high text-on-surface px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                    {entry.keyword}
                  </span>
                  <IconButton
                    icon="delete"
                    label="Delete lore entry"
                    size="sm"
                    onClick={() => handleDelete(entry.id)}
                    className="text-on-surface-variant/40 hover:text-error"
                  />
                </div>
                <p className="text-on-surface text-body-sm mt-sm flex-1 italic line-clamp-4">
                  "{entry.content}"
                </p>
                {entry.is_global && (
                  <span className="text-[10px] text-on-surface-variant/50 mt-xs">Global Knowledge</span>
                )}
              </div>
            ))}
            {filteredEntries.length === 0 && entries.length > 0 && (
              <div className="col-span-full py-10 flex flex-col items-center justify-center opacity-30">
                <Icon name="search_off" size="xl" className="mb-2" />
                <p>No lore matches your search.</p>
              </div>
            )}
            {entries.length === 0 && (
              <div className="col-span-full py-10 flex flex-col items-center justify-center opacity-30">
                <Icon name="auto_stories" size="xl" className="mb-2" />
                <p>The library is empty.</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default LorebookView;
