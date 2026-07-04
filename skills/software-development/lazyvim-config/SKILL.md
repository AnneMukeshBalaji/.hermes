---
name: lazyvim-config
title: LazyVim Configuration Management
description: Manage a LazyVim-based Neovim setup -- install/swap colorschemes, add plugins, and adjust config files while respecting the LazyVim plugin spec structure.
triggers:
  - user wants to change neovim colorscheme
  - user wants to add/remove a neovim plugin
  - user asks about lazyvim config structure
  - user wants to modify neovim appearance or behavior
category: software-development
tags:
  - neovim
  - lazyvim
  - colorscheme
  - lua
---

# LazyVim Configuration Management

This user runs LazyVim (folke/lazy.nvim plugin manager) with their config at `~/.config/nvim/`. The setup uses a structured plugin spec pattern — not a flat vimrc.

## Config File Structure

```
~/.config/nvim/
  init.lua              # Entry point, requires config/lazy
  lazyvim.json          # LazyVim extras manifest (langs, tools)
  lua/
    config/
      lazy.lua          # Lazy.nvim bootstrap + plugin spec root
      options.lua       # Neovim options
      keymaps.lua       # Key mappings
    plugins/            # One file per plugin or plugin category
      colorscheme.lua   # Colorscheme plugin + config
      mason.lua
      lualine.lua
      conform.lua
      ...
```

## Swapping a Colorscheme

Two files must be updated:

### 1. `lua/plugins/colorscheme.lua` — the plugin definition

This is a lazy.nvim plugin spec. The pattern depends on the theme type:

**Lua-based themes with opts table** (e.g. `navarasu/onedark.nvim`, `olimorris/onedarkpro.nvim`):
```lua
return {
  "author/repo",
  lazy = false,
  priority = 1000,
  opts = {
    -- theme-specific options go here
    -- Lua themes expose a .setup(opts) or .load() call
  },
  config = function(_, opts)
    require("theme_module").setup(opts)
    require("theme_module").load()  -- if required
  end,
}
```

**Themes with global-selection variable** (e.g. `olimorris/onedarkpro.nvim`):
```lua
return {
  "olimorris/onedarkpro.nvim",
  lazy = false,
  priority = 1000,
  opts = {
    -- options go in opts table (styles, options.transparency, etc.)
    options = { transparency = true },
  },
  config = function(_, opts)
    -- MUST set the theme globals BEFORE setup() call
    vim.g.onedarkpro_theme = "onedark_dark"  -- or onedark, onedark_vivid, onelight, vaporwave
    require("onedarkpro").setup(opts)
    vim.cmd.colorscheme("onedark")
  end,
}
```

**Vimscript-based themes** (e.g. `joshdick/onedark.vim`):
```lua
return {
  "author/repo",
  lazy = false,
  priority = 1000,
  init = function()
    -- Set vim.g.* variables BEFORE colorscheme loads
    vim.g.onedark_hide_endofbuffer = 1
  end,
  config = function()
    vim.cmd.colorscheme("name")
  end,
}
```

### 2. `lua/config/lazy.lua` — LazyVim colorscheme ref

Find the `LazyVim/LazyVim` spec line and update the `colorscheme` option:

```lua
{ "LazyVim/LazyVim", import = "lazyvim.plugins", opts = { colorscheme = "name" } }
```

This tells LazyVim which colorscheme to default to, avoiding conflicts with LazyVim's built-in theme loader.

## Overriding Specific Colors

Some themes expose `on_colors` and `on_highlights` callbacks to override individual palette colors after your opts are applied.

**solarized-osaka example** — replace a color (yellow -> orange):
```lua
config = function(_, opts)
  -- Add callbacks BEFORE setup so theme applies them during load
  opts.on_colors = function(colors)
    colors.yellow = colors.orange     -- swap a palette color
    colors.warning = colors.orange    -- also swap derived colors
  end
  opts.on_highlights = function(highlights, colors)
    highlights.Type = { fg = colors.purple }  -- override highlight groups
  end
  require("solarized-osaka").setup(opts)
  vim.cmd.colorscheme("solarized-osaka")
end
```

**onedarkpro example** — override colors and highlights:
```lua
require("onedarkpro").setup({
  colors = {
    red = "#FF0000",                    -- replace a color with hex
    my_custom = require("onedarkpro.helpers").darken("green", 10, "onedark"),
  },
  highlights = {
    Error = { fg = "${my_custom}", bg = "${red}" },  -- reference custom colors with ${}
  },
})
```

Check each theme's README for `on_colors`/`on_highlights` support — not all themes have them.

## Transparent Background

Some themes expose `transparent = true` (solarized-osaka), others use `transparent_background = true` (night-owl). Check each theme's README.

**Multi-level transparency**: Some themes (e.g. solarized-osaka) have separate transparency controls for sidebars and floats via `styles`:

```lua
opts = {
  transparent = true,          -- main editor transparent
  styles = {
    sidebars = "transparent",  -- sidebar windows transparent (not "dark")
    floats = "transparent",    -- floating windows transparent (not "dark")
  },
}
```

When user says "make everything transparent", sidebars and floats need their own setting too. The `styles.sidebars` and `styles.floats` accept `"transparent"`, `"dark"`, or `"normal"`.

**Undercurl support**: Some themes (e.g. night-owl.nvim) have `undercurl = true` as a top-level `opts` key alongside `bold`, `italics`, `underline`.

**Vimscript themes** need an autocmd override:

```lua
vim.api.nvim_create_autocmd("ColorScheme", {
  pattern = "themename",
  callback = function()
    vim.api.nvim_set_hl(0, "Normal", { bg = "none" })
    vim.api.nvim_set_hl(0, "NormalFloat", { bg = "none" })
  end,
  once = true,
})
```

## After Changes

Always sync the plugin manager to install/remove/update:

```bash
nvim --headless "+Lazy! sync" +qa
```

Then verify the colorscheme loads:
```bash
nvim --headless "+colorscheme name" "+echo 'OK'" +qa
```

## Common Themes Tried

| Repo | Type | Variants | Notes |
|---|---|---|---|
| `navarasu/onedark.nvim` | Lua | dark, darker, cool, deep, warm, warmer, light | `require("onedark").setup({style="darker"}); require("onedark").load()` |
| `olimorris/onedarkpro.nvim` | Lua | onedark, onedark_dark, onedark_vivid, onelight, vaporwave | `require("onedarkpro").setup({theme="onedark_dark"})` |
| `joshdick/onedark.vim` | Vimscript | flat (single style) | `vim.g.*` in `init`, `vim.cmd.colorscheme("onedark")` in `config` |
| `shaunsingh/nord.nvim` | Lua | flat (nord palette) | `require("nord").set()` |
| `oxfist/night-owl.nvim` | Lua | flat (one dark variant) | `require("night-owl").setup(opts)`, then `vim.cmd.colorscheme("night-owl")` — uses `transparent_background = true` |
| `craftzdog/solarized-osaka.nvim` | Lua | solarized-inspired | `require("solarized-osaka").setup(opts)`, then `vim.cmd.colorscheme("solarized-osaka")` — has `styles.sidebars`/`styles.floats` accepting `"transparent"`, `"dark"`, `"normal"` |

## Pitfalls

- **Forgetting lazy.lua update**: if you only change colorscheme.lua but don't update the `colorscheme` option in lazy.lua, LazyVim may override your theme on startup.
- **Wrong config function signature**: For Lua themes using `opts`, the `config` function receives `(_, opts)` where opts is the merged result. For themes without opts, use `config = function() ... end`.
- **Vimscript themes have no `opts`**: They use `init` for `vim.g` vars and `config` for `vim.cmd.colorscheme()`.
- **onedarkpro theme selected via global**: `vim.g.onedarkpro_theme = "onedark_dark"` MUST be set BEFORE `require("onedarkpro").setup(opts)`. If you put it after, it is ignored.
- **Sibling subagent file corruption**: When delegate_task spawns a sibling that also edits `colorscheme.lua` or `lazy.lua`, the file may end up with leftover garbage (orphaned lines from the sibling's edit that got merged into the wrong position). Always use `write_file` instead of `patch` when the file has been touched by a parallel agent, or read the file first to verify no garbage remains.
