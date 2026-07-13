---
id: 09-datavision-analytics
source: ITPR078770 PDF, pages 11 & 15
state: current (with retirement notes)
confidence: verified
tags: [DataVision, DataHub ODS, DB2, EDW, Tableau, analytics]
---
# Analytics & Reporting — DataVision / DataHub ODS

## Components
- DG feeds DB2 (in datacenter)
- Enterprise Data Warehouse — flagged "Subject to Retire (need to move data extract logic to DataHub ODS)"
- Legacy Operational Data Store (SQL Server) — flagged "will also go away after EDW"
- Data Vision (DataHub ODS): IBM DB2 with Tidal ETL, Python custom scripts, DataStage; DV Datamarts → Tableau
- Note: "Enterprise may not want to keep with DB2"
- Consumers/feeders: Salesforce, Digital Team (Portals)
- EBI pulls from Analytics & Reporting → GCP Meritain buckets → Zelis (print/mail), 1mage (archive); SmartComm (AWS) → SMS Gateway/Mail server (future; "Future is SmartPath")

## Inferred
- DataVision is the current de facto reporting hub and a likely early consumer of the Enterprise Data Platform (BigQuery)
## Unclear
- EDW retirement timeline; SmartPath scope
