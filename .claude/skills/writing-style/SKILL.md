---
name: writing-style
description: Conference-grade prose quality rules for document assembly. Use in Phase 8 to ensure sentence rhythm, given-new flow, AI-tell avoidance, and correct emphasis hierarchy.
user-invocable: false
---

# Writing Style

Prose quality rules for the document assembly phase. These produce conference-grade academic writing that is also readable and engaging.

---

## Core Style Rules

### One Idea Per Paragraph

Each paragraph introduces ONE idea and explains it fully. If you're writing "Additionally..." mid-paragraph, that's a new paragraph. Target 2-5 sentences; 6+ is a warning sign.

### Sentence Clarity

- Maximum two clauses joined by a comma. Never chain three or more.
- Keep subject and verb close — no long front-loaded modifiers.
- The grammatical subject should be the agent doing the action.
- Target 15-25 words per sentence. Long sentences (25-35 words) only for building momentum — max one per paragraph.

### Given-New Contract

Begin each sentence with information the reader already knows (topic position), end with new information (stress position). New info in sentence N becomes familiar info in sentence N+1.

**BAD (new first):** "A 12-layer Transformer processes the patch tokens. The Vision Transformer introduced this architecture."

**GOOD (old first):** "The Vision Transformer processes images as sequences of patches. Each patch is projected into a token, and a 12-layer Transformer processes the resulting sequence."

### Pronoun Clarity (Shell Nouns)

Never use bare "this," "that," "it," or "these" when the antecedent is ambiguous. Always follow with a clarifying noun:

**BAD:** "We clip the gradient. This is then used to update weights."  
**GOOD:** "We clip the gradient. This clipped gradient is then used to update weights."

### Nominalizations

Convert noun-ified verbs back to verbs:

**BAD:** "The optimization of the loss function was performed using SGD."  
**GOOD:** "We optimized the loss function using SGD."

Watch for: *-tion, -ment, -ness, -ity, -ance, -ence* endings.

### Noun Stacks

Unpack noun stacks of 3+ modifiers using prepositions:

**BAD:** "gradient descent learning rate schedule warm-up strategy"  
**GOOD:** "the warm-up strategy for the learning rate schedule in gradient descent"

---

## Engagement Techniques

### Motivation Before Formalism

Always answer "why should I care?" before "how does it work?"

### Sentence Rhythm (Gary Provost)

Vary sentence length deliberately. Short sentences punch. Long sentences build momentum and carry the reader through complex ideas. Mix them.

### Micro-Surprises

- "You might expect X, but actually Y"
- Rhetorical questions: "But wait — how can that be?"
- Open loops: "We'll see why this matters in the next section"
- Enthusiasm markers: "This is where it gets interesting."

---

## AI-Tell Detection

Remove these phrases that signal AI authorship:

| AI Tell | Replace With |
|---------|-------------|
| "It is worth noting that..." | Just say it |
| "This is a complex topic..." | Just explain it |
| "In conclusion, we have seen..." | "This section showed..." or just end |
| "Furthermore," / "Moreover," | New paragraph, or "Also," |
| "It is important to emphasize..." | Emphasize it directly |
| "Delve into" | "explore," "examine," "analyze" |
| "This nuanced topic..." | Just discuss it |

---

## Citation Format

Inline: `(Dosovitskiy et al., 2020)` or `[Dosovitskiy2020]`

Every specific claim — statistics, findings, framework names, quoted terms — needs an inline citation. A paragraph may have multiple citations; they should feel natural, not forced.

Do not write a citation you cannot verify in a downloaded source file (see source-integrity skill).
