---
id: 10-bamr-repricer
source: ITPR078770 PDF, page 12
state: current
confidence: verified
tags: [BAMR, repricing, claims, Azure, mainframe, Aetna]
---
# BAMR — Business Alliances Manual Repricer

## What it is
BAMR = Business Alliances Manual Repricer. Interacts with the Repricer BoR (Book of Record) and other components to handle pricing logic for claims before they move downstream. 80–90% of DG transactions are rePriced on BAMR.

## Flow
DG sends claim info in a real-time call (in Aetna primary network) → Meritain APIC → BAMR (CVTY/Wholesale) → gets first price → response to DG.

## Infrastructure
- Azure OpenShift Cloud (OCP4), Quay containers, US-East-2 primary active; PODs bamr-oci-prod (prodocp-int-lhzhh-worker-eastus21/23)
- Azure Load Balancer 10.59.54.54; user access https://www20.aetna.com/bamr/login.do (CVS users)
- Mainframe touchpoints: REPRICER (RESUBMIT/IND) CICS region PSODCICG, TRAN WC3, PROGRAM PRMPC0200; BAMR/Repricer BoR AE81/AE83 DB3G, PROGRAM S1JN, BAMR DB DWCI1P0AD; EPDB (MF) DB DSP400P0D; stored procedures
- Integration: MQ, WebService (DataPower), SMS, SCSR service (/getServiceCodeDescription), Audit (SSN masking)

## Related
Other third-party repricers take 3–4 days for repricing (BAMR path is real-time). MCPS (CVTY/Wholesale) is a sunset application.
