# Visual assets

The README cover is an editorial illustration of architectural decision-making: one selected route through a compass and a network of system boundaries. It is decorative, not an executable or literal architecture diagram.

| Property | Value |
|---|---|
| Active cover | [system-design-compass-hero.png](system-design-compass-hero.png) |
| Historical baseline | [system-design-compass-hero-legacy.png](system-design-compass-hero-legacy.png) |
| Square logo (SVG) | [system-design-compass-logo.svg](system-design-compass-logo.svg) |
| Square logo (PNG) | [system-design-compass-logo.png](system-design-compass-logo.png) |
| Intended use | Main README hero, marketplace listings, and reusable project assets. |
| Generation | Subagent `image-generator`, 2026-10-29. |
| Visual direction | Physical Architectural Maquette 2.0: midnight navy drafting board, brushed brass and copper compass, frosted glass and ivory porcelain nodes, inlaid copper bus routes. |
| Accessibility | Keep the descriptive README alt text and the project title as real text. |
| Packaging | Repository asset only; excluded from the distributed skill folder. |

## Generation prompt

The current 2.0 hero cover was generated with this prompt:

```text
Use case: ads-marketing. Asset type: landscape GitHub README hero for the open-source project System Design Compass, a portable AI agent skill for architectural decisions. Create a distinctive premium engineering editorial cover, wide landscape 16:9 / 2:1. Subject: an exquisite, museum-grade physical architectural maquette photographed in an editorial studio from a high three-quarter perspective. In the center-right of the composition sits an ultra-precise mechanical navigation compass instrument, crafted from brushed warm brass and polished copper with subtle knurled thumbscrews, glass optical elements, a delicate needle, and fine micrometer vernier scales. Surrounding the compass is a tactile architectural system relief network set onto a deep midnight-navy matte drafting board with delicate blind-debossed gridlines. The network consists of a few monolithic satin ivory porcelain blocks and geometric translucent frosted glass cubes (representing system boundaries and state owners), interconnected by hairline-etched, laser-inlaid warm copper bus paths. One authoritative, glowing warm copper-orange route runs through the compass mechanism and cleanly reaches the dominant central ivory monolith, while secondary, speculative branching routes remain muted, pale, and frosted. Style: beautifully crafted physical maquette photographed from a high three-quarter view, tactile matte materials, controlled cinematic studio lighting, sharp tiny details, generous negative space on the upper left. Palette: midnight navy, warm ivory, brushed brass, restrained copper-orange. No words, no lettering, no labels, no logos, no fake terminal windows, no characters, no robots, no brain or AI icons, no purple gradients, no neon cyberpunk. Polished, calm, purposeful, memorable.
```

## Legacy asset provenance

The initial 2026-09-30 cover asset is preserved at [system-design-compass-hero-legacy.png](system-design-compass-hero-legacy.png) for historical continuity.

## Skill logo specification

The official square logo ([system-design-compass-logo.svg](system-design-compass-logo.svg), [system-design-compass-logo.png](system-design-compass-logo.png)) is a 512x512 squircle icon designed for marketplace listings, avatars, and documentation headers:
- Geometry: 72 calibrated tick marks, system boundary nodes, and a faceted 4-point compass rose.
- Palette: Midnight navy (`#122230`), burnished copper (`#d97736`, `#f8b677`), titanium steel (`#2c4b64`), and ivory porcelain core (`#f6f1e7`).
- Theme: Visual metaphor for an authoritative failure-path route connecting system boundaries to the central state owner.
