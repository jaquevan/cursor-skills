# PatternFly component library for notes

Full set of PatternFly 6 HTML components used in note output. All components
are CSS-only (no React) — load PF CSS via CDN and use the class names directly.

Use the **PatternFly MCP server** (`searchPatternFlyDocs` / `usePatternFlyDocs`)
to look up any component not listed here or to verify current class names.

---

## CDN dependencies (always include in `<head>`)

```html
<link rel="stylesheet" href="https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;700;900&family=Red+Hat+Text:wght@400;600&family=Red+Hat+Mono:wght@400;700&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
```

---

## Page layout (responsive)

Every note uses the PF Page component for full responsive behavior.
**Do not hardcode max-width.** Use PF's built-in page section padding.

```html
<body class="pf-v6-c-page">
  <a class="pf-v6-c-skip-to-content pf-v6-c-button pf-m-primary" href="#main-content">
    Skip to content
  </a>
  <main class="pf-v6-c-page__main" id="main-content" tabindex="-1">
    <section class="pf-v6-c-page__main-section pf-m-limit-width">
      <div class="pf-v6-c-page__main-body">
        <!-- All note content goes here -->
      </div>
    </section>
  </main>
</body>
```

The `pf-m-limit-width` modifier constrains content to a readable width on large
screens while staying fluid on mobile. The `pf-v6-c-page__main-body` centers
the content within the section.

### Inline style overrides (in `<style>`)

```css
:root { --pf-v6-c-page__main-body--MaxWidth: 900px; }
body { font-family: 'Red Hat Text', sans-serif; color: #151515; }
h1, h2, h3, h4 { font-family: 'Red Hat Display', sans-serif; }
code, pre { font-family: 'Red Hat Mono', monospace; }
```

---

## Back to top

```html
<div class="pf-v6-c-back-to-top">
  <a class="pf-v6-c-button pf-m-primary" href="#main-content">
    <span class="pf-v6-c-button__icon">
      <i class="fas fa-angle-up" aria-hidden="true"></i>
    </span>
    Back to top
  </a>
</div>
```

---

## Title + metadata

```html
<div class="pf-v6-c-content">
  <h1 style="color: #ee0000; font-weight: 900;">Note title here</h1>
  <p><small>2026-06-03 · Meeting · Author</small></p>
</div>
```

---

## Labels (tags)

Color-coded by category. Use the PF LabelGroup for a row of labels.

```html
<div class="pf-v6-c-label-group">
  <div class="pf-v6-c-label-group__list" role="list">
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-red">
        <span class="pf-v6-c-label__content">
          <span class="pf-v6-c-label__icon"><i class="fas fa-redhat" aria-hidden="true"></i></span>
          <span class="pf-v6-c-label__text">rhat</span>
        </span>
      </span>
    </div>
  </div>
</div>
```

### Color mapping

| Category | Modifier | Icon | Examples |
|---|---|---|---|
| Red Hat / brand | `pf-m-red` | `fa-redhat` | rhat, patternfly, openshift |
| People | `pf-m-blue` | `fa-user` | zack, priya |
| Tools / tech | `pf-m-teal` | `fa-wrench` | jira, cursor, mcp |
| Projects | `pf-m-purple` | `fa-diagram-project` | adlc, vlm |
| Status: positive | `pf-m-green` | `fa-check` | decision, shipped |
| Status: warning | `pf-m-orange` | `fa-exclamation` | blocker, action-item |
| Neutral | `pf-m-grey` | `fa-tag` | meeting, standup |

---

## Alerts (callouts)

| Use case | Variant | Modifier |
|---|---|---|
| Summary / TL;DR | info | `pf-m-info` |
| Key insight / tip | success | `pf-m-success` |
| Decision / must-know | danger | `pf-m-danger` |
| Gotcha / caution | warning | `pf-m-warning` |
| Neutral context | custom | `pf-m-custom` |

```html
<div class="pf-v6-c-alert pf-m-info" aria-label="Summary">
  <div class="pf-v6-c-alert__icon"><i class="fas fa-info-circle" aria-hidden="true"></i></div>
  <h4 class="pf-v6-c-alert__title">Title here</h4>
  <div class="pf-v6-c-alert__description"><p>Content here.</p></div>
</div>
```

---

## Cards

Use for highlighted content blocks, key metrics, or side-by-side comparisons.

```html
<div class="pf-v6-c-card">
  <div class="pf-v6-c-card__title">
    <h3 class="pf-v6-c-card__title-text">Card title</h3>
  </div>
  <div class="pf-v6-c-card__body">
    <p>Card content goes here.</p>
  </div>
</div>
```

### Card grid (responsive side-by-side)

Use PF's CSS grid utilities for responsive card layouts:

```html
<div class="pf-v6-l-grid pf-m-gutter pf-m-all-6-col-on-md pf-m-all-12-col-on-sm">
  <div class="pf-v6-l-grid__item">
    <div class="pf-v6-c-card">...</div>
  </div>
  <div class="pf-v6-l-grid__item">
    <div class="pf-v6-c-card">...</div>
  </div>
</div>
```

`pf-m-all-6-col-on-md` = 2 columns on medium+. `pf-m-all-12-col-on-sm` = full width on small.

---

## Tabs

Use for organizing sections without scrolling. Requires minimal JS for toggling.

```html
<div class="pf-v6-c-tabs" id="note-tabs">
  <ul class="pf-v6-c-tabs__list" role="tablist">
    <li class="pf-v6-c-tabs__item pf-m-current" role="presentation">
      <button class="pf-v6-c-tabs__link" role="tab" aria-selected="true" id="tab-1" aria-controls="panel-1">
        <span class="pf-v6-c-tabs__item-text">Discussion</span>
      </button>
    </li>
    <li class="pf-v6-c-tabs__item" role="presentation">
      <button class="pf-v6-c-tabs__link" role="tab" aria-selected="false" id="tab-2" aria-controls="panel-2" tabindex="-1">
        <span class="pf-v6-c-tabs__item-text">Decisions</span>
      </button>
    </li>
  </ul>
</div>
<section class="pf-v6-c-tab-content" id="panel-1" role="tabpanel" aria-labelledby="tab-1">
  <!-- Tab content -->
</section>
<section class="pf-v6-c-tab-content" id="panel-2" role="tabpanel" aria-labelledby="tab-2" hidden>
  <!-- Tab content -->
</section>
```

Include this JS at the bottom of the HTML for tab switching:

```html
<script>
document.querySelectorAll('.pf-v6-c-tabs__link').forEach(tab => {
  tab.addEventListener('click', () => {
    const tabList = tab.closest('.pf-v6-c-tabs');
    tabList.querySelectorAll('.pf-v6-c-tabs__item').forEach(i => i.classList.remove('pf-m-current'));
    tab.closest('.pf-v6-c-tabs__item').classList.add('pf-m-current');
    tabList.querySelectorAll('[role="tab"]').forEach(t => t.setAttribute('aria-selected', 'false'));
    tab.setAttribute('aria-selected', 'true');
    const panelId = tab.getAttribute('aria-controls');
    document.querySelectorAll('.pf-v6-c-tab-content').forEach(p => p.hidden = true);
    document.getElementById(panelId).hidden = false;
  });
});
</script>
```

---

## Accordion (expandable sections)

```html
<div class="pf-v6-c-accordion">
  <h3>
    <button class="pf-v6-c-accordion__toggle" aria-expanded="true" onclick="this.setAttribute('aria-expanded', this.getAttribute('aria-expanded')==='true'?'false':'true'); this.closest('h3').nextElementSibling.hidden = this.getAttribute('aria-expanded')==='false';">
      <span class="pf-v6-c-accordion__toggle-text">Section title</span>
      <span class="pf-v6-c-accordion__toggle-icon"><i class="fas fa-angle-right" aria-hidden="true"></i></span>
    </button>
  </h3>
  <div class="pf-v6-c-accordion__expanded-content" role="region">
    <div class="pf-v6-c-accordion__expanded-content-body">
      <p>Expandable content here.</p>
    </div>
  </div>
</div>
```

---

## Tables

```html
<table class="pf-v6-c-table pf-m-grid-md" role="grid">
  <thead class="pf-v6-c-table__thead">
    <tr class="pf-v6-c-table__tr" role="row">
      <th class="pf-v6-c-table__th" role="columnheader">Column</th>
    </tr>
  </thead>
  <tbody class="pf-v6-c-table__tbody" role="rowgroup">
    <tr class="pf-v6-c-table__tr" role="row">
      <td class="pf-v6-c-table__td" role="cell">Value</td>
    </tr>
  </tbody>
</table>
```

`pf-m-grid-md` makes the table responsive — stacks cells on small screens.

---

## Code blocks

```html
<div class="pf-v6-c-code-block">
  <div class="pf-v6-c-code-block__header">
    <div class="pf-v6-c-code-block__actions">
      <span class="pf-v6-c-label pf-m-grey pf-m-compact"><span class="pf-v6-c-label__content">python</span></span>
    </div>
  </div>
  <div class="pf-v6-c-code-block__content">
    <pre class="pf-v6-c-code-block__pre"><code class="pf-v6-c-code-block__code">code here</code></pre>
  </div>
</div>
```

---

## Lists

```html
<ul class="pf-v6-c-list" role="list">
  <li class="pf-v6-c-list__item">Item one</li>
  <li class="pf-v6-c-list__item">Item two</li>
</ul>
```

### Action items (checkbox list)

```html
<div class="pf-v6-c-check">
  <input class="pf-v6-c-check__input" type="checkbox" id="task-1">
  <label class="pf-v6-c-check__label" for="task-1">
    <strong>@owner</strong> — Task description
  </label>
</div>
```

---

## Banner

```html
<div class="pf-v6-c-banner pf-m-red">
  <span class="pf-v6-c-banner__content">
    <i class="fas fa-redhat" aria-hidden="true"></i> Red Hat internal — do not distribute
  </span>
</div>
```

Variants: `pf-m-red`, `pf-m-blue`, `pf-m-green`, `pf-m-gold`, `pf-m-default`

---

## Divider

```html
<hr class="pf-v6-c-divider">
```

---

## Content (body text)

Wrap all prose in PF Content component for proper spacing:

```html
<div class="pf-v6-c-content">
  <p>Paragraph text here.</p>
  <h2>Section heading</h2>
  <p>More text.</p>
</div>
```

---

## Icons (Font Awesome via CDN)

Common icons for notes:

| Purpose | Icon | Class |
|---|---|---|
| Info | ℹ | `fas fa-info-circle` |
| Success | ✓ | `fas fa-check-circle` |
| Warning | ⚠ | `fas fa-exclamation-triangle` |
| Danger | ✕ | `fas fa-exclamation-circle` |
| Red Hat | 🎩 | `fab fa-redhat` |
| Link | 🔗 | `fas fa-external-link-alt` |
| Code | < > | `fas fa-code` |
| Person | 👤 | `fas fa-user` |
| Project | 📊 | `fas fa-diagram-project` |
| Tool | 🔧 | `fas fa-wrench` |

---

## Link to original source

Always include at the bottom of every note:

```html
<div class="pf-v6-c-alert pf-m-custom pf-m-plain" aria-label="Source">
  <div class="pf-v6-c-alert__icon"><i class="fas fa-file" aria-hidden="true"></i></div>
  <h4 class="pf-v6-c-alert__title">Original source</h4>
  <div class="pf-v6-c-alert__description">
    <a href="./originals/filename.pdf">View original file</a>
  </div>
</div>
```
