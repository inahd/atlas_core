# FE-003: Unify CSS variables across all frontend pages

**Phase**: 4  
**Priority**: LOW  
**Estimated time**: 2–3 hrs

## Context

Each of the 20 HTML pages defines its own CSS color variables. Some are consistent,
some aren't. Extracting to a shared `static/atlas-theme.css` makes global design
changes a single-file edit and ensures visual consistency.

## Instructions

### Step 1: Collect all CSS variable definitions

```bash
grep -h "^\s*--" ~/atlas_core/static/*.html ~/atlas_core/static/widgets/*.html \
  | sed 's/^\s*//' | sort -u
```

### Step 2: Identify the canonical values

From the skill files, the Atlas dark palette is:
```css
:root {
  --bg: #040201;           /* deepest background */
  --bg2: #0a0a08;          /* panel background */
  --text: rgba(220,218,206,0.9);
  --gold: rgba(200,169,110,1);
  --gold-dim: rgba(200,169,110,0.4);
  --green: rgba(93,202,165,1);
  --green-dim: rgba(93,202,165,0.3);
  --amber: rgba(220,160,60,1);
  --red: rgba(200,80,60,0.8);
  --border: rgba(200,169,110,0.15);
  --font-body: 'Cormorant Garamond', Georgia, serif;
  --font-mono: 'Space Mono', monospace;
}
```

Compare these against what's actually in the files. Note any conflicts.

### Step 3: Write static/atlas-theme.css

Create the canonical theme file with all variables, plus:
- Base resets (`*, body { box-sizing: border-box; margin: 0; }`)
- Font imports (Cormorant Garamond + Space Mono from Google Fonts)
- Common utility classes (`.live-badge`, `.field-label`, `.panel`, etc.)

### Step 4: Update pages to use it

For each HTML page:
1. Add `<link rel="stylesheet" href="/static/atlas-theme.css">` in `<head>`
2. Remove the inline `:root { --var: value; }` blocks that are now in atlas-theme.css
3. Keep any page-specific variables that aren't in the theme

Do this one file at a time. Test each in browser before moving on.

### Step 5: Test visual consistency

```bash
# Verify all pages reference the theme
grep -l "atlas-theme.css" ~/atlas_core/static/*.html | wc -l
# Should equal total number of HTML files
```

## Success check

```bash
test -f ~/atlas_core/static/atlas-theme.css && echo "theme file: OK"
wc -l ~/atlas_core/static/atlas-theme.css
# Should be > 30 lines

# No page should still define --bg or --gold inline
grep -l "^\s*--bg:" ~/atlas_core/static/*.html | wc -l
# Should be 0
```

## Output

- Create `static/atlas-theme.css`
- Update all 20 HTML pages to reference it
- Remove duplicate inline variable definitions
