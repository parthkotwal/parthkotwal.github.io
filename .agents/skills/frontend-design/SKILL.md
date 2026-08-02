---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

**Establish an aesthetic direction before writing any code.** The single biggest cause of generic output is starting to code before deciding what the thing should feel like. Every project gets a point of view.

Answer these first — from the user's brief if possible, by inference if not, by asking if the stakes are high:

- **Purpose**: What problem does this interface solve? Who uses it, and in what state of mind (focused work, idle browsing, urgent decision, first impression)?
- **Tone**: Pick a direction and name it in plain language before coding — e.g. "editorial broadsheet," "brutalist terminal," "warm handmade zine," "clinical Swiss precision," "retro-futurist arcade," "quiet Japanese stationery." The name is a commitment device; it makes downstream choices decidable.
- **Constraints**: Framework, performance budget, accessibility requirements, existing design system or brand, dark/light requirements, content that already exists.
- **Differentiation**: Name one or two specific choices that carry the identity — the thing someone would describe if asked what this site looks like. A typographic contrast, a layout signature, an unusual use of color, a distinctive empty state. Everything else supports it.

**If the project already has a committed direction** (a brand, a design system, a prior page in the same product), match it precisely rather than inventing a new one. Consistency beats novelty inside an existing product.

**CRITICAL**: Once a direction is chosen, execute it with precision. A fully committed modest idea beats a hedged ambitious one. Do not blend three directions to be safe — that blending *is* the generic aesthetic.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

These are decision frameworks, not fixed values. Derive the specifics from the chosen direction, then apply them consistently through CSS variables or design tokens.

**Typography** — usually the highest-leverage decision, and the fastest way out of default-looking work.

- Choose a deliberate type system: one family used across weights, or two families in intentional contrast (display vs. text, serif vs. sans, geometric vs. humanist). Name the roles: display, body, label, metadata, code.
- Set a type scale with real jumps between steps. Timid scales read as unconsidered. Headlines should be confidently large relative to body text.
- Tune the details that separate designed from defaulted: line-height (tighter for large display sizes, looser for body), letterspacing (negative for large headlines, positive for small caps and labels), measure (~60–75 characters for reading text), and optical alignment.
- Avoid using the platform default stack unless "system-native" is the actual direction.

**Color & Theme**

- Build a small palette with clear roles: background, surface, primary text, secondary text, border/divider, and one or two accents. Restraint reads as intentional; a large multi-hue palette reads as unconsidered.
- Give backgrounds a temperature. Pure `#FFFFFF` and pure `#000000` are rarely the best choice — a warm off-white or a slightly blue-shifted near-black carries more character.
- Use accent color sparingly and give it a job (interactive state, category, alert). Color that appears everywhere signals nothing.
- Define everything as CSS variables so the theme is changeable in one place. Support dark mode when it serves the use case, and match the default to context — tools and code-adjacent products often want dark, content and commerce usually want light.
- Check contrast against WCAG AA at minimum, especially for secondary text and borders.

**Motion**

- Calibrate motion to the tone. Editorial and reference interfaces should feel still; playful or consumer products can afford more. Either extreme is valid; unmotivated middle-ground motion is not.
- Motion should communicate — reveal state changes, show relationships, confirm actions. If it doesn't explain anything, cut it.
- Keep durations short (150–300ms for most UI transitions) and easing consistent. Define a small set of easing curves and reuse them.
- Respect `prefers-reduced-motion`.

**Spatial Composition**

- Choose a structure that matches the content: asymmetric editorial grids for browsing, tight functional density for tools and dashboards, generous single-column for long-form reading, modular grids for galleries.
- Use a consistent spacing scale (e.g. 4px or 8px based) and vary spacing meaningfully — tight within related groups, generous between sections. Uniform padding everywhere flattens hierarchy.
- Vary element size to create hierarchy. Interfaces where everything is the same size give the eye nowhere to go.
- Let something be big, and let something be empty. Whitespace is a design element, not leftover room.

**Backgrounds & Visual Details**

- Separate content with the lightest tool that works: whitespace first, then hairline rules, then surface tone changes, then borders, and only then shadows.
- If using texture, gradient, or noise, make it purposeful and subtle enough to read as material rather than decoration.
- Keep corner radius, border weight, and elevation consistent across the whole interface. Mixed radii are one of the clearest tells of assembled-from-parts design.
- Design the unglamorous states too: empty, loading, error, and long-content overflow. These are where quality is actually visible.

## The Generic AI Aesthetic — What To Avoid

Avoid the default cluster that signals unconsidered work: Inter (or the system stack) plus a purple-to-blue gradient plus white background plus heavily rounded cards with soft drop shadows plus emoji as iconography plus a centered hero with a gradient CTA button.

Also avoid, unless the direction specifically calls for it:

- Dark mode by default with no reason
- Every surface as a shadowed, rounded card
- Bright multi-color category systems where a label would do
- Glassmorphism, animated gradient backgrounds, and parallax as decoration
- Bouncing, scaling, or floating elements with no functional meaning
- Stock-photo hero imagery leading over content
- Timid type scales where headlines are barely larger than body text

The point isn't that any single one of these is forbidden — it's that reaching for all of them together is what makes work look machine-made.

## Layout

Derive layout from content and direction rather than reaching for a default template.

- **Entry/index views**: Establish hierarchy immediately. Decide what is primary and give it real prominence rather than tiling everything at equal weight.
- **Detail/reading views**: Constrain measure for readability. Supporting material (metadata, related items, navigation) goes in a secondary column or below, visually subordinate.
- **Tools and dashboards**: Optimize for density and scanning. Align numbers, use tabular figures, keep controls predictably placed, minimize chrome.
- **Signature element**: Whatever carries the identity (a marginalia sidebar, an oversized index, an unusual nav, a distinctive data display) should be the most refined part of the build, not an afterthought.

## Responsive Behavior

- Design the layout at each breakpoint rather than letting the desktop grid collapse arbitrarily. Ask what the structure *should* be at that width.
- **Desktop**: Full structure — multi-column, sidebars, persistent navigation.
- **Tablet**: Reduce columns; secondary content moves below primary or into a drawer.
- **Mobile**: Single column. Secondary content becomes expandable sections, bottom sheets, or a separate view. Touch targets at least 44px. Reconsider type scale — display sizes that work at 1400px often need to shrink proportionally less than expected, but they do need tuning.
- Test that nothing overflows horizontally and that long words, long titles, and empty states all hold up.

## Execution

**Match implementation complexity to the aesthetic vision.** A restrained direction is achieved through precise typography and spacing, not added features. An expressive direction earns its complexity. In both cases, refinement comes from consistency: same scale, same easing, same radii, same rules applied everywhere.

Before finishing, review against the named direction: does every choice serve the tone that was committed to at the start? Cut anything that doesn't.