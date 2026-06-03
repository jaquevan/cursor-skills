# PatternFly component mapping

Maps note elements to PatternFly 6 HTML components. Use the PF CSS class names
directly — no React required. PatternFly CSS is loaded via CDN.

CDN link (always use this in the `<head>`):
```html
<link rel="stylesheet" href="https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css">
```

---

## Note title

Use PF Title component classes:

```html
<h1 class="pf-v6-c-title pf-m-2xl" style="font-family: 'Red Hat Display'; color: #ee0000;">
  Note Title Here
</h1>
<p class="pf-v6-c-content--small" style="color: #6a6e73;">
  2026-06-03 · Meeting · Author
</p>
```

---

## Tags (Label + LabelGroup)

```html
<div class="pf-v6-c-label-group">
  <div class="pf-v6-c-label-group__list" role="list">
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-red">
        <span class="pf-v6-c-label__content">rhat</span>
      </span>
    </div>
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-blue">
        <span class="pf-v6-c-label__content">zack</span>
      </span>
    </div>
    <div class="pf-v6-c-label-group__list-item" role="listitem">
      <span class="pf-v6-c-label pf-m-purple">
        <span class="pf-v6-c-label__content">adlc</span>
      </span>
    </div>
  </div>
</div>
```

### Color mapping

| Category | PF modifier class | Hex |
|---|---|---|
| Red Hat / brand | `pf-m-red` | `#c9190b` |
| People | `pf-m-blue` | `#2b9af3` |
| Tools / tech | `pf-m-teal` | `#009596` |
| Projects | `pf-m-purple` | `#6753ac` |
| Status: positive | `pf-m-green` | `#3e8635` |
| Status: warning | `pf-m-orange` | `#f0ab00` |
| Neutral | `pf-m-grey` | `#8a8d90` |

---

## Summary / TL;DR

Use PF Alert (info variant) for the summary block:

```html
<div class="pf-v6-c-alert pf-m-info" aria-label="Summary">
  <div class="pf-v6-c-alert__icon">
    <i class="fas fa-info-circle" aria-hidden="true"></i>
  </div>
  <h4 class="pf-v6-c-alert__title">Summary</h4>
  <div class="pf-v6-c-alert__description">
    <p>One-sentence summary of the note content.</p>
  </div>
</div>
```

---

## Decisions / important callouts

Use PF Alert (danger variant for decisions, warning for gotchas):

```html
<div class="pf-v6-c-alert pf-m-danger" aria-label="Decision">
  <div class="pf-v6-c-alert__icon">
    <i class="fas fa-exclamation-circle" aria-hidden="true"></i>
  </div>
  <h4 class="pf-v6-c-alert__title">Decision</h4>
  <div class="pf-v6-c-alert__description">
    <p>The outcome field is now mandatory for all engineering work.</p>
  </div>
</div>
```

---

## Tips / key insights

Use PF Alert (success variant):

```html
<div class="pf-v6-c-alert pf-m-success" aria-label="Key insight">
  <div class="pf-v6-c-alert__icon">
    <i class="fas fa-check-circle" aria-hidden="true"></i>
  </div>
  <h4 class="pf-v6-c-alert__title">Key insight</h4>
  <div class="pf-v6-c-alert__description">
    <p>Jira auto-fixer success rate increased from 13% to 42%.</p>
  </div>
</div>
```

---

## Section headings

```html
<h2 class="pf-v6-c-title pf-m-xl" style="font-family: 'Red Hat Display'; border-bottom: 1px solid #d2d2d2; padding-bottom: 0.5rem; margin-top: 2rem;">
  Discussion
</h2>
```

---

## Tables

Use PF Table component classes:

```html
<table class="pf-v6-c-table pf-m-grid-md" role="grid">
  <thead class="pf-v6-c-table__thead">
    <tr class="pf-v6-c-table__tr" role="row">
      <th class="pf-v6-c-table__th" role="columnheader">Column A</th>
      <th class="pf-v6-c-table__th" role="columnheader">Column B</th>
    </tr>
  </thead>
  <tbody class="pf-v6-c-table__tbody" role="rowgroup">
    <tr class="pf-v6-c-table__tr" role="row">
      <td class="pf-v6-c-table__td" role="cell">Value 1</td>
      <td class="pf-v6-c-table__td" role="cell">Value 2</td>
    </tr>
  </tbody>
</table>
```

---

## Action items

Use PF Content list with checkbox styling:

```html
<ul class="pf-v6-c-list" role="list">
  <li class="pf-v6-c-list__item">
    <input type="checkbox" class="pf-v6-c-check__input" id="task-1">
    <label class="pf-v6-c-check__label" for="task-1">
      <strong>@owner</strong> — Task description
    </label>
  </li>
</ul>
```

---

## Code blocks

Wrap in a PF code block structure:

```html
<div class="pf-v6-c-code-block">
  <div class="pf-v6-c-code-block__content">
    <pre class="pf-v6-c-code-block__pre">
      <code class="pf-v6-c-code-block__code" style="font-family: 'Red Hat Mono';">
// code here
      </code>
    </pre>
  </div>
</div>
```

---

## Body text

All body text uses Red Hat Text:

```html
<div class="pf-v6-c-content">
  <p>Body text goes here. Use PF content component for proper spacing.</p>
</div>
```

---

## Inline `<style>` overrides

Include these in the `<head>` `<style>` block for Red Hat brand compliance:

```css
body { font-family: 'Red Hat Text', sans-serif; color: #151515; }
h1, h2, h3, h4 { font-family: 'Red Hat Display', sans-serif; }
code, pre { font-family: 'Red Hat Mono', monospace; }
.pf-v6-c-page__main-section { max-width: 900px; margin: 0 auto; padding: 2rem; }
```

---

## Dividers

```html
<hr class="pf-v6-c-divider">
```
