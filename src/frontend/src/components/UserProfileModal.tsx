import React, { useState } from 'react'

interface User {
  name: string
  gender: string
  persona_description?: string
  appearance?: string
}

interface UserProfileModalProps {
  user: User | null
  onClose: () => void
  onUpdate: (name: string, gender: string, persona: string, appearance: string) => Promise<void> | void
}

const UserProfileModal: React.FC<UserProfileModalProps> = ({ user, onClose, onUpdate }) => {
  const [name, setName] = useState(user?.name || '')
  const [gender, setGender] = useState(user?.gender || 'Male')
  const [persona, setPersona] = useState(user?.persona_description || '')
  const [appearance, setAppearance] = useState(user?.appearance || '')
  const [isSaving, setIsSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    await onUpdate(name, gender, persona, appearance)
    setIsSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-surface-container-lowest/80 backdrop-blur-sm z-50 flex items-center justify-center p-sm md:p-md">
      <div className="w-full max-w-[500px] rounded-[1.5rem] bg-[#111111] border border-[#1A1A1A] p-lg md:p-xl flex flex-col gap-lg z-50 animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-start w-full">
          <div className="flex flex-col gap-xs">
            <h2 className="font-heading-lg text-heading-lg text-primary tracking-tight">User Profile</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Update your narrative presence.</p>
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
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="user_name">Display Name</label>
            <input 
              value={name}
              onChange={e => setName(e.target.value)}
              className="input-premium w-full font-body-lg text-body-lg text-primary placeholder-on-surface-variant/30"
              id="user_name"
              placeholder="How should the AI address you?" 
              type="text"
              required
            />
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="user_gender">Gender Identity</label>
            <select 
              value={gender}
              onChange={e => setGender(e.target.value)}
              className="w-full bg-transparent border-0 border-b pb-xs font-body-md text-body-md text-primary focus:ring-0 appearance-none cursor-pointer" 
              id="user_gender"
            >
              <option value="Male" className="bg-[#111111]">Male</option>
              <option value="Female" className="bg-[#111111]">Female</option>
              <option value="Non-binary" className="bg-[#111111]">Non-binary</option>
              <option value="Unknown" className="bg-[#111111]">Prefer not to say</option>
            </select>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="user_appearance">Physical Appearance</label>
            <textarea 
              value={appearance}
              onChange={e => setAppearance(e.target.value)}
              className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
              id="user_appearance"
              placeholder="e.g., Tall, dark hair, wearing a leather jacket..." 
              rows={2}
            />
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-sm text-label-sm text-[#71717A] uppercase" htmlFor="user_persona">Personality / Background</label>
            <textarea 
              value={persona}
              onChange={e => setPersona(e.target.value)}
              className="input-premium w-full font-body-md text-body-md text-primary placeholder-on-surface-variant/30 resize-none"
              id="user_persona"
              placeholder="e.g., Sarcastic, former mercenary, secretly loves cats..." 
              rows={2}
            />
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
              {isSaving ? 'Updating...' : 'Update Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UserProfileModal
