---
id: 22-benton-queues
source: ITPR078770 PDF, page 27
state: current
confidence: verified
tags: [Benton, queues, background processing, claims]
---
# Benton Queues (Background Processing)
Benton queues exist for general background processing, claims processing, PPO processing and special processes. New queues must be set up in Benton and added to several places in DG for tracking/balancing. Claim processing queues don't currently follow the standard setup — a design doc exists to standardize queue setup and improve balancing for claim queues.
Components on Rocket UniVerse host: SYSMGMT (BACKCLAIM/THRESHOLD), BENTON_BACKGROUND config, BENTON_EVENT, admin screens (BENTON BACKGROUNDDS SAV/INO), BACKGROUND.THRESTOP (ensures active queues run, max MVLINES per type), background queues (BACKGROUND[i], BACKCLAIM11, BACKSPEC1), BP.BALANCE.BACKGROUND, BP.MONITOR.BACKGROUND, EDIBATCH, OCRBATEN. Claim-aware balancing logic: count active queues by type, read thresholds + BACKCLAIM MIN CLAIMS TO MOVE, scan queued jobs, accumulate claims until > MIN or move all remaining.
