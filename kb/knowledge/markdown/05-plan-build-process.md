---
id: 05-plan-build-process
source: ITPR078770 PDF, page 6 (meeting screenshots + email)
state: current
confidence: verified (from CVS internal slides, marked "Draft – Highly Preliminary")
sensitivity: internal (contains employee names; no member PHI)
tags: [Plan Build, DG, green screens, business process, SME]
---
# Plan Build & Design Process (Current State)

## Pre-Sale & Onboarding Workflow
1. Plan Sponsor Signs → 2. Member Eligibility is Shared → 3. Plan Build & Design (in DG) → 4. Member Onboarding Communications
- Eligibility files flow into DG through four channels: flat file, standard feeds, 834/812 transactions, manual UI entry
- Plan build occurs in DG's green-screen environment; green screens remain a major challenge (complexity, outdated interfaces, dependency on institutional knowledge)
- DG's design dictates workflow complexity and limits automation
- Welcome packets and ID cards sent by mail; sometimes distributed by brokers or clients; unclear if welcome email is sent today
- Entities in onboarding: Brokers, Navigation partners, Consultants, Meritain internal teams

## Plan Build & Design Workflow (5 steps)
1. Intake of Client Requirements — client-specific benefit designs from brokers/consultants/clients; requirements often inconsistent or non-standard; no structured rules repository; everything manually translated into DG logic
2. Translation of Requirements → DG Build Blueprint — SMEs interpret benefits and map to DG structure (cost-shares, limits, triggers, accumulators); DG has no discrete rule objects; every benefit decomposed across multiple screens
3. Manual Configuration in DG (Green Screens) — 60–80 separate "applications"/views; inputs typed manually; navigation requires muscle memory and deep tribal knowledge; ~150 member letters (20–30 migrated to SmartComm), ~250 claims letters (none migrated yet)
4. Hard-Coded Rules, Letter Triggers, Templates — tightly coupled trigger logic for outbound communications; rules buried across many screens; Plan Build has to manually piece together how each rule works
5. Testing & Validation — no automated regression environment; SMEs and processors must run test claims through DG manually; claim outcomes become the proxy for rule correctness (rules cannot be inspected directly); UAT fully manual, dependent on a small group of experts

## Key people (from email/meeting)
- Lynn Fletcher and Terrie Nicks named as best business resources for Plan Build process
- Jessica Savani sharing Plan Build procedures via Teams (General | Meritain Tech Strategy Execution)

## Inferred
- Plan Build SMEs are a critical knowledge bottleneck and prime target for the knowledge platform
