# Extraction Notes — OCR Corrections & Low-Confidence Readings

## Corrections applied silently during extraction (originals preserved here for audit)
| As extracted (raw) | Corrected to | Confidence |
|---|---|---|
| `Publinsh Plan Events` | Publish Plan Events | high |
| `Thisdiagram`, `presisted`, `Indempotent`, `basatards-CDC` | this diagram, persisted, Idempotent, (garbled — read as "application-level CDC") | high; `basatards` unrecoverable, meaning inferred from duplicate page |
| `?` between components (e.g. `MVDB ? Kafka ? Mongo`) | → (flow arrows) | high (consistent pattern) |
| `AIXMVDB? CDCLayer ? Replication DB? Kafka` | AIX MVDB → CDC Layer → Replication DB → Kafka | high |
| `Aeta Employeer Portal` | Aetna Employer Portal (AEP) | high |
| `External Partnors`, `backnone`, `Enollment`, `HIPPA`, `Proprietry`, `Descision`, `remittence`, `Managment`, `Experiance` | Partners, backbone, Enrollment, HIPAA, Proprietary, Decision, remittance, Management, Experience | high |
| `RTMEI (Rename)` | kept verbatim — appears to be a component pending rename | low — SME confirm |
| `MVX:Performance` | kept verbatim (Rocket MV product name) | medium |
| `OCRBATEN` (Benton diagram) | possibly OCRBATCH | low — flagged, kept raw |
| `BACKGROO,1,1`, `BACKCLAIM11 / BACKCLAIM 1 / BACKCLAIM1,n` | queue-name variants, exact spelling uncertain from raster | low — SME confirm queue names |

## Acronym collision watchlist (one-character-apart systems — DO NOT merge)
| Term | What it is | Evidence |
|---|---|---|
| **MCI** | Meritain Claims Interface — claims UI on Tomcat via LegaSuite (Meritain side) | page 14 |
| **MICS** | Member ID Card System — Aetna-side GKE app subscribing to plan/member events | pages 2/8/9 |
| **MCMM** | Unknown — appears in systems-of-engagement cluster near MeritainConnect | page 19; SME Q9 |
| **1mage** | Imaging product (digit one + "mage") — NOT a typo for "Image" | pages 19, 31 |
| **MEA** vs **MER** | MEA/ODS is Aetna member system of record; do not conflate with Meritain ODS (SQL Server) | pages 2/8/9 vs 19 |
| **CSC** vs **CSI Web** | CSC unknown (near DocStore/Claim Docs); CSI Web = CSR frontend | page 19; SME Q9 |

## Directionality caveats (spatial info not fully recoverable from raster)
- Page 19 landscape: edges recorded with direction ONLY where the label states it (e.g. "I:837 claims O:999"); unlabeled edges recorded as connections without confirmed direction.
- Page 2 canvases were manually segmented into regions before extraction: [current landscape]->doc 06, [North Star]->doc 02, [Transaction Cache]->doc 07, [CDC insets]->docs 01/03. Region assignment confidence: high.
- Page 4 ERD: crow's-foot cardinality symbols not recoverable from text layer. FK columns captured verbatim; cardinality/optionality/composite keys UNKNOWN — see SME questions 25–29.
