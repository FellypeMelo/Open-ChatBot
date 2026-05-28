import React, { useState } from 'react'
import { useSettings } from '../hooks/useSettings'

interface SettingsModalProps {
  onClose: () => void
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const { config, setConfig } = useSettings()
  const [baseUrl, setBaseUrl] = useState(config.base_url)
  const [modelName, setModelName] = useState(config.model_name)
  const [isSaving, setIsSaving] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setConfig({
      base_url: baseUrl,
      model_name: modelName
    })
    setIsSaving(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md">
      <div className="w-full max-w-[500px] bg-[#111111] border border-[#1A1A1A] p-lg md:p-xl flex flex-col gap-lg z-50 animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-start w-full">
          <div className="flex flex-col gap-xs">
            <h2 className="font-headline-lg text-headline-lg text-primary tracking-tight">System Settings</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Configure your local narrative engine.</p>
          </div>
          <button 
            onClick={onClose}
            aria-label="Close modal" 
            className="text-on-surface-variant hover:text-primary transition-colors p-xs" 
            type="button"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-lg w-full">
          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="base_url">Server URL</label>
            <input 
              value={baseUrl}
              onChange={e => setBaseUrl(e.target.value)}
              className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30" 
              id="base_url" 
              placeholder="http://localhost:8080" 
              type="url"
              required
            />
            <p className="font-label-sm text-label-sm text-on-surface-variant/60">The endpoint where llama.cpp is running.</p>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="model_name">Model Identifier</label>
            <input 
              value={modelName}
              onChange={e => setModelName(e.target.value)}
              className="input-line w-full bg-transparent border-0 border-b pb-xs font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30" 
              id="model_name" 
              placeholder="e.g. Llama-3-8B-Instruct" 
              type="text"
            />
            <p className="font-label-sm text-label-sm text-on-surface-variant/60">Optional: Used for internal metadata and prompt optimization.</p>
          </div>

          <div className="flex justify-end items-center gap-md pt-md border-t border-[#1A1A1A] mt-sm">
            <button 
              onClick={onClose}
              disabled={isSaving}
              className="font-body-md text-body-md text-on-surface px-md py-xs border border-transparent hover:border-[#1A1A1A] transition-colors disabled:opacity-50" 
              type="button"
            >
              Cancel
            </button>
            <button 
              disabled={isSaving}
              className="font-body-md text-body-md font-medium bg-primary text-surface-container-lowest px-lg py-xs hover:bg-on-surface transition-colors disabled:opacity-50 min-w-[120px]" 
              type="submit"
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SettingsModal
