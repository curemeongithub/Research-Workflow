---
name: source-integrity
description: Zero World Knowledge rules enforcing that every specific claim traces to a downloaded source. Use during any writing or analysis phase to prevent unsourced factual claims.
user-invocable: false
---

# Source Integrity

Zero World Knowledge rules for all writing and analysis phases. Every specific claim must trace to a downloaded, readable source file.

---

## The Principle

**You know nothing about the topic except what you read from the downloaded sources in this session.**

Your training data may contain information about the topic, but that information may be outdated, incomplete, or wrong. Treat your training knowledge as unreliable for any specific claim.

---

## What Requires a Source

### Hard Ban — Always Requires a Downloaded Source

| Category | Example of Failure |
|---------|------------------|
| **Direct quotes** | Any verbatim attributed text |
| **Statistics and numbers** | "21% improvement" → source required |
| **Named frameworks** | "the ABT framework" → describe from the source you read |
| **Claims about what an author argued** | "Dosovitskiy argues X" → verify in their paper |
| **Paper titles, authors, venues, years** | Training data gets these wrong frequently |
| **Descriptions of specific papers or talks** | Must come from reading the paper/transcript |

### Acceptable Without a Source

| Category | Example |
|---------|---------|
| General domain knowledge | "NeurIPS is a top AI conference" |
| Common definitions | "An abstract summarizes the paper" |
| Structural/rhetorical devices | Chapter organization, analogies |
| Pointing to people as examples | "Karpathy's blog is widely read" (no claim about content) |

### The Test

Before writing any claim, ask: *"Am I making a specific claim that could be wrong?"*

If yes → find it in a downloaded source.  
If not found → drop the claim or download the source.

---

## Source Readability Requirement

Downloaded ≠ readable. Verify before using:

```bash
wc -c sources/{PATH}/content.md   # must be > 500 characters
```

If a source folder lacks a readable text file:
1. Read `web-source-fetching.md` skill FIRST
2. Do NOT guess what it contains
3. Re-extract using the correct method

---

## Sub-Agent Reports Are Navigation Aids

If a sub-agent or earlier phase reports "source X says Y," verify it yourself.

- Sub-agent says "Line 47 contains the key finding" → read line 47 yourself
- Sub-agent quotes an author → verify the quote in the source file
- Sub-agent reports a statistic → find the statistic in the source yourself

The sub-agent may have misread, paraphrased, or hallucinated.

---

## Common Failures to Avoid

1. **The Phantom Read:** Claimed to extract content but produced training data. Check the actual file exists and is readable.

2. **The Restatement Fabrication:** Paraphrased a paper from training data instead of from the downloaded `.tex` file. The paraphrase was subtly wrong.

3. **The Precise Imprecision:** Wrote "20%" instead of the source's "19.7%" because training data rounded.

4. **Wrong Authorship:** Attributed a finding to "Smith et al." when the paper is by someone else.

**When in doubt, download the source. Minutes to download. The reader's trust to lose.**
