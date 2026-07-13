---
source_file: emails.txt
source: email_export
date: '2026-03-27'
state: current
owner: TBD
category: communication
confidence: inferred
tags:
- communication
- ipp
- meritain
extraction_method: plaintext
extracted_on: '2026-07-12'
---

FW: IPP Intake for Meritain
Ali, Muhammad Muddassar

?Kumar, Narendra?
Narendra,

 

Can you check details on it from Chris about OTP. Who is generating and how it is being generated.

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

 

From: Singh, Ankita <SinghA35@aetna.com>
Sent: Monday, March 16, 2026 8:54 AM
To: Lintvedt, Chris <chris.lintvedt@meritain.com>; Narayan, Ram <NarayanR@aetna.com>; Cadman, William K <bill.cadman@meritain.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
Subject: Re: IPP Intake for Meritain

 

Does this mean Meritain Connect will soon start collecting phone numbers (and send OTP for verification) ? What is the timeline for this ?

 

Where will these phone numbers be stored ?

 

Thanks,

Ankita Singh ¦Aetna Technology- IPP Product Manager

p: 540-998-2654

 

From: Lintvedt, Chris <chris.lintvedt@meritain.com>
Sent: Sunday, March 15, 2026 3:04 PM
To: Narayan, Ram <NarayanR@aetna.com>; Cadman, William K <bill.cadman@meritain.com>; Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
Subject: Re: IPP Intake for Meritain

 

Chiming in a little late - but wanted to add some extra detail around existing SFMC 'campaigns' and 'business units' created for Meritain.

 

In reference to your #5 below, about 'does Meritain send SMS text messages'. We WILL soon in a limited capacity.

Just for our Meritain Connect web portal authentication process, for "multi-factor-authentication" (MFA) "one-time-passcodes" (OTP). We currently just send them out via service 'fabric' API's and some interaction with the SFMC email template we have setup with them (custom Meritain specific email template we provided to them).

 

Aetna will be deploying an update to prod soon (Mar 18th) on their side, to support sending out this OTP message via SMS text message, via their existing 'NGA API' (next-gen-authentication API). Once that NGA API update is out there, Meritain's own 'Digital team' will schedule planned minor development work in our next SAFE PI to update Meritain Connect portal to allow a member user to select to receive the OTP code via SMS text message.

 

I dug through my emails from last year,  when corresponding with the Aetna AIM team, Service 'Fabric' team and SFMC team and found these details... they might not mean much, but just passing along in case they do. 

 

My main goal here - is making sure we don't already have some existing processes/configurations already setup across teams that we might want to re-use, as far as SFMC, Fabric or other 'business units' that we might want to re-use with this IPP effort.

 

1. From Inder (on Aetna AIM team - helping Meritain setup NGA API's for MFA OTP):

"Meritain will be calling the AIM OTP Services to generate/validate & deliver the OTP email using Fabric. Fabric APIs take a program id (equivalent to email template) which you need to work with the Fabric team to setup. SFMC team will help set up the template that will be used by Fabric"

 

2.From Sara Doran (Aetna):

"We had a call yesterday with Enterprise Martech regarding Meritain.  I believe it was mentioned in that call (I joined late), that Meritain needed their own business Unit due to not being able to co-mingle data.  If that is the case, should we be sending Meritain transactional messages out of the Enterprise transactional business unit?"

 

3.From Maxwell Junge (CVS Health):

"We did create an Aetna non-members (broker & plan sponsor) business unit for you.

That said, do you know if Meritian has their own firewall / data privacy restrictions since it’s a separate entity? E.g. Does Meritian need to be segregated due to privacy / legal restrictions? That would be what determines whether they need their own BU or not."

 

4.Reply from Bil Cadman (Meritain):

"These data (Portal Users needing a one-time passcode) are not subject to business firewall. If we get into claims details and plan sponsor details we will need to comply with business firewalls."

 

5. More recently, this past few weeks - From Madhuri Gajula (Aetna) with assistance from Prafull Jagalpure (Aetna) - about enabling the OTP messages via SMS text  - SFMC  campaign setting:  

?
Campaign Name

Program ID

I90 Program ID

T-BrokerPS-Meritain-MFA-SMS-QA

5242

2793

T-BrokerPS-Meritain-MFA-SMS-Prod

21215

9570

 

Lastly, for reference - the OTP SMS message is small, the same as the Aetna one only with 'Meritain Health' . Here's an example SMS text message:

"Your authorization code for Meritain Health is 485413"

 

Thanks!

 

Chris Lintvedt (he, him, his) | Technical Lead, Digital Team

952.582.2879

1405 Xenium Lane N Suite 140, Mpls, MN 55441

 

 

From: Narayan, Ram <NarayanR@aetna.com>
Sent: Thursday, March 12, 2026 3:59 PM
To: Cadman, William K <bill.cadman@meritain.com>; Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
Subject: RE: IPP Intake for Meritain

 

Bringing Ajay (IPP Tech lead) in loop.

 

Regards,

Ram Narayan

IPP Domain Lead Director – Correspondence, Marketing, Profile & Preferences

Mobile – 860-990-7150

CVS 

 

From: Cadman, William K <bill.cadman@meritain.com>
Sent: Thursday, March 12, 2026 3:10 PM
To: Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>
Subject: RE: IPP Intake for Meritain

 

Meritain does not currently maintain Do Not Call lists. We would like to use Aetna’s.

 

 

Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology

Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823

 

 

From: Singh, Ankita <SinghA35@aetna.com>
Sent: Thursday, March 12, 2026 2:36 PM
To: Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>; Cadman, William K <bill.cadman@meritain.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
Subject: Re: IPP Intake for Meritain

 

One additional question - Does Meritain maintain its own DNC  (Do not Contact list) or does it rely on Aetna DNC for outreaches via phone (manual/live call, robocall, text) ?

 

 

Thanks,

Ankita Singh ¦Aetna Technology- IPP Product Manager

p: 540-998-2654

signature_3133748786

 

From: Ali, Muhammad Muddassar <mmali@cvshealth.com>
Date: Tuesday, March 10, 2026 at 4:36 PM
To: Singh, Ankita <SinghA35@aetna.com>, Lintvedt, Chris <chris.lintvedt@meritain.com>, Brar, Yadvinder <BrarY@cvshealth.com>, Narayan, Ram <NarayanR@aetna.com>, Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>, Alonso, Joni L <AlonsoJ@AETNA.com>, Cadman, William K <bill.cadman@meritain.com>
Cc: Alabau, Frank <AlabauF@meritain.com>, Kumar, Narendra <Narendra.Kumar@aetna.com>
Subject: RE: IPP Intake for Meritain

See below response:

 

We need very high level ballpark estimate for IPP support. Is it possible you can give us?

 

 

@Cadman, William K,

 

Can you fill in if I miss stated anything?

 

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

 

From: Singh, Ankita <SinghA35@aetna.com>
Sent: Tuesday, March 10, 2026 9:54 AM
To: Lintvedt, Chris <chris.lintvedt@meritain.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>; Cadman, William K <bill.cadman@meritain.com>
Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
Subject: Re: IPP Intake for Meritain

 

Hi,

 

I have a couple of high-level questions about Meritain members

Which application collects the enrollment information for Meritain members (Name, DOB, gender, Email, phone , address etc) ? DG-Meritain backbone application
What is the count of the population ? 2 Million members that may go up to 5 million in next 3 years.
What is the member ID used by Meritain members.(ID available in the ID card if any)? Please share sample ID. ***You will find in IMI. Bill can share this with you as well.
Given that it is mentioned that they are in IMI, can we consider all the Meritain members are considered Aetna members? ****No they are not Aetna members.
Which application collects communication preferences (email, phone, Address, language, paperless) from Meritain.com and via other channels such as CSR or clinical? ***We are going to add this capability in MeritainConnect (member services), CSI Web (CSR app) and Mobile App.
Does Meritain send texts ? Are these texts branded as Aetna or Meritain ? Which Vendor and applications sends these texts ? Which vendor/application collects the opt outs for these texts? This is new capability that we need to build. We will use Enterprise vendors InfoBip and CSG for this purpose.
Are Meritain members expected to login via Aetna health in future ? No, They have their own portal.
Which application supports Meritain members from a CSR standpoint- is it Aetna CSR GPS?***CSI web meritain owned app.
Can Meritain members engage with Aetna Clinical applications such as Medcompass, CEC or OneCM? Nope
Which application sends paperless or paper copy of EOB and other letters, to Meritain members? Zelis vendor
What is the value we are trying to get out of Meritain members getting added to IPP? We are going to connect with Ent Messaging platform (MaCE) for member communication.
Can Meritain members assign POA and/TPA. If yes, how is this done? ****Not happening today. Bill?
Can Meritain members restrict access to any individual  (RES privacy type). If yes, how is this done? ****Not happening today. Bill?

Is UAF involved in the user authentication process for members logging in to meritain.com ?***No
 

 

Please submit an intake to IPP by sharing the below information.

ITPR number
Overall business objective/use case
Scope for IPP - Based on the answers to above questions, we will need to assess the various integrations IPP will need to build/support for Preference, Profile and Privacy
High level timelines
Key Stakeholder POCs (for Clarity allocation and other discussions)
 

 

Thanks,

Ankita Singh ¦Aetna Technology- IPP Product Manager

p: 540-998-2654

signature_3133748786

 

From: Lintvedt, Chris <chris.lintvedt@meritain.com>
Date: Tuesday, March 10, 2026 at 7:04 AM
To: Ali, Muhammad Muddassar <mmali@cvshealth.com>, Brar, Yadvinder <BrarY@cvshealth.com>, Singh, Ankita <SinghA35@aetna.com>, Narayan, Ram <NarayanR@aetna.com>, Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>, Alonso, Joni L <AlonsoJ@AETNA.com>, Cadman, William K <bill.cadman@meritain.com>
Cc: Alabau, Frank <AlabauF@meritain.com>, Kumar, Narendra <Narendra.Kumar@aetna.com>
Subject: RE: IPP Intake for Meritain

Muhammad,

 

ARE they really in IMI already? As a reminder: Meritain has its own domain ad.meritain.com separate from Aetna (AETH) domain. MeritainConnect portal stores users in a custom active directory (AD) – cust.meritain.com. I have another project this year with Aetna Account Manager, where it’ll be directly referring to that cust.meritain.com AD (since Meritain isn’t in IMI nor are we moving there).

 

Thanks,

Chris

 

From: Ali, Muhammad Muddassar <mmali@cvshealth.com>
Sent: Monday, March 9, 2026 5:20 PM
To: Brar, Yadvinder <BrarY@cvshealth.com>; Singh, Ankita <SinghA35@aetna.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
Cc: Cadman, William K <bill.cadman@meritain.com>; Alabau, Frank <AlabauF@meritain.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
Subject: RE: IPP Intake for Meritain

 

Ankita/Ram,

 

We are part of Meritain Health. As part of Meritain modernization effort, we need to use IPP for capturing Meritain members preferences. Currently Meritain members are already in IMI. Let us know what is next step to engage your team for this purpose? Do you have intake process that we need to start with?

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

 

From: Brar, Yadvinder <BrarY@cvshealth.com>
Sent: Monday, March 9, 2026 4:51 PM
To: Ali, Muhammad Muddassar <mmali@cvshealth.com>
Cc: Singh, Ankita <SinghA35@aetna.com>; Narayan, Ram <NarayanR@aetna.com>; Brar, Yadvinder <BrarY@cvshealth.com>
Subject: IPP Intake for Meritain

 

Hi Muhammad,

 

I have added Ram and Ankita for IPP intake. They can help with the process.

 

Yadvinder Brar

Principal Architect

Aetna Technology | Architecture Delivery

BrarY@aetna.com

860 273 1422 T

860 869 7926 M

 From: Brar, Yadvinder <BrarY@cvshealth.com>
 Sent: Monday, March 9, 2026 4:51 PM
 To: Ali, Muhammad Muddassar <mmali@cvshealth.com>
 Cc: Singh, Ankita <SinghA35@aetna.com>; Narayan, Ram <NarayanR@aetna.com>; Brar, Yadvinder <BrarY@cvshealth.com>
 Subject: IPP Intake for Meritain
 
  
 
 Hi Muhammad,
 
  
 
 I have added Ram and Ankita for IPP intake. They can help with the process.
 
  
 
 Yadvinder Brar
 
 Principal Architect
 
 Aetna Technology | Architecture Delivery
 
 BrarY@aetna.com
 
 860 273 1422 T
 
 860 869 7926 M
 
 From: Ali, Muhammad Muddassar <mmali@cvshealth.com>
 Sent: Monday, March 9, 2026 5:20 PM
 To: Brar, Yadvinder <BrarY@cvshealth.com>; Singh, Ankita <SinghA35@aetna.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
 Cc: Cadman, William K <bill.cadman@meritain.com>; Alabau, Frank <AlabauF@meritain.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
 Subject: RE: IPP Intake for Meritain
 
  
 
 Ankita/Ram,
 
  
 
 We are part of Meritain Health. As part of Meritain modernization effort, we need to use IPP for capturing Meritain members preferences. Currently Meritain members are already in IMI. Let us know what is next step to engage your team for this purpose? Do you have intake process that we need to start with?
 
  
 
 Muhammad Muddassar Ali
 
 Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES
 
 724-720-2139 (O)
 
 412-297-9685 (C)
 
 151 Farmington Ave
 
 Hartford, CT
 
 
 
 From: Lintvedt, Chris <chris.lintvedt@meritain.com>
 Date: Tuesday, March 10, 2026 at 7:04 AM
 To: Ali, Muhammad Muddassar <mmali@cvshealth.com>, Brar, Yadvinder <BrarY@cvshealth.com>, Singh, Ankita <SinghA35@aetna.com>, Narayan, Ram <NarayanR@aetna.com>, Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>, Alonso, Joni L <AlonsoJ@AETNA.com>, Cadman, William K <bill.cadman@meritain.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>, Kumar, Narendra <Narendra.Kumar@aetna.com>
 Subject: RE: IPP Intake for Meritain
 
 Muhammad,
 
  
 
 ARE they really in IMI already? As a reminder: Meritain has its own domain ad.meritain.com separate from Aetna (AETH) domain. MeritainConnect portal stores users in a custom active directory (AD) – cust.meritain.com. I have another project this year with Aetna Account Manager, where it’ll be directly referring to that cust.meritain.com AD (since Meritain isn’t in IMI nor are we moving there).
 
  
 
 Thanks,
 
 Chris
 
 From: Singh, Ankita <SinghA35@aetna.com>
 Sent: Tuesday, March 10, 2026 9:54 AM
 To: Lintvedt, Chris <chris.lintvedt@meritain.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>; Cadman, William K <bill.cadman@meritain.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
 Subject: Re: IPP Intake for Meritain
 
  
 
 Hi,
 
  
 
 I have a couple of high-level questions about Meritain members
 
 Which application collects the enrollment information for Meritain members (Name, DOB, gender, Email, phone , address etc) ? DG-Meritain backbone application
 What is the count of the population ? 2 Million members that may go up to 5 million in next 3 years.
 What is the member ID used by Meritain members.(ID available in the ID card if any)? Please share sample ID. ***You will find in IMI. Bill can share this with you as well.
 Given that it is mentioned that they are in IMI, can we consider all the Meritain members are considered Aetna members? ****No they are not Aetna members.
 Which application collects communication preferences (email, phone, Address, language, paperless) from Meritain.com and via other channels such as CSR or clinical? ***We are going to add this capability in MeritainConnect (member services), CSI Web (CSR app) and Mobile App.
 Does Meritain send texts ? Are these texts branded as Aetna or Meritain ? Which Vendor and applications sends these texts ? Which vendor/application collects the opt outs for these texts? This is new capability that we need to build. We will use Enterprise vendors InfoBip and CSG for this purpose.
 Are Meritain members expected to login via Aetna health in future ? No, They have their own portal.
 Which application supports Meritain members from a CSR standpoint- is it Aetna CSR GPS?***CSI web meritain owned app.
 Can Meritain members engage with Aetna Clinical applications such as Medcompass, CEC or OneCM? Nope
 Which application sends paperless or paper copy of EOB and other letters, to Meritain members? Zelis vendor
 What is the value we are trying to get out of Meritain members getting added to IPP? We are going to connect with Ent Messaging platform (MaCE) for member communication.
 Can Meritain members assign POA and/TPA. If yes, how is this done? ****Not happening today. Bill?
 Can Meritain members restrict access to any individual  (RES privacy type). If yes, how is this done? ****Not happening today. Bill?
 
 Is UAF involved in the user authentication process for members logging in to meritain.com ?***No
  
 
  
 
 Please submit an intake to IPP by sharing the below information.
 
 ITPR number
 Overall business objective/use case
 Scope for IPP - Based on the answers to above questions, we will need to assess the various integrations IPP will need to build/support for Preference, Profile and Privacy
 High level timelines
 Key Stakeholder POCs (for Clarity allocation and other discussions)
  
 
  
 
 Thanks,
 
 Ankita Singh ¦Aetna Technology- IPP Product Manager
 
 p: 540-998-2654
 
 signature_3133748786
 
 From: Ali, Muhammad Muddassar <mmali@cvshealth.com>
 Date: Tuesday, March 10, 2026 at 4:36 PM
 To: Singh, Ankita <SinghA35@aetna.com>, Lintvedt, Chris <chris.lintvedt@meritain.com>, Brar, Yadvinder <BrarY@cvshealth.com>, Narayan, Ram <NarayanR@aetna.com>, Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>, Alonso, Joni L <AlonsoJ@AETNA.com>, Cadman, William K <bill.cadman@meritain.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>, Kumar, Narendra <Narendra.Kumar@aetna.com>
 Subject: RE: IPP Intake for Meritain
 
 See below response:
 
  
 
 We need very high level ballpark estimate for IPP support. Is it possible you can give us?
 
  
 
  
 
 @Cadman, William K,
 
  
 
 Can you fill in if I miss stated anything?
 
  
 
  
 
 Muhammad Muddassar Ali
 
 Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES
 
 724-720-2139 (O)
 
 412-297-9685 (C)
 
 151 Farmington Ave
 
 Hartford, CT
 
 
 
 From: Singh, Ankita <SinghA35@aetna.com>
 Sent: Thursday, March 12, 2026 2:36 PM
 To: Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>; Cadman, William K <bill.cadman@meritain.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>
 Subject: Re: IPP Intake for Meritain
 
  
 
 One additional question - Does Meritain maintain its own DNC  (Do not Contact list) or does it rely on Aetna DNC for outreaches via phone (manual/live call, robocall, text) ?
 
  
 
  
 
 Thanks,
 
 Ankita Singh ¦Aetna Technology- IPP Product Manager
 
 p: 540-998-2654
 
 signature_3133748786
 
 From: Cadman, William K <bill.cadman@meritain.com>
 Sent: Thursday, March 12, 2026 3:10 PM
 To: Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Narayan, Ram <NarayanR@aetna.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>
 Subject: RE: IPP Intake for Meritain
 
  
 
 Meritain does not currently maintain Do Not Call lists. We would like to use Aetna’s.
 
  
 
  
 
 Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology
 
 Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823
 
  
 
 
 
 From: Narayan, Ram <NarayanR@aetna.com>
 Sent: Thursday, March 12, 2026 3:59 PM
 To: Cadman, William K <bill.cadman@meritain.com>; Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Lintvedt, Chris <chris.lintvedt@meritain.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
 Subject: RE: IPP Intake for Meritain
 
  
 
 Bringing Ajay (IPP Tech lead) in loop.
 
  
 
 Regards,
 
 Ram Narayan
 
 IPP Domain Lead Director – Correspondence, Marketing, Profile & Preferences
 
 Mobile – 860-990-7150
 
 
 CVS 
 
 From: Lintvedt, Chris <chris.lintvedt@meritain.com>
 Sent: Sunday, March 15, 2026 3:04 PM
 To: Narayan, Ram <NarayanR@aetna.com>; Cadman, William K <bill.cadman@meritain.com>; Singh, Ankita <SinghA35@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
 Subject: Re: IPP Intake for Meritain
 
  
 
 Chiming in a little late - but wanted to add some extra detail around existing SFMC 'campaigns' and 'business units' created for Meritain.
 
  
 
 In reference to your #5 below, about 'does Meritain send SMS text messages'. We WILL soon in a limited capacity.
 
 Just for our Meritain Connect web portal authentication process, for "multi-factor-authentication" (MFA) "one-time-passcodes" (OTP). We currently just send them out via service 'fabric' API's and some interaction with the SFMC email template we have setup with them (custom Meritain specific email template we provided to them).
 
  
 
 Aetna will be deploying an update to prod soon (Mar 18th) on their side, to support sending out this OTP message via SMS text message, via their existing 'NGA API' (next-gen-authentication API). Once that NGA API update is out there, Meritain's own 'Digital team' will schedule planned minor development work in our next SAFE PI to update Meritain Connect portal to allow a member user to select to receive the OTP code via SMS text message.
 
  
 
 I dug through my emails from last year,  when corresponding with the Aetna AIM team, Service 'Fabric' team and SFMC team and found these details... they might not mean much, but just passing along in case they do. 
 
  
 
 My main goal here - is making sure we don't already have some existing processes/configurations already setup across teams that we might want to re-use, as far as SFMC, Fabric or other 'business units' that we might want to re-use with this IPP effort.
 
  
 
 1. From Inder (on Aetna AIM team - helping Meritain setup NGA API's for MFA OTP):
 
 "Meritain will be calling the AIM OTP Services to generate/validate & deliver the OTP email using Fabric. Fabric APIs take a program id (equivalent to email template) which you need to work with the Fabric team to setup. SFMC team will help set up the template that will be used by Fabric"
 
  
 
 2.From Sara Doran (Aetna):
 
 "We had a call yesterday with Enterprise Martech regarding Meritain.  I believe it was mentioned in that call (I joined late), that Meritain needed their own business Unit due to not being able to co-mingle data.  If that is the case, should we be sending Meritain transactional messages out of the Enterprise transactional business unit?"
 
  
 
 3.From Maxwell Junge (CVS Health):
 
 "We did create an Aetna non-members (broker & plan sponsor) business unit for you.
 
 That said, do you know if Meritian has their own firewall / data privacy restrictions since it’s a separate entity? E.g. Does Meritian need to be segregated due to privacy / legal restrictions? That would be what determines whether they need their own BU or not."
 
  
 
 4.Reply from Bil Cadman (Meritain):
 
 "These data (Portal Users needing a one-time passcode) are not subject to business firewall. If we get into claims details and plan sponsor details we will need to comply with business firewalls."
 
  
 
 5. More recently, this past few weeks - From Madhuri Gajula (Aetna) with assistance from Prafull Jagalpure (Aetna) - about enabling the OTP messages via SMS text  - SFMC  campaign setting:  
 
 
 ?
 Campaign Name
 
 Program ID
 
 I90 Program ID
 
 T-BrokerPS-Meritain-MFA-SMS-QA
 
 5242
 
 2793
 
 T-BrokerPS-Meritain-MFA-SMS-Prod
 
 21215
 
 9570
 
  
 
 Lastly, for reference - the OTP SMS message is small, the same as the Aetna one only with 'Meritain Health' . Here's an example SMS text message:
 
 "Your authorization code for Meritain Health is 485413"
 
  
 
 Thanks!
 
  
 
 Chris Lintvedt (he, him, his) | Technical Lead, Digital Team
 
 952.582.2879
 
 1405 Xenium Lane N Suite 140, Mpls, MN 55441
 
  
 
 
 
 From: Singh, Ankita <SinghA35@aetna.com>
 Sent: Monday, March 16, 2026 8:54 AM
 To: Lintvedt, Chris <chris.lintvedt@meritain.com>; Narayan, Ram <NarayanR@aetna.com>; Cadman, William K <bill.cadman@meritain.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>; Brar, Yadvinder <BrarY@cvshealth.com>; Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>; Alonso, Joni L <AlonsoJ@AETNA.com>
 Cc: Alabau, Frank <AlabauF@meritain.com>; Kumar, Narendra <Narendra.Kumar@aetna.com>; Vander Laan, Erin B <ebvanderlaan@cvshealth.com>; Vagumudi, Ajay <VagumudiA@aetna.com>
 Subject: Re: IPP Intake for Meritain
 
  
 
 Does this mean Meritain Connect will soon start collecting phone numbers (and send OTP for verification) ? What is the timeline for this ?
 
  
 
 Where will these phone numbers be stored ?
 
  
 
 Thanks,
 
 Ankita Singh ¦Aetna Technology- IPP Product Manager
 
 p: 540-998-2654
 
 From: Taylor, Sarah N <Sarah.Taylor3@CVSHealth.com>
 Sent: Monday, March 16, 2026 3:32 PM
 To: Alonso, Joni L <AlonsoJ@AETNA.com>; Pothireddy, Dheera <Dheera.Pothireddy@aetna.com>; Ali, Muhammad Muddassar <mmali@cvshealth.com>
 Subject: RE: IPP Intake for Meritain
 
  
 
 I was about to hit send on this but Mohammad pinged me indicating that IPP has a whole new proposal hanging out there to segregate Meritain data.  Can you all help pull together a concise story on what we will achieve in 2026 w th IPP and showcase how this set sus up for su ccess for the future of SMS/RCS?
 
  
 
 These will be stored in DG until we can get the integrations up and running with IPP. It would be great to do a working session to get our data mappings form DG to IPP kicked off so we can outline the detailed deliverables to start moving towards the longer term vision! 
 
  
 
 We would typically kick off this discussion with a list of the APIs that Meritain will need to interact with to send data over. Teams may have already completed this activity and if so, we can start mapping fields from DG over to the APIs. The Meritain engineering team has the IPP integration prioritized to work on in Q2 with planning occurring in early April so we have a few weeks to prepare the runway needed to ensure we are ready to roll.
 
  
 
  
 
  
 
  
 
 Sarah Taylor | Product Management, Aetna Technology - Commercial, Network\Provider, Affiliate  
 C 502-759-2918
 Virtual - Kentucky
 CVS
 
 Ali,
 Muhammad
 Muddassar
 
 ?Taylor, Sarah N;?Alonso, Joni L;?Pothireddy, Dheera?
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 Sarah,
 
  
 
 I think we are having a roadblock to deliver RCS message to Member. Currently we are not having member consent to send them RCS welcome message. This message needs to be delivered before member registration on our portal. Even if we do IPP integration, it can only help us to capture preferences from Member once member get registered with us.
 
  
 
 To send member welcome message, plan sponsors must capture consent & preferences as part of member enrollment process and pass us. Today plan sponsors are sending us consents and preferences only and only for Member EOBs.
 
  
 
 In this case, if we will use member phone number and try to send them welcome message, it will be against TCPA compliance requirements.
 
  
 
 Once member will get enrolled with us, registered on our portal, update consents and preference using MeritainConnect, then we are allowed to send future communication to member, but it will not be welcome RCS message.
 
  
 
 To solve this issue, we need to ask all our plan sponsors to capture member consent and preference for welcome message as well as EOBs. Question is that if this is even practical to get this change done ASAP. I heard that 834 does not have a placeholder for “consent to send member SMS messages”.
 
  
 
 Or we need legal approval to see if we could send these welcome messages to members without having explicit consent.
 
  
 
 See attached sketch that explain this gap.
 
  
 
  
 
 See attached TCPA requirement (Searched using Copilot).
 
  
 
 Generally, no; you cannot send a welcome SMS to a new healthcare member without explicit consent, as it violates the Telephone Consumer Protection Act (TCPA) and HIPAA regulations. While providing a number during registration may imply consent for urgent care-related messages (e.g., appointment reminders), it does not cover general welcome messages or marketing. 
 
  
 
 Key Considerations for Compliance:
 
 Explicit Consent Mandatory: For non-urgent messages, including "welcome" messages, you must have documented, explicit, and informed consent (opt-in) from the member, as per Paubox Email.
 Government Program Exception: The FCC suggests that for government-sponsored plans, providing a phone number on an enrollment form can sometimes be considered prior express consent for messages related to benefits, coverage, and eligibility, according to BeneLynk.
 Opt-Out Requirement: Every text must provide a clear way to opt out, notes Solum Health.
 Security: Messages containing Protected Health Information (PHI) must be sent via secure, encrypted platforms to meet HIPAA standards, says The Joint Commission. 
  
 
 It is highly recommended to include a checkbox on the enrollment form where members can explicitly agree to receive informational SMS messages. 
 
  
 
  
 
  
 
 Muhammad Muddassar Ali
 
 Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES
 
 724-720-2139 (O)
 
 412-297-9685 (C)
 
 151 Farmington Ave
 
 Hartford, CT
 
 
 
 Taylor, Sarah N
 
 ?Ali, Muhammad Muddassar;?Alonso, Joni L;?+1 other?
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 We talked to Meritian leadership on this topic and they have confirmed that consent to send the initial RCS message is provided by the plan sponsor.  We must provide the option for member to “opt out” from there but do not require initial member consent.  Joni and Melissa were both part of these discussions so please conform back with them if needed.
 
  
 
  
 
  
 
  
 
 Sarah Taylor | Product Management, Aetna Technology - Commercial, Network\Provider, Affiliate  
 C 502-759-2918
 Virtual - Kentucky
 CVS
 
 Ali,
 Muhammad
 Muddassar
 
 ?Taylor, Sarah N;?Alonso, Joni L;?+2 others??
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 That initial Phone No with RCS message consent is not currently stored in DG system.
 
  
 
 +Cadman
 
  
 
 Bill,
 
  
 
 Is it possible that Plan sponsor is sending initial RCS message consent as well along with EOB preferences, but we are not storing it in Meritain today?
 
  
 
 Muhammad Muddassar Ali
 
 Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES
 
 724-720-2139 (O)
 
 412-297-9685 (C)
 
 151 Farmington Ave
 
 Hartford, CT
 
 
 
 Cadman, William K
 
 ?Ali, Muhammad Muddassar;?Taylor, Sarah N;?+2 others??
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 Meritain does not receive RCS today. So Meritain does not get number or consent from any entity.
 
  
 
 This is a brand new capability to be built, correct?
 
  
 
 Bill
 
  
 
  
 
  
 
  
 
 Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology
 
 Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823
 
  
 
 
 
 Ali,
 Muhammad
 Muddassar
 
 ?Cadman, William K;?Taylor, Sarah N;?+2 others??
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 Joni,
 
  
 
 Can you check with Melissa as well?
 
  
 
 Muhammad Muddassar Ali
 
 Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES
 
 724-720-2139 (O)
 
 412-297-9685 (C)
 
 151 Farmington Ave
 
 Hartford, CT
 
 
 
 Cadman, William K
 
 ?Ali, Muhammad Muddassar;?Taylor, Sarah N;?+2 others??
 ?Mungovan, Patrick J;?Siavelis, Amalia;?+4 others????
 My apologies I set prematurely.
 
  
 
 Meritain does not have SMS/RCS capabilities today, so until now there has been no reason for Plan Sponsors to send textable phone numbers and consent to Meritain. As part of this effort we will need to define processes and mechanisms to do that.
 
  
 
 Bill
 
  
 
  
 
 Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology
 
Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823

Offline Settings
IPP

?
Summarize this email
Ali,
Muhammad
Muddassar

?Kumar, Narendra?
hi is IMi going to have Individual and proxy for meritain wil eph get IMI event when proxy id change… ipp expectes those to come from eph will that happen 

I need to work on this to get answers. Does it impact estimate a lot?

 

My understanding is that Proxy id is a mandatory field that get assigned to every individual record

 

IPP reads EPH events usually.. so expection is EPH will give the proy ID changes as part of regular process

 

100%

 

so to estimate we just need to know who will give is IID and Proxy ID changes

 

will meritain ID be present in the event or not (EPH does have various ids when sending event for aetna, retail etc)

 

if i just get IID.. and no signal whether this belong to meritain or not.. then my logic will be diff... probablya lil more complex 

 

if i get IID and a signal that this a meritain only or both meritain and Aetna... my logic maybe simpler

 

things like that

 

and again.. where do i read this.. EPH or IMI

 

current expectation for pref is EPH not IMI

 

bt for meritain we have to read IMI not eph

 

we need to build that

 

rather than enhance current integration with EPH

 

Singh, Ankita

will meritain ID be present in the event or not (EPH does have various ids when sending event for aetna, retail etc)

I can check but assume yes it will be one and same process. It is just like another BU of Aetna and process is not different what we have for Aetna

 

Singh, Ankita

will meritain ID be present in the event or not (EPH does have various ids when sending event for aetna, retail etc)

Tooooo much deep dive question. We can find out when detailed design will happen. I would assume if you get ids for other cases then you will get for this as well. It is simply stored in same generic field where others ids are stored.

 

Singh, Ankita

if i get IID and a signal that this a meritain only or both meritain and Aetna... my logic maybe simpler

Using meritaid id you will find proxy id and then you will see what other ids are attached to proxy ids. We could have member belong to both.

 

Singh, Ankita

and again.. where do i read this.. EPH or IMI

IMI

 

I would assume same as Aetna process but for safe side if u want to add hours for IMI then it is fine

 

Aetna process is via EPH

 

we will ssume IMI and assume some additional complex logic to handle it

 

to estimate this

 

another question ... do u have any ask for retrieval of not only meritain preference but also Aetna or CVS data (assuming u getapprovals)

 

for now i am assuming no

 

and estimating accordingly

 

Not at all

 

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

Offline Settings
DataVision preferences

?
Summarize this email
Ali,
Muhammad
Muddassar

?Fleckenstein, Tracy?
?Cadman, William K;?Lintvedt, Chris;?Kumar, Narendra?
Tracy,

 

Currently we have two different data sources for Member preferences:

 

DG member EOB preferences
Member preferences that being managed by MeritainConnect and CSI Web applications in a separate database
 

Can you check if DataVision only have DG preferences or both? If both, are we storing them separately or combined? Are we sending Member preference feedback to DG from MeritainConnect/CSI web database?

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

Cadman, William K

?Ali, Muhammad Muddassar;?Fleckenstein, Tracy?
?Lintvedt, Chris;?Kumar, Narendra?
Data Vision has both. I wrote the feature to load that data for DG and the digital SQL tables.

 

 

 

Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology

Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823

 

Fleckenstein, Tracy

?Ali, Muhammad Muddassar;?Wetzel, Tricia;?+1 other?
?Cadman, William K;?Lintvedt, Chris;?Kumar, Narendra?
Hello,

 

Data Vision (DV) is a transformed view of OLTP data for the purpose of reporting, analytics, and data extracts.

 

My understanding is that DV member preferences (I think being used for SmartComm) is being sourced by DG but I added @Wetzel, Tricia (DV PO) and @Albi, Anthony J (Data Engineer) to this thread so they can correct me if I am wrong and/or share more info as needed.

 

I will be out of the office Wed 3/25/26-Sun 3/29/26.

 

Warm regards,

Tracy

716-984-6436 Mobile

Fleckenstein, Tracy

?Cadman, William K;?+3 others???
?Lintvedt, Chris;?Kumar, Narendra?
@Wetzel, Tricia @Albi, Anthony J See Bill’s response and let us know if you agree/disagree.

Ali,
Muhammad
Muddassar

?Cadman, William K;?Fleckenstein, Tracy?
?Lintvedt, Chris;?Kumar, Narendra?
This is great. My apology if you told me same thing before.

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

Albi, Anthony J

?Fleckenstein, Tracy;?Cadman, William K;?+2 others??
?Lintvedt, Chris;?Kumar, Narendra?
I agree with the Member Preferences (Member Elections) managed by MeritainConnect being loaded into Data Vision. I’m unfortunately not familiar with the ‘DG member EOB preferences’ being stored in DV. It could have been added after I moved to Data Bridge perhaps?

 

Tricia – Do you agree and any thoughts on the ‘DG member EOB preferences’?

Wetzel, Tricia

?Albi, Anthony J;?Fleckenstein, Tracy;?+2 others??
?Lintvedt, Chris;?Kumar, Narendra;?Quinn, Charles?
I double checked within documentation and checked with additional resources and can confirm we did not bring in the EOB preference from DG.

 

As for the SmartComm preferences, we added in the following back in PI12 from CSI Web and I believe a preference from

 

 

Thanks,

 

Trish

Quinn, Charles
Wed 3/18/2026 3:08 PM
Bill, The DG EOB preferences field you are asking for is EMAIL.CONSENT on DEPENDENTS correct? If so, we added the below three fields to DB2 in Jan last year on story 219488. The reason Trish did not find the field in the member extract is because email
Lintvedt, Chris

?Quinn, Charles;?Wetzel, Tricia;?Albi, Anthony J;?+3 others???
?Kumar, Narendra?
I'm still a bit unclear on overall work flow of where this data starts/originates, and how it flows to other systems. Bill, is this a question for you (on the 40,000 view of how this data flows between DG, MC/MemCommService and Datavision)?

DG, and the email.consent - how are those fields populated and when? 
Is that part of an eligibility load - the email.consent, etc. fields being populated in DG?
Charles mentioned GET.DEPENDENT.EMAIL.INFO refers to that field. Do we PUSH that DG data into other systems?

Datavision pulls the data out of the MemberCommService SQL Db (those fields listed below).

MemCommService web service and it's Member_Service SQL db are used by MC and CSIWeb.
In MC, I believe on the register page and also on the COmm pref section of the user profile page.
In CSIWeb, the CSR can update the preferences on behalf of the member when they call if, if requested. This calls that central MemCommService which stores the data in it's Member_Service sql db tables.
I'm not aware of any nightly processes moving data out of this sql db into DG.
I'm also not aware of any nightly processes pulling mem comm pref/email.consent data OUT of DG. 
Thanks!
Chris
Lintvedt, Christopher B

?Quinn, Charles;?Wetzel, Tricia L;?Albi, Anthony J;?+4 others????
?Kumar, Narendra?
+ Bill H.

Bill H., see my question below. We're trying to understand where DG fits in the member communication preferences workflow. Are you familiar with this process, area?

Thanks,
Chris
Hoye, William E

?Lintvedt, Christopher B;?Quinn, Charles;?+5 others?????
?Kumar, Narendra?
Chris – I don’t see what problem you are trying to solve.  But I think you can assume that any data that’s not in DataVision can be added to DataVision if needed.  Depending on the application DataVision may or may not be the best source of data.  Depends on a few things including how quickly we want changes in settings to be reflected.

 

But I don’t think we know what our long term workflow is for all these data items and the other elements we expect to track in the IPP.

 

Hope that helps.

Lintvedt, Christopher B

?Hoye, William E;?Quinn, Charles;?Wetzel, Tricia L;+4 others?????
?Kumar, Narendra?
Hi Bill - I was trying to understand DG's place in this workflow. For example, if a member updates their comm preferences via the portal and that's saved in our MemCommService's related sql server db, is there an 'out of band process' that pushes any updates back into DG?

 

Thanks!

Chris

Hoye, William E

?Lintvedt, Christopher B;?Quinn, Charles;?+5 others?????
?Kumar, Narendra?
My understanding is that most of the  member preference controls stored in the Portal data store only relate to portal behavior.  When the member preference is something that affects processes outside the portal, e.g. EOB Preference, the member selected preference is passed back to DG via a service.

 

If that doesn’t do it then I think a meeting would be helpful to get context and try and get the right answers.

Offline Settings
DataVision preferences

?
Summarize this email
Ali,
Muhammad
Muddassar

?Fleckenstein, Tracy?
?Cadman, William K;?Lintvedt, Chris;?Kumar, Narendra?
Tracy,

 

Currently we have two different data sources for Member preferences:

 

DG member EOB preferences
Member preferences that being managed by MeritainConnect and CSI Web applications in a separate database
 

Can you check if DataVision only have DG preferences or both? If both, are we storing them separately or combined? Are we sending Member preference feedback to DG from MeritainConnect/CSI web database?

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

Cadman, William K

?Ali, Muhammad Muddassar;?Fleckenstein, Tracy?
?Lintvedt, Chris;?Kumar, Narendra?
Data Vision has both. I wrote the feature to load that data for DG and the digital SQL tables.

 

 

 

Bill Cadman (he, him, his) - Technical Advisor, TPA&PS Technology

Meritain Health, Suite 204, 3100 West Road, East Lansing MI 48823

 

Fleckenstein, Tracy

?Ali, Muhammad Muddassar;?Wetzel, Tricia;?+1 other?
?Cadman, William K;?Lintvedt, Chris;?Kumar, Narendra?
Hello,

 

Data Vision (DV) is a transformed view of OLTP data for the purpose of reporting, analytics, and data extracts.

 

My understanding is that DV member preferences (I think being used for SmartComm) is being sourced by DG but I added @Wetzel, Tricia (DV PO) and @Albi, Anthony J (Data Engineer) to this thread so they can correct me if I am wrong and/or share more info as needed.

 

I will be out of the office Wed 3/25/26-Sun 3/29/26.

 

Warm regards,

Tracy

716-984-6436 Mobile

Fleckenstein, Tracy

?Cadman, William K;?+3 others???
?Lintvedt, Chris;?Kumar, Narendra?
@Wetzel, Tricia @Albi, Anthony J See Bill’s response and let us know if you agree/disagree.

Ali,
Muhammad
Muddassar

?Cadman, William K;?Fleckenstein, Tracy?
?Lintvedt, Chris;?Kumar, Narendra?
This is great. My apology if you told me same thing before.

 

Muhammad Muddassar Ali

Principal ARCHITECT • AT ARCH - CLOUDINTEROP AFFILIATES

724-720-2139 (O)

412-297-9685 (C)

151 Farmington Ave

Hartford, CT

Albi, Anthony J

?Fleckenstein, Tracy;?Cadman, William K;?+2 others??
?Lintvedt, Chris;?Kumar, Narendra?
I agree with the Member Preferences (Member Elections) managed by MeritainConnect being loaded into Data Vision. I’m unfortunately not familiar with the ‘DG member EOB preferences’ being stored in DV. It could have been added after I moved to Data Bridge perhaps?

 

Tricia – Do you agree and any thoughts on the ‘DG member EOB preferences’?

Wetzel, Tricia

?Albi, Anthony J;?Fleckenstein, Tracy;?+2 others??
?Lintvedt, Chris;?Kumar, Narendra;?Quinn, Charles?
I double checked within documentation and checked with additional resources and can confirm we did not bring in the EOB preference from DG.

 

As for the SmartComm preferences, we added in the following back in PI12 from CSI Web and I believe a preference from

 

 

Thanks,

 

Trish

Quinn, Charles
Wed 3/18/2026 3:08 PM
Bill, The DG EOB preferences field you are asking for is EMAIL.CONSENT on DEPENDENTS correct? If so, we added the below three fields to DB2 in Jan last year on story 219488. The reason Trish did not find the field in the member extract is because email
Lintvedt, Chris

?Quinn, Charles;?Wetzel, Tricia;?Albi, Anthony J;?+3 others???
?Kumar, Narendra?
I'm still a bit unclear on overall work flow of where this data starts/originates, and how it flows to other systems. Bill, is this a question for you (on the 40,000 view of how this data flows between DG, MC/MemCommService and Datavision)?

DG, and the email.consent - how are those fields populated and when? 
Is that part of an eligibility load - the email.consent, etc. fields being populated in DG?
Charles mentioned GET.DEPENDENT.EMAIL.INFO refers to that field. Do we PUSH that DG data into other systems?

Datavision pulls the data out of the MemberCommService SQL Db (those fields listed below).

MemCommService web service and it's Member_Service SQL db are used by MC and CSIWeb.
In MC, I believe on the register page and also on the COmm pref section of the user profile page.
In CSIWeb, the CSR can update the preferences on behalf of the member when they call if, if requested. This calls that central MemCommService which stores the data in it's Member_Service sql db tables.
I'm not aware of any nightly processes moving data out of this sql db into DG.
I'm also not aware of any nightly processes pulling mem comm pref/email.consent data OUT of DG. 
Thanks!
Chris
Lintvedt, Christopher B

?Quinn, Charles;?Wetzel, Tricia L;?Albi, Anthony J;?+4 others????
?Kumar, Narendra?
+ Bill H.

Bill H., see my question below. We're trying to understand where DG fits in the member communication preferences workflow. Are you familiar with this process, area?

Thanks,
Chris
Hoye, William E

?Lintvedt, Christopher B;?Quinn, Charles;?+5 others?????
?Kumar, Narendra?
Chris – I don’t see what problem you are trying to solve.  But I think you can assume that any data that’s not in DataVision can be added to DataVision if needed.  Depending on the application DataVision may or may not be the best source of data.  Depends on a few things including how quickly we want changes in settings to be reflected.

 

But I don’t think we know what our long term workflow is for all these data items and the other elements we expect to track in the IPP.

 

Hope that helps.

Lintvedt, Christopher B

?Hoye, William E;?Quinn, Charles;?Wetzel, Tricia L;+4 others?????
?Kumar, Narendra?
Hi Bill - I was trying to understand DG's place in this workflow. For example, if a member updates their comm preferences via the portal and that's saved in our MemCommService's related sql server db, is there an 'out of band process' that pushes any updates back into DG?

 

Thanks!

Chris

Hoye, William E

?Lintvedt, Christopher B;?Quinn, Charles;?+5 others?????
?Kumar, Narendra?
My understanding is that most of the  member preference controls stored in the Portal data store only relate to portal behavior.  When the member preference is something that affects processes outside the portal, e.g. EOB Preference, the member selected preference is passed back to DG via a service.

 

If that doesn’t do it then I think a meeting would be helpful to get context and try and get the right answers.
