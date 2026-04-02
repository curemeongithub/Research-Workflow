# Markdown Conventions

Shared Markdown formatting and structure rules for all research chapter workflows.

---

## Folder-Based Structure

Because IDE agents rewrite files from scratch on each edit, a single-file approach causes the entire chapter to be rewritten when editing any section. Instead, use a **folder-based structure** where:
- Each section is a separate file (can be edited independently)
- An index overview file lists the links to all sections.

### File Structure

```
Statistics/
├── Bayesian Credible Intervals.md          ← Overview index file
└── Bayesian Credible Intervals/             ← Folder
    ├── TEXTBOOK-PLAN.md                     ← Created by the research workflow
    ├── _01-introduction.md                 ← Section 1
    ├── _02-the-bayesian-framework.md       ← Section 2
    ├── _03-computing-credible-intervals.md ← Section 3
    ├── _04-examples.md                     ← Section 4
    ├── _98-math-background.md              ← Math Background appendix (if needed)
    ├── _99-closing.md                      ← Summary, questions, resources
    └── sources/                             ← Symlink or note pointing to sources/
```

**Key conventions:**
- **Index file:** `[Topic Name].md` — contains a simple Title and a Table of Contents (Markdown links) to the section files.
- **Folder:** `[Topic Name]/` — same name as the index file (without `.md`)
- **Section files:** Prefixed with `_` to denote they are parts of a whole. 
- **Numeric prefixes:** `_01-`, `_02-`, etc. for ordering.
- **Sources:** Referenced from central `sources/` — see TEXTBOOK-PLAN.md.

---

## Index File Template

The index file should be a standard markdown file providing an overview and links to sections.

```markdown
# Bayesian Credible Intervals

- [Introduction](Bayesian%20Credible%20Intervals/_01-introduction.md)
- [The Bayesian Framework](Bayesian%20Credible%20Intervals/_02-the-bayesian-framework.md)
- [Computing Credible Intervals](Bayesian%20Credible%20Intervals/_03-computing-credible-intervals.md)
- [Examples](Bayesian%20Credible%20Intervals/_04-examples.md)
- [Closing](Bayesian%20Credible%20Intervals/_99-closing.md)
```

---

## Section File Template

Start directly with the section heading:

```markdown
# Introduction

Content goes here...

## Subsection A

## Subsection B
```

**CRITICAL:** Each section file must have exactly **ONE `#` heading** (the section's main heading). Use `##` or lower for nested contents.

---

## Per-Section Source Headers

**Each section should include its own sources** in a blockquote at the top of the file to maintain traceability. 

```markdown
# Section Title

> **Sources for this section:**
> 1. [ViT Paper](https://arxiv.org/abs/2010.11929) - Original ViT equations
> 2. [D2L ViT](https://d2l.ai/chapter_attention/vision-transformer.html) - Implementation details

[Section content...]
```
<!-- IGNORE THE COMMENTED OUT SECTION.
**CRITICAL — Attribution for Blog Content:**

Many sources in this project come from independent researchers' blogs. These are original intellectual contributions that MUST be attributed properly in standard Markdown:

- **Source header**: Always list blog posts in the section source table with the author's name: `[Lilian Weng — "Reward Hacking in RL"](URL)`
- **Figures**: When using images from blog posts, always caption with: `Source: [Author Name], "[Post Title]"`
- **Explanations and framings**: Explicitly state the author in text: *"The following derivation follows Gundersen's treatment in [post title]"* -->

---

## LaTeX Formatting

Even though this is pure markdown, many markdown viewers (like GitHub or modern VS Code) support MathJax.

**Inline equations:** `$equation$`

**Block equations:**
```math
equation
```

### Common LaTeX Mistakes to Avoid

- Use `$...$` for inline math — NOT parentheses `(\theta)`.

---

## Markdown Formatting

### Lists

**Bullet points:**
- Use hyphens (`-`) for bullet points, NOT asterisks (`*`)
- Each bullet point MUST start on its own line
- Add a blank line BEFORE the first bullet point

### Callouts and Notes

Instead of Quarto syntax (`::: {.callout-note}`), use standard markdown blockquotes with bold headers:

```markdown
> **Note:**
> This is an important detail.

> **Warning: Common Misconception**
> This is a misunderstanding. Here is why it's wrong.
```

### Images

Images must be included via standard markdown links.

```markdown
![Image description](images/some-image.png)
```

---
