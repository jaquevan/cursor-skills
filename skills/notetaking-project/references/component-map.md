# Component reference

HTML patterns for note output. No framework dependencies — just CSS loaded via
CDN. Use the PatternFly MCP to verify component details when needed.

---

## CDN (in `<head>`)

```html
<link rel="stylesheet" href="https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;700;900&family=Red+Hat+Text:wght@400;600&family=Red+Hat+Mono:wght@400;700&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
```

---

## Color palette

```css
:root {
  --bg-primary: #ffffff;
  --bg-warm: #faf8f5;
  --bg-dark: #1b2a3d;
  --text-primary: #1a2332;
  --text-secondary: #4a5568;
  --text-subtle: #718096;
  --text-on-dark: #f7fafc;
  --accent: #0066cc;
  --accent-light: #e8f2ff;
  --success: #2f855a;
  --success-bg: #f0fff4;
  --warning: #c05621;
  --warning-bg: #fffaf0;
  --info: #2b6cb0;
  --info-bg: #ebf8ff;
  --border: #e2ddd7;
}
```

---

## Sections

Full-width blocks with alternating backgrounds. No max-width.

```html
<div class="section">content</div>
<div class="section section--warm">content</div>
<div class="section section--dark">content</div>
```

---

## Red Hat hat logo (header branding)

Include the Red Hat fedora in the top-right of the dark header section. Use two
instances: a small visible one (top-right, red, 60px) and a large subtle watermark
(bottom-right, white at 4% opacity, 300px).

The SVG path is stored in `assets/hat-watermark.svg`. Inline it directly in the HTML:

```html
<!-- Visible logo top-right -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 191.8 145"
     style="position:absolute; top:1.5rem; right:2rem; width:60px; opacity:0.7;" aria-hidden="true">
  <path fill="#ee0000" d="M127.47,83.49c12.51,0,30.61-2.58,30.61-17.46a14..."/>
</svg>

<!-- Large watermark background -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 191.8 145"
     style="position:absolute; bottom:-2rem; right:-3rem; width:300px; opacity:0.04;" aria-hidden="true">
  <path fill="#ffffff" d="M127.47,83.49c12.51,0,30.61-2.58,30.61-17.46a14..."/>
</svg>
```

The header section needs `position:relative; overflow:hidden;` to contain the SVGs.

---

## Tags

Pill-shaped, category-colored. No PF Label classes needed.

```html
<div class="tags">
  <span class="tag tag--brand"><i class="fab fa-redhat"></i> openshift</span>
  <span class="tag tag--tool"><i class="fas fa-wrench"></i> cursor</span>
  <span class="tag tag--project"><i class="fas fa-diagram-project"></i> adlc</span>
  <span class="tag tag--neutral"><i class="fas fa-tag"></i> meeting</span>
</div>
```

Colors:
- `tag--brand`: `background: #fee2e2; color: #991b1b;`
- `tag--tool`: `background: #e0f2f1; color: #00695c;`
- `tag--project`: `background: #ede9fe; color: #5b21b6;`
- `tag--neutral`: `background: #f3f4f6; color: #4b5563;`

---

## Summary callout

```html
<div class="summary">
  <h4>Summary</h4>
  <p><strong>Lead with conclusion.</strong> Rest of summary here.</p>
</div>
```

Style: `border-left: 4px solid var(--info); background: var(--info-bg); border-radius: 0 8px 8px 0; padding: 1.5rem 2rem;`

---

## Tables

```html
<div class="table-wrapper">
  <table>
    <thead><tr><th>Column</th><th>Column</th></tr></thead>
    <tbody><tr><td>Value</td><td>Value</td></tr></tbody>
  </table>
</div>
```

Style: rounded border, warm header background, hover rows.

---

## Callouts (insight/warning/info)

```html
<div class="callout callout--success">
  <h4><i class="fas fa-check-circle"></i> Title</h4>
  <p>Content</p>
</div>
```

Variants: `callout--success` (green), `callout--warning` (orange), `callout--info` (blue)

---

## Lists

```html
<ul>
  <li>Item with accent-colored bullet dot</li>
</ul>
```

Styled with `::before` pseudo-element (6px accent-colored circle).

---

## Highlight grid

For key metrics or comparisons (2-3 items max). Simple boxes, no colored borders.

```html
<div class="highlight-grid">
  <div class="highlight">
    <div class="highlight__metric">31</div>
    <div class="highlight__label">violations identified</div>
    <p>Supporting context here.</p>
  </div>
</div>
```

Style: `display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;`
Each highlight: subtle border, padding, no colored top/side accents.

---

## Code blocks

```html
<pre class="code-block"><code>code here</code></pre>
```

Style: `background: #1e293b; color: #e2e8f0; border-radius: 8px; padding: 1.25rem; font-family: 'Red Hat Mono';`

---

## Separator

```html
<div class="separator"></div>
```

Style: `width: 60px; height: 3px; background: var(--accent); border-radius: 2px; margin: 2.5rem 0;`

---

## Original source link (always at bottom)

```html
<div class="source-link">
  <i class="fas fa-file-pdf"></i>
  <a href="./originals/filename.pdf">View original source</a>
</div>
```

Style: subtle, small text, placed in the footer/dark section at the bottom.
