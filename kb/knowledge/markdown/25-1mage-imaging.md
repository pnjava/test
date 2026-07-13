---
id: 25-1mage-imaging
source: ITPR078770 PDF, page 31
state: current
confidence: verified
tags: [1mage, imaging, Citrix, document management]
---
# 1mage Imaging System
Linux server hosting 1mage + 1mage APIs; DG (Unix server, Data General) connects via 1mage Connect; user desktop: terminal emulator → DG screens/processes; SwiftView + WinClient (via Citrix server with Telnet Connect on Windows); browser + 1Access → VIA Web tool on 1mage server. Layered view: user desktop (web app, browser) → middleware (API gateway, authentication service, PIL) → data (screens/processes, image service). Used for claim document image storage/retrieval (get Image for CSC Claim Docs per landscape diagram); receives archive data from EBI/GCP buckets.
