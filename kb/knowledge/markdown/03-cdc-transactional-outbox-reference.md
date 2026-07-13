---
id: 03-cdc-transactional-outbox-reference
source: ITPR078770 PDF, pages 3 & 7 (duplicate content)
state: proposed
confidence: verified (design doc), not yet implemented
tags: [DG, CDC, Transactional Outbox, UniBASIC, Kafka, MongoDB]
---
# DG MVDB → Kafka → MongoDB: Transactional Outbox Reference Architecture (Proposed)

## Non-negotiable principles (verbatim)
1. CDC must be application-level (MVDB has no usable redo/WAL logs)
2. Kafka is the system of record for change events, not MongoDB
3. Events are immutable (replayable)
4. MongoDB is a projection, not the source of truth
5. Idempotency is mandatory (events will replay)

## Design
- All writes wrapped in UniBASIC WRITE/DELETE wrappers (Option A, preferred) or UniVerse file triggers (Option B)
- CDC handler (CDC.ON.CHANGE + file-specific handlers e.g. CDC.HANDLER.CUSTOMERS) writes one OUTBOX record atomically inside the same MV transaction
- OUTBOX record: EVENT_ID, ENTITY, OPERATION (CREATE/UPDATE/DELETE), ENTITY_KEY, SEQUENCE, PAYLOAD (JSON), STATUS (NEW/SENT/ERROR), CREATED_TS
- Background publisher (phantom job / service / Kafka Connect) polls OUTBOX WHERE STATUS=NEW → publishes to Kafka → marks SENT; retries safe, idempotent
- Kafka topic per entity (e.g. mvdb.customer.events), keyed Customer:<CUST_ID>
- MongoDB consumers upsert (idempotent projection); full rebuild via offset reset & replay
- Avro preferred over JSON for schema enforcement once multiple consumers exist
- UniBASIC used ONLY for: write interception, event creation, outbox persistence

## Implementation order
OUTBOX file → CDC handlers → wrappers/triggers → verify integrity → publisher → Kafka topic → Mongo consumer → prove replay → next entity

## Complementary pattern
Rocket U2 Data Replication = HA/DR (MVDB→MVDB); Outbox CDC = integration/streaming. "Complementary, not interchangeable."

## Unclear
- First entity chosen (doc suggests CUSTOMERS/ACCOUNTS as candidates; actual pick unknown)
- Whether this outbox approach or RDRS (page 1) is the final direction — CONTRADICTION with artifact 01
