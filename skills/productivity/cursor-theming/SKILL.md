---
name: cursor-theming
description: Managing and applying system-wide cursor theme configurations across Linux desktop environments (Hyprland, GTK, X11).
---

# Cursor Theming Strategy

Ensuring cursor consistency across a Linux desktop (Hyprland + GTK + X11) requires updates in multiple configuration locations. The most common failure is a stale `XCURSOR_THEME` in `hyprland.conf` that overrides everything else.

## Diagnosis (run these first)

```bash
# 1. Find the actual theme directory name (spaces, parens, casing matter)
ls ~/.icons/ | grep -i diamond

# 2. Check if Hyprland uses hyprcursor or X11 xcursor backend
#    If enable_hyprcursor = false, it uses xcursor. HYPRCURSOR_THEME is then ignored.
grep -A2 'cursor {' ~/.config/hypr/configs/SystemSettings.conf

# 3. Check for overriding env vars (MOST COMMON ROOT CAUSE)
grep XCURSOR_THEME ~/.config/hypr/hyprland.conf

# 4. Check current active state
gsettings get org.gnome.desktop.interface cursor-theme
gsettings get org.gnome.desktop.interface cursor-size
```

## Configuration Files (check all of these)

| File | Key | Priority |
|------|-----|----------|
| `~/.config/hypr/hyprland.conf` | `env = XCURSOR_THEME,...` | **HIGHEST** — overrides everything for X11 cursors on Hyprland |
| `~/.config/hypr/configs/ENVariables.conf` | `env = HYPRCURSOR_THEME,...` | Only applies when hyprcursor enabled |
| `~/.config/hypr/configs/Startup_Apps.conf` | `exec-once = hyprctl setcursor ...` | Set at startup |
| `~/.config/hypr/initial-boot.sh` | `gsettings set ... cursor-theme` | First-boot only |
| `~/.config/gtk-3.0/settings.ini` | `gtk-cursor-theme-name=...` | GTK3 apps |
| `~/.config/gtk-4.0/settings.ini` | `gtk-cursor-theme-name=...` | GTK4 apps |
| `~/.config/xsettingsd/xsettingsd.conf` | `Gtk/CursorThemeName ...` | X11 settings daemon (if installed) |
| `~/.icons/default/index.theme` | `Inherits=...` | X11 fallback |

## Update Process

1. **Sync theme name**: The value in every file must exactly match the directory name under `~/.icons/`. Spaces, parentheses, and capitalisation count.
2. **Sync cursor size**: Ensure all configs use the same size (check gsettings first).
3. **Apply live**:
   ```bash
   hyprctl setcursor "Theme Name" 24
   gsettings set org.gnome.desktop.interface cursor-theme "Theme Name"
   gsettings set org.gnome.desktop.interface cursor-size 24
   ```
4. **Restart affected apps**: Browsers and Electron apps need a restart to pick up the change.

## Pitfalls

- **XCURSOR_THEME in hyprland.conf is king**: If `~/.config/hypr/hyprland.conf` has `env = XCURSOR_THEME,SomeOtherTheme`, it overrides *everything* — gsettings, GTK configs, startup scripts. Always check this file first when a cursor change doesn't take effect.
- **Name mismatch**: A theme directory named `Night Diamond (Blue)` will NOT be found if configs say `NightDiamond`. The exact string in the folder name must be used.
- **Hyprcursor vs XCursor**: If `enable_hyprcursor = false` in SystemSettings.conf, Hyprland uses the X11 xcursor backend. In that case `HYPRCURSOR_THEME` is ignored and only `XCURSOR_THEME` matters.
- **Size inconsistency**: One file with size 20 while others have 24 causes inconsistent cursor sizes across apps. Sync everywhere.
- **xsettingsd not installed**: On pure Wayland/Hyprland setups, `xsettingsd` may not be installed. Its absence is fine — the gsettings-based path covers GTK apps.
