---
id: 15-stoploss
source: ITPR078770 PDF, page 18
state: current
confidence: verified
tags: [stop loss, reinsurance, Axway, SFTP]
---
# Stop Loss Processing

## Business context (verbatim summary)
Two types of insurance (re-insurance/stop-loss policies) for partially self-funded plans: (1) Specific — very serious/expensive; DG keeps track of expenses (e.g. over $100,000 DG files reimbursement claim with insurer; at half, e.g. $50,000, DG notifies plan sponsor of risk); benefit-plan vs insurance-plan coverage differences tracked in Tracking & Adj; individual or family level; higher-risk members can get reduced coverage ("Lazer/focused Spec"). (2) Aggregate — group-level insurance if group is sicker than average; group size changes over the year affect it; claims arrive at end of plan year; 24-month incurred / 12-month paid variants; lots of variance/complexity.
- Insurance company reimbursement is slow; Meritain can front money to plan sponsor and recover on reimbursement (charged; opt in/out)

## Components & flows
DG (Automated Specific Filings, Manual Specific Filings, Aggregate Filings (manual), Reimbursements Posted, Reporting) → Stop Loss extractor → Axway → carrier-hosted or Meritain-hosted SFTP → Stop Loss Carriers; reimbursement/documentation back; payment to Meritain or group (ACH/check). AdminPC2 = Meritain Windows Server landing zone — PGP encrypt/decrypt, zip/unzip (list to remove/replace). Stop Loss UI: http://stoplossui:81/Home/LogOn. SRP (Standard Reporting Package) available to client via Client Portal on MeritainConnect. Reporting: members reaching limits; expenses vs aggregate coverage.
## Unclear
- Stop Loss UI ownership ("Dont know about UI" note on diagram)
