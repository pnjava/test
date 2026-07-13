---
id: 02-north-star-target-architecture
source: ITPR078770 PDF, pages 2, 8, 9 ("Meritain North Star - High Level")
state: proposed (target)
confidence: verified (diagram), priorities verbatim
tags: [north star, modernization, data platform, AI, contact center, Salesforce]
---
# Meritain North Star — Target Architecture

## Central principle (verbatim)
"No one will interact with DG directly. All DG interaction will be done through data platform."

## Priorities (verbatim from diagram)
- P1: CDC (Change Data Capture) from DG
- P2: refactor DG and create domain-driven architecture (domains: Provider/Rates/Network, Claims, Member, Plan Sponsor, Benefit Admin setup, Case setup, Draft Payment)
- P3: Joint venture with AI-based Enterprise contact center; Evaluate Zelis for Member services
- P4: (Superapp question: "Can we use Superapp for Meritain?")
- P5: (unlabeled in extraction)
- P6: Agentic Enrollment Verification Platform + Agentic Claim Decision Platform
- P7: Predictive Analytics Apps (model training, registry, experimentation; care gaps, next best action; LLM for explainability)
- P8: AI-Powered Production Support (incident triage, ticket analysis/auto-resolution, claims debugging assistant, proactive detection, runbook automation)
- P9: Change all integrations with internal partners to real time where possible

## Layers
- Enterprise Data Platform: Data Lake (BigQuery), Data HUB/Transactional Cache, Raw Data (ASIS), Data Mart, Meritain FHIR store
- Ent. Integration Platform: Service Layer, Event Layer, Kong (internal GW), APIGEE/FHIR (external GW), File Gateway/B2B GW
- Contact Center AI layer: Voice/Digital/Process Intelligent Agents, Salesforce Service Cloud Org, Enterprise Service Platform (Salesforce Health Cloud), GPS console, Real-time Omnichannel Engagement Engine, Contact Engagement Decision Engine; Agent Productivity (GenAI): assist/coaching, knowledge assist, interaction summary/transcription
- NextGen assets: NG Corresponding Platform, Engagement Platform, Digital Platform, NG Constituent Platform (reuse for enrollment processing and correspondence incl. ID card printing — to be confirmed with NextGen)

## Agentic platforms (P6, verbatim descriptions)
- Agentic Enrollment Verification: validates enrollment data against client-given rules; copilot to expedite enrollment processing using LLM and RAG; components: Agent Orchestration Layer, RAG Knowledge Layer, Audit & Evidence store, Explanation & Communication Layer (LLM)
- Agentic Claims Decision: addresses manual adjudication; copilot to expedite claim processing using LLM and RAG; same 4-layer structure

## Unclear
- P5 content; Superapp decision; NextGen reuse confirmation status
