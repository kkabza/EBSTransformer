									

ACE PRS ESB Infrastructure
System Architecture Document
Version 1.0





	Prepared By	Reviewed by	Approved By
Name	Kailashnath& Vamshi 	Krishnan T V	Cognizant
Role			
Signature			
Date			

 
		
		Revision History
Date	Doc. Version	Summary of Changes	Author(s)
06/01/2010	1.0	Version 1.0 published	Cognizant
			

 
Table of Contents
1.0	Introduction	7
2.0	Project Overview	8
3.0	Business & Technical Drivers	9
3.1	Non Functional	9
3.2	Constraints	11
3.3	Assumptions and Dependencies	12
4.0	System Context View	13
5.0	Functional View	16
5.1 Enterprise Service Bus	17
5.2 Channels	17
5.3 Service Inventory	18
5.4 Workflow	18
5.5 Service Registry	18
5.6 Monitoring	18
6.0	Key Architectural Consideration/Decisions	19
6.1	Tools & Technologies	21
6.2	ESB Guidelines & Principles	21
7.0	Logical View	23
8.0	Solution View	26
8.1	ESB Core Infrastructure	28
8.1.1	ESB Core	28
8.2	ESB Services	29
8.2.1	On-Ramps	29
8.2.2	Off-Ramps	30
8.2.3	ESB Process Flow	31
Component & Services View	32
8.3	Data Communication Patterns	32
8.3.1	Synchronous	32
8.3.2	Asynchronous outbound	33
8.3.3	Asynchronous Inbound	34
8.4	Component View	34
8.5	Common Framework Artifacts	36
8.5.1	Common Data Model	36
8.5.2	Master Data Management	37
8.5.3	Reusable assets	37
9.0	Deployment View	39
10.0	Conclusion	41
10.1	Benefits	41
10.2	Justification	41
10.3	Risk	41
10.4	Architectural Recommendations	42
 

Definition & Acronyms
CCS	Claims Components Solution
ESB	Enterprise Service Bus
CLUE	Comprehensive Loss Underwriting Exchange
OFAC	Office of Foreign Assets Control
RIS	Recording Interface System
WCF	Windows Communication Foundation
BAM	Business Activity Monitor
BRE	Business Rules Engine
EFT	Electronic Fund Transfer
ACH	Automatic Clearing House
PMSI	Pharmacy Medical services and equipment Settlement Solutions
PIP	Personal Injury Protection
SOA 	Service Oriented Architecture 

 
1.0	Introduction
The purpose of the document is to define the architecture of CCS ESB Integration platform with the objective of capturing the context, structure and behavior of the system to enable design, implementation and roll-out in a structured manner. It covers the following perspectives and may contain references wherever applicable. 
	Architectural Drivers
This section details the architectural and business drivers of the ESB implementation.  The non functional drivers are explained along with constraints, dependencies and assumptions.
	System Context 
System context view provides a perspective of ESB with different interfaces and their interaction mechanisms.
	Functional View
Functional view provides view of BizTalk ESB and its sub systems. 
	Key Architectural Considerations and Decisions
This section explains the considerations for the architecture. The section is explained through the problem in hand, the options, assumptions, motivation and finally the decision.
	Logical View
Logical view explains the ESB logical architecture. The various aspects of ESB are covered in this section.
	Solution View
Solution view provides the BizTalk architecture for CCS solutioning. 
	Components and Services View
Component view goes a level deeper to explain the data communication patterns, the different BizTalk components used, BizTalk framework for implementation 
	Deployment View
Deployment view explains the physical architecture of BizTalk implementation.
 
2.0	Project Overview  
ACE PRS is ESB based integration architecture aligned with ACE Enterprise Architecture principles to build workflow and SOA enabled systems. BizTalk server and Microsoft ESB guidance 2.3 are introduced as ESB infrastructure technologies for interfacing between systems. A loosely coupled architecture is introduced abiding ESB guidance 2.3 SQL; resulting in “indirect” paradigm of interface interactions.
This project will pilot with CCS system to interact with its interfaces in a loosely coupled manner. The ESB infrastructure will provide synchronous or asynchronous interfacing for various internal and external interfaces. It will also facilitate batch processing, communications across various technologies and systems, tracking, notifications and exception handling across systems.
The solution aims at establishing communications between CCS and all its interfaces (as defined in the scope documents) and facilitate the data transformation and auditing required during the process.
 
3.0	Business & Technical Drivers 
ACE PRS envisions establishment of ESB based middleware infrastructure for application interfacing and standard service discovery. ACE PRS is replacing ACLAIM (the current claims processing system) with Accenture based claims system product, CCS. The CCS system would need to interface with various systems that ACLAIM was interfacing with. In this context, ACE PRS intends to introduce ESB as the “liaison” layer between CCS and other “interfacing” systems. 
The integration with different systems is envisioned in a loosely coupled manner. BizTalk server is introduced as a middleware infrastructure so that CCS can interact with internal and external interfaces in an indirect manner. The ESB infrastructure is aligned to enterprise roadmap of ACE.
3.1	Non Functional
Non functional requirements define the qualities and constraints that will affect the performance of the system. The properties that define the qualities are:
Availability 
ESB Integration	Source of Transaction Volume	Annual Estimate 2010	Annual Estimate 2011 (30%)	Frequency	# Trans by frequency
Address Verify	Claim Cardfile	21083	27408	Daily	105
Address Verify	Payments 	23407	30429	Daily	117
Acknowledgement	Acknowledgment 	1740	2262	Daily	87
Acknowledgement	ADL letters	13100	17030	Daily	66
Advocator	N/A	Too new to estimate		N/A	N/A
Scene genesis	TBD	TBD	TBD	TBD	TBD
Bulk Invoice Advocator	N/A	Too new to estimate		N/A	N/A
Bulk Invoice Enterprise	Payment(ENTERP)	1499	1949	monthly	162
Bulk Invoice Appraiser	Payment(SGAPPR)	4118	5353	monthly
	446

Bulk Invoice Metropolitan	Payment(METRO)	1387	1803	monthly	150
Safelite	Safelite Payments	916	1191	monthly	99
ESB Integration	Source of Transaction Volume	Annual Estimate 2010	Annual Estimate 2011 (30%)	Frequency	# Trans by frequency
Check File  Bank Processing	TBD	TBD	TBD	TBD	TBD
Check File Check Print	TBD	TBD	TBD	TBD	TBD
ISO ClaimSearch	ISO Requests	27314	35508	daily	137
OFAC Interface	Payments	23407	30429	Daily	117
PIP Medical Review	TBD	TBD	TBD	TBD	TBD
PMSI	Filenote	1021(3mos)	15927	Weekly
	306
Policy View	New Claims Established	9863	12822	daily	50
RIS	Reserve Trans	13806	17948	daily	69
RIS	Payment Trans	33147	43091	daily	166
RIS	updates				
SAFELITE	Safelite Claims	916	1191	weekly	23
CLUE	TBD	TBD	TBD	TBD	TBD
                                                Table - 1
This should be a highly available system and should be available 24/7 with no down time 
Scalability & Performance
The system should be scalable as more processes are added to the BizTalk. The transaction volume growth for CCS interfaces is expected 30% on a yearly basis. The transaction volume analysis for CCS interface is given below.
BizTalk provides different techniques for optimized performance of servers. Better scalable BizTalk solutions can be implemented by performing performance test on production servers. The best practices for performance testing is consolidated in the link http://msdn.microsoft.com/en-us/library/ee377064(BTS.10).aspx
The interfaces are broadly categorized into 3 patterns. The acceptable response time for each category is given below.


User Category	Average Response Time Required (in seconds)	Tolerable Response time (Upper limit) (in seconds)
Web service	3	5
Batch Inbound	5	8
Batch Outbound	5	8
Table - 2
Security
The current implementation of BizTalk does not require complex security model. The BizTalk server will be implemented in the same domain as CCS application. Further data encryption, secured transport will be implemented as per the needs of interface.
Maintainability
The maintenance plan for the system will be established during detailed design of the system 
Disaster Recovery
Disaster recovery plan is to be established will be established during detailed design of the system 
Auditing
The Audit log in ESB will be configurable with ability to turn on/off, create and delete daily logs 
Backup
Backup Plan is to be established will be established during detailed design of the system 
Archival
Archival Plan is to be established will be established during detailed design of the system
3.2	Constraints 

•	The ESB middleware is designed based on the interface requirements of CCS application only. Application of ESB for other interfaces would require the basic infrastructure defined in this architecture to be scaled commensurate to requirements.
•	The integration patterns identified are relevant for CCS interfacing. In future if any other integration patterns are required, they should be designed ESB framework should be enhanced as required.
•	Interfacing with mainframe systems may present constraints not as yet documented.
•	Interfacing with existing scheduling agents, databases may present constraints not as yet documented.
3.3	Assumptions and Dependencies
Assumptions
•	It is assumed that all the interfaces for CCS will fall either into the integration patterns –
o	Web service
o	Batch Inbound
o	Batch Outbound
o	Batch Inbound/Outbound
•	No special security requirements are needed for data transport.
•	All messaging for interfaces are stateless.
•	No transactional messages are envisaged between interfaces.
•	There is only XSLT transformation for ISO claim in the BizTalk layer.
•	Disaster Recovery and Deployment plans such as high availability, clustering etc are not considered in this document due to lack of information at the time of preparation
Dependencies
•	Data mapping accuracy is dependent on schema produced for the system integration data mapping for each interface.
•	Design for ABIZ, CLUE and Scene genesis, are dependent on finalization of the integration design.
•	Design for check print is dependent on the new printer configurations and changes to the software.
•	Integration testing is dependent on timely availability of interfaces both on CCS side and interface side.

 
4.0	System Context View 
ACE middleware services will establish integration between CCS and various in-house and third party systems. Each service implemented within middleware will be exposed as WCF services which will be consumed by CCS application for outbound communication. Similarly, for inbound services will consume the CCS exposed web services to submit messages like acknowledgement, invoices etc. The following diagram depicts the high level view of the different systems involved during the integration process between CCS and ACE PRS subscribed different systems. 

                                                                      Figure  - 1

CCS is a .Net based claims processing application which uses .Net 3.5 and WCF to connect to the external system. The interfaces that need to interact with the CCS application and transact data are provided in the table below along with the business purpose and the direction of messages.
Sl no	Connection point	Purpose	Direction
1	Acknowledgment	Acknowledgment letters	Batch outbound
2	Address Verification	Address Verification for claim	Synchronous
3	TyMetrix	Legal review	Batch outbound
4	Scene Genesis	Select an appraiser and initiate the assignment process	 Batch Inbound/Outbound
5	Bulk Invoices	TyMetrix	Batch Inbound
		Bulk Invoice - Enterprise Rent-A-Car Integration - Process Invoice	Batch Inbound/Outbound
		Bulk Invoice - Scene Genesis/Mitchell Integration - Process Appraiser Invoice	Batch Inbound
		Bulk Invoice - Metropolitan Interface	Batch Inbound
6	Check File	Bank Processing Interface	Batch Inbound/Outbound
		Check Print	Batch Inbound/Outbound
7	ISO Claim 	ISO Claim Search	Batch Inbound/Outbound
8	OFAC Interface	OFAC search	Batch Inbound/Outbound
9	PIP Medical Review Interface	claim file for medical bill review	Batch Outbound
10	PMSI Medicare Interface	Mandatory Insurer reporting	Batch Inbound/Outbound
11	Policy view	Policy search	Synch
12	Policy view	Policy attach	Synch
Sl no	Connection point	Purpose	Direction
13	RIS	Send claim messages	Batch Outbound
14	HSG	Auto glass claims processing	Synch
14A	HSG	Invoice file 	Batch Inbound
15	ABIZ		
16	CLUE		
17	RedZone		
18	RiskID		
19	GUS		













 
5.0	Functional View
CCS is a .Net based system and has its own native data formats. The ESB infrastructure interprets this data into structures that interface understands. This reduces the data customization effort in CCS. BizTalk server will route the message to interfaces performing required data transformation & translation. Introducing BizTalk is preferred as middleware infrastructure because
•	BizTalk is Microsoft’s Standard Production Class Enterprise Integration (ESB) tool.
•	Integration Technologies support (e.g. File Services, Web Services etc) that either system may need to implement is bundled with BizTalk Server.
•	BizTalk is packaged with business rules engine (BRE) which can be used to abstract frequently changing business variables into rules
•	BizTalk is packaged with the Business Activity Monitor (BAM) for the latest and live reports on business data
•	BizTalk Server 2013 R2 has relatively cheaper licensing options.
All the application services and ESB core services that are deployed as part of the middleware would be available for reuse for the future applications to achieve specific business functions. 
To achieve the goal of establishing service oriented architecture through the ESB layer, Middleware would be using the ESB Guidance 2.3 from Microsoft®. The following diagrams elucidate the functional view of the proposed solution
 
Figure 2 – Functional view
5.1 Enterprise Service Bus
The Enterprise Service Bus manages the activities of the sub-systems within it.
•	Sub-systems within ESB act as trusted users, with their own credentials for authentication and authorization.
•	Messages are tracked for delivery, acknowledgements for message receipt are issued, and messages are persisted during failure conditions.
•	Qualities of Service levels are monitored for performance, availability, regulatory compliance, accessibility, integrity, and security.  These levels will be determined in the Service Level Agreements implemented in the Service Registry

5.2 Channels
The ESB provides Consumers and External Partners with publicly accessible channels for receiving and sending messages.
•	Provides legacy applications and External Partners with a variety of transport protocols for submitting messages and non-message files, including web services, SFTP and File
Is this sentence complete – please list the transport protocols being implemented for CCS
•	Messages are schema validated on receipt to verify harmlessness- please explain further, i.e. give an example
5.3 Service Inventory
The Service Inventory is a superset of complimentary services governed by the Enterprise Service Bus. It includes the Services Framework, internal services that support business processes, and native services that form the technical offering of the ESB.
•	The Services Framework provides the publically visible web services used to send and receive messages.
•	Content validation of messages is performed within workflow.
•	Common Utility services, for messaging, security, data access, monitoring, authentication, translation, exception handling, and event logging are available horizontally to other services and applications within the ESB.
5.4 Workflow
Business processes executed within the Enterprise Service Bus are defined through tooling that employs industry standard notation, such as Business Process Modeling Notation.  Using services that are visible within the Service Registry, the workflow engine provides the ability to combine services into service compositions. Make note of any usage for CCS or note not being used. 
5.5 Service Registry
The Service Registry publishes and manages services implemented in the Service Inventory.  It provides auditing capabilities to identify compliance with governance standards defined by the ACE and sets the service level expectations under which each service operates.
5.6 Monitoring
The Enterprise Service Bus provides operational monitoring capabilities through the Business Activity Monitor (BAM) for use by production control teams.
BAM provides real time operational information about the status of business processes executing within the ESB.
 
6.0	Key Architectural Consideration/Decisions
The motivation for ESB is to build an enterprise message bridge for ACE PRS. Specifically the ESB should be able to handle the interface requirement for CCS application.
Subject Area	ESB Deployment Model
Architectural Decision	Defining the ESB Deployment model for the integration between different systems.
Problem Statement	The need for a deployment model for ESB so that the architecture supports the solution requirements. 
Solution Requirements:
•	Loosely coupled interfacing with different systems
•	Interface communicates in their native language and ESB transforms the data.
•	Host services in ESB that can be accessed enterprise wide.
•	Implement real time integration for interfaces.
Assumptions	The following assumptions need to be identified for implementing ESB
•	Infrastructure design: Generic but interface requirements of CCS only considered.
•	Integration: Patterns considered for ESB are synchronous (web service) and asynchronous (FTP based)
•	Deployment: The infrastructure will be deployed for ACE PRS requirements.

Motivation	The ability to build a middleware infrastructure that supports real time and batch based interactions. The infrastructure will have the capability to support other integrations of similar pattern.
Alternatives	Interaction Patterns
Option 1: Request Response
                Handles request response style of communication.
Option 2: Request/multi response
                Similar to request/response but more than one response can be
                sent.                 
Option 3: Event propagation
                Events are distributed to subscribers. Services can add
                Themselves to the subscriber list.
Mediation patterns
Option 1: Transform
                 Translates the message payload from the requester's schema to
                 the provider's schema. This includes batching, de batching or
                 encryption.  
Option 2:   Enrich
                 Augments the message payload by adding information by  
                 customization parameters defined by the mediation.
Option 3: Route:
                Changes the route of a message, to the service that supports the 
                requirement of the requestor.
Complex patterns
Mediation and interaction patterns are combined to realize complex patterns.
Option 1: Canonical mapping
                The transformation engine can implement a canonical adapter in 
                 Which the messages and business object used across are
                 Normalized to a common format.
Deployment patterns
Option 1: Global ESB
               All services share one namespace, and each service
               provider is visible to every service requester across a
               heterogeneous, centrally administered, geographically distributed 
               environment. Used by departments or small enterprises where all 
               the services are likely to be applicable throughout the 
               organization.
Option 2: Directly connected ESB
               A common service registry makes all of the services in several   
               independent ESB installations visible. Used where services are 
               provided and managed by a line of business but made available 
               enterprise-wide. 
Option 3: Brokered ESB
                Bridge services that selectively expose requesters or providers   
               to partners in other domains regulate sharing among multiple
               ESB installations that each manages its own namespace. 
               Service interactions between ESBs are facilitated through a 
               common broker that implements the bridge services. 
Option 4: Federated ESB 
               One master ESB to which several dependent ESBs are 
               federated. Service consumers and providers connect to the 
               master or to a dependent ESB to access services throughout the
                network. 
Decision	Please site examples for the following patterns.

Interaction Patterns
    Request Response was found to be the ideal for this implementation.
Mediation patterns
    The 3 options identified are appropriate in this implementation. They will be used as appropriate in different scenarios.
Complex patterns
    Analyzing the requirements it’s concluded that there will be necessity to        combine the mediation and interaction patterns to create complex patterns. Canonical mapping will be used for a common data pattern creation.
Deployment patterns
    Global ESB is the ideal candidate to implement the middleware infrastructure. It provides the simple infrastructure to host and provides the paradigm for the organization to scale up at a later stage. 
Justification	ESB road map is in the process of creation. This implementation is for the first time in the organization. Hence the architecture visualized is simple and robust at the same time it can scale to future growth as well.
                                                                                 Table - 4
6.1	Tools & Technologies
BizTalk server is chosen as the implementation platform. This is in line with ACE technology alignment to Microsoft and related technologies. The list of software is
•	Microsoft BizTalk Server 2013 R2
•	Microsoft SQL Server 2014
•	Microsoft Visual Studio 2013 / Team Foundation Server 
•	Microsoft ESB guidance 2.3
•	Microsoft IIS Server
Free downloads - Microsoft/Open source
•	BizUnit/NUnit for unit testing  - Microsoft
•	 Loadgen for performance testing - Microsoft
•	PAL - Performance analyzer of logs – Open source
•	Orchestration profiler -  Open source
•	MSBuild framework for build automation - Microsoft


6.2	ESB Guidelines & Principles
The motivation for implementing an ESB is to build an enterprise message bridge for ACE PRS. Specifically the ESB should be able to handle the interface requirement for the CCS application.
BizTalk server was chosen as the implementation tool. This is in line with ACE technology alignment to Microsoft and related technologies.
The PRS ESB implementation is guided by the following principles.
•	All synchronous requests in ESB will be implemented as web services.

•	The ESB’s primary function is to act as a message router for interfacing systems. ESB will perform required message transformation & translation to effectively route the message. 

•	For all inbound batch processes the ESB will not perform any business logic processing of the message. The messages will only be transformed the way interface interprets.

E.g. Read the message from a flat file segregate record by record and transform into the native format of the interfacing application, call the service in interfacing application to post the message.
•	For inbound and outbound asynchronous messages, the ESB will perform data format checks. If the message fails during this process, a message is sent to acknowledgement service. 

A.	Acknowledgment given by ESB for message transmitted to 3rd party interfaces. This status will be transmitted or not transmitted.

B.	Acknowledgement provided by 3rd party interfaces for receipt of messages. The ESB will route this message back to interfacing application after receipt from the 3rd party interface.
•	All systems communicate in their native format with ESB unless the ESB capabilities or design restricts such messaging.

Required data translation and transformation is performed so that the data is interpreted by other systems.
E.g. For EFT payment outbound messages, the interface will provide message in XML format in a WCF service. The ESB will transform this message into a flat file as required by 3rd party EFT payment interfaces.
•	The ESB will log all exceptions handled and will provide a complete stack trace. 

•	The Audit log in ESB will be configurable with ability to turn it on/off, create daily logs and delete them.
 
7.0	Logical View
 
Figure 3 Logical view
Consumer Interfaces
Consumers for ESB will be CCS web services and interfaces that are attached to the enterprise service bus.
Business Process
This layer includes service orchestrations and compositions. Service composition flows and choreographies are established to accomplish a use case. The services that are aggregated as a business process can be individual or a composite service. This layer includes information exchange flows between (mentioned above in the system context view) participants and business entities to achive business goals.
In the ACE ESB infrastructure this layer will transform and translate the native CCS interface data to the universal format of the interface. Business logic implementation will be limited to data validation, service orchestrations and data format translation before invoking the service layer. The Business Process layer also provides for detailed auditing and logging of the messages flowing through it. 
Service
This layer consists of all the services defined within the ESB infrastructure. The service layer will contain the service descriptions (design time as well as runtime service contract descriptions) and the container for implementing the services. These services will be platform agnostic.
The service specification will include:
• The service policy document
• ESB management descriptions
• Any service dependencies.
In the ACE ESB infrastructure implementation this layer will have all the interface services defined and exposed for internal applications to consume.  
Service Components
This layer contains software components, each of which provide the implementation or“realization” for a service, or operation on a service. They “bind” the service contract to the implementation of the service in the operational systems layer. Service components are hosted in containers which support a service specification.
In the current release of the ESB infrastructure the services are simple and do not require components for complex realizations. 
Operational Systems
This layer captures the new and existing organization infrastructure, including those involving actors, needed to support the middleware infrastructure. This includes:
1. All infrastructures to run the middleware infrastructure and its components.
2. All assets required to support the functionality of the service in the SOA, including custom or packaged application assets, new services, services created through composition or orchestration, infrastructure services.
The different internal and external applications that are interfaced through middleware infrastructure form part of the operational system. Internal applications are 
•	Recording Financials
•	Policy view
•	ABIZ
•	Acknowledgement

Integrations
The integration layer is the enabler for the ESB infrastructure that provides the capability to mediate, transform, route and transport service requests from service requestor to service provider. It also provides support for the ESB’s common business rules capability  This layer provides an integration of business process, service, service components and operational layers.
Quality of Service
The Quality of Service layer provides the service infrastructure solution lifecycle processes with the capabilities required to ensure that the defined policies and NFRs are adhered to. This layers deals with issues like:
Monitoring and Capture of service and solution metrics in an operational sense and signalling non-compliance with non-functional requirements (NFRs) relating to the salient service qualities and policies associated with each ESB infrastructure  layer.
The QOS layer establishes NFR related issues as a primary feature of ESB infrastructure and provides a center point for dealing with them in any given solution. It provides the means of ensuring that the ESB infrastructure meets its requirements with respect to e.g.:
• reliability
• availability
• manageability
• scalability
• security
Information
This layer includes information architecture, business intelligence, meta-data considerations and ensures the inclusion of key considerations pertaining to data architecture and information architectures. This includes meta-data content that is stored in this layer.
Governance
Governance model for the ESB is in progress. This section will be updated once modeling activity is complete.


 
8.0	Solution View
The Ace Enterprise Service Bus is a platform that provides centralized claim transaction processing services for consuming applications.  Through consolidation of specific business processes to a core location, ACE achieves:
•	A common repository for transformations, partner connections, regulatory compliance standards, business rules, and other interfaces, reducing the need for redundant implementations across the enterprise.
•	A secure environment designed to meet predicted peak time and annual transaction volumes, which can scale to accommodate new transaction types or volume
•	Increased organizational agility through the implementation of a Service-Oriented Architecture.
The proposed architecture for this project is the ‘Enterprise Service Bus (ESB) Pattern’ built on BizTalk Server 2013 R2.  This architecture will provide a consistent message exchange pattern between the service consumers and service providers.  This design will provide a layer of abstraction between all entities which, in turn, provide business the flexibility to quickly adapt to the change business needs while limiting the overall impact to other business processes. 
The ESB Design will provide for Dynamic Message and Business Process Resolution and Itinerary-based routing Messaging Patterns.  The benefit of this design is that the consumer of an application tier service does not need to be aware of the location and interface of said service, rather ESB infrastructure will resolve the incoming message to the appropriate Itinerary and the Itinerary will be configured to know what services, or resources, to call and how.  It supports one-way (Request) and two-way (Request/Response) message requests.
Another powerful benefit of the ESB Design is the ability to define and change business process flow while limiting the impact or awareness to the Service Consumers or Service Providers.  If a new business process is required utilizing currently deployed service resources a new itinerary can be created routing the message to those services.  The same can be said for current business processes in the event of a change.  If the business need or requirement changes, the business process can be updated simply by updating the Itinerary without having to make changes directly to the Consumer or Provider, assuming the appropriate message data is available.
Following is a brief overview of the solution design.  
Figure 4 – Solution view
All the CCS web service, external interfaces, databases, third party services etc connect to the ESB middleware layer which routes all the requests from the various systems to their destination. The middleware layer provides the following functionalities for enabling message transactions

8.1	ESB Core Infrastructure

 
                                                                     Figure - 5
8.1.1	ESB Core
The ESB Core provides the main ESB processing functionality.  The ESB Core consists of three main components; these are Itinerary Services, Resolver/Adapter Provider Framework, and the Exception Management Framework.  These artifacts are implemented as a collection of web services and orchestrations built on top of BizTalk Server 2013 R2
8.1.1.1 Itinerary Service
The collection of Itinerary Services will be utilized collectively as part of the design to Implement Itinerary Based Routing.  These services are not called upon explicitly, but rather implicitly through the utilization of the On-Ramps and ESB Pipelines
8.1.1.1.1 Transformation Services
The Transformation Service will be utilized in the Itineraries each time a map or transformation is defined in the business process.
8.1.1.1.2 Routing Services
The Route Service is utilized as part of Itinerary processing to interpret the Itinerary that has been selected at assigned to the Message Context.  The Route Service will determine the path of the message based on that Itinerary to complete the business process.
8.1.1.2 Resolver/Adapter Provider Framework
The Resolver and Adapter Provider Framework support itinerary, transformation, and endpoint resolution and routing.  Similar to the Itinerary Services the Resolvers and Adapter Providers will be utilized implicitly as part of the design to implement Itinerary Based Routing.   As part of the On-Ramp configuration Itinerary Resolvers will be utilized to identify the Itineraries and Transformations/Maps used within the business process.  It will be part of the configuration steps to set up the necessary artifacts for these Resolvers. Adapter Providers will be utilized to sets specific properties of registered Microsoft BizTalk Server adapters prior to a message being sent to a Generic Off-Ramp.
8.1.1.3 Exception Management Framework
The ESB Exception Management Framework is included as part of the ESB Toolkit 2.0.  The Exception Management framework provides global exception handling and routing functionality both from within BizTalk and externally to other systems or other applications through web service interfaces.   Additionally ESB Management Portal is provided as part of the ESB Toolkit 2.0 which allows for the viewing and management of all configured applications exceptions.  Through the ESB Exception Management Portal a system administrator can view exceptions and save messages being processed at the time of the exceptions.  The portal also provides administrator the ability to configure Alerts and Notifications which send e-mail messages to the appropriate system owners in the event of an error or exception in their applications. Also there is a feature of repair and resubmit the messages, the message which threw the error can be updated and resubmitted again for processing.
The ESB Design for Exception Management will implement the following steps: 
1.	The ESB Exception Management Framework will detect and capture errors that occur within the BizTalk Messaging Environment. 
2.	The ESB Exception API will be used to capture the exceptions and errors that are returned from a Service Response.  A Fault Message will be created and published to the ESB Exception Web Service.   The Fault message will contain the Exception that occurred during processing as well as the Message being processed at the time of the exception.

8.2	ESB Services

The ESB Services components expose all of the Enterprise Service Bus core functionality to entities outside of the ESB and the BizTalk environment both as WCF services as well as traditional ASP.NET ASMX services.  This would enable systems and applications, potentially residing on different platforms or environments, to interact with the ESB and take advantage of its capabilities.
8.2.1	On-Ramps
The ESB Toolkit provides a variety of “On-Ramps”.  An ESB On-Ramp is essentially a standard BizTalk Receive port which has been configured to utilize a custom receive pipeline deployed with the toolkit for dynamic message resolution and itinerary selection.
8.2.1.1 Dynamic Resolution
Dynamic Resolution of the message enables dynamic discovery of trusted business process Itinerary based upon Message Type and Message content/context using BRE Resolvers. This process will resolve and validate the message. 
1.	If a schema does not exist for the message, a Fault Message will be returned to the Consumer application. 
2.	If the required data is missing from the message, a Fault Message will be returned to the client. 
3.	If the message is valid, then the Itinerary will be resolved
8.2.1.2 Itinerary Based Routing
When Itinerary-Based Routing is utilized the Itinerary selected as part of the Dynamic Resolution in the On-Ramp pipeline will be assigned to the context of the message.  Having this itinerary as part of the message context provides the Routing Service and Messaging Broker the appropriate information necessary to route the message between the various services, both Business and Transformation, in the business process.
8.2.1.2.1 ESB Itinerary Messaging Services 
When a message is being processed in a BizTalk Server pipeline, using ESB itinerary Messaging services reduces message latency. By implementing back-to-back services in a single pipeline, it is possible to transform a message multiple times and route the message to its endpoints with only a single persistence to the Message Box database. Additionally, messaging-based processing eliminates the additional resource cost of orchestration processing. Messaging-based processing is less resource intensive and provides faster processing than orchestration-based processing.
8.2.1.2.2 ESB Itinerary Orchestration Based Processing
If orchestration-based processing is required, the resolver framework can also be utilized to map messages between orchestrations.  Orchestrations that are part of the business process will be direct bound to the message box utilizing standard BizTalk Routing capabilities.

Basic Itinerary Processing Steps 
1.  The Itinerary will define the steps (Services) required for processing the message. 
2.  Transform the ESB Request Message to the Service Request Message Map. 
3.  Send the Service Request Message. 
4.  Receive the Service Response Message. 
5.  Transform the Service Response Message to the ESB Response Message if necessary. 
6.  If the Service returns an exception or error, then a Fault Message will be returned to the client. 
7.  If the Service does not return an exception or error, the ESB Response Message endpoint is resolved and the ESB Response Message is sent to the client.
8. Repeat steps for Business Process that will call multiple service endpoints.

8.2.2	Off-Ramps
An ESB "off-ramp" corresponds to a BizTalk dynamic send port. As an itinerary is being processed, values are promoted to the context properties of the message to tell the dynamic send port how and where the message is to be sent. 
8.2.3	ESB Process Flow
The below diagram shows the end-to-end steps, using a single Itinerary, which will be implemented using the ESB Toolkit 2.0

 
                                                                            Figure - 6 

Component & Services View 
8.3	Data Communication Patterns

The different integration patterns identified for CCS system interfacing are 
 
                                                                             Figure - 7

8.3.1	Synchronous 
Synchronous messaging describes communications between two systems, where the system places a request and waits for a response before it continues processing. WCF Web services are utilized for providing synchronous processing. Service contracts and data contracts are defined for each service and various web methods cater to individual functions. Since it is a synchronous model, the requestor gets the response immediately. 
 From CCS, the ESB receives messages by a service call. The message is translated and the ESB invokes the service at the external interface. The response is received and transmitted back to CCS after required transformations and formatting. There will be time out period set for each external service, beyond which the system will throw an exception.
BizTalk implements the aggregation and segregator patters to consolidate individual messages to a bulk message or split a bulk message to individual messages. Based on the canonical model defined in the application further mapping will be done to the downstream systems. 
The following is the list of interfaces using Synchronous processing
Sl no	Connection point	Purpose	Direction	Probable BizTalk Design Pattern
1	Policy view	Policy search	Synch	Sequential Convoy
2	Policy view	Policy attach	Synch	Sequential Convoy
3	Safelite	Auto glass claims processing	Synch	 
4	Address Verification	Address Verification for claim	Synch	Splitter

8.3.2	Asynchronous outbound
In an asynchronous process, the sender does not expect an immediate response to the request submitted. If a response is due, it might be made available to the sender through a different channel at a different point in time. Out bound batch processing is an asynchronous process where the requestor pushes the message into the middleware. 
In case of a scenario when CCS pushes the payment messages record by record into middleware, each message will be translated and aggregated into a batch file using BizTalk aggregator pattern. This batch file will be placed in a location where various banks (Bank of America, Atlantic Mutual etc.) can pick up and process the file
The following is the list of interfaces using batch outbound processing
Sl no	Connection point	Purpose	Direction	Probable BizTalk Design Pattern
1	Bulk Invoices	Bulk Invoice - Enterprise Rent-A-Car Integration - Process Invoice	Batch outbound	Aggregator
2	Check File	Bank Processing Interface	Batch outbound	Aggregator
3	Check File	Check Print	Batch outbound	Aggregator
4	ISO Claim 	ISO Claim Search	Batch outbound	Aggregator
5	OFAC Interface	OFAC search	Batch outbound	Aggregator
6	PMSI Medicare Interface	Mandatory Insurer reporting	Batch outbound	Aggregator
7	Acknowledgment	Acknowledgment letters	Batch outbound	Aggregator
8	Advocator	Legal review	Batch outbound	Aggregator
9	PIP Medical Review Interface	claim file for medical bill review	Batch Outbound	Aggregator
10	RIS	Send claim messages	Batch Outbound	Aggregator


8.3.3	Asynchronous Inbound
Inbound message are messages from external systems that come into the middleware.
In the case of Bulk invoices, messages are posted in the file location. Middleware polls for the message. The message is split into individual records using the BizTalk Splitter pattern. The records are updated into CCS by making a sequence of service calls as the number of records in the message. The batch integrity is handled.
Sl no	Connection point	Purpose	Direction	Probable BizTalk Design Pattern
1	Bulk Invoices	Advocator 	Batch Inbound	Splitter
2	Bulk Invoices	Bulk Invoice - Scene Genesis/Mitchell Integration - Process Appraiser Invoice	Batch Inbound	Splitter
3	Bulk Invoices	Bulk Invoice - Metropolitan Interface	Batch Inbound	Splitter
4	Safelite	Invoice file 	Batch Inbound	Splitter
5	Bulk Invoices	Bulk Invoice - Enterprise Rent-A-Car Integration - Process Invoice	Batch Inbound	Splitter
6	Check File	Bank Processing Interface	Batch Inbound	Splitter
7	Check File	Check Print	Batch Inbound	Splitter
8	ISO Claim 	ISO Claim Search	Batch Inbound	Splitter
9	OFAC Interface	OFAC search	Batch Inbound	Splitter
10	PMSI Medicare Interface	Mandatory Insurer reporting	Batch Inbound	Splitter
The following is the list of interfaces using batch inbound processing














8.4	Component View

The component view is explained through various components involved in the middleware solution. It comprises the ESB framework and BizTalk core components.
The component view lists existing and envisioned components and services related to the application. As the development model is iterative, it is expected that the components and services will be added as new use cases are defined. 
Message Flow
The following section details the message flow between Safelite™ and CCS interfaces
•	Safelite initiates the process by sending a request to the Policy Search Service exposed by the middleware component. The request will contain search data such as loss date, policy number or insured name, insured address (including city, state, and zip)
•	Once the request comes from Safelite, through the On Ramp, the Resolver service identifies the itinerary to be run for that particular input file using the business rules engine. 
•	The itinerary service invokes the specific itinerary which in turn calls the required Transformations and Orchestrations through the respective service. The Policy View Service is invoked to retrieve all the details of the Policy.
•	Once the Policy view results obtained, they are passed on back to the Safelite Interface.

The bulk invoices are posted from Safelite on a weekly basis. The corresponding flow is detailed below
•	Safelite sends claim data (including invoices) via FTP on a weekly basis to CCS. 
•	The middleware processes the bulk file and split the same into individual invoice files.
•	The individual invoice files are passed on to CCS service which will be listening for the same.
The Exception Management service, Routing Service and the various custom services help achieve the required business functionality.
 
                                                                 Figure – 8

8.5	Common Framework Artifacts
The following are some of the common components that will be developed as part of the ESB implementation
8.5.1	Common Data Model
The solution will have a common data model for standardizing the communication inside the middleware layer. Since this is a loosely coupled architecture, any changes on the input and the output systems etc should have minimum impact on the middleware design. The design should also be scalable and adaptable to future additions to the ESB. 
For these reasons, an entire set of canonical schemas will be developed and all the data transformations inside the ESB would be based upon the canonical data model. The Canonical schema would contain data definitions for all the business data that is being transacted between CCS and the different interfaces. 

8.5.2	Master Data Management
There will be master data for each Interface, which is required to transform the CCS input message to interface specific data format. This master data will be stored in the SQL Server database RDBMS tables. This data will be configured for each interface and will serve as a data dictionary. Cryptic values in the data file (like Product Codes - PI,AI etc) will be mapped to detailed descriptions (like Personal Insurance, Auto Insurance, etc) It will also serve as a place where system critical static data can be configured and altered easily for each system
This introduces a loosely coupled architecture which facilitates future additions/modifications/deletions to the data definitions. It also provides a seamless way of modifying the data without affecting the installed applications.

8.5.3	Reusable assets
The design considers developing a set to .Net components for various repetitive activities. The following provides a brief list of components that may be required for the proposed solution.
•	Configuration Data Class - .Net classes to retrieve configuration information from SSO DB or configuration file. This class can be called to retrieve configuration details to be used during the runtime of the application. This class will also include functions to retrieve the master data for the particular interface from SQL server databases.
•	Business Rules Helper classes – These classes would be developed to provide for any complex business rules logic that needs to be evaluated for the application. 
•	Custom message transformations functions (Functoids) – These components would further enhance the inbuilt functionality of BizTalk to transform the messages. These may range from simple format modifiers to XSL transformation and loops to create an output file
•	Pipeline Components – There are reusable artifacts that help with formatting of messages, modifying namespaces, adding/removing special characters from input files, compress/decompress incoming and outgoing files, encrypt/decrypt the traffic, archive incoming and outgoing files etc
•	Event Logging –Common components that can used to write database/event log messages for maintaining the state information of the application at each step of the business process are required. This information will be used when debugging the application and can be switched off or on a production setup.
•	Testing and Deployment framework –Dedicated class libraries for the automated testing needs during the development will be created. These libraries would be necessary to deploy a test-based-development methodology. The automation of deployment activities can be achieved with the MS Build framework, power shell scripts or customized windows applications. A series of .Net functions would facilitate this deployment automation
•	Services – Any reusable services to perform the process or backup, emailing a particular user/group, monitoring a particular application for data transmitted volumes etc. All the current services deployed on the ESB can be reused by existing and new applications, using the service registry and discovery mechanisms available in the application.
•	Adapter Development - To connect to end points that are not supported with out of the box functionality in BizTalk, custom adapters will be developed. These components take care of connecting, authentication and authorization, handle data consistency, retry mechanisms etc.  












 
9.0	 Deployment View 

 
The proposed solution for the ACE CCS implementation will address both the requirements of a high availability system with adequate failover scenarios. The four BizTalk servers configuration seen in the diagram is scalable to higher loads and throughput requirements as more applications are added to the ESB.
The above deployment model would provide the necessary capabilities to cater to the current loads as per the NFR transaction volumes and handle future increases in load. 
Of the four BizTalk servers that are deployed, one server will be dedicated for the receiving messages and the other server would be dedicated for sending messages out of the ESB. The two processing servers would be utilized for running all the transformation and business logic implemented inside the middleware. These two servers will be clustered in an active-active mode to enable load sharing between the two.
Two SQL servers would be deployed in 2 way active clustering with an associated SAN storage. SQL Analysis services would have to be deployed on a separate server
One of the SQL servers will have the shared responsibility of running the Microsoft Single Sign On (SSO) service. This service will establish a single point of authentication for the web services using Active Directory user and group accounts. 
The various internal applications like CCS and the interfaces are represented as “Internal LOB Applications”. External traffic would be passing through a firewall. Active directory server and Operations Manager, File share and FTP servers would be external to the setup but necessary for end to end integration.
The deployment view will be revisited further to capacity planning exercise to provide an accurate solution.
 
10.0	  Conclusion
10.1	Benefits

Benefits of using BizTalk and ESB for the ACE PRS landscape are 
•	Better control on the entire business landscape
•	Providing a common platform to integrate other systems of ACE PRS with existing services and other external applications.
•	Simplify future integration of ACE PRS applications which are built on disparate technologies and operating systems
•	Set the base to enable ACE PRS towards service oriented architecture, ease of maintainability, scalability and upgradability.
•	Utilizes ACE’s strategic ESB platform.
10.2	Justification

The ACE PRS is a highly complex environment with different kinds of data communications such as batch files, scheduled jobs, vb applications, mainframes systems, legacy databases, .Net applications, external and in-house web services etc. Also ACE PRS has e various messaging patterns such as synchronous and asynchronous message calls, batch processes, etc. 
An integration platform like BizTalk is best suited to facilitate transactions of information between such technologically and functionally varied systems. Also BizTalk server and ESB 2.0 from Microsoft provide many inbuilt services for exception handling, routing, a business rules engine and message broker services providing a comprehensive platform for building the middleware architecture,
ESB architecture provides multiple advantages in comparison with a combination of isolated web services and windows applications to achieve business goals. It provides a business integration platform on which future services and business functionalities can be added with very less impact on external systems. It is scalable from point solutions to enterprise wide deployment. It provides flexibility of distributed service deployment, incremental upgrades with minimal down time and provide faster accommodation of existing systems.
10.3	Risk

The possible risks associated with the proposed middleware layer and the corresponding mitigation plans are listed below,
Risk 1 
All interfacing transactions will pass through ESB and hence the load that needs to be handled by ESB will be high. If ESB is implemented without proper clustering, it would potentially become a single point of failure
Mitigation - Based on the NFRs defined, detailed capacity planning will be conducted to determine the required load balancing needs and fail over mechanism.
Risk 2 
ESB introduces some latency due to messages flowing through an additional layer leading to overall performance degradation of the systems mitigation 
•	ACE PRS to invest in sizable infrastructure based on the capacity needs
•	Conduct performance testing 
•	Conduct Proof of concepts during the design phase to determine the key performance related bottlenecks and revisit the solution to improve performance of ESB.
10.4	Architectural Recommendations

The following are the major and minor recommendations to define a scalable architecture. As the road map for enterprise architecture is established more recommendations will follow that will have short-term and long-term implications.  
S.No. 	Recommendation 	Rationale
1.		Create an enterprise road map for ESB implementation. Identify the priorities for system to be on ESB	Current architecture is detailed for CCS application and its interfaces.
2.		Identify all ESB integration patterns for better scalability	The integration patterns identified are with CCS application in mind. As BizTalk grows enterprise wide more patterns may emerge.
3.		Enterprise architecture should identify business process that can be service candidates	Currently interface integrations are done through ESB. No business process integration is happening through ESB.




