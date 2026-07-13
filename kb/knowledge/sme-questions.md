# SME Question List — Generated from PDF Extraction
Grouped by suggested owner. All are closed/confirmable questions by design.

## CDC / Data Platform (Rakesh, Ali, data strategy team)
1. Page 1 rates RDRS as best CDC option; pages 3/7 recommend Transactional Outbox. Which is the selected direction, or is RDRS→Replication DB the transport and Outbox the pattern for app-level events? (Top contradiction to resolve)
2. What is the Replication DB technology on Linux (page 1)? 
3. Which DG file/entity is chosen first for CDC (doc suggests CUSTOMERS/ACCOUNTS)?
4. Is the claims data model on page 4 the approved target schema for the Transactional Cache, or a draft?
5. Confluent Cloud vs GCP Managed Kafka — decided?
6. VPN vs Interconnect vs PSC for on-prem→GCP — decided?

## DG Operations (DG SMEs / Meritain Ops)
7. Are the 2014 DRAFTS process details (Benton job #997663, WKALL 4:00pm, per-trust runs) still accurate today?
8. Confirm queue counts: 7 claim queues still correct? Benton queue standardization design implemented or still pending?
9. What do MCMM, MWHCSS, CSC, IMI/Individualize, WorkIT, DMWiz stand for and do?
10. Non-prod DG move off the prod box — completed or still planned?
11. Phoenix→Las Vegas DC migration status?

## Integration (Bob's team)
12. BankTec bypass (24-hr SLA plan) — status?
13. MALF inventory: which extracts still run on it?
14. Sterling vs BizTalk current split: is 837/834 real-time still on BizTalk?
15. WebDE→MVIS replacement timeline and consumer migration order?

## Contact Center (Sunil, Ramesh)
16. Avaya→Five9 migration date?
17. Edify IVR replacement scope under Five9?

## North Star / Strategy (Muhammad, Tony)
18. Priority 5 in the North Star diagram — what is it? (unlabeled in extraction)
19. NextGen reuse for enrollment/correspondence/ID cards — confirmed with NextGen?
20. Superapp for Meritain — decision status?
21. Zelis for member services evaluation (P3) — status?

## Business Process (Lynn Fletcher, Terrie Nicks — per page 6)
22. Confirm: ~150 member letters (20–30 in SmartComm), ~250 claims letters (0 migrated)?
23. Is a welcome email sent to members today (flagged "unclear" on the slide)?
24. Confirm 60–80 green-screen applications/views figure for plan build.

## Data Model Cardinality (whoever owns the page-4 claims model — likely Rakesh/Ali)
25. Is MEMBER's primary key composite (MemberID + DepNo), or MemberID alone with DepNo as attribute?
26. Is SERVICE_LINE keyed on (ClaimNumber + LineNumber)? Mandatory 1-to-many from CLAIM?
27. GROUP_INFO: is DivisionCode part of the PK (composite) or an attribute? Should Group and Division be separate entities?
28. CLAIM->PROVIDER: mandatory or optional (can a claim exist without ProviderID, e.g. member-submitted)?
29. CLAIM_TRACKING and CLAIM_DOCUMENT: one-to-many per claim confirmed? Is TrackingEventID globally unique or per-claim?
