---
source_file: Meritain_IMI_Integration_Q&A.md
source: internal_documentation
date: '2026-03-19'
state: current
owner: TBD
category: process
confidence: inferred
tags:
- meritain
- imi
- faq
extraction_method: passthrough
extracted_on: '2026-07-12'
---

# Meritain IMI Integration - Technical Questions & Decisions

## Questions Being Addressed

### 1. **Will Meritain have Individual (IID) and Proxy IDs?**
- **Answer:** ✓ YES
- **Key Point:** Proxy ID is a mandatory field assigned to every individual record

### 2. **Will EPH get IMI events when Proxy ID changes?**
- **Current Status:** IPP currently reads EPH events
- **Answer:** DIFFERENT for Meritain
  - For Aetna (current): via EPH ✓
  - For Meritain (new): via **IMI** (NOT EPH)
  - This requires **NEW integration** rather than enhancement to existing EPH integration

### 3. **Where do we read IID and Proxy ID changes?**
- **Preference/Current Expectation:** EPH (for Aetna)
- **For Meritain:** IMI (mandatory - not optional)
- **Assumption:** Same process as Aetna but need to build IMI integration

### 4. **Will MeritainID be present in events?**
- **Answer:** ✓ Assume YES (one of several IDs in events)
- **Basis:** Similar to how Aetna has various IDs (retail, etc.)
- **Clarification:** "It will be one and same process, just like another BU of Aetna"
- **Storage:** IDs stored in same generic field where other IDs are stored
- **Note:** This is a deep-dive architectural question - detailed answer expected during design phase

### 5. **How to handle the data - with or without explicit Meritain signal?**
- **With Meritain signal present:** Logic is simpler
- **With ONLY IID (no Meritain indicator):** Logic is more complex as you need to determine business unit context
- **Recommendation:** Assume MeritainID presence in event (Option 1 - simpler)

### 6. **Proxy ID resolution approach**
- Use MeritainID to find Proxy ID
- Then determine what other IDs are attached to that Proxy ID
- **Important:** Members can belong to both Meritain AND Aetna

---

## Estimation Impact

### Key Factors for Estimate:

| Question | Impact on Estimate | Notes |
|----------|------------------|-------|
| IMI integration vs. EPH enhancement | **HIGH** | Need to build NEW IMI reading capability, not enhance existing |
| MeritainID presence in events | **MEDIUM** | Affects logic complexity; presence = simpler; absence = more complex |
| Who provides IID + Proxy ID changes | **HIGH** | Critical dependency; IMI vs EPH determines architecture |
| Cross-BU membership (Aetna + Meritain) | **MEDIUM** | Adds complexity to proxy ID resolution logic |

### Estimate Advice:
**Additional complexity identified that may impact timeline - YES, SIGNIFICANT IMPACT:**

**What adds complexity:**
- ✗ Need to build NEW IMI integration (not just enhance EPH) → **New code path, new testing**
- ✗ IMI may have different API/contract than EPH → **Integration discovery needed**
- ✗ Logic must handle dual membership scenarios → **Additional business logic**
- ✗ Architecture differs from current Aetna/EPH process → **Not a simple copy/paste**
- ✗ May need different transformation/mapping rules for Meritain IDs → **Additional mapping logic**

**Estimation Recommendations:**
1. **Do NOT estimate as:** Simple enhancement to existing EPH integration
2. **DO estimate as:** New subsystem/integration component with similar responsibility but different source
3. **Add buffer for:** IMI API learning curve, potential data structure differences, cross-business-unit logic
4. **Recommend:** Allocate separate effort stream for IMI vs. continuing EPH enhancements in parallel

---

## Assumed Approach (For Estimation)

```
1. Source: IMI (not EPH enhancement)
2. Read: Individual events with IID and MeritainID
3. Logic: MeritainID → find Proxy ID → resolve other attached IDs
4. Scope: Handle single business unit (Meritain) AND cross-BU cases
5. For now: NO separate retrieval of Aetna/CVS preference data
```

---

## Open Questions - Need Answer Before Detailed Design

- [ ] Exact IMI event structure and available fields
- [ ] Frequency/timing of IMI events (daily, real-time, batch?)
- [ ] IMI API/integration method (REST, file, message queue?)
- [ ] Which team will support IMI integration?
- [ ] Detailed mapping of MeritainID ↔ Proxy ID

---

## Assumptions Going Into Estimate

✓ Proxy ID is mandatory field  
✓ MeritainID will be present in events  
✓ Same generic field structure as Aetna IDs  
✓ No additional retrieval scope (Aetna/CVS data) needed  
✓ Need to build NEW IMI integration, not enhance EPH  
✓ Members can belong to multiple business units  

---

**Meeting Notes Source:** Ankita Singh and team discussion
**Date Captured:** March 19, 2026
