# Atlas Visual Standards
# READ THIS BEFORE TOUCHING ANY CSS, SVG, OR COLOR VALUE
# These are not suggestions. Violations break the system.

---

## The One Rule

**Never use opacity to make something less prominent.**
**Never use rgba() with alpha below 0.9 for text.**
**Use a darker solid hex instead.**

Wrong:  `color: rgba(255,255,255,0.3)`
Right:  `color: #4a5a68`

Wrong:  `opacity: 0.5`
Right:  change the hex value

---

## Ground

```css
--shyama:  #0a0d1a   /* Krishna's complexion — never pure black */
--panel:   #141828   /* panel backgrounds */
--card:    #1a2030   /* card backgrounds */
```

Never use `#000000`. Never use `#080808`. Ground is shyama.

---

## Text — Minimum Values (never go below these)

```css
--text:       #ffffff   /* primary — all data values */
--text-dim:   #8899aa   /* labels, secondary — solid hex */
--text-hint:  #5a6a78   /* hints, meta — solid hex */
```

Minimum font size: **14px for data, 11px for labels**
Never below 11px. Never.

---

## Zone Backgrounds (canonical — never change these)

```css
#zone-nw  { background: #0d2818; border-left: 2px solid #5cb87a; }
#zone-n   { background: #0d1828; border-left: 2px solid #8899bb; }
#zone-ne  { background: #1a0d28; border-left: 2px solid #aa77dd; }
#zone-w   { background: #0d2020; border-left: 2px solid #4da8a0; }
#zone-center { background: #0d1428; }
#zone-e   { background: #280d0d; border-left: 2px solid #d44040; }
#zone-sw  { background: #0d2010; border-left: 2px solid #5cb87a; }
#zone-s   { background: #1a1408; border-left: 2px solid #a09070; }
#zone-se  { background: #281808; border-left: 2px solid #f0b060; }
```

---

## Graha Colors (canonical meaning — never invent new colors)

```
Surya    #f0c040   solar gold
Chandra  #c8d8f0   silver-white
Mangala  #d44040   crimson
Budha    #5cb87a   forest green
Guru     #f0b060   warm amber
Shukra   #e090c0   rose-pink
Shani    #8899bb   slate blue
Rahu     #aa77dd   violet
Ketu     #a09070   smoky ochre
```

---

## SVG Rules

All SVG fills and strokes must be solid hex. No rgba().

Wrong:  `fill="rgba(92,184,122,0.2)"`
Right:  `fill="#2a5030"`

Wrong:  `stroke="rgba(255,255,255,0.15)"`
Right:  `stroke="#3a4a58"`

Wrong:  `opacity="0.5"` on any text or visible element
Right:  use a darker/lighter hex

Minimum visible stroke width: 0.5px
Minimum dot radius: 2.5px

---

## Zone Labels (canonical)

```css
.zone-deity {
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-family: 'SF Mono', monospace;
  color: #a0b4c8;   /* solid — never rgba */
}

.zone-label {
  font-size: 22px;
  font-style: italic;
  font-family: 'Cormorant Garamond', serif;
  color: #ffffff;   /* always white */
}

.zone-row-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-family: 'SF Mono', monospace;
  color: #7a8fa0;   /* solid */
}

.zone-row-static {
  font-size: 14px;
  color: #ffffff;
}
```

---

## Checklist Before Any CSS Commit

- [ ] No `rgba()` with alpha below 0.9 anywhere
- [ ] No `opacity:` below 1.0 on any visible element
- [ ] No font-size below 11px
- [ ] No color below #3a4a58 for any visible text
- [ ] All SVG fills are solid hex
- [ ] All SVG strokes are solid hex
- [ ] Zone backgrounds match canonical table above
- [ ] Text on any background passes 4.5:1 contrast

If any box is unchecked — fix before committing.

---

## Enforcement in Claude Code

When given any visual task, Claude Code must:

1. Read this file first
2. State which rules apply to the task
3. After writing code, scan for rgba() and opacity violations
4. Fix any violations before presenting the result

No exceptions.
