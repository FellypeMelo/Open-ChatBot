import React, { useState, useEffect } from 'react'
import * as api from '../services/api'
import type { RunnerStatus } from '../services/api'

interface SettingsModalProps {
  onClose: () => void
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const [status, setStatus] = useState<RunnerStatus | null>(null)
  const [activeTab, setActiveTab] = useState<'inference' | 'embedding'>('inference')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Local form state for inference
  const [infBinary, setInfBinary] = useState('')
  const [infModel, setInfModel] = useState('')
  const [infPort, setInfPort] = useState(8080)
  const [infThreads, setInfThreads] = useState(4)
  const [infGpuLayers, setInfGpuLayers] = useState(-1)
  const [infContext, setInfContext] = useState(4096)
  const [infArgs, setInfArgs] = useState('')

  // Local form state for embedding
  const [embBinary, setEmbBinary] = useState('')
  const [embModel, setEmbModel] = useState('')
  const [embPort, setEmbPort] = useState(8081)
  const [embThreads, setEmbThreads] = useState(4)
  const [embGpuLayers, setEmbGpuLayers] = useState(-1)
  const [embArgs, setEmbArgs] = useState('')

  const loadStatus = async () => {
    try {
      setLoading(true)
      const data = await api.fetchRunnerStatus()
      setStatus(data)
      
      // Populate inference
      setInfBinary(data.inference.config.binary_path)
      setInfModel(data.inference.config.model_path)
      setInfPort(data.inference.config.port)
      setInfThreads(data.inference.config.threads)
      setInfGpuLayers(data.inference.config.gpu_layers)
      setInfContext(data.inference.config.context_size)
      setInfArgs(data.inference.config.additional_args)

      // Populate embedding
      setEmbBinary(data.embedding.config.binary_path)
      setEmbModel(data.embedding.config.model_path)
      setEmbPort(data.embedding.config.port)
      setEmbThreads(data.embedding.config.threads)
      setEmbGpuLayers(data.embedding.config.gpu_layers)
      setEmbArgs(data.embedding.config.additional_args)
      
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch AI runner status from backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStatus()
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!status) return
    
    setLoading(true)
    try {
      const newConfig = {
        inference: {
          binary_path: infBinary,
          model_path: infModel,
          port: infPort,
          threads: infThreads,
          gpu_layers: infGpuLayers,
          context_size: infContext,
          additional_args: infArgs
        },
        embedding: {
          binary_path: embBinary,
          model_path: embModel,
          port: embPort,
          threads: embThreads,
          gpu_layers: embGpuLayers,
          context_size: 4096, // Fixed default
          additional_args: embArgs
        }
      }
      await api.saveRunnerConfig(newConfig)
      await api.restartAllServers()
      await loadStatus()
      alert('AI Configuration updated and servers restarted successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to save settings.')
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (type: 'inference' | 'embedding') => {
    setLoading(true)
    try {
      await api.startServer(type)
      await loadStatus()
    } catch (err: any) {
      setError(err.message || `Failed to start ${type} server. Check GGUF path.`);
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async (type: 'inference' | 'embedding') => {
    setLoading(true)
    try {
      await api.stopServer(type)
      await loadStatus()
    } catch (err: any) {
      setError(err.message || `Failed to stop ${type} server.`);
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-[#050505]/90 backdrop-blur-md z-50 flex items-center justify-center p-sm md:p-md overflow-y-auto">
      <div className="w-full max-w-[650px] bg-[#0A0A0A] border border-white/10 rounded-[1.5rem] p-md md:p-lg flex flex-col gap-md z-50 animate-in zoom-in-95 duration-300 shadow-2xl relative overflow-hidden">
        {/* Ambient mesh gradient backgrounds */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-[#ffffff]/5 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

        <div className="flex justify-between items-start w-full relative z-10">
          <div className="flex flex-col gap-2">
            <span className="font-label-sm text-[10px] uppercase tracking-[0.2em] text-[#71717A] bg-white/5 border border-white/10 px-2 py-0.5 rounded-full w-max">
              AI INFRASTRUCTURE
            </span>
            <h2 className="font-sans text-2xl font-bold tracking-tight text-white">Local Narrative Core</h2>
          </div>
          <button 
            onClick={onClose}
            aria-label="Close modal" 
            className="text-[#71717A] hover:text-white transition-all duration-300 p-1 bg-white/5 hover:bg-white/10 rounded-full border border-white/10 flex items-center justify-center"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-sm rounded-[0.75rem] text-sm font-label-sm relative z-10 flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Tab Selector */}
        <div className="flex border-b border-white/10 relative z-10">
          <button
            onClick={() => setActiveTab('inference')}
            className={`px-md py-sm font-label-sm text-xs tracking-wider transition-all duration-300 border-b-2 uppercase ${
              activeTab === 'inference' 
                ? 'border-white text-white font-medium' 
                : 'border-transparent text-[#71717A] hover:text-white'
            }`}
          >
            Inference Engine {status?.inference.running ? '●' : '○'}
          </button>
          <button
            onClick={() => setActiveTab('embedding')}
            className={`px-md py-sm font-label-sm text-xs tracking-wider transition-all duration-300 border-b-2 uppercase ${
              activeTab === 'embedding' 
                ? 'border-white text-white font-medium' 
                : 'border-transparent text-[#71717A] hover:text-white'
            }`}
          >
            Embedding Vector {status?.embedding.running ? '●' : '○'}
          </button>
        </div>

        <form onSubmit={handleSave} className="flex flex-col gap-md w-full relative z-10">
          {activeTab === 'inference' && (
            <div className="flex flex-col gap-md">
              {/* Server Status Header */}
              <div className="flex justify-between items-center bg-white/5 border border-white/10 rounded-[1rem] p-sm">
                <div className="flex items-center gap-2">
                  <span className={`w-3.5 h-3.5 rounded-full ${status?.inference.running ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                  <div className="flex flex-col">
                    <span className="font-label-sm text-xs uppercase text-white font-medium">
                      Inference Engine: {status?.inference.running ? 'ACTIVE' : 'STOPPED'}
                    </span>
                    <span className="font-label-sm text-[10px] text-[#71717A]">
                      Port: {infPort}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {status?.inference.running ? (
                    <button
                      type="button"
                      onClick={() => handleStop('inference')}
                      disabled={loading}
                      className="font-label-sm text-[10px] bg-red-950/40 hover:bg-red-950 border border-red-500/30 text-red-400 px-3 py-1.5 rounded-full transition-all duration-300"
                    >
                      STOP SERVER
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleStart('inference')}
                      disabled={loading || !infModel}
                      className="font-label-sm text-[10px] bg-emerald-950/40 hover:bg-emerald-950 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded-full transition-all duration-300 disabled:opacity-50"
                    >
                      START SERVER
                    </button>
                  )}
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-sm">
                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-binary" className="font-label-sm text-[10px] text-[#71717A] uppercase">Runner Binary</label>
                  <select
                    id="inf-binary"
                    value={infBinary.replace('llama_bin/', '')}
                    onChange={e => setInfBinary(`llama_bin/${e.target.value}`)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                  >
                    {status?.available_binaries.map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                    {status?.available_binaries.length === 0 && (
                      <option value="llama-server.exe">llama-server.exe (Default)</option>
                    )}
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-model" className="font-label-sm text-[10px] text-[#71717A] uppercase">Active GGUF Model</label>
                  <select
                    id="inf-model"
                    value={infModel.replace('models/', '')}
                    onChange={e => setInfModel(e.target.value ? `models/${e.target.value}` : '')}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  >
                    <option value="">-- Choose Model --</option>
                    {status?.available_models.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                  {status?.available_models.length === 0 && (
                    <span className="text-[10px] text-amber-500 font-label-sm mt-0.5">
                      No models in ./models directory. Add GGUF files.
                    </span>
                  )}
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-port" className="font-label-sm text-[10px] text-[#71717A] uppercase">Port</label>
                  <input
                    id="inf-port"
                    type="number"
                    value={infPort}
                    onChange={e => setInfPort(parseInt(e.target.value) || 8080)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-threads" className="font-label-sm text-[10px] text-[#71717A] uppercase">CPU Threads</label>
                  <input
                    id="inf-threads"
                    type="number"
                    value={infThreads}
                    onChange={e => setInfThreads(parseInt(e.target.value) || 4)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-gpu-layers" className="font-label-sm text-[10px] text-[#71717A] uppercase">GPU Layers (-1 to disable)</label>
                  <input
                    id="inf-gpu-layers"
                    type="number"
                    value={infGpuLayers}
                    onChange={e => setInfGpuLayers(parseInt(e.target.value) ?? -1)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="inf-context" className="font-label-sm text-[10px] text-[#71717A] uppercase">Context Size (tokens)</label>
                  <input
                    id="inf-context"
                    type="number"
                    value={infContext}
                    onChange={e => setInfContext(parseInt(e.target.value) || 4096)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label htmlFor="inf-args" className="font-label-sm text-[10px] text-[#71717A] uppercase">Additional CLI Arguments</label>
                <input
                  id="inf-args"
                  type="text"
                  value={infArgs}
                  onChange={e => setInfArgs(e.target.value)}
                  placeholder="e.g. --cache-type-k q8_0"
                  className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                />
              </div>
            </div>
          )}

          {activeTab === 'embedding' && (
            <div className="flex flex-col gap-md">
              {/* Server Status Header */}
              <div className="flex justify-between items-center bg-white/5 border border-white/10 rounded-[1rem] p-sm">
                <div className="flex items-center gap-2">
                  <span className={`w-3.5 h-3.5 rounded-full ${status?.embedding.running ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                  <div className="flex flex-col">
                    <span className="font-label-sm text-xs uppercase text-white font-medium">
                      Embedding Server: {status?.embedding.running ? 'ACTIVE' : 'STOPPED'}
                    </span>
                    <span className="font-label-sm text-[10px] text-[#71717A]">
                      Port: {embPort}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {status?.embedding.running ? (
                    <button
                      type="button"
                      onClick={() => handleStop('embedding')}
                      disabled={loading}
                      className="font-label-sm text-[10px] bg-red-950/40 hover:bg-red-950 border border-red-500/30 text-red-400 px-3 py-1.5 rounded-full transition-all duration-300"
                    >
                      STOP SERVER
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleStart('embedding')}
                      disabled={loading || !embModel}
                      className="font-label-sm text-[10px] bg-emerald-950/40 hover:bg-emerald-950 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded-full transition-all duration-300 disabled:opacity-50"
                    >
                      START SERVER
                    </button>
                  )}
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-sm">
                <div className="flex flex-col gap-1">
                  <label htmlFor="emb-binary" className="font-label-sm text-[10px] text-[#71717A] uppercase">Runner Binary</label>
                  <select
                    id="emb-binary"
                    value={embBinary.replace('llama_bin/', '')}
                    onChange={e => setEmbBinary(`llama_bin/${e.target.value}`)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                  >
                    {status?.available_binaries.map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                    {status?.available_binaries.length === 0 && (
                      <option value="llama-server.exe">llama-server.exe (Default)</option>
                    )}
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="emb-model" className="font-label-sm text-[10px] text-[#71717A] uppercase">Active GGUF Model</label>
                  <select
                    id="emb-model"
                    value={embModel.replace('models/', '')}
                    onChange={e => setEmbModel(e.target.value ? `models/${e.target.value}` : '')}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  >
                    <option value="">-- Choose Model --</option>
                    {status?.available_models.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="emb-port" className="font-label-sm text-[10px] text-[#71717A] uppercase">Port</label>
                  <input
                    id="emb-port"
                    type="number"
                    value={embPort}
                    onChange={e => setEmbPort(parseInt(e.target.value) || 8081)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="emb-threads" className="font-label-sm text-[10px] text-[#71717A] uppercase">CPU Threads</label>
                  <input
                    id="emb-threads"
                    type="number"
                    value={embThreads}
                    onChange={e => setEmbThreads(parseInt(e.target.value) || 4)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1 col-span-2">
                  <label htmlFor="emb-gpu-layers" className="font-label-sm text-[10px] text-[#71717A] uppercase">GPU Layers (-1 to disable)</label>
                  <input
                    id="emb-gpu-layers"
                    type="number"
                    value={embGpuLayers}
                    onChange={e => setEmbGpuLayers(parseInt(e.target.value) ?? -1)}
                    className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label htmlFor="emb-args" className="font-label-sm text-[10px] text-[#71717A] uppercase">Additional CLI Arguments</label>
                <input
                  id="emb-args"
                  type="text"
                  value={embArgs}
                  onChange={e => setEmbArgs(e.target.value)}
                  placeholder="e.g. --pooling cls"
                  className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                />
              </div>
            </div>
          )}

          <div className="flex justify-end items-center gap-md pt-md border-t border-white/10 mt-sm">
            <button 
              onClick={onClose}
              disabled={loading}
              className="font-label-sm text-xs text-[#71717A] hover:text-white px-md py-xs border border-transparent hover:border-white/10 rounded-full transition-all duration-300 disabled:opacity-50" 
              type="button"
            >
              Cancel
            </button>
            <button 
              disabled={loading || !infModel || !embModel}
              className="font-label-sm text-xs font-semibold bg-white text-black px-lg py-xs hover:bg-[#E4E4E7] rounded-full transition-all duration-300 disabled:opacity-50 flex items-center gap-1.5" 
              type="submit"
            >
              {loading ? 'Reconfiguring...' : 'Save & Restart AI'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SettingsModal
