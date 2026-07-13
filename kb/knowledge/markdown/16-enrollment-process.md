---
id: 16-enrollment-process
source: ITPR078770 PDF, page 20
state: current
confidence: verified
tags: [enrollment, 834, BizTalk, Sterling, eligibility, plan sponsor]
---
# Enrollment Process Flow (TPA Payers)

## Flow
Employee/Plan Sponsor → Generate Enrollment Batch Files (834 XML / Custom / Meritain Standard) → SFTP → Axway → SFTP → decision: Is 834? → Yes: BizTalk (x12 only; 834 conversion XML-to-flat-file; EDI validation/translation) → Receive Data → DG Eligibility Load (Pre-Processing → Data Mapping → Post-Processing) → Screen Validation/Reports (proposed changes) → Create/Update Records (current changes) → DG MV-DBMS. Data Entry Screen / Update Eligibility for manual entry. Eligibility Processing and ID Card Printing Processing hang off record creation. MeritainConnect Plan Sponsor Portal for small changes (uses DG enrollment systems, needs approval).

## Process facts (verbatim from Bob's note)
- BizTalk supports current 837 in/outbound, 834 in/outbound, 277CA outbound, real-time 270/271 & 276/277 validation/translation
- Sterling Gateway used for all other file-based activity (275s from Aetna, 278 inbound, extract formatting, moving files to Axway or GCP); SmartComm solutioned on Sterling
- No new development on BizTalk (decision made 2020); all new translation on Sterling ITX/ITXA
- MALF (Meritain Automated Lightsout Framework): internally developed .Net + XSLT translation app; fair number of extract/inbound processes; no new development

## Business process (7 steps)
1. Employer (plan sponsor) is source of truth (elections, QLEs, terms) 2. Employee makes elections 3. Employer sends 834 (weekly/monthly, not real-time) 4. TPA validates & loads 5. Enrollment visible in TPA systems (reflects most recent file) 6. Downstream feeds (networks, COBRA, PBMs, carve-outs) may lag 7. Claim-time re-verification; retro changes can void prior active status → denials/reversals
