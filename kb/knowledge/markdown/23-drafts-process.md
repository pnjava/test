---
id: 23-drafts-process
source: ITPR078770 PDF, pages 28 & 29 (Drafts process flow.vsd, updated 7-8-2014, Joe Trainor)
state: current (dated 2014 — verify still accurate)
confidence: verified (against 2014 doc)
tags: [DRAFTS, end of day, payments, Benton, claims]
---
# DRAFTS Process (End-of-Day Payment Run)
Nightly process started by Benton job #997663 (WKALL 4:00pm); must be scheduled by someone with DRAFTS security-list permissions. START.DRAFTS.AUTO (emails errors & aborts on problems) → passes NEXT.DATE, CHECK.CYCLES, START.TIME → START.DRAFTS (prompts: Trust, TOBEPAID, check cycle [SF only], defer — default 7:00pm; hard-coded to defer to Sat 3:00am when run on Friday) → CHANGE.DATE → DRAFTS started in background per TRUST. Files: SYSMGMT (key TOBEPAID.trust), START.DRAFTS (key=DATE; drafts only run on dates in this file), HISTORY/HIST2 (HSPAIDDATE, H2HELD.REASON), DRAFTS.EARLY flow (REQUEST.DRAFTS.EARLY → email group DRAFTS.EARLY). Other files: SUPRESS.AUDIT (prevents audit holds near group renewal), ABF.DATA (files to Echo/ABF), CKREG.OPTIONS (SF check register creation/delivery), DRAFTS.MONITOR.trust status reports in &HOLD& (view via VOC CHECK.DRAFTS). CLAIMMENU options DG/D/G entry points.
Runtime today: 5 days/week, 11–17 hrs starting midnight (per landscape facts).
