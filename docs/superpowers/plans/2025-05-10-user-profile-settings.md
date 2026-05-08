# User Profile Settings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a frontend UI in `App.tsx` to edit User Name and Gender, syncing with the `/users/me` backend API.

**Architecture:** Add user state and fetch/update logic to the main `App` component. Use a modal for the editing interface and a sidebar button as the trigger.

**Tech Stack:** React, Tailwind CSS, Lucide Icons, Fetch API.

---

### Task 1: State and Types

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add User interface**
Add the `User` interface after `Character` interface.
```typescript
interface User {
  id: number
  name: string
  gender: string
  is_active: boolean
}
```

- [ ] **Step 2: Add state variables**
Add `user` and `showProfileModal` state inside `App` component.
```typescript
const [user, setUser] = useState<User | null>(null)
const [showProfileModal, setShowProfileModal] = useState(false)
const [editUserName, setEditUserName] = useState('')
const [editUserGender, setEditUserGender] = useState('Male')
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): add user types and state"
```

### Task 2: API Integration

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Implement fetchUser**
Add `fetchUser` function and call it in `useEffect`.
```typescript
const fetchUser = async () => {
  try {
    const response = await fetch('/users/me')
    const data = await response.json()
    setUser(data)
    setEditUserName(data.name)
    setEditUserGender(data.gender)
  } catch (err) {
    console.error('Failed to fetch user', err)
  }
}

useEffect(() => {
  fetchCharacters()
  fetchUser() // Add this
}, [])
```

- [ ] **Step 2: Implement updateUser**
Add `updateUser` function.
```typescript
const updateUser = async () => {
  try {
    const response = await fetch('/users/me', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: editUserName, gender: editUserGender })
    })
    const data = await response.json()
    setUser(data)
    setShowProfileModal(false)
  } catch (err) {
    console.error('Failed to update user', err)
  }
}
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): implement user api integration"
```

### Task 3: Sidebar UI

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add profile trigger to sidebar**
Modify the sidebar footer to include the user profile button.
```tsx
{/* Global Systems Link */}
<div className="p-4 border-t border-zinc-800 bg-zinc-900/80 backdrop-blur space-y-2">
  <button 
    onClick={() => setShowProfileModal(true)}
    className="w-full flex items-center gap-2 p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 text-sm transition-colors"
  >
    <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500">
      <UserIcon size={14} />
    </div>
    <span className="truncate">{user?.name || 'Perfil'}</span>
  </button>
  <button className="w-full flex items-center gap-2 p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 text-sm transition-colors">
    <TagIcon size={16} /> Gerenciar Tags
  </button>
</div>
```
*Note: Make sure to import `User as UserIcon` from `lucide-react`.*

- [ ] **Step 2: Commit**
```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): add user profile trigger to sidebar"
```

### Task 4: Profile Modal

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add UserProfileModal JSX**
Add the modal JSX at the end of the component, similar to `Character Creator Modal`.
```tsx
{/* User Profile Modal */}
{showProfileModal && (
  <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div className="bg-zinc-900 border border-zinc-800 w-full max-w-md rounded-3xl p-8 shadow-2xl animate-in zoom-in-95 duration-200">
      <h2 className="text-2xl font-bold mb-6 text-white">Seu Perfil</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Nome</label>
          <input 
            type="text" 
            value={editUserName}
            onChange={e => setEditUserName(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors text-white"
            placeholder="Seu nome..."
          />
        </div>
        <div>
          <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1.5">Gênero</label>
          <select 
            value={editUserGender}
            onChange={e => setEditUserGender(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors text-white appearance-none"
          >
            <option value="Male">Masculino</option>
            <option value="Female">Feminino</option>
            <option value="Non-binary">Não-binário</option>
            <option value="Other">Outro</option>
          </select>
        </div>
      </div>
      <div className="flex gap-3 mt-8">
        <button 
          onClick={() => setShowProfileModal(false)}
          className="flex-1 px-4 py-3 rounded-xl bg-zinc-800 hover:bg-zinc-700 font-bold transition-colors text-white"
        >
          Cancelar
        </button>
        <button 
          onClick={updateUser}
          className="flex-1 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold transition-all text-white"
        >
          Salvar
        </button>
      </div>
    </div>
  </div>
)}
```

- [ ] **Step 2: Commit**
```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): add user profile modal"
```

### Task 5: Verification

- [ ] **Step 1: Run dev server**
Ensure the backend is running. Start the frontend.
Run: `cd frontend && pnpm dev` (if applicable) or verify in existing environment.

- [ ] **Step 2: Test profile update**
1. Open app.
2. Click on user name in sidebar.
3. Change name and gender.
4. Click Save.
5. Verify sidebar name updates.
6. Refresh page and verify data persists.

- [ ] **Step 3: Final Commit**
```bash
git commit -m "feat: complete user profile settings UI"
```
