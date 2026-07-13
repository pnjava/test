---
source_file: Meritain_RCS_Roadmap_final v2.1.pptx
source: presentation
date: '2026-03-26'
state: current
owner: Muhammad Mudassar
category: architecture
confidence: inferred
tags:
- meritain
- rcs
- roadmap
- presentation
- ipp
- mace
- tcpa
extraction_method: claude-fable-5 vision on soffice/pdftoppm-rendered slides, locked prompt v1.0 (src/vision_prompt.md); replaces earlier python-pptx titles-only pass
extracted_on: '2026-07-12'
review_status: pending_human_review (T1.4)
---

# Extraction: Meritain RCS Roadmap final v2.1 (11 slides)

## Overview

11-slide Meritain Health deck ("An Aetna Company" logo on every slide, footer "Meritain Health | Member Communications"). Proposes a phased RCS member-communications rollout: Day 1 (2026) low-risk transactional welcome campaign using DataVision, Day 2 full omnichannel capability on IPP. Slide 11 is the conceptual design diagram that the Meritain_RCS_Solution_Architecture.md document was derived from.

## Slide 1 — Title

> Meritain Member RCS Communication Roadmap
> Simple phased approach for member communications

## Slide 2 — Background

Three boxes, verbatim:
1. "Meritain business wants to enable compliant, branded, low-risk Member welcome communications in 2026."
2. "Regulatory pressure (TCPA) requires controlled member communications"
3. "IPP is key for TCPA communication. However, IPP team would not be able to fully integrate with Meritain in 2026."

## Slide 3 — Recommendation

Three columns (header / body), verbatim:
- **Enable** — "Enable member RCS communications in three phases."
- **Focus on** — "Focus on TCPA compliance requirements for every phase."
- **Initial** — "Initial scope limited to newly enrolled members only."

## Slide 4 — Day 1 – RCS Welcome Campaign (2026)

Four boxes, verbatim:
1. "Welcome campaign using RCS/SMS/Email"
2. "Plan sponsors must collect phone number with Prior express consent."
3. "Transactional messages only (no marketing)"
4. "All Messages must be free of charge and branded as Meritain to be complaint with TCPA." [verbatim "complaint" — presumably "compliant"]

## Slide 5 — Day 1 – Limitations & Dependencies

Five boxes, verbatim:
1. "Applies only to new enrollments"
2. "MaCE Opt-out must be integrated with Meritain local preference DB."
3. "CSI Web & Meritain Connect capture phone and RCS opt-out"
4. "Meritain–MaCE integration for RCS enrollment trigger"
5. "DataVision remains source of preferences so no IPP integration."

## Slide 6 — Day 1 – Risks (TCPA)

Two boxes, verbatim:
1. "No RND check"
2. "No eDNC or Federal DNC check (Risk considered low for transactional-only messages)"

## Slide 7 — Day 2 – Full RCS/ECS Capability

Three boxes, verbatim:
1. "Supports multiple campaign types."
2. "Fully TCPA compliant"
3. "Supports both marketing and non-marketing messages"

## Slide 8 — Day 2 – Capabilities

Six boxes, verbatim:
1. "IPP as single source of member preferences"
2. "RCS/SMS/EMAIL with opt-out (STOP)"
3. "Multiple consent types per plan sponsor"
4. "Preferences managed across all channels"
5. "Existing members prompted to set preferences"
6. "Integrated eDNC and Federal DNC"

## Slide 9 — Day 2 – Dependencies

Four rows (label / body), verbatim:
- **Enhance** — "Enhance plan sponsor setup for default preference configurations"
- **Enhance** — "Enhance CSI Web, Mobile App, and Meritain Connect"
- **Integrate** — "Integrate CSI & Meritain Connect with IPP"
- **Update** — "Update DG enrollment to create default preferences"

## Slide 10 — Summary

Three icon columns (handshake / checkmark / car), verbatim:
1. "Day 1 focus on low-risk onboarding for new sponsors and new enrollments"
2. "Day 2 enables full omnichannel, compliant communications"
3. "Roadmap balances speed, compliance, and scalability"

## Slide 11 — Conceptual design (diagram)

Diagram title: **"Meritain RCS implementation Solution"**; outer container **"Meritain Ecosystem"**.

### Legend (color coding, verbatim)
- "New Components" (light blue)
- "Existing process require changes" (orange)
- "Day 2 (Subject to IPP readiness)" (olive/tan)
- "Day 1 Subjec to Sunset (After IPP implementation)" [verbatim "Subjec"] (pink)

### Components
- **Engagement and digital layer** (orange container): **CSI Web**, **Meritain Connect**
- **Plan sponsor enrollment files (With Prior express consent)** — orange
- **Enrollment Process (Use Group configuration for Plan sponsor collected preferences)** — orange
- **Digital preference apis** — pink (Day 1, sunset after IPP)
- **IPP Apis** — olive (Day 2); a second **IPP Apis** olive box sits outside the ecosystem at right, connected to MaCE
- **OLTP** container holding: **Digital Preference Data** (pink cylinder), **IPP (BoR)** (olive cylinder), and a **DG** sub-container holding **DG Preferences** (pink cylinder)
- **DataVision/EDP (Preference source of Truth)** — orange, full-width
- **Meritain Welcome Message Service** — light blue (new component)
- **MaCE messaging platform** — gray, outside the ecosystem

### Connections (arrowheads visible)
- CSI Web / Meritain Connect → Digital preference apis (red) and → IPP Apis (dark)
- Plan sponsor enrollment files → Enrollment Process
- Enrollment Process → IPP Apis; Enrollment Process → DG Preferences (red)
- Digital preference apis → Digital Preference Data (orange); IPP Apis → IPP (BoR)
- Digital Preference Data / IPP (BoR) / DG Preferences → DataVision/EDP
- Horizontal line labeled **"Stop/Unsubscribe disposition"** running from the Welcome Message Service side back toward Digital Preference Data / IPP (BoR) (red and dark segments)
- DataVision/EDP → Meritain Welcome Message Service, labeled **"Email, phone Preference"** (red)
- DG container → Meritain Welcome Message Service (blue)
- Meritain Welcome Message Service ↔ MaCE messaging platform (large hollow double-headed arrow)
- MaCE messaging platform ↔ IPP Apis (right side, hollow double-headed arrow)

### Sticky-note annotations (yellow, verbatim)
- "Enhance current UI to capture preferences for RCS and Emails for EOBs and other compaigns" [verbatim "compaigns"]
- "Newly onboarded Plan sponsors must collect Cell No from Members with \"Prior express consent\" for Healthcare Message"
- "Modify enrollment process to store email, cell no and enrollment preferences in IPP."
- "Dependency on IPP for: 1. Unsubscribe for RCS/SMS 2. RND process implementation 3. Federal DNC and Enterprise DNC check — Muhammad Muddassar A…" [name truncated on note]
- "Day 1: Tactical support for phone and consent — Muhammad Muddassar A…" (appears twice: once at Digital preference apis, once at Digital Preference Data)
- "Day 1: Tactical support for Opt-out come back from MaCE — Muhammad Muddassar A…"
- "TCPA compliance (Capability to opt-out, RND process, DNC process) — Muhammad Muddassar A…"
- "Existing datavision preferences will be replaced with IPP preferences"

## Inferred

- INFERRED: The deck's author is Muhammad Muddassar Ali — evidence: sticky notes signed "Muhammad Muddassar A…" (truncated), matching "Ali, Muhammad Muddassar" in the emails.md thread and "Muhammad Mudassar (Lead Architect)" in the solution architecture doc.
- INFERRED: "ECS" in "Full RCS/ECS Capability" (slide 7) is a channel/communication acronym paired with RCS — not expanded anywhere in the deck (see Unclear).
- INFERRED: Slide 11's color model implies the migration sequence: pink components (Digital preference apis, Digital Preference Data, DG Preferences) are Day 1 tactical builds destined for sunset once olive IPP components are ready — evidence: legend text "Day 1 Subjec to Sunset (After IPP implementation)" + "Day 2 (Subject to IPP readiness)".
- INFERRED: The Day 1 "Meritain local preference DB" (slide 5) is the same thing as "Digital Preference Data" on slide 11 — evidence: both described as Day 1 tactical preference storage; not explicitly equated.

## Unclear

- **"ECS"** (slide 7 title) — never expanded. Alias-registry candidate; SME question.
- **"three phases"** (slide 3) vs. the deck's Day 1/Day 2 structure everywhere else — is there an unstated Day 3/phase 3?
- **"Mobile App"** (slide 9) — a Meritain mobile app is named as a Day 2 enhancement target, but no mobile app appears anywhere in the solution architecture doc or the E2E diagram. Which app is this?
- Sticky-note signature "Muhammad Muddassar A…" — truncated by note width on every occurrence.
- Slide 11: exact endpoints of the "Stop/Unsubscribe disposition" line are partially obscured where it crosses the OLTP container border.
- Slide 11: the red arrow adjacent to the legend (bottom right, pointing down) — meaning not labeled.
- Slides 2–10 contain no diagrams; slide bodies are fully transcribed above, so no unlabeled boxes remain — this section's remaining items all concern slides 3, 7, 9, 11 as listed.
