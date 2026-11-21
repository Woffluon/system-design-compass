# Visual assets

This directory holds the vector brand marks and historical cover illustrations for System Design Compass. All files in `assets/` stay outside the distributable `skills/system-design-compass/` runtime package so the skill surface contains only Markdown and YAML files.

| File | Format | Dimensions / viewBox | Role |
|---|---|---|---|
| [system-design-compass-logo.svg](system-design-compass-logo.svg) | SVG | `0 0 256 256` | Primary square symbol (`Vector Gate`) for README headers, avatars, and favicons. |
| [system-design-compass-logo.png](system-design-compass-logo.png) | PNG | `512x512` | Raster export of the primary square symbol with transparent background. |
| [system-design-compass-lockup.svg](system-design-compass-lockup.svg) | SVG | `0 0 944 256` | Horizontal combination mark pairing the `Vector Gate` symbol with the outlined wordmark. |
| [system-design-compass-hero.png](system-design-compass-hero.png) | PNG | `16:9` raster | Archived 2026-10-29 physical maquette editorial cover illustration. |
| [system-design-compass-hero-legacy.png](system-design-compass-hero-legacy.png) | PNG | `16:9` raster | Archived 2026-09-30 baseline cover illustration kept for provenance. |

## Vector Gate geometry

The `Vector Gate` mark replaces the earlier 72-tick dial illustration with a pure geometric construction built from two flat vector paths and `13` total anchor points. It uses zero gradients, zero raster filters (`feGaussianBlur`, `feColorMatrix`), and zero live `<text>` tags.

| Component | Coordinate specification (`256x256` grid) | Architectural meaning |
|---|---|---|
| Invariant state ring | Centered at `(128, 128)`, outer radius `R_out = 100` (nominal `98` before optical expansion), inner radius `R_in = 68` (nominal `66`), thickness `32` units | Bounded state ownership and failure containment boundary. |
| Northeast decision gate | Open aperture in the 45-degree northeast quadrant with cut jaws angled at `150` degrees and `120` degrees, parallel to the needle edges across a `22`-unit negative-space channel | Single verified decision exit through system constraints. |
| Asymmetric compass needle | Northeast apex at `(230, 26)` with `2` units of optical overshoot past the ring bounding box, waist vertices at `(100.67, 100.67)` and `(155.33, 155.33)`, southwest tail at `(80.66, 175.34)` | Directional vector resolving architectural trade-offs toward one verified route. |
| Invariant state core | Circular negative-space cutout centered at `(128, 128)` with radius `r = 15.5` (`fill-rule="evenodd"`) | Central invariant state owner anchoring the decision axis. |

## Color system

The mark uses two flat engineering colors on light or dark surfaces, with one-color monochrome fallbacks (`#0F172A`, `#2563EB`, `#000000`, or `#FFFFFF`) for constrained contexts.

| Role | Name | HEX | RGB | Usage |
|---|---|---|---|---|
| Primary structural ink | Invariant Slate | `#0F172A` | `15, 23, 42` | Outer circular state boundary ring and wordmark paths on light backgrounds. |
| Directional accent | Verification Cobalt | `#2563EB` | `37, 99, 235` | 45-degree northeast compass needle in both the standalone symbol and lockup. |
| Light surface | Drafting Paper | `#F8FAFC` | `248, 250, 252` | Default light background for documentation and print sheets. |
| Dark surface | Deep Slate Canvas | `#090D16` | `9, 13, 22` | App icon tile and dark-mode container background (paired with `#F8FAFC` ring and `#3B82F6` needle). |

## Typography and scale rules

In [system-design-compass-lockup.svg](system-design-compass-lockup.svg), the two-line wordmark (`SYSTEM DESIGN` at `56` units cap height above `COMPASS` at `66` units cap height) is derived from `Inter SemiBold` (`SIL Open Font License 1.1`). All glyph contours are converted into self-contained cubic Bezier `<path>` outlines (`279` total anchors across the lockup) so rendering stays identical across machines without installed fonts.

| Parameter | Rule |
|---|---|
| Minimum symbol size | `16px` (`16x16` favicon and inline badge floor). |
| Minimum lockup size | `120px` width (`32px` height). Below `120px` width, use [system-design-compass-logo.svg](system-design-compass-logo.svg) alone. |
| Clear space | Leave at least `31` grid units (equal to the diameter of the `r = 15.5` central state core, or `12%` of symbol height) of empty margin around all four sides. |
| Prohibited modifications | Do not add drop shadows, blur filters, gradients, or dial ticks. Do not rotate the needle away from its 45-degree northeast axis. |

## Historical cover provenance

The archived raster covers [system-design-compass-hero.png](system-design-compass-hero.png) (generated 2026-10-29) and [system-design-compass-hero-legacy.png](system-design-compass-hero-legacy.png) (generated 2026-09-30) remain in this folder so earlier commits and external references continue to resolve.
