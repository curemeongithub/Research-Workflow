---
name: markdown-conventions
description: Formatting, citation, and frontmatter rules for pipeline research documents. Use when assembling the final document in Phase 8 to ensure consistent structure and inline citation format.
user-invocable: false
---

# Markdown Conventions

Formatting and citation rules for the final research document (Phase 8).

---

## Document Structure

### Headings

- `#` — Document title (one per document)
- `##` — Major sections (Executive Summary, Literature Review, etc.)
- `###` — Sub-sections within major sections
- `####` — Sub-sub-sections (use sparingly)

### Frontmatter

All pipeline artifact files require YAML frontmatter:

```yaml
---
phase: {N}
status: complete
timestamp: 2026-04-05T14:30:00Z
depends_on: [sources/manifest.yaml]
token_estimate: 4200
---
```

The `token_estimate` helps downstream agents budget context before loading the file.

---

## Citation Format

**Inline citations** use author-year format:

```
(Dosovitskiy et al., 2020)
[Dosovitskiy2020]
```

Use parenthetical format at sentence end, bracketed format mid-sentence:
- "The Vision Transformer achieves 86.5% top-1 accuracy on ImageNet (Dosovitskiy et al., 2020)."
- "The [Dosovitskiy2020] architecture uses a patch-based tokenization scheme."

**Every specific statistic, finding, or quote must have an inline citation.**

### Bibliography Entry Format

```markdown
## References

- Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al. (2020). *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale*. arXiv:2010.11929. https://arxiv.org/abs/2010.11929

- Weng, L. (2022). *Vision Transformer*. Lil'Log. https://lilianweng.github.io/posts/2022-06-09-vlm/
```

---

## LaTeX in Markdown

**Inline equations:** `$equation$`  
**Block equations:** `$$equation$$`

```markdown
The attention mechanism computes $\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V$.
```

Number important equations:

```markdown
$$
\mathcal{L} = \mathbb{E}_{x \sim p_{\text{data}}} \left[ \log p_\theta(x) \right]
\tag{1}
$$
```

---

## Tables

Use Markdown tables for comparisons, scoring, and reference material:

```markdown
| Method | Accuracy | Parameters | Year |
|--------|---------|-----------|------|
| ViT-B/16 | 81.8% | 86M | 2020 |
| ViT-L/16 | 85.2% | 307M | 2020 |
```

---

## Code Blocks

Use fenced code blocks with language hints:

````markdown
```python
model = ViT(image_size=224, patch_size=16, num_classes=1000)
```
````

---

## Figures

Embed figures using standard Markdown:

```markdown
![Caption describing the figure. Source: Author et al. (Year), Figure N.](path/to/figure.png)
```

For arXiv figures, always use the PDF-converted PNG (see source-management skill).

---

## Collapsible Source Headers (Per Section)

When writing section files, include sources at the top:

```markdown
> **Sources for this section:**
> 1. [ViT Paper](https://arxiv.org/abs/2010.11929) — original ViT equations, Fig. 1
> 2. [Lilian Weng — Vision Transformer](https://lilianweng.github.io/posts/2022-06-09-vlm/) — implementation details

[Section content...]
```

---

## Length Targets

| Section | Target Length |
|---------|--------------|
| Executive Summary | 400-500 words |
| Introduction | ~600 words |
| Literature Review | ~2,000 words |
| Key Paper Summaries | ~150 words per paper |
| Gap Analysis | ~1,200 words |
| Hypotheses | ~800 words |
| Methodology | ~1,500 words |
| Discussion | ~600 words |
| **Total** | **9,000-11,000 words** |
