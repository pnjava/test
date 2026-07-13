---
source_file: Estimate_Impact_Summary.md
source: internal_documentation
date: '2026-03-19'
state: current
owner: Narendra
category: decision
confidence: verified
tags:
- meritain
- imi
- estimation
- effort_multiplier
extraction_method: passthrough
extracted_on: '2026-07-12'
---

# Impact on Estimate - Executive Summary

## DIRECT ANSWER: YES, IT SIGNIFICANTLY IMPACTS THE ESTIMATE

---

## The Key Finding

**Meritain is NOT a simple "copy" of Aetna integration**

The critical difference discovered in the discussion:

| Aspect | Aetna (Current) | Meritain (New) | Impact |
|--------|-----------------|---|--------|
| **Source** | EPH (Enterprise Provider Hub) | IMI (Individual Member IMI) | DIFFERENT SYSTEM → NEW INTEGRATION |
| **Integration Type** | Enhancement | New Build | ~3-5x more effort |
| **Code Reuse** | Can reuse EPH patterns | Similar patterns but different API | ~40-60% reusable |
| **API Stability** | Known/Stable | Potentially Unknown | Risk factor |
| **Testing Scope** | Add test cases | Full new test suite | 2x effort |

---

## Effort Multiplier Analysis

### If treated as "simple Aetna copy":
❌ **INCORRECT APPROACH**
- Baseline: 1.0x effort
- Expected: Easy enhancement
- Reality: Will hit roadblocks when IMI API differs

### If treated as NEW integration (CORRECT):
✓ **CORRECT APPROACH**
- Baseline: ~3-5x effort compared to fixing a bug
- ~1.5-2x effort compared to similar-sized new feature
- Justification: 
  - New API to learn
  - New event structure
  - New business logic
  - New test scenarios

---

## Bottom Line Numbers

### Conservative Estimate Impact

| Component | Baseline (Similar Feature) | With IMI Complexity | Delta |
|-----------|--------------------------|-----------------|-------|
| API Integration | 1 week | 2 weeks | +1 week |
| Data Mapping | 1 week | 2 weeks | +1 week |
| Business Logic (IID→Proxy resolution) | 1.5 weeks | 3 weeks | +1.5 weeks |
| Cross-BU Deduplication | 1 week | 1.5 weeks | +0.5 weeks |
| Testing | 1.5 weeks | 2.5 weeks | +1 week |
| **TOTAL** | **6 weeks** | **11 weeks** | **+5 weeks (83% increase)** |

### Realistic Range with Unknowns
- **Optimistic:** 7-8 weeks (if IMI is well-documented)
- **Nominal:** 10-12 weeks (likely scenario)
- **Pessimistic:** 14-16 weeks (if IMI API issues discovered)

---

## Why It's NOT a Simple Add-On

### 5 Key Complexity Factors

**1. NEW EVENT SOURCE (IMI vs EPH)**
- EPH event structure ≠ IMI event structure
- Need separate consumer/parser code
- Different error handling patterns
- **Impact:** +40% integration code

**2. PROXY ID RESOLUTION LOGIC**
- Requires lookup (may be synchronous or async)
- May need caching strategy
- Performance SLA implications
- **Impact:** +30% business logic code

**3. CROSS-BUSINESS-UNIT SCENARIOS**
- Same individual in both Meritain AND Aetna
- May have different Proxy IDs in different systems
- Deduplication logic required
- **Impact:** +25% complexity

**4. DATA MODEL DIFFERENCES**
- Aetna fields ≠ Meritain fields
- May need transformation layer
- Field mapping may not be 1:1
- **Impact:** +20% mapping code

**5. TESTING MULTIPLIER**
- Test with Aetna data: ~40% of effort
- Test with Meritain data: ~40% of effort  
- Cross-BU test scenarios: ~20% of effort
- **Impact:** ~60% MORE testing than feature alone

---

## What WILL Get Easier

Some aspects ARE similar enough to reuse:
- ✓ General event processing framework
- ✓ Proxy ID concept (already exists for Aetna)
- ✓ Enrichment service patterns
- ✓ Error handling framework
- ✓ Logging/monitoring patterns

**Reuse value:** ~40-50% of code written can follow Aetna patterns

---

## Recommendation: How to Estimate This

### DON'T DO:
- ❌ Add 10-15% to Aetna integration estimate
- ❌ Treat as "quick add-on feature"
- ❌ Assume "similar means same effort"

### DO:
- ✓ **Create separate estimate for IMI integration**
- ✓ **Use 3-5x multiplier** on base "new API integration" effort
- ✓ **Include discovery phase:** 1-2 weeks for IMI API learning
- ✓ **Build in buffer:** 15-20% for unknowns (IMI may surprise you)
- ✓ **Plan parallel:** If possible, do IMI in parallel with other EPH enhancements

---

## The Uncertainty Premium

**Unknown factors that could add 2-4 weeks:**

1. **IMI API documentation quality** - If poor, +1-2 weeks
2. **Cross-BU member behavior** - If more complex than expected, +1 week
3. **Performance requirements** - If real-time only (vs batch), +1 week
4. **Integration dependencies** - If IMI requires other system changes, +1-2 weeks

**Recommendation:** Add 20% buffer to nominal estimate

---

## Resource Implications

### Team Composition Needed:
- **1 Backend Engineer** (full-time, 10-12 weeks)
- **1 QA Engineer** (2-3 weeks focused on IMI scenarios)
- **0.5 Data Engineer** (for data model analysis, 3-4 weeks)
- **0.25 Architect** (design reviews, 2-3 weeks)

### This is NOT a "side project" task
- Cannot be done in spare time during other work
- Needs dedicated focus and expertise
- Requires proper testing environment
- May need dedicated IMI API access/sandbox

---

## Questions Before Committing to Estimate

Get answers to these BEFORE finalizing estimate:

1. **Scope Confirmation**
   - [ ] Is Aetna+Meritain parallel desired, or sequential?
   - [ ] Must both go to production together, or independent timelines?

2. **Technology Readiness**
   - [ ] Is IMI API available now or TBD?
   - [ ] Do we have IMI API documentation?
   - [ ] Has anyone in our team integrated with IMI before?

3. **Business Rules**
   - [ ] Are cross-BU rules finalized or still being defined?
   - [ ] Can we get sample IMI events for analysis?

4. **Dependencies**
   - [ ] Does IMI integration depend on other platform changes?
   - [ ] Is the IMI system owned by our team or another team?

---

## Conclusion

### The bottom line for your discussion:
**"Building Meritain on IMI will take significantly longer than simply extending Aetna+EPH. Plan for 50-100% more effort. This is a different architecture, not an add-on."**

---

*Document prepared based on: Technical discussion with Ankita Singh and team*  
*Date: March 19, 2026*  
*Status: Ready for detailed estimation workshop*
