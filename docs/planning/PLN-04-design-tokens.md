# PLN-04 · TK-OPS Semantic Design Tokens

## Scope + extraction coverage

- Source set reviewed: `tk_ops`, `_1`–`_24`, `ai_1`, `ai_2`, `crm`
- HTML reviewed: 27 `code.html` files
- Screenshot-only page: `_6/screen.png` (approximate-only extraction)
- Method: direct extraction from inline hex, Tailwind config, Tailwind utility usage, and one screenshot cross-check
- Rule: any value not explicitly present in source is marked **[derived]**

## Source patterns observed

- Core brand/background constants repeat in nearly every mockup:
  - `primary`: `#00f0e8` or `#00F2EA`
  - `background-light`: `#f5f8f8`
  - `background-dark`: `#0f2323`
- Role colors are explicitly defined in `tk_ops/code.html`:
  - manager `#FF6B6B`, creator `#4ECDC4`, analyst `#95E1D3`, automation `#F38181`
- Most light/dark neutrals come from Tailwind slate utilities; hex values below are **[derived from Tailwind utility resolution]**.

---

## 1) Color Tokens

### 1.1 Surface tokens

| Token | Light | Dark | Evidence |
|---|---:|---:|---|
| `surface.primary` | `#F5F8F8` | `#0F2323` | explicit `background-light/background-dark` |
| `surface.secondary` | `#FFFFFF` | `#0F172A` **[derived]** | `bg-white`, `dark:bg-slate-900` across most cards/panels |
| `surface.tertiary` | `#F8FAFC` **[derived]** | `#1E293B` **[derived]** | `bg-slate-50`, `dark:bg-slate-800` |
| `surface.elevated` | `#FFFFFF` | `#0F172A` **[derived]** | modal/card shells + shadows |
| `surface.sunken` | `#F1F5F9` **[derived]** | `#1E293B` **[derived]** | inputs, chips, table headers, editor wells |

### 1.2 Text tokens

| Token | Light | Dark | Evidence |
|---|---:|---:|---|
| `text.primary` | `#0F172A` **[derived]** | `#F1F5F9` **[derived]** | `text-slate-900`, `dark:text-slate-100` |
| `text.secondary` | `#64748B` **[derived]** | `#94A3B8` **[derived]** | `text-slate-500`, `dark:text-slate-400` |
| `text.tertiary` | `#94A3B8` **[derived]** | `#64748B` **[derived]** | `text-slate-400`, `dark:text-slate-500` |
| `text.disabled` | `#CBD5E1` **[derived]** | `#475569` **[derived]** | low-emphasis labels / disabled-like states |
| `text.inverse` | `#0F2323` | `#0F2323` | buttons on primary almost always use `text-slate-900` / `text-background-dark` |

### 1.3 Brand tokens

| Token | Light | Dark | Notes |
|---|---:|---:|---|
| `brand.primary` | `#00F2EA` | `#00F2EA` | canonicalized from `#00f0e8` / `#00F2EA` inconsistency |
| `brand.primary_hover` | `rgba(0,242,234,0.90)` **[derived]** | `rgba(0,242,234,0.90)` **[derived]** | from `hover:bg-primary/90`, `hover:opacity-90`, `brightness-105` |
| `brand.primary_pressed` | `rgba(0,242,234,0.80)` **[derived]** | `rgba(0,242,234,0.80)` **[derived]** | from `hover:bg-primary/80` + active states |
| `brand.secondary` | `#101818` | `#101818` | explicit `_18` `slate-custom`; best fit as secondary brand dark accent |
| `brand.accent` | `#5E8D8B` | `#5E8D8B` | explicit `_18` `slate-muted`; supportive accent |

### 1.4 Role tokens

| Token | Light | Dark | Evidence |
|---|---:|---:|---|
| `role.manager` | `#FF6B6B` | `#FF6B6B` | explicit |
| `role.creator` | `#4ECDC4` | `#4ECDC4` | explicit |
| `role.analyst` | `#95E1D3` | `#95E1D3` | explicit |
| `role.automation` | `#F38181` | `#F38181` | explicit |

### 1.5 Semantic tokens

| Token | Light | Dark | Evidence |
|---|---:|---:|---|
| `status.success` | `#10B981` **[derived]** | `#34D399` **[derived]** | `emerald-500`, `dark:...emerald-400` |
| `status.warning` | `#F59E0B` **[derived]** | `#FBBF24` **[derived]** | `amber-500`, `amber-400`, `yellow-400` |
| `status.error` | `#EF4444` **[derived]** | `#F87171` **[derived]** | `red-500`, `red-400`, some `rose-500` usage |
| `status.info` | `#3B82F6` **[derived]** | `#60A5FA` **[derived]** | `blue-500`, `blue-400/300` usage |
| `border.default` | `#E2E8F0` **[derived]** | `#1E293B` **[derived]** | `border-slate-200`, `dark:border-slate-800` |
| `border.strong` | `#CBD5E1` **[derived]** | `#334155` **[derived]** | `border-slate-300`, `dark:border-slate-700` |
| `border.focus` | `rgba(0,242,234,0.50)` **[derived]** | `rgba(0,242,234,0.50)` **[derived]** | `focus:ring-primary/50`, `ring-primary/20`, `border-primary/50` |

### 1.6 Chart / data visualization tokens

| Token | Value | Source |
|---|---:|---|
| `chart.series[0]` | `#00F2EA` | primary charts |
| `chart.series[1]` | `#F00078` | explicit `_3` palette |
| `chart.series[2]` | `#7800F0` | explicit `_3` palette |
| `chart.series[3]` | `#0078F0` | explicit `_3` palette |
| `chart.series[4]` | `#F0B400` | explicit `_3` palette |
| `chart.series[5]` | `#4ECDC4` | role creator reused in charts/icons |
| `chart.series[6]` | `#FF6B6B` | role manager / negative series |
| `chart.series[7]` | `#95E1D3` | role analyst / soft series |

> Reserve accent observed but not included in 0–7 set: `#F38181`.

---

## 2) Typography Tokens

### 2.1 Font family

| Token | Value | Source |
|---|---|---|
| `font.family.primary` | `"Spline Sans", sans-serif` | explicit across all mockups |
| `font.family.chinese` | `"Noto Sans SC", "Microsoft YaHei", sans-serif` **[derived normalization]** | explicit in `_1`, `_8`, `_10`, `_18`, `_20`, `_24`; YaHei fallback appears in `_12`, `_23` |
| `font.family.mono` | `ui-monospace, "SFMono-Regular", "SF Mono", Consolas, "Liberation Mono", Menlo, monospace` **[derived from Tailwind `font-mono`]** | `font-mono` usage in IDs/logs/timestamps |

### 2.2 Font size

| Token | Value | Notes |
|---|---:|---|
| `font.size.xs` | `11px` | requested canonical; observed micro labels also use `8/9/10px` |
| `font.size.sm` | `12px` | frequent body small / helper text |
| `font.size.md` | `14px` | dominant UI body size |
| `font.size.lg` | `16px` | strong body / section headings |
| `font.size.xl` | `18px` | card/page subheads |
| `font.size.xxl` | `24px` | frequent large heading size |
| `font.size.display` | `32px` | **[derived normalization]**; source also contains 30/36/48-like display moments |

### 2.3 Font weight

| Token | Value |
|---|---:|
| `font.weight.regular` | `400` |
| `font.weight.medium` | `500` |
| `font.weight.semibold` | `600` |
| `font.weight.bold` | `700` |

### 2.4 Line height

| Token | Value | Notes |
|---|---:|---|
| `line.height.tight` | `1.2` | title/kpi usage |
| `line.height.normal` | `1.5` | default body |
| `line.height.relaxed` | `1.75` | long-form content blocks |

---

## 3) Spacing Tokens

### 3.1 Core spacing scale

| Token | Value | Source |
|---|---:|---|
| `spacing.2xs` | `2px` | table dots, micro separators, pill borders |
| `spacing.xs` | `4px` | `gap-1`, `p-1`, mini chips |
| `spacing.sm` | `6px` | explicit rhythm target + `gap-1.5` approx |
| `spacing.md` | `8px` | `gap-2`, `p-2` |
| `spacing.lg` | `12px` | `p-3`, `gap-3` |
| `spacing.xl` | `16px` | `p-4`, `gap-4` |
| `spacing.2xl` | `24px` | `p-6`, `gap-6` |
| `spacing.3xl` | `32px` | `p-8`, `gap-8` |
| `spacing.4xl` | `48px` | `p-12`, large canvas/dropzones |

### 3.2 Layout spacing

| Token | Value | Notes |
|---|---:|---|
| `layout.content_padding` | `32px` | frequent `p-8` pages |
| `layout.card_padding` | `24px` | frequent `p-6` cards |
| `layout.section_gap` | `24px` | frequent `gap-6` between blocks |
| `layout.sidebar_width.raw` | `240 / 256 / 288 / 320 / 400 / 480px` | actual observed widths |
| `layout.sidebar_width.canonical` | `280px` **[derived]** | normalization for QSS engine between recurring `256px` and `288px` |

---

## 4) Border Radius Tokens

| Token | Value | Source |
|---|---:|---|
| `radius.sm` | `4px` | explicit Tailwind `DEFAULT 0.25rem` |
| `radius.md` | `8px` | explicit Tailwind `lg 0.5rem` |
| `radius.lg` | `12px` | explicit Tailwind `xl 0.75rem` |
| `radius.xl` | `16px` **[derived]** | normalized from frequent `rounded-2xl` usage |
| `radius.pill` | `9999px` | explicit `full` |

---

## 5) Shadow Tokens

Most screens mix `shadow-sm`, `shadow-lg`, `shadow-xl`, `shadow-2xl`, and one explicit `shadow-level2`.

| Token | Light | Dark | Source |
|---|---|---|---|
| `shadow.sm` | `0 1px 2px rgba(0,0,0,0.05)` **[derived]** | `0 1px 2px rgba(0,0,0,0.18)` **[derived]** | `shadow-sm` |
| `shadow.md` | `0 4px 6px -1px rgba(0,0,0,0.10), 0 2px 4px -2px rgba(0,0,0,0.10)` | `0 4px 6px -1px rgba(0,0,0,0.28), 0 2px 4px -2px rgba(0,0,0,0.28)` **[derived]** | explicit `shadow-level2` + Tailwind `shadow-md` family |
| `shadow.lg` | `0 10px 15px -3px rgba(0,0,0,0.10), 0 4px 6px -4px rgba(0,0,0,0.10)` **[derived]** | `0 10px 15px -3px rgba(0,0,0,0.32), 0 4px 6px -4px rgba(0,0,0,0.32)` **[derived]** | `shadow-lg` |
| `shadow.xl` | `0 20px 25px -5px rgba(0,0,0,0.10), 0 8px 10px -6px rgba(0,0,0,0.10)` **[derived]** | `0 20px 25px -5px rgba(0,0,0,0.36), 0 8px 10px -6px rgba(0,0,0,0.36)` **[derived]** | `shadow-xl`, `shadow-2xl` usage |

Glow-like accents also appear:

- `shadow.glow.brand = 0 0 10px rgba(0,242,234,0.50)` **[derived from `_2`, `_15`, `_24`]**

---

## 6) Animation Tokens

### 6.1 Raw motion values found

- `duration-200`
- `duration-300`
- `duration-500`
- `animate-pulse`
- `animate-ping`
- `animate-spin`
- many unqualified `transition-all`, `transition-colors`, `transition-opacity`, `transition-transform`

### 6.2 Canonical motion tokens for QSS

| Token | Value | Notes |
|---|---:|---|
| `duration.fast` | `150ms` **[derived]** | normalized below observed 200ms |
| `duration.normal` | `250ms` **[derived]** | normalized between observed 200/300ms |
| `duration.slow` | `400ms` **[derived]** | normalized below observed 500ms |
| `easing.default` | `cubic-bezier(0.4, 0, 0.2, 1)` **[derived]** | Tailwind-like default |
| `easing.bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` **[derived]** | no explicit bounce curve in source; only pulse/ping/spin |

---

## 7) Component-Specific Tokens

| Token | Value | Notes |
|---|---:|---|
| `sidebar.width.expanded` | `280px` **[derived]** | raw widths vary: `240/256/288/320px` |
| `sidebar.width.collapsed` | `64px` | explicit `w-16` in `_2`, `_21` |
| `card.padding` | `24px` | `p-6` dominant |
| `card.radius` | `12px` | `rounded-xl` dominant |
| `card.shadow` | `shadow.md` | most consistent semantic choice |
| `input.height` | `40px` | `h-10` dominant; 48px variant also exists |
| `input.padding` | `12px 16px` **[derived]** | from `py-2/2.5` + `px-4` |
| `input.radius` | `8px` | `rounded-lg` dominant |
| `button.height.sm` | `36px` | `h-9` |
| `button.height.md` | `40px` | `h-10` |
| `button.height.lg` | `48px` | `h-12` |
| `button.padding` | `8px 16px` / `12px 24px` | compact vs primary CTA |
| `button.radius` | `8px` | `rounded-lg` dominant |
| `table.row_height` | `48px` **[derived]** | based on `py-4` table rows |
| `table.header_bg` | `#F8FAFC` **[derived]** | `bg-slate-50` |
| `table.header_bg.dark` | `rgba(30,41,59,0.50)` **[derived]** | `dark:bg-slate-800/50` |
| `tag.font_size` | `10px` | extremely common badge size |
| `tag.padding` | `2px 8px` **[derived]** | `px-2 py-0.5` dominant |
| `tag.radius` | `4px` or `9999px` | both rectangular and pill badges exist |
| `tag.color.neutral` | `#F1F5F9 / #1E293B` **[derived]** | neutral chips |
| `tag.color.brand` | `rgba(0,242,234,0.10) / #00F2EA` | brand chips |
| `tag.color.success` | `#D1FAE5 / #10B981` **[derived]** | success badges |
| `tag.color.warning` | `#FEF3C7 / #F59E0B` **[derived]** | warning badges |
| `tag.color.error` | `#FEE2E2 / #EF4444` **[derived]** | error badges |

---

## 8) QSS Variable Mapping

```css
/* semantic token aliases */
@surface.primary: #F5F8F8;
@surface.secondary: #FFFFFF;
@surface.sunken: #F1F5F9;
@text.primary: #0F172A;
@text.secondary: #64748B;
@brand.primary: #00F2EA;
@border.default: #E2E8F0;
@radius.md: 8px;
@radius.lg: 12px;
@spacing.sm: 6px;
@spacing.lg: 12px;
@spacing.xl: 16px;

QWidget#MainWindow {
    background-color: @surface.primary;
    color: @text.primary;
}

QFrame[variant="card"] {
    background-color: @surface.secondary;
    border: 1px solid @border.default;
    border-radius: @radius.lg;
}

QLineEdit,
QTextEdit,
QComboBox {
    background-color: @surface.sunken;
    color: @text.primary;
    border: 1px solid @border.default;
    border-radius: @radius.md;
    padding: @spacing.lg @spacing.xl;
}

QPushButton {
    background-color: @brand.primary;
    color: @text.inverse;
    border-radius: @radius.md;
    padding: @spacing.sm @spacing.lg;
}

QPushButton:hover {
    background-color: rgba(0,242,234,0.90);
}

QPushButton:pressed {
    background-color: rgba(0,242,234,0.80);
}

QListWidget::item:selected {
    background-color: rgba(0,242,234,0.10);
    border-left: 4px solid @brand.primary;
    color: @brand.primary;
}

QTableView {
    gridline-color: @border.default;
    alternate-background-color: @surface.tertiary;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: @text.secondary;
    padding: @spacing.xl;
    border: none;
    border-bottom: 1px solid @border.default;
}
```

---

## 9) Inconsistencies found across mockups

1. **Primary cyan casing/value drift**
   - `#00f0e8` dominates
   - `#00F2EA` appears in `tk_ops` and `_24`
   - Recommendation: canonicalize to `#00F2EA`

2. **Font stack drift**
   - `Spline Sans` only
   - `Spline Sans + Noto Sans SC`
   - `Spline Sans + system-ui`
   - `Spline Sans + Microsoft YaHei`
   - Recommendation: `Spline Sans` primary + `Noto Sans SC` Chinese fallback

3. **Dark surface drift**
   - page base is explicit `#0F2323`
   - components alternate between `slate-900` (`#0F172A`) and `slate-800` (`#1E293B`) **[derived]**
   - Recommendation: keep page/base separate from component dark surfaces

4. **Radius drift beyond config**
   - config defines only `4 / 8 / 12 / full`
   - mockups also use `rounded-2xl`, `rounded-3xl`
   - Recommendation: add `radius.xl = 16px` **[derived]** for engine consistency

5. **Sidebar width drift**
   - observed widths: `240`, `256`, `288`, `320`, `400`, `480`
   - recommendation: canonical desktop nav width `280px` **[derived]**, keep special panels separate

6. **Shadow drift**
   - some screens are flat; others use `shadow-sm`, `shadow-lg`, `shadow-xl`, `shadow-2xl`, or custom `level2`
   - recommendation: normalize to `sm/md/lg/xl`

7. **Motion drift**
   - observed durations: `200/300/500ms`
   - requested engine tokens: `150/250/400ms` must therefore be **[derived normalization]**

8. **Chart palette drift**
   - some charts are monochrome-primary only
   - others use role colors or experimental palette (`#F00078`, `#7800F0`, `#0078F0`, `#F0B400`)
   - recommendation: freeze one 8-color chart set

---

## 10) Recommended semantic alias set for QSS engine

```text
brand.primary           -> #00F2EA
surface.primary         -> #F5F8F8 / #0F2323
surface.secondary       -> #FFFFFF / #0F172A
surface.sunken          -> #F1F5F9 / #1E293B
text.primary            -> #0F172A / #F1F5F9
text.secondary          -> #64748B / #94A3B8
border.default          -> #E2E8F0 / #1E293B
border.focus            -> rgba(0,242,234,0.50)
role.manager            -> #FF6B6B
role.creator            -> #4ECDC4
role.analyst            -> #95E1D3
role.automation         -> #F38181
status.success          -> #10B981 / #34D399
status.warning          -> #F59E0B / #FBBF24
status.error            -> #EF4444 / #F87171
status.info             -> #3B82F6 / #60A5FA
```

This document is the semantic normalization layer for the QSS theme engine; raw Tailwind classes should not be used as token names.
