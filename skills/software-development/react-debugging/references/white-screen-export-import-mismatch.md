# White Screen: Named Export vs Default Import Mismatch

## Session Context

User was building a React music player app following a YouTube tutorial. Getting a white screen on open.

## Project Structure

```
react-projects/
├── index.html                  ← <div id="root"> + script to /src/main.jsx
├── vite.config.js              ← standard @vitejs/plugin-react
├── package.json                ← react 19, react-router v8, vite 8
└── src/
    ├── main.jsx                ← createRoot → <App />
    ├── App.jsx                 ← BrowserRouter, imports MusicPlayer/AllSongs/Playlists
    ├── index.css               ← dark theme, styled
    └── components/
        ├── MusicPlayer.jsx     ← export default function MusicPlayer()
        ├── AllSongs.jsx        ← export const AllSongs = () => ...   ← NAMED export
        └── Playlists.jsx       ← export const Playlists = () => ...  ← NAMED export
```

## Root Cause

Two components (`AllSongs`, `Playlists`) used **named exports** (`export const X`), but `App.jsx` imported them as **default imports** (`import X from "./components/X"`).

In ESM, when a named-export-only module is default-imported, the import resolves to `undefined`. React then tries `<undefined />` → throws → blank screen.

## Build Output (confirms diagnosis)

```
[MISSING_EXPORT] "default" is not exported by "src/components/AllSongs.jsx".
    at src/App.jsx:2:8
    import AllSongs from "./components/AllSongs";

[MISSING_EXPORT] "default" is not exported by "src/components/Playlists.jsx".
    at src/App.jsx:3:8
    import Playlists from "./components/Playlists";
```

## Fix

Change each component to a default export:

```jsx
// Before (named export):
export const AllSongs = () => { return <div>AllSongs</div> }

// After (default export):
const AllSongs = () => { return <div>AllSongs</div> }
export default AllSongs
```

Or one-liner:
```jsx
export default function AllSongs() { return <div>AllSongs</div> }
```

## Key Takeaway

- `export const X` / `export function X` → default import `X` from `"..."` is WRONG
- `export default X` or `export default function X` → default import `X` from `"..."` is CORRECT
- `export const X` → named import `{ X }` from `"..."` is CORRECT
