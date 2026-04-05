# Visualization Standards

Shared visualization rules for all markdown chapter workflows (research, write, edit, update).

**Goal:** Your chapter should contain the absolutely perfect picture to explain each concept.

---

## Visual Priority Order (CRITICAL)

**Follow this order when choosing how to illustrate a concept:**

1. **Source images from downloaded papers** — Check the TEXTBOOK-PLAN.md Source Image Catalog FIRST. These are canonical, authoritative figures that readers expect to see. Copy them to `{Chapter}/images/` and embed.
2. **D2 diagrams** — for concept maps, flowcharts, and structural diagrams. 
3. **Python/hvplot (bokeh backend)** — for data visualizations, distributions, function plots, and ANY visual that must be numerically accurate.
4. **Web downloads** — for images not in sources/ (search and download during writing).
5. **generate_image** — ONLY for decorative/conceptual illustrations where numerical accuracy is irrelevant.

> **NEVER use `generate_image` for plots, charts, graphs, reliability diagrams, bar charts, heatmaps, confusion matrices, or ANY visual that needs to display accurate data.**

---

## Source Images (From Downloaded Papers — PREFERRED)

1. Check the TEXTBOOK-PLAN.md **Source Image Catalog** for images assigned to this section
2. **CRITICAL: Always convert from PDF, never just copy the PNG.** arXiv source PNGs are frequently low-resolution thumbnails (e.g., 586x288px) or blank white placeholders. Even when a PNG exists and looks non-empty, it is almost always a low-DPI version of the PDF. The PDF is the authoritative source.
3. Embed with caption and attribution:
   ```markdown
   ![Caption describing the figure. Source: Author et al. (Year), Figure N.]([Topic Name]/images/descriptive-name.png)
   ```

---

## D2 Diagrams (Structures, Flowcharts, Concept Maps)

> **MANDATORY: ALWAYS USE D2 FOR ALL DIAGRAMS**
>
> Write D2 code in a standard markdown `d2` code block. 
> Example:
> ```d2
> direction: right
> A -> B -> C
> ```
> (If you have access to the terminal, you may render it to PNG and embed the PNG instead.)

### The "Modern SaaS" Theme (Default)

**6 Semantic Color Classes** for complex concept maps:

| Class | Purpose | Stroke Color | Fill Color |
|---|---|---|---|
| `input` | Data, observations, givens | `#6366F1` (Indigo) | `#EEF2FF` |
| `process` | Transformations, computations | `#10B981` (Emerald) | `#ECFDF5` |
| `decision` | Branches, choices, alternatives | `#F59E0B` (Amber) | `#FFFBEB` |
| `output` | Final results, conclusions | `#1D4ED8` (Blue) | `#3B82F6` |
| `highlight` | Key concepts, "aha moments" | `#F43F5E` (Rose) | `#FFF1F2` |
| `container` | Grouping related nodes | `#D1D5DB` (Gray) | `#F9FAFB` |
