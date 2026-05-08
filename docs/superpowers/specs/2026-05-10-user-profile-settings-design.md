# Design Doc: User Profile Settings UI

## Overview
Implement a frontend interface to allow users to view and edit their profile (Name and Gender). This data is used by the backend character engine to personalize interactions.

## Architecture
- **State Management:** Add `user` state to `App.tsx` using `useState`.
- **API Integration:** 
  - `fetchUser`: GET `/users/me` on component mount.
  - `updateUser`: POST `/users/me` when the profile is saved.
- **UI Components:**
  - `UserProfileModal`: A new modal component (or inline JSX in `App.tsx` following existing patterns) for editing.
  - Sidebar Trigger: A button in the sidebar footer to open the modal.

## UI Details
- **Trigger:** Located in the sidebar footer, showing the current user's name.
- **Modal Fields:**
  - Name (Text Input)
  - Gender (Select Dropdown: Male, Female, Non-binary, Other)
- **Styling:** Consistent with the existing zinc/emerald dark theme. Use `lucide-react` icons (User, Settings).

## Data Flow
1. App starts -> `useEffect` calls `fetchUser`.
2. User clicks sidebar profile button -> `setShowProfileModal(true)`.
3. User edits fields and clicks "Save".
4. `updateUser` is called with new data.
5. On success, local `user` state is updated, and modal closes.

## Success Criteria
- User can change their name and gender.
- Changes persist after page refresh (verified by fetching from backend).
- UI follows existing design patterns and is responsive.
