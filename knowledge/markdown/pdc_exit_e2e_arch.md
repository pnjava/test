---
source_file: ITPR078770 - Meritain 2025 PDC Exit Migration - Meritain E2E Arch.png
source: email_attachment
date: '2026-03-27'
state: current
owner: TBD
category: architecture
confidence: inferred
tags:
- meritain
- pdc
- architecture
- e2e
- diagram
- dg
extraction_method: claude-fable-5 vision, locked prompt v1.0 (src/vision_prompt.md)
extracted_on: '2026-07-12'
review_status: pending_human_review (T1.4)
---

# Extraction: Meritain E2E Architecture (PDC Exit Migration)

## Overview

End-to-end architecture diagram of the Meritain ecosystem. The central element is a large green box labeled "DG", identified in the legend as "TPA Admin backnone system DG" (verbatim, including the "backnone" typo). Surrounding it: a "System of Engagement" column (left), "External Partners" groups (top, left, right), "Business operations/Services" (top), "Financial Managment" (verbatim spelling), "Health Fund Admin", "Analytics & Reporting", "Constituent AR & AP", "Constituent", integration middleware (AXway, Biztalk, EDI27X, WebDE), cloud services (AWS, GCP), and two annotation lists of operational facts. A legend color-codes: Vendor Assets (Deployed in Meritain Network), External Partnors [verbatim], System of Engagements, TPA Admin backnone system DG, Integration Apps, Home Grown apps, Enterprise shared app, Sunset applications; plus "Key processes" (blue text) and "Real time interaction" (orange text).

## Components

### DG core (green box, center — legend: "TPA Admin backnone system DG")
- **DG** — large green box; internal functions listed vertically (blue text = key processes): "Enrollment processing", "ID card printing", "Eligibility Processing", "Claim Adjudication", "Draft Processing (End of Day Process)"
- **DG Loader** — sub-box inside green area (left side)
- **DG Extracter** [verbatim] — sub-box inside green area (right side)
- **WebDE** — gray box docked at top of DG block (service layer; see note 5)
- **Benton/Job scheduler** — box directly under WebDE
- Annotation inside DG block: "5 days a week (11 to 17 hrs processing)"

### System of Engagement (left column)
- **MCMM**
- **MeritainConnect**
- **IVR App (Edify)**
- **HealthyMerits Portal**
- **Right Fax** — with red annotation "Exception process"
- Actor icons: "Prospect Customer" (CUSTOMER graphic), "Providers", "Broker", "Plan Sponsor", "Members", "External Auditor" (Audit Portal)

### External Partners (top group)
- **HealthSparq (Cost Estimator Tool)**, **USBank**, **ChangeHealthCare**, **Aetna**

### External Partners (bottom-left group)
- **Plan sponsors backoffice staff or IT system**
- **ChangeHealthCare, Availity and other clearing houses**
- **PBMs**
- **Medical managment (including AHH)** [verbatim spelling]
- **BankTEC**

### External Partners (right group)
- **HealthSparq (Cost estimator)**, **CMS**, **PBMs**, **Medical managment vendors including AHH**, **Reinsurance carriers**, **Navigation Partners (Quantum, Accolade and others)**, **Subrogation Vendors (PHIA)**, **Lyric (Claim XTEN)/Claim Edit vendor**, **BankTec**

### Business operations/Services (top group)
- **MemberAdvocacy**, **MHAT**, **1mage**, **StopLoss Web interface**, **MH SalesForce**, **QuickClicks**, **CSI Web**, **MCI** — pink boxes (legend: Home Grown apps); "1mage" is tan (vendor asset)
- Actor: "Meritain Operations team" (people icons)
- Small stacked box top-right of this group: **CSI Web / MCI / DG**

### Financial Managment [verbatim]
- **Sage 300 (AccPac)**

### Health Fund Admin
- **MWHCSS**, **Wex Health**

### Analytics & Reporting
- **Meritain Ent, Data Warehouse** [verbatim punctuation]
- **Meritain Legacy ODS (SQL server)**
- **Meritain DataHUBODS (Tidal, Python DB2 & DataStage) a.k.a DataVision**

### Correspondence / Care Management
- **Correspondence** group: **WorkIT**, **DMWiz**
- **Care Managment (Wholesale)** [verbatim]: **iSuite**
- **Kofax**

### Integration & middleware (gray/tan boxes)
- **AXway** — two instances (left of DG, right of DG)
- **Biztalk** — three instances (834 path, claims path, paper claims path); plus **Biztalk-1** (near PCI Services, with "Translation" connector to EDI27X)
- **EDI27X**
- **PCI Services**
- **Meritain APIC** — multiple instances (near External Partners top, below DG, near HSA/ID card paths)
- **Aetna APIC**
- **CSC** — two instances
- **Zelis** — multiple instances (ID cards path, Constituent AR & AP, print/mail path)
- **HSA Extract**, **LegaSuite**, **Stop Loss extractor**, **IVRS**, **DocStore**, **EBI** (two instances)

### Constituent AR & AP
- **Zelis** — "Paper checks information"
- **ECHO** — "eChecks and ERAs", "Provider funds information"

### Constituent
- **IMI** — blue box (legend: Enterprise shared app)

### CVTY/Wholesale
- **BAMR (repricer)** — annotation: "80% to 90% transactions are rePriced here."
- **MCPS** — separate CVTY/Wholesale box (bottom right), red arrow from BankTec labeled "Repricing claim data"; adjacent note "Future plan is to bypass BankTec layer to change SLA to 24 hrs."
- **Other third party repricer** — with note "Takes 3-4 days for rePricing"

### Cloud / messaging (top right)
- **AWS** cloud: **SmartComm**
- **GCP** cloud: **Meritain buckets**
- **Future functionality** box: **SMS Gateway**, **Mail server** (with SMS / Email arrows from SmartComm)
- **Zelis** and **1mage** (print/mail + archive path via EBI)

## Connections

(Direction stated only where arrowhead visible; orange lines = "Real time interaction" per legend, blue = key processes flows, black = other.)

- Prospect Customer → MCMM: "Marketing/Brochure"; "Customer Website access" into System of Engagement
- Providers → MeritainConnect: "Provider Portal"
- Broker → MeritainConnect: "Access Broker Portal"
- Plan Sponsor → MeritainConnect: "Plan sponsor portal" / "Enrollment changes by Plan Sponsor"
- Members → self service / "Member services"; Members → HealthyMerits Portal: "Wellness offer"
- External Auditor → "Audit Portal"
- MeritainConnect → WebDE: "ID card access", "DG Connect", "get data from DG using WebDE"
- Right Fax → DG: "Sends Enroll/Update changes via outlook to business users (Manual entry in DG)" — red label "Exception process"
- Kofax ← "Paper claims submitted at Meritain.com"; Kofax → Correspondence (WorkIT/DMWiz): "Doc Lookup/Workflow"
- iSuite ← Meritain Operations team: "Precert Lookup"
- Meritain Operations team → business ops apps: "Track/Interact" (MemberAdvocacy), "Log Audit" (MHAT), "Access Image data" (1mage), "Monitor stop filing" (StopLoss Web interface), "Sales Marketing" (MH SalesForce), "Web tool" (QuickClicks), "CSR Frontend" (CSI Web), MCI; "get Image" (1mage); "Telnet DG"; "Case Install (Setup plan and customers) and many more services"; "Wex Lookup" (Members icon)
- Business operations/Services → Financial Managment: "Finance operations"
- External Partners (top) ↔ integration: "SSO" links (HealthSparq, USBank); "US bank does store members credit card data" (italic note); "COBRA & Retire Plans cost share / Bank pay info/Result" (Meritain APIC path); Aetna/ChangeHealthCare → EDI27X: "270/271 & 276/277" with italic note "Real time response of 20 seconds. 2 million calls per day for 270/271 and 10k for 276/277. Lookup"; "Accumulators/Cost calcaultion" [verbatim] via PCI Services; Biztalk-1 → EDI27X: "Translation"
- EDI27X → WebDE (orange, into DG block)
- Zelis (ID cards) — "ID cards access" / "ID cards via WebDE"; Meritain APIC/CSC paths → WebDE: "COBRA & Retire Plans cost share", "get data from DG using WebDE"
- Health Fund Admin: MWHCSS/Wex Health ← "SSO"; "Parsed data" and "Id CARD access" arrows toward business ops / WebDE area
- HSA path: "HSA data (claims)" → HSA Extract → (toward DG/AXway area); LegaSuite → "ScreenScraper tool" label; Meritain APIC + "ID card" → Zelis
- CSI Web/MCI/DG small stack ← "Access data via WebDE" (two arrows from WebDE side, labels "Claim Docs", "Access data via WebDE")
- Plan sponsors backoffice → AXway (left): "Batch enroll files (834 & Proprietary format)" and "Batch enroll files ( Propriety format)" [verbatim]; AXway → Biztalk: "834"; Biztalk → DG Loader
- ChangeHealthCare/Availity clearing houses ↔ AXway (blue, bidirectional): "I:837 claims O:999 (ACK) - Daily" and "I:837 claims O:999 (ACK) - Hourly (Availity)"; → Biztalk → DG Loader
- PBMs → AXway: "RX claims"
- Medical managment (including AHH) → AXway: "PreCerts batch files"
- BankTEC → Biztalk: "Paper claims (converted to 837) and image (OCR)"; Biztalk → DG Loader
- DG/WebDE → DocStore: "Static reports"; DocStore ← IVRS; IVRS → WebDE (orange)
- DG Extracter → AXway (right side) → External Partners (right), labeled flows: "Batch feed for Cost estimator supporting data" (HealthSparq), "HIPPA eligibility request/response/claims (COB claims)" [verbatim "HIPPA"] (CMS, blue bidirectional), "Eligibility/Accumulator" (PBMs), "Eligibility/claims" (Medical managment vendors), "Stop loss filing" (Reinsurance carriers, via "Stop Loss extractor"), "Claims/Eligibility/Accumulators" (Navigation Partners), "Claim Data (candidate for other type of insurance)" (Subrogation Vendors), "I: Claim feed for claim edits O: 837 response" (Lyric), "Claim rePricing feed & Member Demographic" + "Individualize" (BankTec), "Individual record info" → IMI (Constituent)
- DG (bottom) → Meritain APIC → BAMR (repricer): "Real time call", "Repricing claim data" (CVTY/Wholesale)
- BankTec → MCPS (red arrow): "Repricing claim data"
- DG → Constituent AR & AP: "EOBs, Letters and ID cards data" → Zelis; "Provider funds information" → ECHO; Zelis → "Paper Checks and paper remittance" → Providers; ECHO → "eChecks and ERAs" → Providers; Members ← "EOBs, Letters and ID cards data"
- Analytics & Reporting ← "AR/AP", "Data extracts and reporting" (from DG area); EBI → Analytics & Reporting
- SmartComm (AWS) ← "XML Payload"; SmartComm → SMS Gateway (SMS) and Mail server (Email) in "Future functionality" box; "Output" arrow
- GCP Meritain buckets ← "XML payload"; → EBI → Zelis ("Print/Mail") and 1mage ("Archive data")

## Labels

Standalone text transcribed verbatim:

- Title annotations (top right): "1) Meritain current membership is around 2M." / "2) Advocate Health expected membership is 250K members" / "3) Future potential volume = 4M" / "4) Clinical platform is American Health iSuite Medical Management."
- Numbered operational notes (right, mid-page):
  1. "7 Queues to process claims."
  2. "Realtime Eligibility requests 2 million per day."
  3. "Realtime claim status calls 10k per day"
  4. "50% EDI27X calls are from Aetna and 50% from ChangeHealthCare."
  5. "WebDE is service layer on DG box written in same technology (Universe)."
  6. "Prod DG is on Singular AIX P9-PI80 54 CPUs (44 CPUs are dedicated to Prod)."
  7. "Non-Prod DG is on same Prod box with 3 CPU. (Plan is to move to other box)"
  8. "DR for DG is on Nevada Data center but not in same size. Its AIX P9-PI50."
  9. "Some repricing happens within DG box."
  10. "Avaya is planned to be replaced with Five9"
  11. "80%-90%of transactions are rePriced on BAMR."
  12. "DG is UniVerse DB and Pick programming language."
  13. "Current DC is Phoenix AZ (Planned for migration to Las Vegas)"
  14. "Draft Process(End of day processing) runs 5 days a week and take 11 to 17 hrs starting midnight."
  15. "For reporting on Data Vision business uses Tableau."
- BAMR annotation: "80% to 90% transactions are rePriced here."
- MCPS annotations: "Future plan is to bypass BankTec layer to change SLA to 24 hrs." / "Takes 3-4 days for rePricing" (Other third party repricer)
- Legend entries: "Vendor Assets (Deployed in Meritain Network)", "External Partnors", "System of Engagements", "TPA Admin backnone system DG", "Integration Apps", "Home Grown apps", "Enterprise shared app", "Sunset applications", "Key processes", "Real time interaction"

## Inferred

- INFERRED: "DG" is the core claims/enrollment administration platform ("TPA Admin backbone") — evidence: legend entry "TPA Admin backnone system DG" (typo for "backbone") + central position + enrollment/eligibility/claims functions listed inside it.
- INFERRED: The green DG block's internal blue labels (Enrollment processing, ID card printing, Eligibility Processing, Claim Adjudication, Draft Processing) are DG's key processes — evidence: legend says blue text = "Key processes".
- INFERRED: Orange connector lines denote real-time integrations — evidence: legend "Real time interaction" in orange.
- INFERRED: "1mage" is a document-imaging vendor product — evidence: tan color (vendor asset per legend) and "get Image"/"Access Image data"/"Archive data" flows.
- INFERRED: Pink boxes such as "Meritain Legacy ODS (SQL server)" and "Sunset applications" legend share a similar color; some pink boxes may be marked for sunset — evidence: color similarity only. NOT certain which specific boxes are sunset vs. home-grown (both appear pink-ish).
- INFERRED: "IMI" being a blue box means it is an enterprise shared application (shared with Aetna/CVS enterprise) — evidence: legend "Enterprise shared app" is the only blue legend entry.
- INFERRED: "EDI27X" refers to the X12 27x transaction family (270/271 eligibility, 276/277 claim status) — evidence: connector label "270/271 & 276/277" attached to it.

## Unclear

- Small stacked box near Business operations reading "CSI Web / MCI / DG" — purpose of this grouping is not labeled (access list? shared UI?).
- "MCMM" — no expansion given anywhere on the diagram.
- "MHAT", "MCI", "MWHCSS", "EBI", "CSC", "MCPS", "BAMR" — acronyms never expanded on the diagram.
- Distinction between "Home Grown apps" (pink) and "Sunset applications" (also pink/red-ish) is hard to resolve at several boxes (e.g. "WorkIT", "Meritain Legacy ODS (SQL server)", "Sunset applications" swatch) — colors are too close to call per-box.
- Several connector lines cross dense regions around WebDE/EDI27X; exact source/target of two orange arrows entering WebDE from the Health Fund Admin area could not be traced with certainty.
- "Benton/Job scheduler" — "Benton" may be a product name or a typo; nothing on the diagram clarifies it.
- Text "Individualize" on the BankTec flow — meaning not defined on the diagram.
- The arrow labeled "Finance operations" runs from Business operations/Services toward Financial Managment across the full page; intermediate stops (if any) are ambiguous.
- Some tiny italic text near the top ("Case Install (Setup plan and customers) and many more services") is legible but its exact anchor (which target box) is ambiguous.
