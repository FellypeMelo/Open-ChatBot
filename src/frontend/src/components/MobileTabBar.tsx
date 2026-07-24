import React from 'react'
import Icon from './Icon'

interface MobileTabBarProps {
  currentView: string
  setView: (view: string) => void
  // Immersive reading: slide the bar off-screen (it's fixed, so translating it
  // down clears the viewport cleanly) while the user scrolls down into a chat.
  hidden?: boolean
}

/** The four primary destinations, shared conceptually with the desktop Sidebar. */
const TABS = [
  { id: 'characters', label: 'Characters', icon: 'group' },
  { id: 'chat', label: 'Chat', icon: 'chat_bubble' },
  { id: 'library', label: 'Lore', icon: 'menu_book' },
  { id: 'archives', label: 'Tags', icon: 'bookmarks' },
] as const

/**
 * Thumb-reachable bottom navigation for phones. Replaces the hamburger drawer
 * as the primary way to switch views on mobile: icon + micro-label per tab,
 * one accent, consistent 44px+ hit areas. Rendered only under the `md`
 * breakpoint (see useIsMobile) so it never duplicates the desktop Sidebar nav.
 */
const MobileTabBar: React.FC<MobileTabBarProps> = ({ currentView, setView, hidden = false }) => (
  <nav
    aria-label="Primary"
    className={`fixed bottom-0 inset-x-0 z-40 flex items-stretch bg-[#0A0A0B]/95 backdrop-blur-md border-t border-white/10 pb-[env(safe-area-inset-bottom)] transition-transform duration-300 ${
      hidden ? 'translate-y-full pointer-events-none' : 'translate-y-0'
    }`}
  >
    {TABS.map((tab) => {
      const isActive = currentView === tab.id
      return (
        <button
          key={tab.id}
          type="button"
          onClick={() => setView(tab.id)}
          aria-current={isActive ? 'page' : undefined}
          className={`flex-1 flex flex-col items-center justify-center gap-0.5 min-h-14 pt-1.5 pb-1 transition-colors touch-manipulation active:scale-95 cursor-pointer ${
            isActive ? 'text-white' : 'text-[#71717A]'
          }`}
        >
          <Icon name={tab.icon} size="md" filled={isActive} />
          <span className="font-mono text-[10px] tracking-wide uppercase leading-none">
            {tab.label}
          </span>
        </button>
      )
    })}
  </nav>
)

export default MobileTabBar
