---
id: 17-eligibility-flows
source: ITPR078770 PDF, page 21
state: current
confidence: verified
tags: [eligibility, 270/271, 276/277, DG, membership, vendors]
---
# DG Eligibility — Incoming & Outgoing Flows

## Incoming
Group enrollment files (FTP; 834 custom one-time), COBRA enrollments/payments/communications (USPS/Fax/EFT), Employer Portal eligibility transactions (MeritainConnect Plan Sponsor/HR — small changes, needs approval), 270 eligibility inquiry (EDI web service), Aetna Redirect 270/276 request (API; inquiries to Aetna redirected to Meritain — tool has list of customers that moved Aetna→Meritain), Wex inbound (web service), Section 111 responses (CMS site download), 276 claim status request (EDI web service), Coverage Inquiry ASC X12 SOAP, UI manual update

## Outgoing (from DG Membership Info)
Vendor extracts (FTP), letters (DG-USPS, Zelis, Smartcom), SimplePay/Coup Health (FTP), ID cards (Zelis), fully-insured medical & dental certs of coverage (USPS), state-mandated reports (All Payer, assessments — varies by state), Wex outbound (web service), Payflex extracts (FTP), COBRA notifications/forms/letters/coupons (USPS), Aetna Redirect 271/277 response (API), Medicare Crossover COBA (direct connect to CMS, EFT), billing statement to employers (Employer Portal), 277 response (EDI web service), 271 response (EDI web service), Section 111 uploads to CMS (group & member mandated, group TIN mandated, query not mandated)

## Eligibility data content
Member ID, name, DOB, SSN; coverage type; effective/termination dates; dependents; plan codes/tiers

## TPA eligibility characteristics (important)
- Eligibility reflects last employer file received; retro changes possible ("a yes today can become retro-term tomorrow")
- Dependent rules employer-defined, not uniform
- COBRA often via separate vendors; visibility delays common
- Wex: COTS SaaS for flexible benefits (pre-tax set-asides); 2-way with DG (could be batch + mini service to establish common key)
