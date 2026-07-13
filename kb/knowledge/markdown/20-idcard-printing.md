---
id: 20-idcard-printing
source: ITPR078770 PDF, page 25
state: current
confidence: verified
tags: [ID cards, Zelis, Axway, eligibility]
---
# ID Card Printing (Current Architecture)
UniVerse MVDBMS (Eligibility) → extractIntoFile(Daily) → ID Card Printing Service → createFile(FixedLength) → text file → SFTP to Axway → SFTP to Zelis.
