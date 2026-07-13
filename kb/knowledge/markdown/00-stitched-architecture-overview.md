---
id: 00-stitched-architecture-overview
source: Synthesized from ITPR078770 PDF (pages 1–31); see per-artifact docs for evidence
state: mixed (current + proposed clearly marked)
confidence: verified unless marked inferred
---
# Meritain / DG — Stitched Architecture Overview

## 1. What DG is
DG ("Data General") is Meritain's TPA administration backbone: a Rocket UniVerse MultiValue database with Pick/UniBASIC application code, running on a single AIX P9-PI80 (54 CPUs, 44 prod / 3 non-prod on the same box) in Phoenix AZ (Las Vegas migration planned), with a smaller DR box (P9-PI50) in Nevada. It is simultaneously the system of record and the application platform for claims adjudication, enrollment, eligibility, ID cards, and the nightly Draft (payment) process — which runs 5 days a week and takes 11–17 hours. Membership ~2M, with +250K (Advocate Health) expected and 4M potential. [Sources: 06]

## 2. How the world reaches DG (current state)
Nothing reaches DG "natively" — everything goes through one of five doorways:
1. **WebDE** — the real-time service layer, written in Universe, running ON the DG box (RedBack stack). Serves Meritain APIC (accumulators, ID cards), EDI27X real-time 270/271 & 276/277 (2M eligibility calls/day, 20-sec SLA, 50% Aetna / 50% ChangeHealthCare), CSI Web (CSR frontend), IVR (Edify), QuickClicks, Claim System Connect. Slated for replacement by MVIS. [11, 06]
2. **File/EDI batch** — Axway (managed file transfer) + BizTalk (x12: 837/834/277CA; frozen since 2020) + Sterling ITX/ITXA (all new translation) + MALF (legacy .Net/XSLT). 834 enrollment, 837 claims, vendor extracts, stop-loss filings. [16, 06]
3. **Screen scraping** — LegaSuite/Rocket Modern Experience powering MCI (Claims UI on Tomcat) for the Operations team. [12]
4. **Green screens / Telnet** — direct DG screens for plan build (60–80 apps/views, fully manual, tribal knowledge) and case install. [05, 06]
5. **Paper/fax** — BankTec (paper claims → 837 + OCR), Exela, RightFax (manual entry into DG), Kofax. [06, 14]

## 3. Claims value chain (current)
Inbound (clearinghouses 837, Aetna redirect API, paper via BankTec/Exela, PBM feeds, Medicare COBA) → pre-adjudication edits (ClaimsXten) + network pricing → **repricing**: 80–90% via real-time call to BAMR (Azure OpenShift + mainframe CICS/DB2 stack on the Aetna side); a minority via the internal UniBASIC repricing engine inside DG; other third-party repricers take 3–4 days → adjudication in DG (7 claim queues, Benton scheduler; HSTRACKING/BHIST files) → Drafts end-of-day generates check registers → AccPac (Sage 300) accounting, ECHO payments, Zelis EOB/check print & ID cards, 1mage archival, PHIA subrogation, PBM accumulator extracts, EDW/DataVision reporting → Tableau. [18, 10, 21, 22, 23, 06, 09]

## 4. Eligibility & enrollment (current)
Employer is source of truth → 834/custom files (weekly/monthly) via Axway → BizTalk/Sterling → DG eligibility load (pre-process, map, post-process) or manual UI entry; MeritainConnect plan sponsor portal for small changes (needs approval). Eligibility redistributed to repricers, ID card vendors (Zelis via daily fixed-length extract), Wex, Payflex, COBRA vendors, CMS Section 111. Retroactive changes are normal — claim-time re-verification can void prior eligibility. [16, 17, 20]

## 5. Target state (North Star, proposed)
Governing principle: **"No one will interact with DG directly. All DG interaction will be done through data platform."** Priorities: P1 CDC out of DG; P2 refactor DG into domain-driven architecture (Claims, Member, Plan Sponsor, Provider/Rates/Network, Benefit Admin, Case setup, Draft Payment); P3 AI contact center JV + evaluate Zelis for member services; P6 agentic enrollment-verification and claims-decision copilots (LLM + RAG, orchestration, audit/evidence store); P7 predictive analytics; P8 AI-powered production support; P9 real-time internal integrations. Enterprise Data Platform = BigQuery lake + MongoDB Transactional Cache + FHIR store; integration via Kong (internal) / Apigee (external) / event layer. [02]

## 6. The CDC bridge (proposed — decision pending)
Two documented approaches, **currently in tension**:
- **Page 1 evaluation**: RDRS (Rocket Data Replicate & Sync) rated best → AIX MVDB → CDC layer → Linux Replication DB → lightweight Kafka forwarder → GCP Kafka → Kafka Connect → MongoDB Atlas (Transactional Cache), over VPN/Interconnect/PSC.
- **Pages 3/7 reference architecture**: application-level Transactional Outbox in UniBASIC (no usable WAL in MVDB), OUTBOX file written atomically in-transaction, background publisher → Kafka (system of record for events) → idempotent Mongo projections, full rebuild via replay.
These may be complementary (RDRS for replication/HA, Outbox for business-semantic events — the docs say U2 replication and CDC outbox are "complementary, not interchangeable"), but the chosen production pattern is an open SME question (#1). The Aetna-side Commercial Member/Plan/Product Transaction Cache (MEA/ODS + PSBoR → Kafka → GKE caches + Apigee + Pub/Sub) is the enterprise pattern reference. [01, 03, 07]

## 7. Biggest architectural risks visible in the artifacts
- Single-box concentration: prod + non-prod + WebDE service layer + repricing all on one AIX machine; DR undersized. [06]
- Tribal-knowledge dependency: plan build has no rules repository; rules only verifiable by running test claims; small expert group; ~400 letter templates mostly unmigrated. [05]
- Batch-era SLAs embedded in business promises (Drafts 11–17 hrs; BankTec multi-day; repricing 3–4 days off-BAMR). [06, 18]
- CDC direction unresolved while downstream (Transactional Cache, 96 MDS endpoints, portals, AI copilots) depends on it. [01, 03, 02]

## 8. Gaps
24 SME questions catalogued in sme-questions.md; alias registry in aliases.yaml (6 pending confirmations).
