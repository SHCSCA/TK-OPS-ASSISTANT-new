# UI Usability Visual Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize the TK-OPS shell and linked pages so notification overlays, resize behavior, click targets, analytics interactions, filters, selects, pagination, and selection states are usable and visually consistent without adding new business features.

**Architecture:** The work stays inside the current runtime chain: the static HTML shell, shared CSS tokens/components, and page-level JS binders/loaders. First harden shell structure and overlay behavior, then normalize shared components, then repair analytics page binding and information presentation, and finally patch list/config pages plus regression tests.

**Tech Stack:** Vanilla HTML/CSS/JavaScript in `desktop_app/assets/`, PySide6-hosted web shell, Python `pytest` for lightweight frontend baseline tests.

---

## File Map

- `desktop_app/assets/app_shell.html`
  - Shell DOM for title bar actions, notification trigger/panel, status affordances, sidebar footer anchor, and overlay containers.
- `desktop_app/assets/css/variables.css`
  - Shared tokens for z-index, spacing, control heights, state colors, and responsive widths.
- `desktop_app/assets/css/shell.css`
  - Grid shell, sidebar/footer freezing, title bar layout, detail panel behavior, resize breakpoints, and fixed/sticky structure.
- `desktop_app/assets/css/components.css`
  - Shared button, filter bar, pagination, select, tabs, status, and notification styles.
- `desktop_app/assets/css/pages-analytics.css`
  - Analytics-specific chart blocks, funnel/persona selection treatment, side insight layout, and data explanation styling.
- `desktop_app/assets/css/pages-core.css`
  - Shared page section/list/table shells and generic selection states.
- `desktop_app/assets/css/pages-config.css`
  - Config/list/form control styling, select polish, and footer/pagination layout.
- `desktop_app/assets/css/interactions.css`
  - Hover/focus/active/disabled transitions and overlay motion rules.
- `desktop_app/assets/js/main.js`
  - Global event binding, resize handling, responsive sync, and route-level interaction resets.
- `desktop_app/assets/js/ui-notifications.js`
  - Notification toggle/panel lifecycle, outside-click handling, and duplicate listener prevention.
- `desktop_app/assets/js/charts-analytics.js`
  - Analytics selection binders, side insight updates, canvas redraws, and duplicate-binding prevention.
- `desktop_app/assets/js/page-loaders.js`
  - Cross-page component rewiring, select/pagination helpers, and page-specific behavior fixes.
- `desktop_app/assets/js/routes.js`
  - Sidebar summary and status rendering text, plus any shell-facing wording cleanup needed for the top status affordance.
- `tests/test_frontend_style_baseline.py`
  - CSS/HTML selector-level regression guard for shell, overlay, select, pagination, and analytics component presence.

## Task 1: Lock Down The Shell Structure

**Files:**
- Modify: `desktop_app/assets/app_shell.html`
- Modify: `desktop_app/assets/css/variables.css`
- Modify: `desktop_app/assets/css/shell.css`
- Modify: `desktop_app/assets/js/main.js`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing shell regression tests**

Add assertions to `tests/test_frontend_style_baseline.py` for these selectors/markers:

```python
required_shell_markers = [
    'id="notificationPanel"',
    'id="sidebarSummary"',
    '.sidebar__footer {',
    '.sidebar__content {',
    '.notification-panel {',
    '.notification-panel.is-open {',
    '.shell-floating-panel {',
]
```

- [ ] **Step 2: Run shell regression test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because the new shell footer/floating panel selectors are not present yet.

- [ ] **Step 3: Restructure the shell HTML minimally**

Update `desktop_app/assets/app_shell.html` to:

```html
<aside class="sidebar">
  <div class="sidebar__content">...</div>
  <div class="sidebar__footer" id="sidebarSummary"></div>
</aside>

<button class="icon-button" id="statusSummaryToggle" aria-label="运行状态" type="button">
  <span class="shell-icon">况</span>
</button>
```

Keep existing navigation/routes intact; only wrap the scrollable menu content and rename/clarify the top status affordance.

- [ ] **Step 4: Implement shell CSS for frozen footer and overlay-safe layout**

In `desktop_app/assets/css/variables.css` add stable layer tokens such as:

```css
--z-base: 1;
--z-sticky: 20;
--z-popover: 60;
--z-overlay: 80;
--control-height-md: 38px;
```

In `desktop_app/assets/css/shell.css` implement:

```css
.sidebar {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.sidebar__content {
    flex: 1;
    min-height: 0;
    overflow: auto;
}

.sidebar__footer {
    position: sticky;
    bottom: 0;
    z-index: var(--z-sticky);
}

.notification-panel {
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    z-index: var(--z-popover);
}
```

Also add any needed `min-width: 0`, `overflow: visible`, and responsive detail-panel rules so resize does not misalign hit targets.

- [ ] **Step 5: Harden resize state sync in JS**

In `desktop_app/assets/js/main.js` add a deduplicated resize sync path such as:

```javascript
let resizeFrame = 0;

function handleShellResize() {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
        uiState.detailPanelForced = null;
        document.body.classList.remove('has-stale-overlay');
        syncResponsiveState();
        if (typeof renderAnalyticsCanvases === 'function') renderAnalyticsCanvases();
    });
}
```

Bind this instead of raw repeated resize work.

- [ ] **Step 6: Run shell regression test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for shell structure assertions.

## Task 2: Fix Notification Layering And Global Overlay Lifecycle

**Files:**
- Modify: `desktop_app/assets/js/ui-notifications.js`
- Modify: `desktop_app/assets/css/components.css`
- Modify: `desktop_app/assets/css/interactions.css`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing overlay baseline assertions**

Extend `tests/test_frontend_style_baseline.py` with selectors like:

```python
required_overlay_selectors = [
    '.notification-panel {',
    '.notification-panel__header {',
    '.notification-panel__list {',
    '.notification-item.is-unread {',
    '.icon-button[aria-expanded',
]
```

- [ ] **Step 2: Run baseline test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because expanded-state styling and overlay markers are not fully present.

- [ ] **Step 3: Refactor notification init to avoid duplicate handlers**

Update `desktop_app/assets/js/ui-notifications.js` to use singleton guards:

```javascript
let notificationSystemBound = false;

function setNotificationPanelOpen(panel, btn, open) {
    panel.classList.toggle('shell-hidden', !open);
    panel.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
}
```

Ensure the document click handler is bound once, uses capture-safe `closest()` checks, and closes the panel on resize or route transition if needed.

- [ ] **Step 4: Add overlay polish styles**

Implement/adjust in `desktop_app/assets/css/components.css` and `desktop_app/assets/css/interactions.css`:

```css
.notification-panel.is-open {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
}

.notification-panel.shell-hidden {
    pointer-events: none;
}
```

Also refine unread item emphasis and panel max-height/scroll behavior.

- [ ] **Step 5: Run baseline test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for overlay selectors and existing baseline checks.

## Task 3: Normalize Shared Controls And Selection States

**Files:**
- Modify: `desktop_app/assets/css/components.css`
- Modify: `desktop_app/assets/css/pages-core.css`
- Modify: `desktop_app/assets/css/pages-config.css`
- Modify: `desktop_app/assets/css/interactions.css`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing control baseline assertions**

Extend `tests/test_frontend_style_baseline.py` with selectors for:

```python
required_control_selectors = [
    '.filter-bar {',
    '.pagination {',
    '.pagination__info {',
    '.config-native-select {',
    '.is-selected {',
    '.primary-button:disabled',
    '.secondary-button:disabled',
]
```

- [ ] **Step 2: Run control baseline test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because unified filter/pagination selectors are not fully defined yet.

- [ ] **Step 3: Implement shared filter/select/pagination/button styles**

Add focused shared CSS in `desktop_app/assets/css/components.css` such as:

```css
.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.config-native-select,
.form-select,
select {
    min-height: var(--control-height-md);
    border-radius: var(--radius-md);
}

.pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
```

In `desktop_app/assets/css/interactions.css`, standardize hover/focus/active/disabled treatment for shared controls.

- [ ] **Step 4: Patch page loader rewiring for select state and pagination placeholders**

In `desktop_app/assets/js/page-loaders.js` add minimal helper(s) like:

```javascript
function ensurePagination(root, summaryText) {
    if (!root || root.querySelector('.pagination')) return;
    root.insertAdjacentHTML('beforeend', '<div class="pagination"><div class="pagination__info">' + summaryText + '</div><div class="pagination__actions"><button class="secondary-button" type="button">上一页</button><button class="secondary-button" type="button">下一页</button></div></div>');
}
```

Use it only on existing list/config sections that currently end abruptly.

- [ ] **Step 5: Run control baseline test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for filter/select/pagination selectors.

## Task 4: Repair Analytics Interaction Binding And Side Panels

**Files:**
- Modify: `desktop_app/assets/js/charts-analytics.js`
- Modify: `desktop_app/assets/js/main.js`
- Modify: `desktop_app/assets/css/pages-analytics.css`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing analytics baseline assertions**

Extend `tests/test_frontend_style_baseline.py` to require:

```python
required_analytics_selectors = [
    '.analytics-chart-card {',
    '.analytics-chart-card__summary {',
    '.analytics-side-panel {',
    '.funnel-step.is-active {',
    '.persona-grid article.is-active {',
]
```

- [ ] **Step 2: Run analytics baseline test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because the new analytics information and active-state selectors are not defined yet.

- [ ] **Step 3: Prevent duplicate analytics event binding**

In `desktop_app/assets/js/charts-analytics.js`, gate the binder per route/root:

```javascript
function bindAnalyticsInteractions() {
    const mainHost = document.getElementById('mainHost');
    if (!mainHost || mainHost.dataset.analyticsBound === '1') return;
    mainHost.dataset.analyticsBound = '1';
```

For each interactive cluster, bind once and update one side insight region instead of spawning parallel UI reactions.

- [ ] **Step 4: Improve analytics information containers and active styling**

Add/adjust `desktop_app/assets/css/pages-analytics.css` with a stable information card layout:

```css
.analytics-chart-card__summary {
    display: grid;
    gap: 6px;
}

.analytics-side-panel {
    position: sticky;
    top: 0;
}

.funnel-step.is-active,
.persona-grid article.is-active {
    border-color: color-mix(in srgb, var(--brand-primary) 44%, var(--border-default));
    background: color-mix(in srgb, var(--brand-primary) 10%, var(--surface-secondary));
}
```

Also reduce placeholder-noise styling and increase labels/legend clarity.

- [ ] **Step 5: Ensure canvases redraw safely on route switch and resize**

In `desktop_app/assets/js/main.js`, after route transitions or resize, call the analytics render path only when analytics DOM is present, preventing stacked canvases or stale geometry.

- [ ] **Step 6: Run analytics baseline test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for analytics selectors and baseline checks.

## Task 5: Make Analytics Pages Readable Rather Than Decorative

**Files:**
- Modify: `desktop_app/assets/css/pages-analytics.css`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/routes.js`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing readability baseline assertions**

Add checks for selectors or markers that prove charts have context areas, for example:

```python
required_readability_markers = [
    '.analytics-chart-meta {',
    '.analytics-key-takeaway {',
    '.analytics-legend {',
    '.analytics-empty-state {',
]
```

- [ ] **Step 2: Run readability test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because chart meta/takeaway selectors are not present yet.

- [ ] **Step 3: Add chart context blocks in analytics loaders/routes**

Patch the analytics route rendering/loaders to inject or normalize supporting content like:

```html
<div class="analytics-chart-meta">
  <span>时间范围：近 7 天</span>
  <span>维度：渠道 / 人群</span>
</div>
<div class="analytics-key-takeaway">结论：加购到下单为当前最大流失点，应优先复核详情页与优惠策略。</div>
```

Do this for the funnel/persona/traffic/report pages without changing business behavior.

- [ ] **Step 4: Add low-noise readability styling**

Implement matching CSS in `desktop_app/assets/css/pages-analytics.css` to make summary text, legend, and takeaways visually clear but restrained.

- [ ] **Step 5: Run readability baseline test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for chart meta/takeaway selectors.

## Task 6: Patch List And Config Page Pagination / Control Feedback

**Files:**
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/css/pages-core.css`
- Modify: `desktop_app/assets/css/pages-config.css`
- Modify: `desktop_app/assets/css/components.css`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: Write the failing pagination/footer assertions**

Add test markers like:

```python
required_list_selectors = [
    '.list-footer {',
    '.pagination__actions {',
    '.config-section__footer {',
]
```

- [ ] **Step 2: Run pagination baseline test to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: FAIL because list footer and config footer selectors are not fully implemented.

- [ ] **Step 3: Add minimal pagination/footer shells to unfinished pages**

In `desktop_app/assets/js/page-loaders.js`, append lightweight footers to list/config pages that currently stop abruptly. Keep behavior minimal and honest — show counts and navigation affordances without inventing backend pagination.

- [ ] **Step 4: Style those footers consistently**

Implement `list-footer`, `config-section__footer`, and pagination alignment in the CSS files above.

- [ ] **Step 5: Run pagination baseline test to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
Expected: PASS for list/config footer selectors.

## Task 7: Full Verification And Cleanup

**Files:**
- Modify: any of the files above if verification reveals issues
- Test: `tests/test_frontend_style_baseline.py`
- Test: `tests/test_task_enum_compat.py`
- Test: `tests/`

- [ ] **Step 1: Run targeted frontend tests**

Run: `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py tests/test_task_enum_compat.py -v`
Expected: PASS.

- [ ] **Step 2: Run the full suite**

Run: `venv\Scripts\python.exe -m pytest tests/ -v`
Expected: PASS for the existing suite.

- [ ] **Step 3: Manual verification pass in the desktop shell**

Run: `venv\Scripts\python.exe desktop_app\main.py`

Manually verify:

1. Notification center opens above content and closes cleanly.
2. Resize no longer causes dead click zones.
3. Conversion funnel and fan profile only update one side detail region per click.
4. Filters/selects/buttons/selected states look consistent.
5. Sidebar bottom summary stays visible.

- [ ] **Step 4: Document any remaining gaps before commit**

If anything still cannot be fixed without new backend behavior, note it explicitly instead of faking completion.
