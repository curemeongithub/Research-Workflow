---
name: talk-design
description: Narrative arc patterns, pacing rules, timing tables, and structural 
  guidelines for academic talks. Use in Phase P6 (talk-architecture) when designing 
  the slide-by-slide structure and act timing.
user-invocable: false
---

# Talk Design

## The Four-Act Structure

All academic talks have four acts regardless of length:

1. **Motivation** — why this question, why now, why the audience should care
2. **Background** — minimum context needed to understand the results
3. **Core Results** — the 2–3 things you actually want them to remember
4. **Close** — what's open, what comes next, the one-sentence takeaway

## Time Allocation Table

| Total | Act 1: Motivation | Act 2: Background | Act 3: Core | Act 4: Close |
|-------|------------------|-------------------|-------------|--------------|
| 7 mins | 1 min | 2 min | 3 min | 1 min |
| 15 min | 2 min | 4 min | 6 min | 3 min |
| 20 min | 3 min | 5 min | 9 min | 3 min |
| 30 min | 5 min | 8 min | 12 min | 5 min |
| 45 min | 6 min | 12 min | 20 min | 7 min |
| 60 min | 8 min | 15 min | 27 min | 10 min |

Adjust by goal from talk_spec:
- survey: add 2 minutes to Background, subtract from Core
- argue_position: add 2 minutes to Core, subtract from Background
- introduce_open_problems: add 2 minutes to Close, subtract from Core
- present_result: add 3 minutes to Core, subtract from Motivation and Close

## Slide Budget

Rough rule: 1 slide per 90 seconds of speaking on average.
Reserve 2 title slides (title + optional outline), 1 conclusion slide.
Reserve backup_count = floor(duration_minutes / 10) backup slides.

```
total_slides ≈ (duration_minutes / 1.5) - 3 + backup_count
```

## The One-Sentence Takeaway

Every talk must have one sentence that captures its contribution. Write 
this before designing any slides. Every slide either:
- Builds toward it (sets up the context, proves a prerequisite)
- Delivers it (states the result directly)
- Contextualises it (explains implications, connections, limitations)

If a slide does none of these, it should be cut or moved to backup.

## The Climax Rule

The most surprising, important, or counterintuitive result should land 
at approximately 65–75% of total duration. Earlier: the audience doesn't 
have enough context. Later: there's no time to process it.

For a 30-minute talk: climax at ~20 minutes in.

## The Map Slide Rule

Every 8–10 minutes of content, give the audience an orientation slide: 
one sentence that says "here's where we've been and here's where we're going."
This can be as simple as a re-display of a roadmap figure or a 
"What we've established so far:" text slide. 
It prevents the audience from getting lost and signals respect for their attention.

## Audience-Specific Adaptations

### domain_experts
- Act 1 can be abbreviated (they know why this is important)
- Act 2 can start deeper (skip basic definitions)
- Act 3 can include proof sketches
- Act 4 should emphasise what's still open and why it's hard
- Q&A checkpoint: after Act 3, before Act 4

### mixed_academic
- Act 1 needs a concrete example early (slide 2 or 3)
- Act 2 must define all notation on first use
- Act 3 should state results plainly before formally
- Act 4 should emphasise broader implications
- No Q&A checkpoints during the talk

### general
- Act 1 must start with a real-world consequence
- Act 2 uses only analogies, no formal notation
- Act 3 communicates conclusions only, not mechanisms
- Act 4 closes with a question anyone can care about

## Backup Slides

Backup slides are for anticipated Q&A. They are NOT "if time permits" content.
Design them as if you will definitely be asked the triggering question.
Backup slides should be more technical or more detailed than the main talk, 
not less — they serve an audience member who wants to go deeper.

## Cuts Under Time Pressure

Identify in advance which slides are safest to cut. A slide is safe to cut if:
- It supports the narrative but does not carry the main claim
- It can be collapsed into an adjacent slide's speaking notes
- Cutting it does not introduce an undefined term in a later slide

Never cut the Climax slide. Never cut the Takeaway slide.
If forced to cut more than 20% of slides, reduce Act 2 first, then Act 4, 
then Act 1. Never reduce Act 3.
