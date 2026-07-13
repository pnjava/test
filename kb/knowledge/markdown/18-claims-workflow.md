---
id: 18-claims-workflow
source: ITPR078770 PDF, pages 22 & 23 (duplicate views)
state: current
confidence: verified
tags: [claims, adjudication, DG, EDI 837, Zelis, ECHO, PBM]
---
# Meritain DG Claims Workflow

## Inbound claims
Clearinghouses (837 EDI), paper claims/faxes via Exela (837), Aetna Redirect (API), Medicare Crossover COBA (previously via ChangeHealth; setting up direct connect CMS NDM/IP), MSAS (Meritain Shared Admin Svcs) inbound claims (SFTP), PBM & Specialty PBM claims/invoices/accumulators (SFTP), SimplePay claims from Aetna (SFTP, 2025)

## Pre-adjudication
ClaimsXten (ChangeHealthcare, fka Intelliclaim) — EDI, high volume; Network Pricing (internal, online near-line, wholesale ops; batch/SFTP)

## During adjudication (internal routing)
CERis; PBS, FCR, OON Negotiation Pricing; TRIBAL tribal pricing (SFTP); Prepayment Audit (high dollar, e.g. hospital bills); SimplePay member share (SFTP); HCBB vendor API (HealthCare BlueBook, "Rewardable?"); Facility Plan (deeper discount); IDX Price and Pass / Price and Pay

## DG internals
DG Files: HSTRACKING (where/when claim was routed and returned), BHIST (claim details on DG screen). Claims UI app runs on Tomcat, separated by plan/user; LegaSuite COTS = workflow UI via screen scraping.

## Completion of adjudication
Drafts process generates check registers → uploaded to AccPac (Accounts Receivable); check registers to groups (Employer Portal, secure email); email notification "EOB available" (member portal; EOB images via API from Zelis); DG printed letters/correspondence (USPS)

## Post-adjudication outputs
Payment file to ECHO (SFTP); EOB & check print file to Zelis; printed EOBs/checks (USPS); electronic payments/EPPs to providers; SimplePay payment detail; 50% large claim reports & stop-loss filings (FTP); PHIA subro claims extract (SFTP) + PHIA auto-adjustment file (FTP, working on API); claims/accumulations extracts to PBMs (SFTP) + PBM Data Router (web service); postpayment audit (random); FSA vendors: Benefit Wallet, Payflex/Inspira, Health Equity incl ICMA-RC (SFTP); state surcharge (state portal upload); Wex (web service); extracts to vendors (SFTP); Standard Reporting Package (client portal); internal data warehouse (EDW/ODS, DB2/DataVision); Aetna VBC ~2025 (global thru cloud)

## Extra data feeds in
Precertifications (SFTP), network provider files (SFTP), fee schedules for DG-priced networks (SFTP), FairHealth data URC and Mean (SFTP)
