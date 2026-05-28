import { useState, useEffect } from 'react';
import type { LLMConfig } from '../services/api';

export const useSettings = () => {
  const [config, setConfig] = useState<LLMConfig>(() => {
    const saved = localStorage.getItem('llm_config');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse llm_config from localStorage:', e);
      }
    }
    return { base_url: 'http://localhost:8080', model_name: '' };
  });

  useEffect(() => {
    localStorage.setItem('llm_config', JSON.stringify(config));
  }, [config]);

  return { config, setConfig };
};
