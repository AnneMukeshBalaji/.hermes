---
name: react-debugging
description: "Systematic debugging of React applications — blank screens, rendering errors, and build failures."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [react, debugging, frontend, troubleshooting, vite]
    related_skills: [systematic-debugging, node-inspect-debugger]
---

# React Application Debugging

## Overview

React apps that show a white screen / blank page typically fail BEFORE rendering anything — the JS failed to compile, an import resolved to `undefined`, or a component threw during its first render. This skill provides a structured approach to finding the root cause.

**Core principle:** The blank page is a symptom of a failed *load or first render*. Trace the chain backwards: page load → module compilation → component mount.

## When to Use

- App shows a white screen / blank page on dev or production build
- "Nothing renders" — no errors visible in the browser (but check devtools console)
- Components appear at build time but produce blank output at runtime
- Import or module resolution issues

**Pair with `systematic-debugging`** for complex bugs that require data-flow tracing through the component tree.

## Common White Screen Causes (check in order)

### 1. Build / Compilation Errors

Run the build first — it catches problems the dev server might mask or show as overlay:

```bash
npm run build   # or: npx vite build
```

Ignore the "foreground command" guard if it triggers — run in background (`notify_on_complete=true`) and read the output. Look for:

- `[MISSING_EXPORT] "default" is not exported by X` — default import vs named export mismatch
- `[MISSING_EXPORT] "X" is not exported by Y` — named import vs named export name mismatch
- `Module not found` — file doesn't exist or path is wrong

Compilation errors mean the bundle never loads → white screen is expected. Fix the imports/exports, re-build.

### 2. Named Export vs Default Import Mismatch (very common in tutorial code)

In the component file:
```jsx
export const MyComponent = () => { ... }   // named export
```

In the parent:
```jsx
import MyComponent from "./MyComponent"    // default import — WRONG for named export
```

This makes `MyComponent` resolve to `undefined`. React renders `<undefined />` → throws → blank screen.

**What to check:**
- Read every component file's export statement
- Read every import in the parent (especially App.jsx)
- Match: `export default Function` or `export default function` ↔ `import X from "..."` (default)
- Match: `export const X` or `export function X` ↔ `import { X } from "..."` (named)

**Quick scan command:**
```bash
grep -rn "^export" src/                      # all exports
grep -rn "^import" src/App.jsx               # all imports in App
```

### 3. Missing or Incorrect Entry Point Chain

Verify the chain: `index.html` → `main.jsx` → `App.jsx` → routes/components

**Check index.html:**
- Does `<div id="root">` exist?
- Does the script tag point to the right entry (`/src/main.jsx`)?

**Check main.jsx:**
- Does it call `createRoot(document.getElementById('root'))`?
- Does it render `<App />`?
- Is `index.css` imported (CSS can hide content)?

### 4. Missing Imported Component Module

If `App.jsx` imports a component from a file that doesn't exist:
```jsx
import MusicPlayer from "./components/MusicPlayer"  // file doesn't exist
```

Vite's build will error (`Module not found`), but the dev server might silently fail.

**Check:** List files in the import directory:
```bash
ls src/components/
```

### 5. CSS That Hides Content

Less common, but check if CSS has:
- `display: none` on root elements
- `opacity: 0` or `visibility: hidden` on `#root` or `.app`
- `overflow: hidden` that clips content
- No background color set (text renders white on white)

**Quick test:** Open browser devtools → inspect `#root` element → check computed styles.

### 6. Runtime Error During Initial Render

If compilation succeeds but the app still shows blank:

- Check browser console for errors (dev server overlays may be dismissed)
- Check for missing providers — `BrowserRouter`, context providers, data fetching:
  - `useParams()` / `useSearchParams()` used outside a `<Routes>` or `<Router>` context
  - `useNavigate()` called outside a `<Router>`
  - Context `useContext()` with no matching provider
- Check for `undefined` being used as a child in JSX:
  ```jsx
  {items.map(item => ...)}  // items is undefined → crash
  ```

## Step-by-Step Diagnosis Flow

Use this order — it goes from cheapest to most expensive checks:

```
1. npx vite build              ← catches compile errors first
   ↓ (if passes)
2. Check index.html → main.jsx → App.jsx chain
   ↓ (if chain looks right)
3. Check all imports vs exports (named vs default)
   ↓ (if matching)
4. Check component files exist at import paths
   ↓ (if they exist)
5. Check browser devtools console for runtime errors
```

## Pitfalls

- **Dev server can mask import errors.** A component may import fine on the dev server (hot reload) but fail on build. Always run `vite build` to confirm.
- **Error overlays.** In React 19 + Vite, some errors show as an overlay on the dev page that you need to dismiss to see the white screen behind it. The user may be seeing the overlay and calling it a white screen — ask them to check.
- **react-router v8 imports.** In v8, `BrowserRouter`, `Routes`, `Route` are available from `"react-router"` directly (not `"react-router-dom"`). If the package.json has `react-router` (not `react-router-dom`), importing from `"react-router"` is correct.
- **Named export, multiple ways.** `export default function Foo` and `export default Foo` are both default exports. `export const Foo = ...` and `export function Foo() {}` are both named exports. Don't confuse them.

## Related

- `systematic-debugging` — for the generic 4-phase debugging process (tight feedback loop, root cause investigation)
- `node-inspect-debugger` — for React Node/SSR debugging
