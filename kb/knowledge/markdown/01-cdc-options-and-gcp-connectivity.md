---
id: 01-cdc-options-and-gcp-connectivity
source: ITPR078770 PDF, page 1
state: proposed
confidence: verified (diagram content), design not yet implemented
tags: [DG, CDC, Kafka, MongoDB, GCP, connectivity]
---
# CDC Options & DG→GCP Connectivity (Proposed)

## Components
- DG MVDB on AIX P9-PI80 (on-prem, legacy)
- CDC Layer options: Rocket Data Replicate & Sync (RDRS), MVX:Performance
- Replication DB on Linux OS (on-prem)
- Kafka Producer (Forwarder) Service — small Java/Python/Go/.NET service using Kafka Producer SDK; reads Replication DB, pushes JSON/Avro to Kafka topics in GCP
- GCP: Kafka Cluster (Confluent Cloud or GCP Managed Kafka), Kafka Connect (distributed mode), MongoDB Sink Connector
- MongoDB Atlas (GCP) = Meritain MongoDB Transactional Cache, with Data Denormalization step
- Connectivity: PSC endpoints on both GCP VPC and MongoDB VPC; VPC peering or private endpoint between them

## CDC Option Ratings (verbatim from table)
| Option | Fit | Notes |
|---|---|---|
| Rocket Data Replicate & Sync (RDRS) | ***** Best | Enterprise-grade CDC, ideal for AIX→Linux replication |
| MVX:Performance replication | **** | Native MV replication layer; great for MV→MV or MV→relational DB |
| Transactional Outbox | **** | Good when apps can be modified; modern design pattern |
| Trigger-based CDC (Audit Logging) | *** | Best for targeted event capture or compliance |
| API-level via MVIS | ** | Not CDC, but good for app modernization |
| Polling | x | Not appropriate for MV scale |

## Flow (proposed)
AIX MVDB → CDC Layer (RDRS/MVX) → Replication DB (Linux) → Lightweight Forwarder → Kafka over VPN/Interconnect/PSC → GCP Kafka → Kafka Connect + MongoDB Sink → MongoDB Atlas

## Network options
VPN (encrypted tunnel, bandwidth-limited), PSC (private service endpoint, no public internet), Interconnect (dedicated physical link, 10–100 Gbps)

## Unclear
- Which CDC option was actually selected (page 1 rates RDRS best; pages 3/7 recommend Transactional Outbox — CONTRADICTION to resolve)
- Replication DB technology (unnamed Linux DB)
