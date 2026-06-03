# PatternFly 6 component library

HTML-only components for note output. No React — just PF CSS classes loaded
via CDN. Use the PatternFly MCP (`searchPatternFlyDocs` / `usePatternFlyDocs`)
to look up any component not listed here.

---

## CDN (always in `<head>`)

```html
<link rel="stylesheet" href="https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;700;900&family=Red+Hat+Text:wght@400;600&family=Red+Hat+Mono:wght@400;700&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
```

---

## Page layout

```html
<body class="pf-v6-c-page">
  <a class="pf-v6-c-skip-to-content pf-v6-c-button pf-m-primary" href="#main-content">
    Skip to content
  </a>
  <main class="pf-v6-c-page__main" id="main-content" tabindex="-1">
    <section class="pf-v6-c-page__main-section pf-m-limit-width">
      <div class="pf-v6-c-page__main-body">
        <!-- content -->
      </div>
    </section>
  </main>
</body>
```

Inline style override for max-width:
```css
:root { --pf-v6-c-page__main-body--MaxWidth: 900px; }
```

---

## Back to top

```html
<div class="pf-v6-c-back-to-top">
  <a class="pf-v6-c-button pf-m-primary" href="#main-content">
    <span class="pf-v6-c-button__icon"><i class="fas fa-angle-up" aria-hidden="true"></i></span>
  </a>
</div>
```

---

## Card

```html
<div class="pf-v6-c-card">
  <div class="pf-v6-c-card__title">
    <h2 class="pf-v6-c-card__title-text">Title</h2>
  </div>
  <div class="pf-v6-c-card__body">Body</div>
  <div class="pf-v6-c-card__footer">Footer</div>
</div>
```

### Compact card

```html
<div class="pf-v6-c-card pf-m-compact">
  <div class="pf-v6-c-card__title">
    <h3 class="pf-v6-c-card__title-text">Compact card</h3>
  </div>
  <div class="pf-v6-c-card__body">Smaller padding for dense layouts.</div>
</div>
```

### Card grid (responsive)

```html
<div class="pf-v6-l-grid pf-m-gutter pf-m-all-6-col-on-md pf-m-all-12-col-on-sm">
  <div class="pf-v6-l-grid__item">
    <div class="pf-v6-c-card">
      <div class="pf-v6-c-card__title"><h3 class="pf-v6-c-card__title-text">Card A</h3></div>
      <div class="pf-v6-c-card__body">Content A</div>
    </div>
  </div>
  <div class="pf-v6-l-grid__item">
    <div class="pf-v6-c-card">
      <div class="pf-v6-c-card__title"><h3 class="pf-v6-c-card__title-text">Card B</h3></div>
      <div class="pf-v6-c-card__body">Content B</div>
    </div>
  </div>
</div>
```

Grid modifiers: `pf-m-all-12-col` (full), `pf-m-all-6-col` (half), `pf-m-all-4-col` (third).
Breakpoints: append `-on-sm`, `-on-md`, `-on-lg`, `-on-xl`.

---

## Tabs

```html
<div class="pf-v6-c-tabs" id="note-tabs">
  <ul class="pf-v6-c-tabs__list" role="tablist">
    <li class="pf-v6-c-tabs__item pf-m-current" role="presentation">
      <button class="pf-v6-c-tabs__link" role="tab" id="tab-1"
              aria-selected="true" aria-controls="panel-1">
        <span class="pf-v6-c-tabs__item-text">Discussion</span>
      </button>
    </li>
    <li class="pf-v6-c-tabs__item" role="presentation">
      <button class="pf-v6-c-tabs__link" role="tab" id="tab-2"
              aria-selected="false" aria-controls="panel-2" tabindex="-1">
        <span class="pf-v6-c-tabs__item-text">Decisions</span>
      </button>
    </li>
  </ul>
</div>
<section class="pf-v6-c-tab-content" id="panel-1" role="tabpanel"
         aria-labelledby="tab-1" tabindex="0">
  <div class="pf-v6-c-tab-content__body">Content for tab 1</div>
</section>
<section class="pf-v6-c-tab-content" id="panel-2" role="tabpanel"
         aria-labelledby="tab-2" tabindex="0" hidden>
  <div class="pf-v6-c-tab-content__body">Content for tab 2</div>
</section>
```

Tab switching JS (include at bottom of HTML):
```html
<script>
document.querySelectorAll('.pf-v6-c-tabs__link').forEach(tab => {
  tab.addEventListener('click', () => {
    const tabs = tab.closest('.pf-v6-c-tabs');
    tabs.querySelectorAll('.pf-v6-c-tabs__item').forEach(i => i.classList.remove('pf-m-current'));
    tab.closest('.pf-v6-c-tabs__item').classList.add('pf-m-current');
    tabs.querySelectorAll('[role="tab"]').forEach(t => { t.setAttribute('aria-selected','false'); t.tabIndex = -1; });
    tab.setAttribute('aria-selected','true'); tab.tabIndex = 0;
    document.querySelectorAll('.pf-v6-c-tab-content').forEach(p => p.hidden = true);
    document.getElementById(tab.getAttribute('aria-controls')).hidden = false;
  });
});
</script>
```

---

## Accordion

```html
<div class="pf-v6-c-accordion">
  <h3>
    <button class="pf-v6-c-accordion__toggle" aria-expanded="true"
            aria-controls="accordion-panel-1" id="accordion-toggle-1">
      <span class="pf-v6-c-accordion__toggle-text">Section title</span>
      <span class="pf-v6-c-accordion__toggle-icon">
        <i class="fas fa-angle-right" aria-hidden="true"></i>
      </span>
    </button>
  </h3>
  <div class="pf-v6-c-accordion__expanded-content" id="accordion-panel-1"
       role="region" aria-labelledby="accordion-toggle-1">
    <div class="pf-v6-c-accordion__expanded-content-body">
      <p>Expanded content here.</p>
    </div>
  </div>

  <h3>
    <button class="pf-v6-c-accordion__toggle" aria-expanded="false"
            aria-controls="accordion-panel-2" id="accordion-toggle-2">
      <span class="pf-v6-c-accordion__toggle-text">Collapsed section</span>
      <span class="pf-v6-c-accordion__toggle-icon">
        <i class="fas fa-angle-right" aria-hidden="true"></i>
      </span>
    </button>
  </h3>
  <div class="pf-v6-c-accordion__expanded-content" id="accordion-panel-2"
       role="region" aria-labelledby="accordion-toggle-2" hidden>
    <div class="pf-v6-c-accordion__expanded-content-body">
      <p>This content is hidden by default.</p>
    </div>
  </div>
</div>
```

Accordion toggle JS:
```html
<script>
document.querySelectorAll('.pf-v6-c-accordion__toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    const panel = document.getElementById(btn.getAttribute('aria-controls'));
    panel.hidden = expanded;
  });
});
</script>
```

---

## Alert

```html
<div class="pf-v6-c-alert pf-m-info" aria-label="Info alert">
  <div class="pf-v6-c-alert__icon"><i class="fas fa-info-circle" aria-hidden="true"></i></div>
  <h4 class="pf-v6-c-alert__title">Alert title</h4>
  <div class="pf-v6-c-alert__description"><p>Alert content.</p></div>
</div>
```

Variants: `pf-m-info`, `pf-m-success`, `pf-m-warning`, `pf-m-danger`, `pf-m-custom`

Icons per variant:
- info: `fa-info-circle`
- success: `fa-check-circle`
- warning: `fa-exclamation-triangle`
- danger: `fa-exclamation-circle`
- custom: `fa-bell`

### Inline alert (compact, no background)

```html
<div class="pf-v6-c-alert pf-m-success pf-m-inline">
  <div class="pf-v6-c-alert__icon"><i class="fas fa-check-circle" aria-hidden="true"></i></div>
  <h4 class="pf-v6-c-alert__title">Inline success</h4>
</div>
```

---

## Label + LabelGroup

```html
<div class="pf-v6-c-label-group">
  <div class="pf-v6-c-label-group__list" role="list">
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-red">
        <span class="pf-v6-c-label__content">
          <span class="pf-v6-c-label__icon"><i class="fab fa-redhat" aria-hidden="true"></i></span>
          <span class="pf-v6-c-label__text">rhat</span>
        </span>
      </span>
    </div>
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-blue">
        <span class="pf-v6-c-label__content">
          <span class="pf-v6-c-label__icon"><i class="fas fa-user" aria-hidden="true"></i></span>
          <span class="pf-v6-c-label__text">zack</span>
        </span>
      </span>
    </div>
  </div>
</div>
```

Colors: `pf-m-red`, `pf-m-blue`, `pf-m-teal`, `pf-m-green`, `pf-m-orange`, `pf-m-purple`, `pf-m-grey`
Variants: add `pf-m-outline` for outlined, `pf-m-compact` for smaller labels.

---

## Table

```html
<table class="pf-v6-c-table pf-m-grid-md" role="grid" aria-label="Data table">
  <thead class="pf-v6-c-table__thead">
    <tr class="pf-v6-c-table__tr" role="row">
      <th class="pf-v6-c-table__th" role="columnheader" scope="col">Column A</th>
      <th class="pf-v6-c-table__th" role="columnheader" scope="col">Column B</th>
    </tr>
  </thead>
  <tbody class="pf-v6-c-table__tbody" role="rowgroup">
    <tr class="pf-v6-c-table__tr" role="row">
      <td class="pf-v6-c-table__td" role="cell" data-label="Column A">Value 1</td>
      <td class="pf-v6-c-table__td" role="cell" data-label="Column B">Value 2</td>
    </tr>
  </tbody>
</table>
```

`pf-m-grid-md` = responsive — cells stack vertically on screens below `md` breakpoint.
`data-label` on `<td>` provides visible labels when stacked.

### Compact table

Add `pf-m-compact` to the `<table>` for denser rows.

---

## Code block

```html
<div class="pf-v6-c-code-block">
  <div class="pf-v6-c-code-block__header">
    <div class="pf-v6-c-code-block__actions">
      <span class="pf-v6-c-label pf-m-compact pf-m-grey">
        <span class="pf-v6-c-label__content">python</span>
      </span>
    </div>
  </div>
  <div class="pf-v6-c-code-block__content">
    <pre class="pf-v6-c-code-block__pre">
      <code class="pf-v6-c-code-block__code">def hello():
    print("world")</code>
    </pre>
  </div>
</div>
```

---

## Content (body text)

```html
<div class="pf-v6-c-content">
  <h2>Heading</h2>
  <p>Paragraph text with proper PF spacing applied automatically.</p>
  <ul>
    <li>List item</li>
  </ul>
</div>
```

---

## List

```html
<ul class="pf-v6-c-list" role="list">
  <li class="pf-v6-c-list__item">Item one</li>
  <li class="pf-v6-c-list__item">Item two</li>
</ul>
```

### With icons

```html
<ul class="pf-v6-c-list pf-m-plain" role="list">
  <li class="pf-v6-c-list__item">
    <span class="pf-v6-c-list__item-icon"><i class="fas fa-check" aria-hidden="true"></i></span>
    Item with icon
  </li>
</ul>
```

---

## Banner

```html
<div class="pf-v6-c-banner pf-m-red">
  <span class="pf-v6-c-banner__content">
    <i class="fab fa-redhat" aria-hidden="true"></i> Red Hat internal
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

## Brand / logo

```html
<div class="pf-v6-c-brand">
  <img src="https://www.patternfly.org/assets/images/pf_logo.svg" alt="PatternFly logo">
</div>
```

---

## Badge

```html
<span class="pf-v6-c-badge pf-m-read">7</span>
<span class="pf-v6-c-badge pf-m-unread">24</span>
```

---

## Icons reference

| Purpose | Class |
|---|---|
| Red Hat | `fab fa-redhat` |
| Info | `fas fa-info-circle` |
| Success | `fas fa-check-circle` |
| Warning | `fas fa-exclamation-triangle` |
| Danger | `fas fa-exclamation-circle` |
| User/person | `fas fa-user` |
| Project | `fas fa-diagram-project` |
| Tool | `fas fa-wrench` |
| Code | `fas fa-code` |
| External link | `fas fa-external-link-alt` |
| File | `fas fa-file` |
| PDF | `fas fa-file-pdf` |
| Calendar | `fas fa-calendar` |
| Tag | `fas fa-tag` |
| Expand/angle | `fas fa-angle-right` |
| Up/back-to-top | `fas fa-angle-up` |

---

## Original source link (bottom of every note)

```html
<div class="pf-v6-c-alert pf-m-custom pf-m-inline" aria-label="Source">
  <div class="pf-v6-c-alert__icon"><i class="fas fa-file-pdf" aria-hidden="true"></i></div>
  <h4 class="pf-v6-c-alert__title">Original source</h4>
  <div class="pf-v6-c-alert__description">
    <a href="./originals/filename.pdf">View original file</a>
  </div>
</div>
```
