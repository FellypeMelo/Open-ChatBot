import React from 'react'

interface SidebarProps {
  currentView: string
  setView: (view: string) => void
  userName?: string
  onProfileClick?: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, setView, userName, onProfileClick }) => {
  const navItems = [
    { id: 'library', label: 'Library', icon: 'book' },
    { id: 'chat', label: 'Active Stories', icon: 'chat_bubble' },
    { id: 'characters', label: 'Characters', icon: 'person' },
    { id: 'archives', label: 'Archives', icon: 'inventory_2' },
  ]

  return (
    <nav className="hidden md:flex bg-surface-container-low text-on-surface border-r border-outline-variant h-screen w-64 flex-col py-md px-sm flex-shrink-0 z-40 fixed left-0 top-0">
      {/* Brand Header */}
      <div className="flex items-center gap-sm px-2 mb-lg">
        <div className="w-8 h-8 rounded-full bg-surface-container-highest border border-outline-variant flex items-center justify-center overflow-hidden shrink-0">
          <span className="material-symbols-outlined text-primary">auto_stories</span>
        </div>
        <div>
          <h1 className="font-display text-headline-lg font-bold text-primary tracking-tight">Open Chat</h1>
          <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mt-1">Writers Room</p>
        </div>
      </div>

      {/* Navigation Links */}
      <ul className="flex-1 flex flex-col gap-unit">
        {navItems.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-sm px-2 py-2 rounded transition-all group ${
                currentView === item.id
                  ? 'text-primary border-l-2 border-primary pl-2 bg-surface-container scale-[0.99]'
                  : 'text-on-surface-variant pl-2 hover:bg-surface-container'
              }`}
            >
              <span 
                className={`material-symbols-outlined transition-colors ${
                  currentView === item.id ? 'text-primary' : 'group-hover:text-primary'
                }`}
                style={{ fontVariationSettings: currentView === item.id ? "'FILL' 1" : "'FILL' 0" }}
              >
                {item.icon}
              </span>
              <span className={`font-body-md text-body-md ${currentView === item.id ? 'font-medium' : ''}`}>
                {item.label}
              </span>
            </button>
          </li>
        ))}
      </ul>

      {/* CTA Button at Bottom */}
      <div className="mt-auto pt-md">
        <button className="w-full py-2 px-4 border border-outline-variant text-primary rounded font-body-md text-body-md hover:border-outline hover:bg-surface-container transition-all flex justify-center items-center gap-xs">
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Story
        </button>
      </div>

      {/* Profile area */}
      <div 
        onClick={onProfileClick}
        className="mt-4 pt-sm border-t border-outline-variant flex items-center gap-sm px-xs cursor-pointer hover:opacity-80 transition-opacity"
      >
        <div className="w-8 h-8 rounded-full bg-surface-container-highest border border-outline-variant flex items-center justify-center overflow-hidden shrink-0">
          <span className="material-symbols-outlined text-on-surface-variant text-sm">person</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-body-md text-body-md truncate">{userName || 'User Profile'}</p>
        </div>
      </div>
    </nav>
  )
}

export default Sidebar
