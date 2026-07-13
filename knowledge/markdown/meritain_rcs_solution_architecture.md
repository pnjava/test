---
source_file: Meritain_RCS_Solution_Architecture.md
source: internal_documentation
date: '2026-03-26'
state: current
owner: Narendra
category: architecture
confidence: verified
tags:
- meritain
- rcs
- architecture
- day1
- day2
- ipp
- datavision
extraction_method: passthrough
extracted_on: '2026-07-12'
---

# Meritain RCS Implementation — Detailed Solution Architecture

> **Status:** DRAFT — Requires validation with Chris Byrd, IPP Team, DG Team, MaCE Team  
> **Author:** Narendra (Solution Architect)  
> **Reviewed by:** Muhammad Mudassar (Lead Architect)  
> **Date:** March 26, 2026  
> **Version:** 0.1  
> **Source:** Conceptual design from Meritain_RCS_Roadmap_final v2.1.pptx (Slide 11)

---

## 1. Executive Summary

This document transforms Muhammad's **conceptual design** into a **detailed solution architecture** for the Meritain RCS (Rich Communication Services) Member Communications platform. It covers Day 1 (tactical, DataVision-based) and Day 2 (strategic, IPP-based) implementations.

**Objective:** Enable Meritain Health to send RCS/SMS/Email welcome and onboarding messages to newly enrolled members, with proper consent management and TCPA compliance.

---

## 2. Architecture Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MERITAIN ECOSYSTEM                               │
│                                                                         │
│  ┌──────────┐  ┌──────────────┐   ┌──────────────────────────────────┐ │
│  │ CSI Web  │  │  Meritain    │   │  Plan Sponsor Enrollment Files   │ │
│  │ (CSR App)│  │  Connect     │   │  (with Prior Express Consent)    │ │
│  └────┬─────┘  └──────┬───────┘   └──────────────┬───────────────────┘ │
│       │               │                          │                     │
│       ▼               ▼                          ▼                     │
│  ┌─────────────────────────┐    ┌──────────────────────────────────┐   │
│  │  Digital Preference     │    │  Enrollment Process              │   │
│  │  APIs                   │───▶│  (Group Config for Plan Sponsor  │   │
│  │  (Day 1: Local SQL)     │    │   collected preferences)         │   │
│  │  (Day 2: IPP APIs)      │    └──────────────┬───────────────────┘   │
│  └─────────┬───────────────┘                   │                       │
│            │                                    │                       │
│            ▼                                    ▼                       │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────┐                   │
│  │ Digital Pref │  │ IPP      │  │ DG             │                   │
│  │ Data (SQL)   │  │ (BoR)    │  │ Preferences    │                   │
│  └──────┬───────┘  └────┬─────┘  └───────┬────────┘                   │
│         │               │                │                             │
│         └───────────────┼────────────────┘                             │
│                         ▼                                              │
│  ┌─────────────────────────────────────────────────┐                   │
│  │  DataVision / EDP (Preference Source of Truth)   │                   │
│  │  [Day 1: Active]  [Day 2: Sunset by IPP]        │                   │
│  └──────────────────────┬──────────────────────────┘                   │
│                         │ Email, Phone, Preference                     │
│                         ▼                                              │
│  ┌─────────────────────────────────────┐     ┌───────────────────────┐ │
│  │ Meritain Welcome Message Service    │────▶│  MaCE Messaging       │ │
│  │ (Trigger & Orchestration)           │     │  Platform             │ │
│  └─────────────────────────────────────┘     └───────┬───────────────┘ │
│                                                      │                 │
└──────────────────────────────────────────────────────┼─────────────────┘
                                                       │
                                              ┌────────┼────────┐
                                              ▼        ▼        ▼
                                          ┌──────┐ ┌──────┐ ┌──────────┐
                                          │Infobip│ │ CSG  │ │Salesforce│
                                          │(RCS)  │ │(SMS) │ │(Email)   │
                                          └──────┘ └──────┘ └──────────┘
```

---

## 3. Component Inventory

### 3.1 Engagement & Digital Layer

| Component | Owner | Technology | Hosting | Status |
|-----------|-------|-----------|---------|--------|
| **CSI Web** | Chris Byrd | ASP.NET / SQL Server | On-Prem (TBD) | Existing — needs enhancement |
| **Meritain Connect** | TBD | Web Portal | On-Prem (TBD) | Existing — needs enhancement |

**Day 1 Changes Required:**
- Add UI fields to capture: Cell Phone Number, SMS Consent (Y/N), RCS Preference, Email Preference
- Store preferences in local SQL Server database (Chris Byrd's existing DB)
- Add consent timestamp and consent source tracking

**Day 2 Changes Required:**
- Replace local DB calls with IPP API calls for preference CRUD
- Remove local preference storage (sunset local SQL DB)

**Open Questions:**
- [ ] Q1: What is the current tech stack for CSI Web? (ASP.NET? Node.js? Java?)
- [ ] Q2: Is the local SQL Server DB on the same server or separate?
- [ ] Q3: Is Chris Byrd making direct DB calls or using an API/service layer?
- [ ] Q4: What authentication does CSI Web use? (AD? OAuth? SAML?)

---

### 3.2 Plan Sponsor Enrollment Files

| Aspect | Detail |
|--------|--------|
| **File Format** | TBD (CSV? EDI 834? Fixed-width?) |
| **Transport** | TBD (SFTP? Axway? Direct upload?) |
| **Frequency** | Per enrollment cycle (daily? weekly?) |
| **Key Fields** | MemberID, CellPhone, ConsentFlag, PlanSponsorID, Email |

**Day 1 Assumption:**
- If enrollment file contains a phone number → assume prior express consent is granted
- Store in DG Preferences
- No explicit consent capture required for Day 1 (transactional messages = low TCPA risk)

**Day 2 Requirement:**
- Enrollment files must include explicit consent flag
- Store consent in IPP via IPP APIs
- Track consent source, date, and type (transactional vs marketing)

**Open Questions:**
- [ ] Q5: What is the exact file format of enrollment files?
- [ ] Q6: Who processes these files today? (Which team? What system?)
- [ ] Q7: Where do enrollment files land? (File share? SFTP? S3?)
- [ ] Q8: Is there an existing enrollment processing pipeline we need to modify?

---

### 3.3 Digital Preference APIs (Day 1 — Tactical)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Tactical support for phone number and consent storage |
| **Hosting** | On-Prem SQL Server (Chris Byrd's existing infrastructure) |
| **Technology** | TBD — likely REST API or direct DB calls |
| **Database** | Local SQL Server (preference tables) |

**API Endpoints Needed (Day 1):**

| # | Method | Endpoint (Proposed) | Description |
|---|--------|---------------------|-------------|
| 1 | GET | `/api/v1/preferences/{memberId}` | Retrieve member preferences |
| 2 | PUT | `/api/v1/preferences/{memberId}` | Update member preferences |
| 3 | POST | `/api/v1/preferences/{memberId}/consent` | Record consent action |
| 4 | GET | `/api/v1/preferences/{memberId}/consent-history` | Consent audit trail |

**Data Model (Day 1 Local DB):**

```sql
-- Proposed schema for local preference storage
CREATE TABLE MemberPreferences (
    PreferenceID        INT IDENTITY(1,1) PRIMARY KEY,
    MemberID            VARCHAR(20) NOT NULL,
    PlanSponsorID       VARCHAR(20),
    CellPhone           VARCHAR(15),
    Email               VARCHAR(255),
    SMSConsentFlag      BIT DEFAULT 0,
    RCSConsentFlag      BIT DEFAULT 0,
    EmailConsentFlag    BIT DEFAULT 0,
    EOBPreference       VARCHAR(10),  -- 'EMAIL', 'PAPER', 'BOTH'
    ConsentSource       VARCHAR(50),  -- 'ENROLLMENT_FILE', 'CSI_WEB', 'MERITAIN_CONNECT'
    ConsentTimestamp     DATETIME2,
    ConsentType         VARCHAR(20),  -- 'TRANSACTIONAL', 'MARKETING'
    CreatedDate         DATETIME2 DEFAULT GETDATE(),
    ModifiedDate        DATETIME2 DEFAULT GETDATE(),
    IsActive            BIT DEFAULT 1
);

CREATE TABLE ConsentAuditLog (
    AuditID             INT IDENTITY(1,1) PRIMARY KEY,
    MemberID            VARCHAR(20) NOT NULL,
    Action              VARCHAR(20),  -- 'OPT_IN', 'OPT_OUT', 'UPDATE'
    Channel             VARCHAR(10),  -- 'SMS', 'RCS', 'EMAIL'
    OldValue            VARCHAR(50),
    NewValue            VARCHAR(50),
    Source              VARCHAR(50),
    Timestamp           DATETIME2 DEFAULT GETDATE(),
    UserAgent           VARCHAR(255)
);
```

---

### 3.4 IPP (Intelligent Preference Platform)

| Aspect | Detail |
|--------|--------|
| **Full Name** | Intelligent Preference Platform |
| **Owner** | Enterprise (CVS/Aetna) |
| **Role** | Book of Record (BoR) for all member preferences and consent |
| **Hosting** | Cloud (GCP or Azure — TBD) |
| **Integration** | REST APIs (assumed) |

**IPP Capabilities (from conceptual design):**
1. Store member preferences (channel, format, consent)
2. Store prior express consent with audit trail
3. Provide preference lookup APIs for MaCE
4. Handle unsubscribe/opt-out disposition
5. RND (Reassigned Number Database) process
6. Federal DNC + Enterprise DNC checks

**IPP API Endpoints (Expected — Need Swagger from IPP Team):**

| # | Method | Endpoint (Expected) | Purpose | Day |
|---|--------|---------------------|---------|-----|
| 1 | GET | `/ipp/v1/members/{id}/preferences` | Get member preferences | Day 2 |
| 2 | PUT | `/ipp/v1/members/{id}/preferences` | Update preferences | Day 2 |
| 3 | POST | `/ipp/v1/members/{id}/consent` | Record consent | Day 2 |
| 4 | GET | `/ipp/v1/members/{id}/consent` | Get consent status | Day 2 |
| 5 | POST | `/ipp/v1/members/{id}/unsubscribe` | Process opt-out | Day 2 |
| 6 | GET | `/ipp/v1/dnc/check/{phoneNumber}` | DNC registry check | Day 2 |
| 7 | GET | `/ipp/v1/rnd/check/{phoneNumber}` | Reassigned number check | Day 2 |

**Authentication (Expected):**
- OAuth 2.0 Client Credentials flow
- Token API endpoint for service-to-service auth
- mTLS for API gateway connectivity

**Open Questions:**
- [ ] Q9: Where is IPP hosted? (GCP? Azure? On-Prem?)
- [ ] Q10: What is the IPP API Swagger/OpenAPI spec?
- [ ] Q11: What authentication does IPP require? (OAuth2? API Key? mTLS?)
- [ ] Q12: What is the IPP team's contact for integration support?
- [ ] Q13: Is IPP available now, or still in development?
- [ ] Q14: What is IPP's SLA for API response time?

---

### 3.5 DG (Data Governance / Digital Gateway) Preferences

| Aspect | Detail |
|--------|--------|
| **Purpose** | Current storage for enrollment-based preference data (primarily EOB) |
| **Owner** | Bill Cadman / DG Team |
| **Technology** | TBD |
| **Current Data** | EOB delivery preferences (email/paper) |

**Day 1:**
- Continue storing enrollment-based preferences in DG
- Add cell phone and consent fields to DG preference store
- DG feeds into DataVision/EDP

**Day 2:**
- Enrollment process writes to IPP APIs instead of DG
- DG preferences sunset for communication preferences (may retain for EOB)

**Open Questions:**
- [ ] Q15: What is DG's tech stack? (SQL Server? Oracle? API-based?)
- [ ] Q16: How does the enrollment process currently write to DG? (API? File? Direct DB?)
- [ ] Q17: Can DG accept new fields (cell phone, SMS consent) without major changes?
- [ ] Q18: What is DG's relationship with DataVision/EDP?

---

### 3.6 DataVision / EDP (Preference Source of Truth — Day 1)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Data warehouse — current source of truth for preferences |
| **Role Day 1** | Primary preference source for generating welcome messages |
| **Role Day 2** | Sunset — replaced by IPP as source of truth |
| **Outputs** | Email, Phone, Preference → feeds Meritain Welcome Message Service |

**Open Questions:**
- [ ] Q19: How does DataVision expose data? (Views? APIs? Direct SQL? File export?)
- [ ] Q20: What is the refresh frequency? (Real-time? Nightly batch?)
- [ ] Q21: What database technology? (SQL Server? Teradata? Snowflake?)

---

### 3.7 Meritain Welcome Message Service

| Aspect | Detail |
|--------|--------|
| **Purpose** | Orchestrate welcome/onboarding messages for new members |
| **Hosting** | TBD (On-Prem? Cloud?) |
| **Technology** | TBD (needs to be built or configured) |
| **Trigger** | New member enrollment detected in DataVision (Day 1) / IPP (Day 2) |

**Functional Requirements:**
1. Detect newly enrolled members with valid phone + consent
2. Determine message type (Welcome, Onboarding, EOB notification)
3. Build message payload (member name, plan info, links)
4. Submit to MaCE messaging platform
5. Track delivery status and opt-out responses

**Day 1 Data Flow:**
```
DataVision/EDP → [Query: new members with phone + consent]
    → Meritain Welcome Message Service
        → Build message payload
        → POST to MaCE API
            → MaCE routes to Infobip (RCS) / CSG (SMS) / Salesforce (Email)
```

**Day 2 Data Flow:**
```
IPP → [Event: new member preference stored]
    → Meritain Welcome Message Service
        → Call IPP API for full preferences
        → Call IPP API for DNC check
        → Build message payload
        → POST to MaCE API
            → MaCE routes to Infobip (RCS) / CSG (SMS) / Salesforce (Email)
```

**Open Questions:**
- [ ] Q22: Does this service exist today or needs to be built from scratch?
- [ ] Q23: Where should it be hosted? (Same infra as CSI Web? Separate service?)
- [ ] Q24: What programming language/framework? (C#/.NET? Java? Python?)
- [ ] Q25: How will it detect new enrollments? (Polling? Event-driven? File-based?)

---

### 3.8 MaCE Messaging Platform

| Aspect | Detail |
|--------|--------|
| **Full Name** | MaCE (Messaging and Communications Engine) |
| **Owner** | Enterprise (CVS/Aetna) |
| **Purpose** | Multi-channel message orchestration and delivery |
| **Channels** | RCS (Infobip), SMS (CSG), Email (Salesforce) |
| **Connectivity** | Already has IPP connectivity (Day 2 ready) |

**Integration with Meritain:**

| Channel | Provider | Protocol | Day |
|---------|----------|----------|-----|
| RCS | Infobip | API (REST) | Day 1 |
| SMS | CSG | API (REST) | Day 1 |
| Email | Salesforce | API (REST/SOAP) | Day 1 |

**MaCE API (Expected):**

| # | Method | Endpoint (Expected) | Purpose |
|---|--------|---------------------|---------|
| 1 | POST | `/mace/v1/messages/send` | Submit message for delivery |
| 2 | GET | `/mace/v1/messages/{id}/status` | Check delivery status |
| 3 | POST | `/mace/v1/messages/batch` | Batch message submission |
| 4 | GET | `/mace/v1/templates` | List available message templates |

**Opt-Out Flow (MaCE → IPP):**
```
Member replies STOP → MaCE receives opt-out
    → MaCE calls IPP unsubscribe API
    → IPP updates preference (consent revoked)
    → Stop/Unsubscribe disposition flows back to DataVision (Day 1)
```

**Open Questions:**
- [ ] Q26: What is MaCE's API spec / Swagger?
- [ ] Q27: Does MaCE require message templates to be pre-registered?
- [ ] Q28: How does MaCE handle opt-out responses from each channel?
- [ ] Q29: What is MaCE's SLA for message delivery?
- [ ] Q30: Does MaCE already have Meritain as a registered client?

---

## 4. Data Flow Diagrams

### 4.1 Day 1 Flow (Red Routes — Tactical)

```
[Plan Sponsor] ──enrollment file──▶ [Enrollment Process]
                                          │
                                    (phone + assumed consent)
                                          │
                                          ▼
                                     [DG Preferences]
                                          │
                     ┌────────────────────┤
                     ▼                    ▼
              [Local SQL DB]     [DataVision/EDP]
              (Chris Byrd)       (Source of Truth)
                     │                    │
                     │              (Email, Phone,
      [CSI Web] ────┘               Preference)
      [Meritain Connect]                 │
         (read/write local)              ▼
                               [Meritain Welcome
                                Message Service]
                                         │
                                    (POST message)
                                         │
                                         ▼
                                      [MaCE]
                                    ┌────┼────┐
                                    ▼    ▼    ▼
                                 Infobip CSG  SF
                                 (RCS) (SMS) (Email)
                                    │
                                    ▼
                              (opt-out comes back)
                                    │
                                    ▼
                            [Tactical opt-out
                             handling in MaCE]
```

### 4.2 Day 2 Flow (Brown Routes — Strategic, after IPP readiness)

```
[Plan Sponsor] ──enrollment file──▶ [Enrollment Process]
                                          │
                                    (explicit consent)
                                          │
                                          ▼
                                     [IPP APIs] ◀──── [CSI Web]
                                         │        ◀──── [Meritain Connect]
                                    (BoR for all
                                     preferences)       
                                         │
                             ┌───────────┼───────────┐
                             │           │           │
                             ▼           ▼           ▼
                        [Consent]  [Preferences] [DNC Check]
                        [Store]    [Store]       [RND Check]
                             │           │
                             ▼           ▼
                      [MaCE] ◀── IPP Preferences Lookup
                        │
                   ┌────┼────┐
                   ▼    ▼    ▼
                Infobip CSG  SF
                (RCS) (SMS) (Email)
                   │
                   ▼
             (opt-out → MaCE → IPP unsubscribe API)
```

---

## 5. Infrastructure & Connectivity (TBD — Needs Validation)

### 5.1 Hosting Topology (Assumptions)

| Component | Hosting | Cloud/On-Prem | VPC/Network |
|-----------|---------|---------------|-------------|
| CSI Web | On-Prem | On-Prem | Corporate LAN |
| Meritain Connect | On-Prem | On-Prem | Corporate LAN |
| Local Preference DB | On-Prem (SQL Server) | On-Prem | Same as CSI Web |
| DG | TBD | TBD | TBD |
| DataVision/EDP | On-Prem (likely) | On-Prem | Data Center |
| IPP | Cloud (GCP or Azure) | Cloud | Enterprise VPC |
| MaCE | Cloud (GCP or Azure) | Cloud | Enterprise VPC |
| Infobip | External SaaS | Cloud | Internet |
| CSG | External SaaS | Cloud | Internet |
| Salesforce | External SaaS | Cloud | Internet |

### 5.2 Connectivity Requirements

| From | To | Protocol | Port | Auth | Network Path |
|------|----|----------|------|------|-------------|
| CSI Web | Local Pref DB | SQL/TDS | 1433 | Windows Auth/SQL Auth | LAN |
| CSI Web | IPP APIs (Day 2) | HTTPS | 443 | OAuth 2.0 | On-Prem → Secure Hub → Cloud VPC |
| Meritain Connect | IPP APIs (Day 2) | HTTPS | 443 | OAuth 2.0 | On-Prem → Secure Hub → Cloud VPC |
| Enrollment Process | DG | TBD | TBD | TBD | TBD |
| Enrollment Process | IPP APIs (Day 2) | HTTPS | 443 | OAuth 2.0 | TBD |
| DataVision/EDP | Msg Service | TBD | TBD | TBD | Data Center |
| Msg Service | MaCE | HTTPS | 443 | OAuth 2.0 / API Key | On-Prem → Cloud VPC |
| MaCE | IPP | HTTPS | 443 | Internal (same VPC) | Cloud internal |
| MaCE | Infobip | HTTPS | 443 | API Key | Cloud → Internet |
| MaCE | CSG | HTTPS | 443 | API Key | Cloud → Internet |
| MaCE | Salesforce | HTTPS | 443 | OAuth 2.0 | Cloud → Internet |

### 5.3 Security & Authentication

| Integration | Auth Method | Token Endpoint | Certificate |
|-------------|-----------|----------------|-------------|
| On-Prem → IPP | OAuth 2.0 Client Credentials | TBD | mTLS (TBD) |
| On-Prem → MaCE | OAuth 2.0 / API Key | TBD | mTLS (TBD) |
| MaCE → IPP | Internal service auth | Internal | Internal cert |
| MaCE → Infobip | API Key in header | N/A | TLS 1.2+ |
| MaCE → CSG | API Key / OAuth | TBD | TLS 1.2+ |

### 5.4 Firewall Rules Needed

| Rule | Source | Destination | Port | Protocol | Direction |
|------|--------|-------------|------|----------|-----------|
| FR-01 | CSI Web server | IPP API Gateway | 443 | HTTPS | Outbound |
| FR-02 | Meritain Connect server | IPP API Gateway | 443 | HTTPS | Outbound |
| FR-03 | Message Service server | MaCE API Gateway | 443 | HTTPS | Outbound |
| FR-04 | Enrollment server | IPP API Gateway | 443 | HTTPS | Outbound |
| FR-05 | MaCE | Infobip endpoints | 443 | HTTPS | Outbound |
| FR-06 | MaCE | CSG endpoints | 443 | HTTPS | Outbound |

---

## 6. TCPA Compliance Architecture

### 6.1 Day 1 (Tactical — Low Risk)

| Aspect | Approach |
|--------|----------|
| **Consent** | Implied from enrollment file (phone number present = assumed consent) |
| **Message Type** | Transactional only (welcome/onboarding = informational) |
| **DNC Check** | Not required (transactional exempt) |
| **Opt-Out** | Tactical handling via MaCE (STOP keyword) |
| **Audit** | ConsentAuditLog table in local DB |
| **Risk Level** | LOW (transactional messages to enrolled members) |

### 6.2 Day 2 (Full Compliance — Required for Marketing)

| Aspect | Approach |
|--------|----------|
| **Consent** | Explicit prior express consent captured and stored in IPP |
| **Message Type** | Transactional + Marketing |
| **Federal DNC** | IPP checks Federal DNC Registry before sending |
| **Enterprise DNC (eDNC)** | IPP checks internal enterprise DNC list |
| **RND** | IPP checks Reassigned Number Database |
| **Opt-Out** | Full unsubscribe via IPP API (MaCE → IPP) |
| **Audit** | Full audit trail in IPP with consent source, date, type |
| **Risk Level** | LOW (full compliance stack) |

---

## 7. Non-Functional Requirements

| Requirement | Target | Notes |
|-------------|--------|-------|
| **API Response Time** | < 500ms (P95) | For real-time preference lookups |
| **Message Delivery SLA** | < 5 minutes from trigger | Welcome message after enrollment |
| **Availability** | 99.9% | For preference APIs and message service |
| **Data Retention** | 7 years | Consent records for TCPA compliance |
| **Throughput** | TBD | Depends on enrollment volume |
| **Disaster Recovery** | RPO: 1 hour, RTO: 4 hours | For preference data |
| **Logging** | All API calls logged | Centralized logging (Splunk/ELK) |
| **Monitoring** | Real-time dashboards | Message delivery rates, failures, opt-outs |

---

## 8. Day 1 vs Day 2 Implementation Comparison

| Aspect | Day 1 (Tactical) | Day 2 (Strategic) |
|--------|-------------------|-------------------|
| **Preference Storage** | Local SQL DB + DG | IPP (Book of Record) |
| **Consent Model** | Implied (phone in enrollment = consent) | Explicit prior express consent in IPP |
| **Preference API** | Local Digital Preference APIs | IPP APIs |
| **DNC/RND** | Skipped (transactional exemption) | Full Federal DNC + eDNC + RND via IPP |
| **Opt-Out** | Tactical (MaCE handles STOP) | Full unsubscribe → IPP API |
| **UI Changes** | Minimal (add phone/consent fields) | Full IPP API integration |
| **Message Source** | DataVision/EDP | IPP |
| **Dependencies** | DataVision, DG, MaCE | IPP, MaCE |
| **Risk** | Medium (tactical shortcuts) | Low (full compliance) |
| **Sunset** | After IPP implementation | N/A (final state) |

---

## 9. Open Questions Summary (Prioritized)

### Priority 1: MUST answer before design finalization

| # | Question | Ask Who | Status |
|---|----------|---------|--------|
| Q1 | What is CSI Web's tech stack? | Chris Byrd | ⬜ Open |
| Q3 | Direct DB calls or API/service layer in CSI Web? | Chris Byrd | ⬜ Open |
| Q9 | Where is IPP hosted? (GCP/Azure/On-Prem) | IPP Team | ⬜ Open |
| Q10 | IPP API Swagger/OpenAPI spec? | IPP Team | ⬜ Open |
| Q11 | IPP authentication method? | IPP Team | ⬜ Open |
| Q15 | DG tech stack and integration method? | Bill Cadman | ⬜ Open |
| Q22 | Does Welcome Message Service exist or build new? | Muhammad | ⬜ Open |
| Q26 | MaCE API spec / Swagger? | MaCE Team | ⬜ Open |

### Priority 2: Should answer before development

| # | Question | Ask Who | Status |
|---|----------|---------|--------|
| Q5 | Enrollment file format? | DG Team | ⬜ Open |
| Q13 | Is IPP API available now? | IPP Team | ⬜ Open |
| Q14 | IPP API response time SLA? | IPP Team | ⬜ Open |
| Q19 | How does DataVision expose data? | DataVision Team | ⬜ Open |
| Q20 | DataVision refresh frequency? | DataVision Team | ⬜ Open |
| Q27 | MaCE message template registration? | MaCE Team | ⬜ Open |

### Priority 3: Nice to have for detailed design

| # | Question | Ask Who | Status |
|---|----------|---------|--------|
| Q2 | Local SQL DB location? | Chris Byrd | ⬜ Open |
| Q4 | CSI Web authentication? | Chris Byrd | ⬜ Open |
| Q29 | MaCE delivery SLA? | MaCE Team | ⬜ Open |
| Q30 | Meritain registered in MaCE? | MaCE Team | ⬜ Open |

---

## 10. Recommended Next Steps

| # | Action | Owner | Target Date | Dependencies |
|---|--------|-------|-------------|-------------|
| 1 | Schedule call with **Chris Byrd** — understand CSI Web stack, local DB, current preference handling | Narendra | Week of Mar 30 | None |
| 2 | Schedule call with **IPP Team** — get API specs, hosting info, auth requirements | Narendra | Week of Mar 30 | None |
| 3 | Schedule call with **Bill Cadman (DG)** — understand enrollment file flow, DG tech stack | Narendra | Week of Apr 6 | None |
| 4 | Schedule call with **MaCE Team** — get API specs, template process, opt-out handling | Narendra | Week of Apr 6 | None |
| 5 | Review Muhammad's PowerPoint thoroughly | Narendra | Done ✅ | None |
| 6 | Update this document with findings from calls | Narendra | Ongoing | Steps 1-4 |
| 7 | Create PlantUML/Draw.io detailed diagram | Narendra | After Step 6 | Steps 1-4 |
| 8 | Review with Muhammad | Narendra + Muhammad | After Step 7 | Step 7 |

---

## 11. IMI Integration Consideration

Per the separate analysis in [Meritain_IMI_Integration_Q&A.md](Meritain_IMI_Integration_Q&A.md), the Meritain integration uses **IMI (Individual Master Index)** rather than EPH. Key implications for RCS:

- IMI individualizes members across CVS business units (pharmacy, minuteclinic, Aetna, Meritain)
- IMI matches on: First Name, Last Name, DOB, SSN, Zip Code, Address
- When a member is recognized across BUs, IMI links them → avoids duplicate messages
- For RCS purposes: IMI provides the authoritative member identity that IPP preferences attach to
- Cross-BU scenario: A member in both Aetna and Meritain should receive one welcome message, not two

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **RCS** | Rich Communication Services — enhanced messaging (rich cards, carousels, suggested replies) |
| **IPP** | Intelligent Preference Platform — enterprise BoR for member preferences and consent |
| **MaCE** | Messaging and Communications Engine — multi-channel message orchestration |
| **DG** | Data Governance / Digital Gateway — current preference store |
| **DataVision/EDP** | Enterprise Data Platform / Data Warehouse — current preference source of truth |
| **DNC** | Do Not Call — Federal DNC Registry |
| **eDNC** | Enterprise DNC — internal CVS do-not-call list |
| **RND** | Reassigned Number Database — checks if phone numbers were reassigned |
| **TCPA** | Telephone Consumer Protection Act — consent and DNC compliance |
| **IMI** | Individual Master Index — enterprise member identity resolution |
| **BoR** | Book of Record — authoritative source system |
| **CSI Web** | Customer Service Interface — CSR-facing web application |
| **EOB** | Explanation of Benefits |
| **CSG** | SMS delivery provider |

---

## Appendix B: Related Documents

- [Meritain_RCS_Roadmap_final v2.1.pptx](../Meritain_RCS_Roadmap_final v2.1.pptx) — Muhammad's conceptual design
- [Estimate_Impact_Summary.md](Estimate_Impact_Summary.md) — IMI integration effort estimate
- [Meritain_IMI_Implementation_Paths.md](Meritain_IMI_Implementation_Paths.md) — IMI integration architecture options
- [Meritain_IMI_Integration_Q&A.md](Meritain_IMI_Integration_Q&A.md) — IMI technical Q&A
- [ipp.drawio.xml](../AHH/ipp.drawio.xml) — Draw.io diagram (basic version)
