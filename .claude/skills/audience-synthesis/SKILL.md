---
name: audience-synthesis
description: Rules for converting dense academic content into presentation-ready 
  material. Use in all presentation branch phases when making decisions about 
  what to include, how to sequence concepts, when to use analogy, and how to 
  handle mathematical formalism for a live audience.
user-invocable: false
---

# Audience Synthesis

## The Listener's Constraint

A reader can re-read. A listener cannot. Every concept must be introduced 
before it is used, every transition must be spoken aloud, and nothing can 
be assumed unless it was said in the same talk.

This constraint governs every decision in the presentation branch:
- A result that requires 10 minutes of setup is less presentation-worthy 
  than a result that can be stated in 30 seconds, even if it is more important.
- A contested area that can be described as "X and Y disagree on this" is 
  more useful to a talk than one requiring 5 minutes to frame.
- A notation that must be defined takes 30 seconds of audience attention. 
  Use it only if it pays off in clarity elsewhere.

## The Formalism Budget

A 30-minute talk can sustain 2–3 equations shown on screen before 
a significant fraction of the audience disengages. Each equation needs:
1. A plain-language statement BEFORE it appears: "What I'm about to show 
   you says, in symbols, that..."
2. A verbal walkthrough of its terms when it appears: "This first term is 
   the training loss... this second term is the regulariser..."
3. A sentence on what it implies AFTER: "What this means is..."

Theorems should be stated in plain language first ("Two-layer ReLU networks 
are equivalent to convex programs"), then precisely if the audience needs it.

## The Surprise Principle

Audiences remember talks that violated their expectations. For each major 
result, identify: what would a reasonable person have expected instead? 
State the expectation explicitly before revealing the result.

Pattern: "You might expect that... [wrong answer]. But [Author] showed 
that... [actual result]."

This pattern is more memorable than simply stating the result.

## Analogy Rules

- Use analogies only when they are structurally correct, not just evocative.
- State the analogy's limits explicitly: "The analogy breaks down when..."
- One analogy per act maximum. More than one dilutes the impact of each.
- Domain experts: analogies should clarify, not condescend. 
  Connect the new result to something they already know precisely.
- Mixed academic: analogies should connect to general mathematical 
  intuition (e.g., Lagrangian duality as "finding the price that makes 
  supply equal demand").

## Q&A Positioning

Three types of Q&A moments have different effects:
1. A question the speaker pre-empts in the talk: signals expertise and 
   preparation. Use for the 2–3 most obvious objections.
2. A question answered from the Q&A bank during discussion: signals 
   thorough preparation. Never answer "I don't know" when you do know 
   and could have prepared.
3. A question the speaker genuinely doesn't know and says so honestly: 
   builds more trust than deflection. "That's an open question — and 
   actually it's exactly what I'd work on next" is a strong answer.

## Slide Text Rules

- A slide is a visual anchor, not a teleprompter.
- Maximum 5 lines of text per slide; each line is a noun phrase.
- The speaking notes contain full sentences; the slide contains anchors.
- If you find yourself putting a full sentence on a slide, it belongs 
  in the speaking notes instead.
- One main visual element per slide. Two competing visuals split attention.

## Pacing by Audience Type

| Audience | New concepts per minute | Notation per slide | Proof depth |
|----------|------------------------|-------------------|-------------|
| domain_experts | 0.7 | Up to 3 symbols | Sketch in 3 steps |
| mixed_academic | 0.4 | 1 symbol, defined | State result only |
| general | 0.2 | Avoid | Metaphor only |
