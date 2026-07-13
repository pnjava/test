---
id: 13-ebi-smartcomm
source: ITPR078770 PDF, pages 15 & 16
state: current + future
confidence: verified
tags: [EBI, SmartComm, GCP, AWS, correspondence]
---
# EBI & SmartComm

## EBI (Enterprise Business Integration)
Agile team providing enterprise solutions to simplify data exchange to/from internal systems; configurable solutions that reduce programming needed to deliver "any data, anywhere, anytime". Flow: DG → Analytics & Reporting (EDW, Legacy ODS, DataVision) → EBI → GCP Meritain buckets → Print/Mail (Zelis), Archive data (1mage).

## SmartComm
SmartComm (SmartCOMM SaaS on AWS, multi-tenant: Design/Content/Admin/Interactive/On-demand/Batch, S3) handles correspondence. Future: SMS Gateway + Mail server ("Future is SmartPath"). Connectivity: on-prem Meritain network (Certificate Authority, Identity Mgmt, F5 LB) via private MPLS (multiple 10Gb/1Gb links) → Cloud Networking Secure Hub (Azure) → Spoke VNet → SmartCOMM cloud; also CVS GCP cloud path. XML payload output from DG side.
## Unclear
- SmartPath definition/timeline; SmartComm-on-Sterling relationship detail
