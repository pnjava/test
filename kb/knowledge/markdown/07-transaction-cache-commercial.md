---
id: 07-transaction-cache-commercial
source: ITPR078770 PDF, pages 2, 8, 9 ("Transaction Cache solution – Commercial Member/Plan/Product")
state: current/in-flight (Aetna commercial side; pattern reference for Meritain)
confidence: verified (diagram)
tags: [transactional cache, MongoDB, Kafka, GKE, Apigee, member, plan, product]
---
# Transaction Cache Solution — Commercial Member/Plan/Product (Aetna side)

## Sources
- MEA/ODS (on-prem, DB2): Commercial Member Data — daily refresh + one-time initial load via EDML GCS bucket / Enterprise Data Movement Framework; Cloud Composer DAG stores member data into GCS; Raw Viewable BigQuery
- PSBoR/PBoR (on-prem, DB2): Commercial Plan/Product data — daily refresh + one-time initial load
- Incremental transaction updates via Confluent Kafka (GCP)

## Caches & services (GKE)
- Commercial Member cache — RTMEI (rename); Lucene search function; Apigee X API; member name search microservice
- Commercial Plan/Product cache (probably reuse BRAGS DB); Plan Services microservices; Cloud Pub/Sub publishes Plan Events (change stream) and Member Events
- Consumers: Aetna Employer Portal (AEP BFF, member search), Vendor Eligibility sub-app (eligibility extract generation; subscribes to plan events), MICS Member ID Card system (ID Card Portal, MICS BFF; subscribes to plan events), LGIT/MHP/QTL related sub app

## Users
Aetna super users, plan sponsors, brokers, constituent super users, Aetna UI admin

## Inferred
- This is the enterprise pattern the Meritain Transactional Cache is expected to mirror (MongoDB + Kafka + GKE microservices + Apigee)
## Unclear
- Whether Meritain will literally reuse these components or only the pattern
