---
source_file: Meritain_IMI_Implementation_Paths.md
source: internal_documentation
date: '2026-03-19'
state: current
owner: TBD
category: process
confidence: inferred
tags:
- meritain
- imi
- implementation
extraction_method: passthrough
extracted_on: '2026-07-12'
---

# Meritain IMI Integration - Decision Tree & Implementation Paths

## High-Level Decision Path

```
START: Meritain Integration Requirements
│
├─ Question 1: Where do IID + Proxy ID changes originate?
│  ├─ ANSWER: IMI (for Meritain) vs EPH (for Aetna) ← THIS IS CONFIRMED
│  │
│  └─ Impact: This determines entire architecture
│     ├─ IF from EPH: Enhance existing EPH integration (simpler, ~20% effort)
│     └─ IF from IMI: Build NEW IMI integration (complex, ~100% effort) ← WE ARE HERE
│
├─ Question 2: Will MeritainID be present in events?
│  ├─ ANSWER: Assume YES (similar to Aetna BU IDs)
│  │
│  └─ Impact: Affects downstream logic complexity
│     ├─ IF YES (assumption): Direct business unit identification (simpler logic)
│     └─ IF NO (risk scenario): Need fuzzy matching/context inference (complex logic)
│
├─ Question 3: Can members belong to multiple business units simultaneously?
│  ├─ ANSWER: YES (members can be in both Meritain AND Aetna)
│  │
│  └─ Impact: Proxy ID resolution algorithm
│     └─ Need cross-referencing logic between Meritain and Aetna proxy IDs
│
└─ Question 4: How should we retrieve MeritainID to Proxy ID mapping?
   ├─ Direct field in event (preferred)
   ├─ Lookup table/API call (adds latency)
   └─ Cache-based resolution (adds complexity)
```

---

## Implementation Scenarios

### Scenario A: Simple Case (Best Case)
**Conditions:**
- MeritainID present in IMI event ✓
- Events contain Proxy ID directly ✓
- No cross-BU logic needed
- Separate IMI consumer (no mixing with EPH)

**Effort:** Medium  
**Risk:** Low  
**Code Pattern:** Simple event mapper → Single-BU processor

---

### Scenario B: Nominal Case (Most Likely)
**Conditions:**
- MeritainID present in IMI event ✓
- Must resolve Proxy ID via lookup ✓
- Cross-BU logic needed (members in both BUs) ✓
- Need deduplication logic

**Effort:** High  
**Risk:** Medium  
**Code Pattern:** Event mapper → Enricher (add Proxy ID) → Deduplicator → Multi-BU processor

---

### Scenario C: Complex Case (Risk Scenario)
**Conditions:**
- MeritainID NOT clearly present in events ✗
- Proxy ID requires complex lookup ✗
- Cross-BU membership common ✗
- Different event schema than Aetna

**Effort:** Very High  
**Risk:** High  
**Code Pattern:** Complex mapper (with BU inference) → Multiple resolvers → Complex deduplicator → Multi-BU processor

---

## Architecture Options

### Option 1: Parallel Consumers (Recommended)
```
IMI Events Stream
        ↓
    [IMI Consumer]  ← NEW CODE
        ↓
    [Event Processor - Meritain]
        ↓
    [Enrichment Service]
        ↓
    [Proxy ID Resolver]
        ↓
    [Central Event Handler]
        │
        ├─→ [Aetna Processor]
        ├─→ [Meritain Processor]
        └─→ [Cross-BU Deduplicator]
```
**Pros:** Clean separation, independent scaling, easier testing  
**Cons:** Some code duplication, need coordination at center  
**Effort:** ~40% more code

---

### Option 2: Unified Consumer with Router
```
EPH Events Stream
        ↓
    [EPH Consumer] (existing)
        ↓
    [Event Router by Source]
        ├─→ [Aetna Path]
        │
        IMI Events Stream
            ↓
        [IMI Consumer] ← NEW
        ↓
        └─→ [Meritain Path]
        ↓
    [Unified Event Handler]
        ↓
    [Central Processing Logic]
```
**Pros:** Single event handler, reusable logic  
**Cons:** Complex router, tight coupling  
**Effort:** ~60% more code

---

### Option 3: Event Transformation Layer (Most Flexible)
```
EPH Events          IMI Events
    ↓                   ↓
[EPH Consumer]  [IMI Consumer]
    ↓                   ↓
[EPH Transformer]  [IMI Transformer]
    ↓                   ↓
    └────→ [Canonical Event Format]
            ↓
        [Single Handler]
            ↓
        [Processor]
            ↓
        [Enrichment → Resolution → Dedup]
```
**Pros:** Maximum reusability, protects core logic from source changes  
**Cons:** Extra transformation layer, more complex testing  
**Effort:** ~50% more code

---

## Team Responsibilities (NEEDED FOR ESTIMATION)

### Current State:
- ✓ EPH Integration: Owned by [TEAM?]
- ✗ IMI Integration: Needs ownership assignment

### Questions to Answer:
- [ ] **Who owns IMI integration work?** (Same team as EPH? New team?)
- [ ] **Who has IMI API expertise?** (May need external training)
- [ ] **Who will support IMI in production?** (Long-term ownership)
- [ ] **Are there existing IMI consumers elsewhere in the platform?** (Code reuse opportunity)

---

## Pre-Design Validation Checklist

Before detailed design, confirm:

- [ ] **IMI Event Structure**: Get sample IMI event payload with all event types
- [ ] **Proxy ID Behavior**: Understand Meritain Proxy ID assignment rules
- [ ] **Cross-BU Rules**: Document exact member-proxy ID combinations (1:1? 1:N? N:N?)
- [ ] **Event Frequency**: Real-time? Batch? What's the expected volume?
- [ ] **Consistency Model**: Eventual consistency OK? Need strong consistency?
- [ ] **Performance SLA**: What's the acceptable latency from event to processing?
- [ ] **API Availability**: Is IMI API always available or batch-only?
- [ ] **Error Handling**: How to handle event parsing errors, lookup failures, etc.?

---

## Effort Estimation Ranges

| Scenario | Code Size | Test Size | Integration | **Total Estimate** |
|----------|-----------|-----------|-------------|-------------------|
| Scenario A (Simple) | 500-1000 LOC | 200-400 LOC | 1-2 weeks | **2-3 weeks** |
| Scenario B (Nominal) | 1500-2500 LOC | 600-1000 LOC | 2-4 weeks | **4-6 weeks** |
| Scenario C (Complex) | 2500-4000 LOC | 1000-1500 LOC | 4-8 weeks | **6-10 weeks** |

**Note:** Estimates DO NOT include detailed design phase or organizational overhead

---

## Risk Flags for Management

🚩 **HIGH RISK if:**
- IMI API not yet documented or unstable
- Cross-business-unit logic not clearly defined
- No existing IMI consumers (no reference implementations)
- Tight deadline expecting Scenario A but likely Scenario B

🟡 **MEDIUM RISK if:**
- IMI team not yet assigned ownership
- Event schema may change during implementation
- Performance SLAs not defined

🟢 **LOW RISK if:**
- Clear IMI API contract in place
- Similar systems already consuming IMI elsewhere
- Flexible timeline for iterative delivery
