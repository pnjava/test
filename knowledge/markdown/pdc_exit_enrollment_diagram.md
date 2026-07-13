---
source_file: ITPR078770 - Meritain 2025 PDC Exit Migration - Enrolment.png
source: email_attachment
date: '2026-03-27'
state: current
owner: TBD
category: process
confidence: inferred
tags:
- meritain
- pdc
- enrollment
- diagram
- dg
- biztalk
- sterling
extraction_method: claude-fable-5 vision, locked prompt v1.0 (src/vision_prompt.md)
extracted_on: '2026-07-12'
review_status: pending_human_review (T1.4)
---

# Extraction: Enrollment Flow (PDC Exit Migration)

## Overview

Flow diagram of enrollment batch-file intake into DG, plus a long blue narrative text block (top right) signed "Bob" describing the BizTalk vs Sterling Gateway integration split. The flow runs: Employee/Plan Sponsor → enrollment batch file generation → SFTP → Axway → SFTP → an "Is 834?" decision → BizTalk (X12 files) or direct SFTP → "Recieve Data" [verbatim] → DG → a dashed "Eligibility Load" pipeline (Pre-Processing → Data Mapping → Post Processing) → screen validation → record creation → a blue database cylinder "DG MV-DBMS", with ID card printing and eligibility processing as downstream endpoints.

## Components

- **Employee / Plan Sponser** [verbatim spelling] — rounded box, top left
- **Generate Enrolment Batch Files** [verbatim "Enrolment"] — box; fans out to three file icons: **"834 Enrolment XML"**, **"Custom"**, **"Meritain Standard"**
- **SFTP** — icon, twice on the main path (before and after Axway) and once on the "No" branch
- **Axway** — rounded box
- **Is 834?** — diamond (decision)
- **BizTalk (Just x12 files)** — rounded box; fans out to two boxes: **"834 Conversion - XML to Flat File"** and **"EDI Validation / Translation"** (this second box is outlined in orange/red)
- **Recieve Data** [verbatim spelling] — box, right side
- **DG** — rounded box, right side (below Recieve Data)
- **Eligibility Load** — dashed-border container holding three boxes, flow right-to-left: **Pre-Processing** → **Data Mapping** → **Post Processing**
- **Screen Validation / Reports** — rounded box; yellow note **"Proposed Changes"** attached
- **Create / Update Records** — box; yellow note **"Commit Changes"** attached
- **Eligibility Processing** — green rounded box → circle **(A) "endpoint"**
- **DG MV-DBMS** — blue database cylinder
- **Data Entry Screen / Update Eligibility** — box (feeds the cylinder)
- **ID Card Printing Processing** — green rounded box ← from cylinder; ← circle **(A) "endpoint"** on its left
- **Meritain Connect Plan Sponser Portal** [verbatim] — rounded box, bottom left

## Connections

- Employee / Plan Sponser → Generate Enrolment Batch Files
- Employee / Plan Sponser → Meritain Connect Plan Sponser Portal (long vertical line, arrowhead at portal)
- Generate Enrolment Batch Files → 834 Enrolment XML / Custom / Meritain Standard (three arrows)
- Generate Enrolment Batch Files → SFTP → Axway → SFTP → "Is 834?" diamond
- Is 834? — **Yes** → BizTalk (Just x12 files); **No** → SFTP → Recieve Data
- BizTalk → 834 Conversion - XML to Flat File; BizTalk → EDI Validation / Translation (two arrows down)
- BizTalk → Recieve Data (horizontal arrow)
- Recieve Data → DG (vertical arrow down)
- DG → Pre-Processing (into dashed Eligibility Load container)
- Pre-Processing → Data Mapping → Post Processing → Screen Validation / Reports (leftward arrows)
- Screen Validation / Reports → Create / Update Records
- Create / Update Records ↔ Eligibility Processing (double-headed arrow); Eligibility Processing → (A) endpoint
- Create / Update Records → DG MV-DBMS (arrow down into cylinder)
- Data Entry Screen / Update Eligibility → DG MV-DBMS
- DG MV-DBMS → ID Card Printing Processing; (A) endpoint circle sits left of ID Card Printing Processing
- Meritain Connect Plan Sponser Portal → Pre-Processing (long line across the bottom, arrowhead at Pre-Processing)

## Labels

Blue narrative block (top right), transcribed verbatim:

> BizTalk – Supports current 837 Claim, inbound and outbound files. 834 Enrollment, inbound and outbound. 277CA Outbound. Real Time transactions 270/271, 276/277 for validation and translation. 837 and 834 involves validation of inbound files and translation functionality in both directions.
>
> Sterling Gateway is used for all other file based activity that has been brought to Integration to solution for. This included the 275's from Aetna, some 278 needs that have come up for inbound file translation. Then a host of other extract processing to format in the files as the recipients are requiring. Also used for moving files from internal locations to Axway when necessary or up to our GCP instance as well. One notable process solutioned on Sterling is SmartComm.
>
> There is no new development being done on BizTalk. There can be targeted enhancements like what was done recently to improve performance. But any new translation needs for files including X12 files are now accomplished on Sterling with ITX/ITXA. I made the decision that all new translation and file processing activity is done with Sterling back in 2020.
>
> One more note, there is another file translation application that was internally developed called MALF (Meritain Automated Lightsout Framework), that leverages .Net and XSLT translation capabilities. That still has a fair number of extract process and other inbound file processing activities on it. But that too does not have new development work, only minor updates where applicable.
>
> Bob

Other standalone labels: "Yes", "No" (decision branches), "Proposed Changes", "Commit Changes" (yellow notes), "endpoint" (both A circles), "Eligibility Load" (dashed container title).

## Inferred

- INFERRED: "DG MV-DBMS" means DG runs on a MultiValue DBMS — evidence: "MV-DBMS" suffix on the database cylinder; consistent with the E2E diagram note "DG is UniVerse DB and Pick programming language" (UniVerse is a MultiValue database).
- INFERRED: The two "(A) endpoint" circles are off-page connectors linking "Eligibility Processing" output to "ID Card Printing Processing" input — evidence: identical "A" labels, one at each flow end.
- INFERRED: The narrative author "Bob" is an integration SME/decision-maker — evidence: first-person "I made the decision that all new translation and file processing activity is done with Sterling back in 2020."
- INFERRED: The orange/red outline on "EDI Validation / Translation" marks it as highlighted for attention (possibly migration-relevant) — evidence: it is the only box with non-black border; no legend explains the color.
- INFERRED: The "No" branch of "Is 834?" carries non-834 files (Custom / Meritain Standard formats) directly to Receive Data without BizTalk translation — evidence: branch topology.

## Unclear

- **"Bob"** — surname/role not given anywhere on the diagram. (Candidate: cross-reference the emails.md thread for a Bob in integration.)
- The orange/red highlight on "EDI Validation / Translation" — meaning not defined (no legend on this diagram).
- "Recieve Data" box — which system performs this receive step is not stated (DG intake layer? Axway landing zone?).
- "Meritain Connect Plan Sponser Portal → Pre-Processing" — what payload this connection carries (portal-entered enrollments?) is unlabeled.
- The dashed "Eligibility Load" container — whether this is a DG-internal process or a separate application is not stated.
- "Data Entry Screen / Update Eligibility" — which application hosts this screen is not stated (CSI Web? DG terminal?).
- "ITX/ITXA" (in narrative) — not expanded; IBM Transformation Extender products assumed but not stated on the diagram.
- Small icon at the top-right corner of the Eligibility Load dashed box — too small to identify.
