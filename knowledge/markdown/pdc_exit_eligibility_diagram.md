---
source_file: ITPR078770 - Meritain 2025 PDC Exit Migration - Eligibility.png
source: email_attachment
date: '2026-03-27'
state: current
owner: TBD
category: architecture
confidence: inferred
tags:
- meritain
- pdc
- eligibility
- diagram
- dg
extraction_method: claude-fable-5 vision, locked prompt v1.0 (src/vision_prompt.md)
extracted_on: '2026-07-12'
review_status: pending_human_review (T1.4)
---

# Extraction: Eligibility Data Flows (PDC Exit Migration)

## Overview

Diagram titled by its two containers: "Eligibility Incoming" (center) and "Eligibility Outgoing" (right), with a database cylinder labeled "DG" containing a box "Membership Info" between them. A long explanatory text block on the left is titled "Eligibility Data Distribution". Yellow sticky-note annotations qualify several flows. A "Shape Legend" panel defines the notation (Container - System, Container - Context, System, Database, API, Service, File, Event - Pub / Sub, Message - Queue, SFTP, Email, User / Role, Cloud, UI / Browser, Capability, Scheduler).

## Components

### Central data store
- **DG** — database cylinder shape (legend: Database), containing sub-box **"Membership Info"**

### Eligibility Incoming (container, center)
- **Group Enrollment Files (FTP)** — fans out to three file icons labeled **"834"**, **"Custom"**, **"One Time"**
- **COBRA enrolments, payments, communications (USPS, Fax, EFT)** [verbatim "enrolments"]
- **Employer Portal (Eligibility Transactions)**
- **270 Health Care Eligibility/Benefit Inquiry (EDI Web Service)**
- **276 Health Care Claim Status Request (EDI Web Service)**
- **Aetna Redirect - 270/276 Request (API)**
- **Wex Inbound (Web Service)**
- **Section 111 \*Group & Member response \*Group TIN response \*Query response (download from CMS site)**

### Eligibility Outgoing (container, right — top to bottom)
- **Vendor Extracts (FTP)**
- **Letters (DG-USPS, Zelis, Smartcom)**
- **SimplePay / Coup Health (FTP)**
- **ID Cards (Zelis)**
- **Fully Insured: Medical & Dental Certs of Coverage (USPS)**
- **271 Health Care Eligibility/Benefit Response (EDI Web Service)**
- **277 Health Care Claim Status Response (EDI Web Service)**
- **Aetna Redirect - 271/277 Response (API)**
- **Wex Outbound (Web Service)**
- **State mandated reports including: All Payer, Assessments, etc. (varied by state)**
- **Other reports as requested**
- **Payflex Extracts (FTP)**
- **COBRA notifications, forms, letters, coupons (USPS)**
- **Medicare Crossover - COBA (previously through Change Health setting up Direct Connect - CMS - EFT** [verbatim; closing parenthesis not visible]
- **Billing Statement to Employers (Employer Portal)**
- **Section 111 \*Group & Member mandated \*Group TIN mandated \*Query not mandated (upload to CMS site)**

### Annotations (yellow sticky notes)
- "UI Manual Update" — adjacent to COBRA enrolments box
- "Also other View Portals like Employer, Broker etc." → feeds the next note
- "Meritain Connect (Plan Sponsor/HR) Small Changes - Uses DG Enrolment Systems, Needs Approval" → arrow into Employer Portal
- "Coverage Inquiry ASC X12 SOAP" → arrow into 270 Inquiry
- "Enquiries to Aetna get redirected to Meritain. (Individual Benefits Inquiry??) Tool has list of Customers which were Aetna and now is Meritain" → arrow into Aetna Redirect - 270/276 Request (API)
- "Set aside money (pre-tax) for e.g. childare (medical benefits) / COTS product SAAS - to administer these flexible benefit options. 2 way from DG to Wex (Could be Batch and mini service to establish common key)" [verbatim "childare"] → arrow into Wex Inbound
- "Req from Fed to tell Fed about member coverage (To find Primary and Secondary covarage) BATCH file to CMS every so often" [verbatim "covarage"] → arrow into Section 111 (incoming)
- "Process movings to Smartcom" [verbatim] ← arrow from COBRA notifications (outgoing)
- "Clients payments to Meritain (EFT)" ← arrow from Billing Statement to Employers

## Labels

Left text block, transcribed:

> **Eligibility Data Distribution**
> Once MEA processes an enrollment event and determines a member's coverage, it generates eligibility data. This data must be shared with several downstream systems and vendors to ensure the member receives benefits and services correctly.
>
> **Eligibility Data Goes**
> 1. Repricing Vendors — Purpose: These vendors (e.g., Zelis, MultiPlan) use eligibility data to determine how claims should be priced. Why It Matters: If a member is newly enrolled or changes plans, the repricer needs to know what coverage applies to ensure correct discounts and allowed amounts. Format: Often EDI 834 or custom flat files.
> 2. ID Card Vendors — Purpose: Vendors responsible for printing and mailing ID cards (e.g., IDCardExpress) need eligibility data to know: Who is covered / What plan they're on / When coverage starts. Trigger: A new enrollment or plan change usually initiates this.
> 3. Internal Systems for Claims Adjudication — Purpose: The TPA's core claims system must have up-to-date eligibility data to: Validate member coverage when a claim is received / Apply correct benefits (copay, deductible, coinsurance). Examples: Internal eligibility tables, adjudication engines, or databases.
>
> **What's in the Eligibility Data**
> Member ID, name, DOB, SSN / Coverage type (e.g., Medical PPO) / Effective and termination dates / Dependent information / Plan codes and tiers
>
> **Why This Step Is Critical**
> Prevents claim denials due to outdated coverage / Ensures accurate pricing and payment / Enables timely delivery of ID cards and member communications

Shape Legend entries (verbatim): Container - System, Container - Context, System, Database, API, Service, File, Event - Pub / Sub, Message - Queue, SFTP, Email, User / Role, Cloud, UI / Browser, Capability, Scheduler.

## Connections

- Group Enrollment Files (FTP) → three file icons: 834, Custom, One Time (arrowheads visible)
- "Eligibility Incoming" container → DG cylinder (single arrow, arrowhead at DG)
- DG cylinder → "Eligibility Outgoing" container (single arrow, arrowhead at container)
- Yellow-note arrows as listed under Annotations (each with visible arrowhead toward the named box)
- COBRA notifications (outgoing) → "Process movings to Smartcom" note
- Billing Statement to Employers → "Clients payments to Meritain (EFT)" note

## Inferred

- INFERRED: DG's "Membership Info" is the eligibility/membership master data store — evidence: it sits inside the DG database cylinder between all incoming and outgoing eligibility flows.
- INFERRED: "MEA" in the text block refers to an enrollment-processing application upstream of eligibility distribution — evidence: sentence "Once MEA processes an enrollment event and determines a member's coverage, it generates eligibility data." No expansion given (see Unclear).
- INFERRED: The 270/271 and 276/277 pairs are X12 EDI real-time eligibility and claim-status transactions — evidence: standard names spelled out in box labels ("Health Care Eligibility/Benefit Inquiry"/"Response", "Health Care Claim Status Request"/"Response").
- INFERRED: "Aetna Redirect" boxes represent former-Aetna members whose eligibility inquiries are rerouted to Meritain — evidence: yellow note "Enquiries to Aetna get redirected to Meritain... Customers which were Aetna and now is Meritain."
- INFERRED: Wex is a COTS SaaS flexible-benefits (FSA/HSA-style) administrator with two-way DG integration — evidence: yellow note "Set aside money (pre-tax)... COTS product SAAS... 2 way from DG to Wex."

## Unclear

- **"MEA"** — acronym never expanded anywhere on the diagram. Candidate for alias registry; needs SME confirmation. (Possibly the enrollment application; possibly relates to "Meritain Enrollment App".)
- **"SimplePay / Coup Health (FTP)"** — "Coup Health" may be a truncation or typo (Coupe Health?); rendered small.
- **"Process movings to Smartcom"** — grammar suggests "Process moving to Smartcom"; transcribed verbatim.
- The single arrows container→DG and DG→container aggregate ALL flows; per-flow direction/protocol between individual boxes and DG is not drawn.
- Medicare Crossover box text ends without closing parenthesis — possibly cropped text.
- "IDCardExpress" appears in the left prose as an example ID-card vendor, but the outgoing box says "ID Cards (Zelis)" — relationship between the two vendors is not stated.
- Individual file icons (834 / Custom / One Time) have no further routing shown beyond Group Enrollment Files.
- The question marks in "(Individual Benefits Inquiry??)" are in the source note itself — the author was unsure; not an extraction artifact.
