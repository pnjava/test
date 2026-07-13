---
id: 11-webde
source: ITPR078770 PDF, page 13
state: current
confidence: verified
tags: [WebDE, RedBack, DG, service layer, Rocket]
---
# WebDE — DG Service Layer

## What it is
Service layer running ON the DG box, written in same technology (Universe). COTS by Rocket (2nd version). Exposes Universe files as objects — only 2 properties and 1 method. To be replaced with MultiValueIS (MVIS) — Rocket Universe.

## Components (verbatim from Rocket docs excerpt)
- RedBack Object Server: manages access to RedBack applications, dynamic runtime interfaces, maintains repository of definitions/code
- Java Scheduler (Connection Manager): manages data transfer between RedBack Object Server and web server; load balancing; allocates U2 licenses as webshares
- Admin API Server; RedBeans (Java API) and RedPages.NET (.NET API); Web Designer (Eclipse-based RBO design tool); U2 Web Designer desktop config tool

## Consumers of WebDE
- Meritain APIC: Accumulators/Cost Calc; ID Cards
- EDI27X: 270/271 & 276/277
- Claim System Connect: small .Net app serializing XML for .Net (from Meritain portals); QuickClicks (web page search e.g. plan docs & certs)
- Customer Service Interface Web (CSI Web): front end for DG for customer services — data lookup and call logging
- IVRS (Edify IVR)

## Unclear
- MVIS replacement timeline and scope
