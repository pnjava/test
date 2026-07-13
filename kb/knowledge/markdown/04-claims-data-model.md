---
id: 04-claims-data-model
source: ITPR078770 PDF, page 4
state: proposed (target model, likely for Transactional Cache)
confidence: verified (diagram), purpose inferred
tags: [data model, claims, member, provider, MongoDB]
---
# Claims Domain Data Model

## Entities (fields verbatim)
- MEMBER: PK MemberID, DepNo, FirstName, LastName
- CLAIM: PK ClaimNumber; ClaimType, ClaimStatusCode, ClaimStatusDescription; FK MemberID, DepNo, GroupID, DivisionCode, ProviderID; ServiceFromDate, ServiceToDate, ReceiveDate, PaidDate; TotalIncurred, PaidAmount, PatientResponsibility, AllowedAmount, BilledCharges
- SERVICE_LINE: FK ClaimNumber; LineNumber, ServiceCode, ServiceCodeType, Modifier, PlaceOfService, BilledAmount, AllowedAmount, PaidAmount, PatientResponsibility, DiagnosisCodes[]
- GROUP_INFO: PK GroupID, DivisionCode
- PROVIDER: PK ProviderID, ProviderName, TIN, PayeeName, Address1/2, City, State, Zip
- CLAIM_TRACKING: TrackingEventID; FK ClaimNumber; EventType, EventDate, User, Notes, VendorName, VendorSentDate, VendorReturnedDate, VendorProcessedDate
- CLAIM_DOCUMENT: DocumentID; FK ClaimNumber; DocumentType, FileName, CreatedDate, DeliveryMethod, Source, ContentLocation

## Inferred
- This is the normalized target schema for the claims read model (Transactional Cache), not the native DG MultiValue file structure
## Unclear
- Mapping from DG files (e.g. BHIST, HSTRACKING) to these entities
- Whether this is approved or draft
