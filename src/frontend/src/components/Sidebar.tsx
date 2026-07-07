import React from 'react'

interface SidebarProps {
  currentView: string
  setView: (view: string) => void
  userName?: string
  onProfileClick?: () => void
  onSettingsClick?: () => void
  isOpen?: boolean
  onClose?: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ 
  currentView, 
  setView, 
  userName, 
  onProfileClick, 
  onSettingsClick,
  isOpen,
  onClose 
}) => {
  const navItems = [
    { id: 'characters', label: 'Characters', icon: 'group' },
    { id: 'chat', label: 'Direct Chat', icon: 'chat_bubble' },
    { id: 'library', label: 'Lorebook', icon: 'menu_book' },
    { id: 'archives', label: 'Knowledge Tags', icon: 'bookmarks' },
  ]

  return (
    <nav className={`fixed md:sticky top-0 bottom-0 left-0 z-50 flex md:h-[100dvh] w-64 flex-col bg-[#0A0A0B]/95 md:bg-[#0A0A0B]/85 backdrop-blur-md text-white border-r border-white/5 py-lg px-md transition-transform duration-300 md:translate-x-0 flex-shrink-0 overflow-hidden ${
      isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full md:translate-x-0'
    }`}>
      {/* Ambient background glow inside sidebar */}
      <div className="absolute -top-20 -left-20 w-48 h-48 bg-white/5 rounded-full blur-[60px] pointer-events-none" />

      {/* Brand Header */}
      <div className="flex items-center gap-3 px-1 mb-xl relative z-10">
        <div className="w-9 h-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden shrink-0 shadow-lg">
          <span className="material-symbols-outlined text-white text-md">auto_stories</span>
        </div>
        <div className="flex flex-col gap-0.5">
          <h1 className="font-sans text-lg font-bold text-white tracking-tight leading-none">Open-ChatBot</h1>
          <span className="font-label-sm text-[9px] text-[#71717A] uppercase tracking-[0.2em]">
            Writers Room
          </span>
        </div>
        
        {/* Mobile close button */}
        <button 
          onClick={onClose}
          className="md:hidden ml-auto text-[#71717A] hover:text-white"
        >
          <span className="material-symbols-outlined text-lg">close</span>
        </button>
      </div>

      {/* Navigation Links */}
      <ul className="flex-1 flex flex-col gap-2 relative z-10">
        {navItems.map((item) => {
          const isActive = currentView === item.id
          return (
            <li key={item.id}>
              <button
                onClick={() => {
                  setView(item.id)
                  onClose?.()
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-full border transition-all duration-300 group ${
                  isActive
                    ? 'bg-white text-black border-white shadow-lg font-medium scale-[0.98]'
                    : 'text-[#A1A1AA] border-transparent hover:text-white hover:bg-white/5 hover:border-white/5'
                }`}
              >
                <span 
                  className={`material-symbols-outlined text-[18px] transition-all duration-300 ${
                    isActive ? 'text-black' : 'text-[#71717A] group-hover:text-white'
                  }`}
                  style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {item.icon}
                </span>
                <span className="font-label-sm text-xs tracking-wider uppercase">
                  {item.label}
                </span>
              </button>
            </li>
          )
        })}
      </ul>

      {/* Profile Area */}
      <div className="mt-auto pt-md border-t border-white/5 flex items-center justify-between gap-2 relative z-10">
        <div 
          onClick={() => {
            onProfileClick?.()
            onClose?.()
          }}
          className="flex-1 flex items-center gap-3 px-2 py-1.5 cursor-pointer hover:bg-white/5 rounded-full border border-transparent hover:border-white/5 transition-all duration-300 min-w-0"
        >
          <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-[#A1A1AA] text-sm">person</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-label-sm text-[11px] uppercase tracking-wider text-white truncate">
              {userName || 'User Profile'}
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            onSettingsClick?.()
            onClose?.()
          }}
          className="w-8 h-8 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 text-[#A1A1AA] hover:text-white transition-all duration-300 flex items-center justify-center shrink-0"
          title="Settings"
        >
          <span className="material-symbols-outlined text-[16px]">settings</span>
        </button>
      </div>
    </nav>
  )
}

export default Sidebar
