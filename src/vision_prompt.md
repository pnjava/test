# Vision Extraction Prompt — LOCKED TEMPLATE v1.0

> Do not edit casually. Any change bumps the version and requires re-running
> the golden set (T6.2) against re-extracted artifacts.
> Used by: T1.3 vision extraction of diagrams and rendered slides.

---

## Prompt (verbatim)

You are extracting knowledge from a technical diagram for an enterprise
knowledge base. Accuracy matters more than completeness.

Describe every component, connection, label (verbatim), and flow.
Mark anything inferred as INFERRED. Do not guess unlabeled elements —
list them under UNCLEAR.

Rules:
1. Transcribe labels VERBATIM, including abbreviations, typos, and casing.
2. A connection may only be reported if a line/arrow is visible. State
   direction only if an arrowhead is visible.
3. If you interpret meaning beyond visible text (e.g. "this is probably a
   database because of the cylinder shape"), prefix that claim with
   INFERRED and give the visual evidence.
4. Unlabeled boxes, ambiguous arrows, cropped/illegible text → UNCLEAR
   section. Never invent a name for an unlabeled element.
5. Do not merge or normalize system names (e.g. do not rewrite "DG" as
   "Digital Gateway") — that is the alias registry's job (T2.1), not yours.

Output format (structured Markdown):

## Overview
One paragraph: what the diagram depicts overall, citing visible title text.

## Components
Bullet per component: verbatim label, shape/visual type, position hint.

## Connections
Bullet per visible line/arrow: source → target (verbatim labels),
line style, any text on the connector (verbatim).

## Labels
All standalone text verbatim: titles, legends, annotations, footnotes.

## Inferred
Every claim that goes beyond visible pixels, each with its evidence.

## Unclear
Unlabeled elements, illegible text, ambiguous connections. Non-empty if
ANY element lacks a legible label.
