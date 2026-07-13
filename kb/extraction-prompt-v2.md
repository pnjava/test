# Vision Extraction Prompt v2 (adds region segmentation + corruption logging)
Use this locked template for every image/PDF-page extraction.

---
You are extracting enterprise architecture knowledge from an image for a RAG knowledge base. Follow these steps IN ORDER:

STEP 0 — REGION SEGMENTATION (mandatory for any page with more than one diagram)
Before extracting anything, divide the page into visual regions. A region = one self-contained diagram, table, note cluster, or screenshot. For each region assign:
- region_id (R1, R2, ...)
- position (e.g. top-left, center)
- type: architecture_diagram | data_model | process_flow | table | text_notes | screenshot | template/sample | legend
- lifecycle: CURRENT | TARGET | PROPOSED | HISTORICAL | DEPRECATED | UNKNOWN (use titles, legends, colors, and notes like "Future", "Sunset", "North Star", "Draft" as evidence — state your evidence)
NEVER connect components across regions. Cross-region links are proposed only in the stitching phase, as hypotheses.

STEP 1 — PER-REGION EXTRACTION
For each region produce: Components / Connections / Labels (VERBATIM) / Inferred / Unclear.
Connection rules: record direction ONLY if an arrowhead or directional label (I:/O:, ->, "sends", "reads") is visible; otherwise record as UNDIRECTED. Record the transport if labeled (SFTP, API, EDI, USPS...).

STEP 2 — EXCLUSION FILTER
Mark as EXCLUDED (do not emit as knowledge): template/sample shapes (e.g. Lucidchart "Entity/Field" placeholders), tool tutorials, watermarks, empty legends. Emit one line stating what was excluded and why.

STEP 3 — CORRUPTION LOG
List every OCR artifact you corrected (raw -> corrected -> confidence high/medium/low). If a token is unrecoverable, keep it verbatim and mark UNRECOVERABLE. Never silently guess acronyms: if a term is 1-2 characters from a known system name (MCI/MICS/MCMM, 1mage/Image), flag it in the log instead of normalizing.

STEP 4 — SCREENSHOT HANDLING
If the region is a screenshot (email, Teams, slide photo), tag: source_type: SME_meeting_evidence, authority: informal, approval_status: unverified, contains_personal_information: possible. List person names found so they can be masked or retained by policy — do not weave them into architecture facts.

STEP 5 — OUTPUT
One Markdown doc per region (or per artifact if regions belong to one artifact), with YAML frontmatter: id, source (file+page+region), state (lifecycle), confidence, tags. Do not guess to fill gaps — gaps go under Unclear.
