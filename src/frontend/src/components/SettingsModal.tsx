import React, { useState, useEffect } from 'react'
import * as api from '../services/api'
import type { RunnerStatus } from '../services/api'

// Default llama-server config values (used for initial state and when a numeric
// field is cleared) and the storage-path prefixes the backend expects.
const DEFAULT_INFERENCE_PORT = 8080
const DEFAULT_EMBEDDING_PORT = 8081
const DEFAULT_THREADS = 4
const DEFAULT_GPU_LAYERS = -1
const DEFAULT_CONTEXT_SIZE = 4096
const BINARY_PREFIX = 'llama_bin/'
const MODEL_PREFIX = 'models/'

// Shared control styling for every field in the server-config forms (both the
// inference and embedding tabs render the same input/select chrome).
const FIELD_CLASS = 'bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none'
const FIELD_LABEL_CLASS = 'font-label-sm text-[10px] text-[#71717A] uppercase'

// Label + control wrapper. `wrapperClassName` lets a field span grid columns.
const Field: React.FC<{
  id: string
  label: string
  wrapperClassName?: string
  children: React.ReactNode
}> = ({ id, label, wrapperClassName = 'flex flex-col gap-1', children }) => (
  <div className={wrapperClassName}>
    <label htmlFor={id} className={FIELD_LABEL_CLASS}>{label}</label>
    {children}
  </div>
)

// Numeric config field. `fallback` is used when the input is cleared; set
// `allowZero` for fields where 0 is a real value (GPU layers) rather than a
// sentinel that should snap back to the fallback (port/threads/context).
const NumberField: React.FC<{
  id: string
  label: string
  value: number
  onChange: (v: number) => void
  fallback: number
  allowZero?: boolean
  disabled?: boolean
  wrapperClassName?: string
}> = ({ id, label, value, onChange, fallback, allowZero, disabled, wrapperClassName }) => (
  <Field id={id} label={label} wrapperClassName={wrapperClassName}>
    <input
      id={id}
      type="number"
      value={value}
      onChange={(e) => {
        const v = parseInt(e.target.value, 10)
        onChange(Number.isNaN(v) ? fallback : allowZero ? v : v || fallback)
      }}
      className={FIELD_CLASS}
      required
      disabled={disabled}
    />
  </Field>
)

interface SettingsModalProps {
  onClose: () => void
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const [status, setStatus] = useState<RunnerStatus | null>(null)
  const [activeTab, setActiveTab] = useState<'inference' | 'embedding' | 'samplers'>('inference')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Local form state for inference
  const [infBinary, setInfBinary] = useState('')
  const [infModel, setInfModel] = useState('')
  const [infPort, setInfPort] = useState(DEFAULT_INFERENCE_PORT)
  const [infThreads, setInfThreads] = useState(DEFAULT_THREADS)
  const [infGpuLayers, setInfGpuLayers] = useState(DEFAULT_GPU_LAYERS)
  const [infContext, setInfContext] = useState(DEFAULT_CONTEXT_SIZE)
  const [infArgs, setInfArgs] = useState('')

  // Local form state for embedding
  const [embBinary, setEmbBinary] = useState('')
  const [embModel, setEmbModel] = useState('')
  const [embPort, setEmbPort] = useState(DEFAULT_EMBEDDING_PORT)
  const [embThreads, setEmbThreads] = useState(DEFAULT_THREADS)
  const [embGpuLayers, setEmbGpuLayers] = useState(DEFAULT_GPU_LAYERS)
  const [embArgs, setEmbArgs] = useState('')

  // Consolidated mode state (whether embedding runs on the same server/port/model)
  const [isConsolidated, setIsConsolidated] = useState(false)

  // Sampler state
  const [presets, setPresets] = useState<api.SamplerPreset[]>([])

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
      
      const consolidated = data.embedding.config.port === data.inference.config.port
      setIsConsolidated(consolidated)
      
      const loadedPresets = await api.fetchPresets()
      setPresets(loadedPresets)
      
      setError(null)
    } catch {
      setError('Failed to fetch AI runner status from backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    const init = async () => {
      await Promise.resolve()
      if (active) {
        await loadStatus()
      }
    }
    init()
    return () => {
      active = false
    }
  }, [])

  // Synchronize embedding settings when consolidated is active
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (isConsolidated) {
      setEmbPort(infPort)
      setEmbModel(infModel)
      setEmbBinary(infBinary)
      setEmbThreads(infThreads)
      setEmbGpuLayers(infGpuLayers)
      setEmbArgs(infArgs)
    }
  }, [isConsolidated, infPort, infModel, infBinary, infThreads, infGpuLayers, infArgs])
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleConsolidatedChange = (checked: boolean) => {
    setIsConsolidated(checked)
    if (checked) {
      setEmbPort(infPort)
      setEmbModel(infModel)
      setEmbBinary(infBinary)
      setEmbThreads(infThreads)
      setEmbGpuLayers(infGpuLayers)
      setEmbArgs(infArgs)
    } else {
      setEmbPort(DEFAULT_EMBEDDING_PORT)
    }
  }

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
          binary_path: isConsolidated ? infBinary : embBinary,
          model_path: isConsolidated ? infModel : embModel,
          port: isConsolidated ? infPort : embPort,
          threads: isConsolidated ? infThreads : embThreads,
          gpu_layers: isConsolidated ? infGpuLayers : embGpuLayers,
          context_size: DEFAULT_CONTEXT_SIZE, // embedding server ignores context; keep a sane default
          additional_args: isConsolidated ? infArgs : embArgs
        }
      }
      await api.saveRunnerConfig(newConfig)
      await api.restartAllServers()
      await loadStatus()
      alert('AI Configuration updated and servers restarted successfully!')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to save settings.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (type: 'inference' | 'embedding') => {
    setLoading(true)
    try {
      await api.startServer(type)
      await loadStatus()
    } catch (err) {
      const msg = err instanceof Error ? err.message : `Failed to start ${type} server. Check GGUF path.`
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async (type: 'inference' | 'embedding') => {
    setLoading(true)
    try {
      await api.stopServer(type)
      await loadStatus()
    } catch (err) {
      const msg = err instanceof Error ? err.message : `Failed to stop ${type} server.`
      setError(msg)
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
          <button
            onClick={() => setActiveTab('samplers')}
            className={`px-md py-sm font-label-sm text-xs tracking-wider transition-all duration-300 border-b-2 uppercase ${
              activeTab === 'samplers' 
                ? 'border-white text-white font-medium' 
                : 'border-transparent text-[#71717A] hover:text-white'
            }`}
          >
            Samplers
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
                <Field id="inf-binary" label="Runner Binary">
                  <select
                    id="inf-binary"
                    value={infBinary.replace(BINARY_PREFIX, '')}
                    onChange={e => setInfBinary(`${BINARY_PREFIX}${e.target.value}`)}
                    className={FIELD_CLASS}
                  >
                    {status?.available_binaries.map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                    {status?.available_binaries.length === 0 && (
                      <option value="llama-server.exe">llama-server.exe (Default)</option>
                    )}
                  </select>
                </Field>

                <Field id="inf-model" label="Active GGUF Model">
                  <select
                    id="inf-model"
                    value={infModel.replace(MODEL_PREFIX, '')}
                    onChange={e => setInfModel(e.target.value ? `${MODEL_PREFIX}${e.target.value}` : '')}
                    className={FIELD_CLASS}
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
                </Field>

                <NumberField id="inf-port" label="Port" value={infPort} onChange={setInfPort} fallback={DEFAULT_INFERENCE_PORT} />
                <NumberField id="inf-threads" label="CPU Threads" value={infThreads} onChange={setInfThreads} fallback={DEFAULT_THREADS} />
                <NumberField id="inf-gpu-layers" label="GPU Layers (-1 to disable)" value={infGpuLayers} onChange={setInfGpuLayers} fallback={DEFAULT_GPU_LAYERS} allowZero />
                <NumberField id="inf-context" label="Context Size (tokens)" value={infContext} onChange={setInfContext} fallback={DEFAULT_CONTEXT_SIZE} />
              </div>

              <Field id="inf-args" label="Additional CLI Arguments">
                <input
                  id="inf-args"
                  type="text"
                  value={infArgs}
                  onChange={e => setInfArgs(e.target.value)}
                  placeholder="e.g. --cache-type-k q8_0"
                  className={FIELD_CLASS}
                />
              </Field>
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
                  {isConsolidated ? (
                    <span className="font-label-sm text-[10px] text-[#71717A] uppercase bg-white/5 border border-white/10 px-3 py-1.5 rounded-full">
                      Managed by Inference
                    </span>
                  ) : status?.embedding.running ? (
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

              {/* Consolidated Mode Toggle */}
              <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-[1rem] p-sm relative z-10">
                <div className="flex flex-col gap-0.5">
                  <span className="font-label-sm text-xs text-white font-medium">Consolidated Server Mode</span>
                  <span className="font-label-sm text-[10px] text-[#71717A] max-w-[380px]">
                    Run embeddings on the same server instance as inference (shares model & port, enables LLM --embedding option).
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer select-none">
                  <input 
                    type="checkbox" 
                    checked={isConsolidated} 
                    onChange={(e) => handleConsolidatedChange(e.target.checked)} 
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-[#27272A] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-4 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-white/90"></div>
                </label>
              </div>

              {isConsolidated && (
                <div className="text-[10px] text-emerald-400/90 font-label-sm bg-emerald-500/5 border border-emerald-500/10 rounded-[0.75rem] p-sm flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">info</span>
                  <span>Sharing port {infPort} and model {infModel.replace(MODEL_PREFIX, '') || 'Inference Model'}. Llama server will launch consolidated.</span>
                </div>
              )}

              {/* Form Fields */}
              <div className={`grid grid-cols-1 md:grid-cols-2 gap-sm transition-all duration-300 ${isConsolidated ? 'opacity-40 pointer-events-none' : ''}`}>
                <Field id="emb-binary" label="Runner Binary">
                  <select
                    id="emb-binary"
                    value={embBinary.replace(BINARY_PREFIX, '')}
                    onChange={e => setEmbBinary(`${BINARY_PREFIX}${e.target.value}`)}
                    className={FIELD_CLASS}
                    disabled={isConsolidated}
                  >
                    {status?.available_binaries.map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                    {status?.available_binaries.length === 0 && (
                      <option value="llama-server.exe">llama-server.exe (Default)</option>
                    )}
                  </select>
                </Field>

                <Field id="emb-model" label="Active GGUF Model">
                  <select
                    id="emb-model"
                    value={embModel.replace(MODEL_PREFIX, '')}
                    onChange={e => setEmbModel(e.target.value ? `${MODEL_PREFIX}${e.target.value}` : '')}
                    className={FIELD_CLASS}
                    required
                    disabled={isConsolidated}
                  >
                    <option value="">-- Choose Model --</option>
                    {status?.available_models.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </Field>

                <NumberField id="emb-port" label="Port" value={embPort} onChange={setEmbPort} fallback={DEFAULT_EMBEDDING_PORT} disabled={isConsolidated} />
                <NumberField id="emb-threads" label="CPU Threads" value={embThreads} onChange={setEmbThreads} fallback={DEFAULT_THREADS} disabled={isConsolidated} />
                <NumberField id="emb-gpu-layers" label="GPU Layers (-1 to disable)" value={embGpuLayers} onChange={setEmbGpuLayers} fallback={DEFAULT_GPU_LAYERS} allowZero disabled={isConsolidated} wrapperClassName="flex flex-col gap-1 col-span-2" />
              </div>

              <Field id="emb-args" label="Additional CLI Arguments">
                <input
                  id="emb-args"
                  type="text"
                  value={embArgs}
                  onChange={e => setEmbArgs(e.target.value)}
                  placeholder="e.g. --pooling cls"
                  className={`${FIELD_CLASS} ${isConsolidated ? 'opacity-40 pointer-events-none' : ''}`}
                  disabled={isConsolidated}
                />
              </Field>
            </div>
          )}

          {activeTab === 'samplers' && (
            <div className="flex flex-col gap-md">
              <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-[1rem] p-sm relative z-10">
                <div className="flex flex-col gap-0.5">
                  <span className="font-label-sm text-xs text-white font-medium">Global Sampler Preset</span>
                  <span className="font-label-sm text-[10px] text-[#71717A]">
                    Select the default sampling behavior for text generation.
                  </span>
                </div>
                <select
                  value={presets.find(p => p.is_default)?.id || ''}
                  onChange={async (e) => {
                    const id = parseInt(e.target.value, 10);
                    if (id) {
                      setLoading(true);
                      try {
                        const preset = presets.find(p => p.id === id);
                        if (preset) {
                          await api.updatePreset(id, { ...preset, is_default: true });
                          const updated = await api.fetchPresets();
                          setPresets(updated);
                        }
                      } catch {
                        setError('Failed to update default preset.');
                      } finally {
                        setLoading(false);
                      }
                    }
                  }}
                  className="bg-[#111] border border-white/10 rounded-[0.75rem] px-sm py-xs text-white font-label-sm text-sm focus:border-white focus:outline-none"
                >
                  {presets.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              {presets.find(p => p.is_default) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-sm mt-sm">
                  {Object.entries(presets.find(p => p.is_default)!).filter(([k]) => !['id', 'name', 'is_default'].includes(k)).map(([k, v]) => (
                    <div key={k} className="flex justify-between items-center border border-white/5 p-2 rounded-lg bg-white/[0.02]">
                      <span className="font-label-sm text-[10px] text-[#71717A] uppercase">{k.replace('_', ' ')}</span>
                      <span className="font-mono text-[10px] text-white">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end items-center gap-md pt-md border-t border-white/10 mt-sm">
            <button 
              onClick={onClose}
              disabled={loading}
              className="font-label-sm text-xs text-on-surface hover:text-white px-md py-xs border border-transparent hover:border-white/10 rounded-full transition-all duration-300 disabled:opacity-50"
              type="button"
            >
              Cancel
            </button>
            <button 
              disabled={loading || !infModel || (!isConsolidated && !embModel)}
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
