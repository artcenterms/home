# Design Customization Audit

This audit captures the main CollectionBuilder-CSV constraints that currently limit deep visual customization in this project. The goal is not to discard the framework, but to identify where we should refactor it so the Arts Center site can support a more intentional, fully branded design system.

## Summary

The current theme layer is useful for:

- site identity in `_config.yml`
- broad typography and color settings in `_data/theme.yml`
- field visibility and navigation through CSV config files
- late-stage CSS overrides in `_sass/_custom.scss`

That is enough for light reskinning, but not enough for a design-forward rebuild. The main blockers are:

1. shared sections such as hero, nav, footer, browse controls, and item metadata are structurally hard-coded
2. the browse grid is generated in JavaScript string templates, which makes component-level redesign awkward
3. Bootstrap utility classes and fixed semantic choices are embedded throughout templates instead of being abstracted behind reusable component classes
4. several major sections rely on inline `<style>` blocks, preventing a clean design-token workflow

## Findings

### 1. Hero and banner systems are tightly coupled to one visual pattern

Files:

- `_includes/collection-banner.html`
- `_layouts/about.html`

Relevant code:

- `_includes/collection-banner.html:21-67`
- `_layouts/about.html:18-56`

Issues:

- both hero systems embed inline style blocks inside the templates
- both hard-code a dark translucent overlay pattern with `text-white bg-dark bg-opacity-75`
- both assume a background-image hero instead of supporting multiple hero modes such as logo-forward, split-layout, editorial text block, or minimal heading
- the about hero duplicates the same logic instead of sharing a configurable component

Impact:

- we can restyle the existing hero, but we cannot easily create alternate hero compositions without editing templates directly
- design experiments become one-off overrides instead of reusable patterns

Recommendation:

- replace the current hero includes with a single component-driven hero system
- support named hero variants such as `logo`, `image-overlay`, `split`, and `minimal`
- move all hero styling from inline `<style>` blocks into SCSS and expose layout options via front matter or theme config

### 2. Browse page structure is locked to a Bootstrap input-group and JS-built cards

Files:

- `_layouts/browse.html`
- `_includes/js/browse-js.html`

Relevant code:

- `_layouts/browse.html:12-91`
- `_includes/js/browse-js.html:55-103`

Issues:

- the filter bar is built as a single Bootstrap `input-group`, which is efficient but visually rigid
- control labels, spacing, and control hierarchy are fixed in the template
- browse cards are assembled as HTML strings inside JavaScript
- card markup includes hard-coded classes such as `card`, `text-center`, `btn-secondary`, `btn-outline-secondary`, and `btn-light`
- the JS renderer mixes data logic and view logic in one function

Impact:

- browse is the hardest page to redesign cleanly
- any meaningful change to card hierarchy, metadata placement, tag treatment, CTA style, or masonry/list behavior requires editing JS string templates
- accessibility and maintainability suffer because the template structure lives inside concatenated strings

Recommendation:

- extract browse cards into a real HTML template pattern
- either:
  - render cards server-side with Liquid and progressively enhance with JS, or
  - use a client-side template element instead of string concatenation
- break the browse toolbar into discrete layout regions with semantic wrappers instead of one large Bootstrap input group

### 3. Item pages are content-flexible but layout-rigid

Files:

- `_layouts/item/item-page-base.html`
- `_includes/item/metadata.html`
- related item partials in `_includes/item/`

Relevant code:

- `_layouts/item/item-page-base.html:8-45`
- `_includes/item/metadata.html:7-24`

Issues:

- item pages assume a single narrow-column reading experience with metadata below the primary media
- metadata output is a plain description list without grouping, visual sections, or configurable sublayouts
- citation and rights are fixed as adjacent cards after metadata
- the “Item Info” jump button is hard-coded into the title row

Impact:

- we can change colors and spacing, but not the deeper reading experience
- we cannot easily switch to a museum-style split layout, sticky metadata rail, editorial caption flow, or full-bleed media treatment without reworking the base item layout

Recommendation:

- redesign item pages around slots:
  - header
  - primary media
  - metadata rail or metadata sections
  - contextual actions
  - citation and rights footer
- keep `_data/config-metadata.csv` as the source of field visibility, but change the renderer to support field groups and richer display patterns

### 4. Theme configuration is strong for content configuration, weak for component design

Files:

- `_data/theme.yml`
- `_data/config-theme-colors.csv`
- `assets/css/cb.scss`

Relevant code:

- `assets/css/cb.scss:1-35`

Issues:

- the theme layer exposes fonts, link color, navbar color, and Bootstrap semantic colors
- it does not expose component-level decisions such as card radius, hero mode, nav layout mode, container widths, tag style, or metadata presentation
- design decisions are still mostly hard-coded in templates and partials

Impact:

- the configuration system is data-driven for content, but not yet data-driven for visual components

Recommendation:

- introduce a richer theme schema in `_data/theme.yml` for component tokens, for example:
  - `layout-style`
  - `hero-style`
  - `nav-style`
  - `card-style`
  - `metadata-style`
  - `surface-colors`
  - `border-radius`
  - `container-max-width`

### 5. Hard-coded Bootstrap semantic classes bypass the theme system

Files:

- `_includes/collection-banner.html`
- `_includes/footer.html`
- `_includes/js/browse-js.html`
- many feature and item partials

Examples:

- `bg-black`, `bg-dark`, `text-white`, `text-dark`
- `btn-secondary`, `btn-outline-secondary`, `btn-light`

Issues:

- semantic color classes are chosen directly in markup instead of through stable component classes
- this makes site-wide design changes harder because the visual intent is buried in dozens of files

Impact:

- branding work becomes a series of CSS overrides instead of a durable component system

Recommendation:

- replace repeated Bootstrap semantic decisions with project classes such as:
  - `.site-nav`
  - `.site-hero`
  - `.browse-card`
  - `.meta-chip`
  - `.section-panel`
  - `.item-actions`
- let those classes own the design language, while Bootstrap remains the layout utility layer

## What We Can Keep

These parts of CollectionBuilder still work well for the Arts Center site:

- `_data/config-nav.csv` for navigation structure
- `_data/config-browse.csv` for browse field selection
- `_data/config-metadata.csv` for metadata field visibility
- `_plugins/cb_page_gen.rb` for item generation
- the overall content model driven by `_data/<metadata>.csv`

The refactor should preserve the data architecture while replacing the presentation architecture.

## Recommended Refactor Plan

### Phase 1. Create a real design system layer

- establish component classes and CSS variables
- stop styling major areas through scattered Bootstrap semantic classes
- define global surface, spacing, type, and accent tokens

### Phase 2. Rebuild global chrome

- refactor banner/hero into reusable variants
- rebuild nav and footer as branded components
- remove inline style blocks from templates

### Phase 3. Rebuild browse as a customizable interface

- replace JS string-built card rendering with template-driven rendering
- split toolbar into composable regions
- support multiple browse presentation modes such as grid, editorial cards, or compact list

### Phase 4. Rebuild item page architecture

- create a more flexible base item layout
- support metadata grouping and alternate rail/stack variants
- unify citation, rights, and action modules

### Phase 5. Expand theme config for reusable visual variants

- add component-level theme settings to `_data/theme.yml`
- reduce the number of direct template edits required for future redesigns

## Suggested First Build Target

The best first refactor target is the browse stack:

- `_layouts/browse.html`
- `_includes/js/browse-js.html`

That area currently carries the highest visual debt and will unlock the biggest improvement in the shortest time. After that, the hero/nav/footer system should be next.
