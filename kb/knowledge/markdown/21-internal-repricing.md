---
id: 21-internal-repricing
source: ITPR078770 PDF, page 26
state: current
confidence: verified
tags: [repricing, UniBASIC, claims]
---
# Internal Repricing Engine (within DG)
Claim intake layer (EDI 837, portal, fax) → member & provider lookup (eligibility, network) → internal repricing engine core (contract rate lookup, fee schedule mapping, bundling rules engine, modifier adjustments) → allowed amount calc (plan pays vs member pays) → payment & EOB generation (copay, deductible, etc.). Implemented as Re-Pricing UniBASIC Local Service against UniVerse MV DBMS (applyRePricingRules). Note: this is the "some repricing happens within DG box" from the landscape facts; 80–90% goes to BAMR instead.
