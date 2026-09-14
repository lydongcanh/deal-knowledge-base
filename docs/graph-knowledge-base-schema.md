# Graph Knowledge Base Schema

This page defines the production schema for knowledge extracted from Ansarada data-room content.

The graph knowledge base does **not** replace the existing application databases. Existing systems remain the source of truth for Data Rooms, Documents, DocumentFiles, users, permissions, indexes, and operational metadata. The graph stores only the references and derived knowledge required for cross-document understanding, provenance, reconciliation, and graph queries.

The governing principle is:

> **Keep the schema for representing knowledge stable and controlled, while allowing the domain ontology and extracted knowledge to evolve.**

## Design Principles

The schema must:

- represent knowledge from any document type
- preserve exact provenance for every extracted assertion
- distinguish source claims from reconciled knowledge
- support conflicts, amendments, supersession, negation, conditions, and temporal validity
- resolve different mentions of the same entity, concept, predicate, or value
- allow new domain concepts and relationships without changing the core storage model
- prevent the LLM from directly changing the governed schema
- support complete deletion and reprocessing when a DocumentFile changes or is removed
- remain strictly scoped to a Data Room
- provide a query-optimized domain graph without making that projection the source of truth

## System-of-Record Boundary

The existing Ansarada databases continue to own:

- Data Room metadata and lifecycle
- Document metadata and hierarchy
- DocumentFile metadata and lifecycle
- permissions and access control
- users, teams, and roles
- source file storage
- operational processing state

The graph knowledge base stores lightweight references to those objects so that derived knowledge can point back to them.

In LadybugDB, these are node types stored in node tables. They are **reference nodes**, not replacements for the existing relational tables.

```text
Existing application databases
        |
        | stable IDs
        v
Graph reference nodes
        |
        v
Evidence, Claims, Entities, Canonical Statements
```

## Schema Overview

```text
SOURCE REFERENCES
-----------------
DataRoom
  |
  v
Document
  |
  v
DocumentFile
  |
  v
Evidence
  |
  v
Mention

EXTRACTED KNOWLEDGE
-------------------
Entity
Value
Claim
ExtractionRun
ResolutionDecision

ONTOLOGY
--------
OntologyRelease
Concept
Predicate
TermLabel
OntologyConstraint
OntologyProposal

RECONCILED KNOWLEDGE
--------------------
CanonicalStatement
ReconciliationRun
Materialized Domain Graph

DERIVED APPLICATION OUTPUT
--------------------------
Finding
```

The processing direction is:

```text
DocumentFile
    |
    v
Evidence + Mentions
    |
    v
Claims
    |
    v
Resolution + Reconciliation
    |
    v
Canonical Statements
    |
    v
Materialized Domain Graph
    |
    v
Risk analysis, search, Q&A, and other features
```

## Identity and Keys

Every node table uses a stable primary key. Source-reference nodes reuse the existing Ansarada IDs:

```text
DataRoom      -> data_room_id
Document      -> document_id
DocumentFile  -> document_file_id
```

All graph-owned objects use generated immutable IDs:

```text
evidence_id
mention_id
entity_id
value_id
claim_id
resolution_decision_id
canonical_statement_id
...
```

Names, labels, source text, and normalized values must never be used as primary keys because they can change or collide.

Reprocessing creates a new ExtractionRun and new extracted objects. Previous objects are invalidated or superseded through lifecycle state rather than silently overwritten.

## Source Reference Nodes

### DataRoom

Represents the Data Room boundary for all knowledge.

Required field:

```text
DataRoom
`-- data_room_id
```

`data_room_id` is the existing Ansarada identifier.

The graph does not duplicate region, tenant, name, status, permissions, or other Data Room metadata. Those remain in the source systems.

Every room-derived node must be connected to exactly one DataRoom, unless the graph is physically isolated one Data Room per database or namespace.

### Document

Represents the logical Document already managed by Ansarada.

Required field:

```text
Document
`-- document_id
```

Relationship:

```text
(DataRoom)-[:CONTAINS_DOCUMENT]->(Document)
```

The graph does not duplicate the Document title, index path, permissions, or status unless a query-specific cache is intentionally added later.

### DocumentFile

Represents one uploaded file belonging to a Document.

A user may upload a new DocumentFile to an existing Document. Extracted knowledge must therefore point to the exact DocumentFile that produced it, not merely to the logical Document.

Required field:

```text
DocumentFile
`-- document_file_id
```

Relationship:

```text
(Document)-[:HAS_FILE]->(DocumentFile)
```

The source application remains authoritative for file version order, file metadata, storage location, and lifecycle.

## Evidence and Extraction Lineage

### Evidence

Represents an exact source location within a DocumentFile.

Evidence is the bridge between graph knowledge and the source content. It should identify the source precisely enough to reopen or retrieve the supporting passage, cell, slide, or region.

Required fields:

```text
Evidence
|-- evidence_id
|-- locator_type
`-- locator
```

Required relationship:

```text
(Evidence)-[:FROM_FILE]->(DocumentFile)
```

`locator_type` identifies how the location is interpreted, for example:

```text
text_span
pdf_region
page
section
spreadsheet_cell
spreadsheet_range
slide_region
structured_record
```

`locator` is a typed application object serialized for storage. Examples include:

```text
PDF:
{ page: 48, start_offset: 1052, end_offset: 1244 }

Spreadsheet:
{ sheet: "Employees", row: 72, column: "Base Salary" }

Presentation:
{ slide: 14, element_id: "shape-7" }
```

Evidence should reference existing extracted content by stable identifiers where available, such as a chunk ID or content object ID. The graph should not duplicate full document text when that content already exists in regional object storage or LanceDB.

Optional cached excerpts may be stored for performance, but they are not authoritative.

### Mention

Represents the literal surface form found in source content before normalization.

Examples:

```text
"ABC Holdings Pty Ltd"
"the Company"
"the Borrower"

"NDA"
"confidentiality agreement"

"thirty days"
"30 days"
```

Required fields:

```text
Mention
|-- mention_id
`-- surface_form
```

Required relationship:

```text
(Mention)-[:APPEARS_IN]->(Evidence)
```

A Mention may resolve to an Entity, Concept, Predicate, or Value through a ResolutionDecision.

Keeping the original surface form is necessary because normalization and entity resolution may improve over time.

### ExtractionRun

Represents the immutable configuration used to produce extracted knowledge from a DocumentFile.

Required fields:

```text
ExtractionRun
|-- extraction_run_id
|-- extractor_version
|-- model_id
|-- prompt_version
|-- extraction_schema_version
|-- ontology_release_id
`-- completed_at
```

Required relationship:

```text
(ExtractionRun)-[:PROCESSED]->(DocumentFile)
```

Only successful runs that contribute knowledge need to be represented in the graph. Operational job status and retry state remain in the existing processing systems.

Every extracted Mention, Claim, and OntologyProposal must be attributable to an ExtractionRun.

## Knowledge Objects

### Entity

Represents a canonical thing identified within one Data Room.

Examples include:

```text
TargetCo
BigBank
Credit Agreement
Clause 14.2
Patent 123
Employee 72
Transaction 2026
Consent Requirement 17
```

Required fields:

```text
Entity
|-- entity_id
`-- canonical_name
```

Required relationships:

```text
(Entity)-[:IN_DATA_ROOM]->(DataRoom)
(Entity)-[:INSTANCE_OF]->(Concept)
```

An Entity is the canonical identity, not every textual reference to it.

```text
"ABC Holdings Pty Ltd"
"ABC"
"the Company"
"the Borrower"
        |
        v
Entity: TargetCo
```

Entity identity is Data Room-scoped by default. Similar names in different Data Rooms must not be merged automatically.

### Value

Represents a normalized literal value used as the object of a Claim.

Required fields:

```text
Value
|-- value_id
|-- datatype
`-- canonical_value
```

Optional typed fields are used when required for correct filtering and comparison:

```text
number_value
date_value
datetime_value
boolean_value
text_value
unit_code
currency_code
calendar_basis
precision
```

Examples:

```text
"thirty days"
"30 days"
        |
        v
Duration: 30 calendar days
```

```text
"USD 5m"
"$5,000,000"
        |
        v
Money: 5,000,000 USD
```

```text
"1 March 2026"
"March 1st, 2026"
        |
        v
Date: 2026-03-01
```

The raw form remains available through Mention and Evidence.

Normalization must preserve meaningful differences:

```text
30 calendar days != 30 business days
```

### Claim

Represents an assertion made by source content.

A Claim is not automatically treated as objective truth.

Every Claim has the logical structure:

```text
Subject -> Predicate -> Object
```

The object is either an Entity or a Value.

Required fields:

```text
Claim
|-- claim_id
|-- polarity
|-- assertion_mode
|-- extraction_confidence
`-- claim_status
```

Required relationships:

```text
(Claim)-[:IN_DATA_ROOM]->(DataRoom)
(Claim)-[:HAS_SUBJECT]->(Entity)
(Claim)-[:USES_PREDICATE]->(Predicate)
(Claim)-[:HAS_OBJECT_ENTITY]->(Entity)
                    OR
(Claim)-[:HAS_OBJECT_VALUE]->(Value)
(Claim)-[:SUPPORTED_BY]->(Evidence)
(Claim)-[:GENERATED_BY]->(ExtractionRun)
```

Exactly one object relationship is permitted: entity or value.

Examples:

```text
TargetCo -> partyTo -> CreditAgreement
Clause14_2 -> requiresConsentFrom -> BigBank
Agreement88 -> expiresOn -> 2027-06-30
TargetCo -> FY2025Revenue -> USD 120,000,000
```

`polarity` distinguishes positive and negated assertions:

```text
positive
negative
```

`assertion_mode` prevents forecasts, intentions, estimates, and possibilities from being treated as established facts:

```text
asserted
reported
estimated
forecast
intended
possible
hypothetical
```

Domain meaning such as obligation, permission, or prohibition should normally be represented by the Predicate or by an explicit domain Entity.

`claim_status` supports lifecycle management:

```text
active
superseded
retracted
invalidated
```

`extraction_confidence` represents confidence that the source was extracted correctly. It does **not** represent the legal or factual authority of the source.

### Claim Context and Qualifiers

Some assertions require more than a simple binary relationship.

Examples include:

- conditional obligations
- exceptions
- thresholds
- temporal validity
- jurisdictional scope
- estimates and forecasts
- rights, permissions, and prohibitions

Simple temporal fields may be stored directly on the Claim when they have a single unambiguous meaning:

```text
valid_from
valid_to
as_of_date
```

For semantically important context, create an Entity representing the event, obligation, right, restriction, or other n-ary fact.

Example:

```text
ConsentRequirement17
|-- appliesTo           -> CreditAgreement
|-- triggeredBy         -> ChangeOfControl
|-- consentFrom         -> BigBank
|-- threshold           -> 50%
`-- exception           -> InternalRestructuring
```

This is preferred over placing many unrelated properties on an edge.

## Ontology Schema

The ontology defines what extracted knowledge means. It is versioned separately from room-specific graph data.

The ontology may be stored in a global, non-sensitive registry and referenced by stable IDs from regional room graphs.

### OntologyRelease

Represents an immutable release of the ontology.

Required fields:

```text
OntologyRelease
|-- ontology_release_id
|-- version
`-- released_at
```

Every ExtractionRun and ReconciliationRun must reference the ontology release it used.

### Concept

Defines the type of thing an Entity may represent.

Examples:

```text
Organization
Company
Subsidiary
Person
Agreement
CreditAgreement
NonDisclosureAgreement
Clause
ChangeOfControlClause
Obligation
TakeOrPayObligation
Event
Transaction
Payment
CyberIncident
```

Required fields:

```text
Concept
|-- concept_id
|-- preferred_label
|-- definition
|-- concept_kind
`-- lifecycle_status
```

Typical `concept_kind` values include:

```text
entity_type
event_type
agreement_type
clause_type
obligation_type
document_type
risk_type
```

Required relationship:

```text
(Concept)-[:DEFINED_IN]->(OntologyRelease)
```

Hierarchy relationships:

```text
(Concept)-[:NARROWER_THAN]->(Concept)
```

Example:

```text
ChangeOfControlClause
    -> NARROWER_THAN
ContractClause
    -> NARROWER_THAN
Clause
```

### Predicate

Defines a canonical relationship or property used by Claims and CanonicalStatements.

Examples:

```text
partyTo
contains
requiresConsentFrom
expiresOn
owns
subsidiaryOf
hasRevenue
amends
supersedes
```

Required fields:

```text
Predicate
|-- predicate_id
|-- preferred_label
|-- definition
|-- object_kind
`-- lifecycle_status
```

`object_kind` is one of:

```text
entity
value
either
```

Required relationship:

```text
(Predicate)-[:DEFINED_IN]->(OntologyRelease)
```

Optional semantic relationships:

```text
(Predicate)-[:INVERSE_OF]->(Predicate)
(Predicate)-[:NARROWER_THAN]->(Predicate)
(Predicate)-[:RELATED_TO]->(Predicate)
(Predicate)-[:DEPRECATED_IN_FAVOR_OF]->(Predicate)
```

### TermLabel

Stores searchable labels and aliases for Concepts and Predicates.

Required fields:

```text
TermLabel
|-- term_label_id
|-- text
|-- language
`-- label_type
```

`label_type` is one of:

```text
preferred
alias
abbreviation
legacy
```

Relationships:

```text
(TermLabel)-[:LABEL_FOR]->(Concept)
                    OR
(TermLabel)-[:LABEL_FOR]->(Predicate)
```

Example:

```text
Concept: NonDisclosureAgreement

preferred:
"Non-Disclosure Agreement"

aliases:
"NDA"
"non disclosure agreement"
"confidentiality agreement"
```

An alias is a candidate-resolution aid, not proof of exact equivalence. Context still determines whether a mention maps to the term.

### OntologyConstraint

Defines validation expectations for ontology terms.

Required fields:

```text
OntologyConstraint
|-- ontology_constraint_id
|-- constraint_type
|-- severity
`-- parameters
```

Typical constraints include:

```text
allowed subject concepts
allowed object concepts
allowed value datatypes
cardinality expectations
required companion predicates
mutual exclusivity
```

Example:

```text
requiresConsentFrom

expected subject:
Clause | Agreement | Obligation

expected object:
Organization | Person | Authority
```

Constraints are validation and confidence signals. They should not automatically reject a plausible new pattern merely because the ontology has not encountered it before.

### OntologyProposal

Represents a proposed ontology change discovered during extraction or review.

Required fields:

```text
OntologyProposal
|-- ontology_proposal_id
|-- proposal_type
|-- proposed_label
|-- proposed_definition
|-- proposal_status
`-- proposal_confidence
```

Typical proposal types:

```text
new_concept
new_predicate
new_alias
new_mapping
new_constraint
```

Required relationships:

```text
(OntologyProposal)-[:GENERATED_BY]->(ExtractionRun)
(OntologyProposal)-[:SUPPORTED_BY]->(Evidence)
```

Optional relationships:

```text
(OntologyProposal)-[:CANDIDATE_MATCH]->(Concept)
(OntologyProposal)-[:CANDIDATE_MATCH]->(Predicate)
(OntologyProposal)-[:RESOLVED_TO]->(Concept)
(OntologyProposal)-[:RESOLVED_TO]->(Predicate)
```

The LLM proposes ontology evolution. A governed resolver accepts, maps, keeps provisional, or rejects the proposal.

### Ontology Lifecycle

Concepts and Predicates use the following lifecycle states:

```text
canonical
provisional
deprecated
mapped
rejected
```

- `canonical`: approved for normal extraction and querying
- `provisional`: accepted temporarily but not yet governed as canonical
- `deprecated`: retained for historical compatibility but not used for new extraction
- `mapped`: redirected to another canonical term
- `rejected`: invalid, duplicate, or too noisy for use

The LLM may create OntologyProposals. It must never directly alter the core schema or promote ontology terms to canonical status.

## Resolution Schema

### ResolutionDecision

Records how a Mention or extracted candidate was mapped to a canonical object.

Required fields:

```text
ResolutionDecision
|-- resolution_decision_id
|-- resolution_type
|-- resolver_version
|-- resolution_confidence
`-- resolution_status
```

`resolution_type` may be:

```text
entity
concept
predicate
value
```

Required relationships:

```text
(ResolutionDecision)-[:RESOLVES_INPUT]->(Mention)
(ResolutionDecision)-[:GENERATED_BY]->(ExtractionRun)
```

Exactly one selected target relationship is used:

```text
(ResolutionDecision)-[:SELECTED_ENTITY]->(Entity)
(ResolutionDecision)-[:SELECTED_CONCEPT]->(Concept)
(ResolutionDecision)-[:SELECTED_PREDICATE]->(Predicate)
(ResolutionDecision)-[:SELECTED_VALUE]->(Value)
```

Optional candidate relationships preserve alternatives considered by the resolver.

Resolution must be auditable because a future ontology or resolver version may produce a different result.

## Canonical Knowledge

### ReconciliationRun

Represents one execution of the rules that convert Claims into CanonicalStatements.

Required fields:

```text
ReconciliationRun
|-- reconciliation_run_id
|-- reconciliation_ruleset_version
|-- ontology_release_id
`-- completed_at
```

### CanonicalStatement

Represents the system's current reconciled view of a subject-predicate-object statement.

Required fields:

```text
CanonicalStatement
|-- canonical_statement_id
|-- canonical_status
`-- canonical_confidence
```

Optional temporal fields:

```text
valid_from
valid_to
as_of_date
```

Required relationships:

```text
(CanonicalStatement)-[:IN_DATA_ROOM]->(DataRoom)
(CanonicalStatement)-[:HAS_SUBJECT]->(Entity)
(CanonicalStatement)-[:USES_PREDICATE]->(Predicate)
(CanonicalStatement)-[:HAS_OBJECT_ENTITY]->(Entity)
                              OR
(CanonicalStatement)-[:HAS_OBJECT_VALUE]->(Value)
(CanonicalStatement)-[:PRODUCED_BY]->(ReconciliationRun)
(CanonicalStatement)-[:SUPPORTED_BY_CLAIM]->(Claim)
```

Optional relationship:

```text
(CanonicalStatement)-[:CONTRADICTED_BY_CLAIM]->(Claim)
```

`canonical_status` is one of:

```text
accepted
disputed
superseded
invalidated
```

Example:

```text
CanonicalStatement
FacilityAgreement -> maturityDate -> 2029-12-31

supported by:
- Claim from Amendment 2
- Claim from Q&A response

contradicted by:
- Claim from Original Agreement
```

A CanonicalStatement does not delete or overwrite source Claims.

### Reconciliation Rules

Reconciliation may consider:

```text
document-file chronology
explicit amendment or supersession relationships
source authority
source type
number of independent supporting claims
temporal validity
human confirmation
extraction confidence
```

Extraction confidence must never be treated as equivalent to source authority.

Some conflicts should remain unresolved and produce a `disputed` CanonicalStatement rather than a forced answer.

## Materialized Domain Graph

CanonicalStatements are projected into a query-friendly domain graph.

Example:

```text
(TargetCo)-[:PARTY_TO]->(CreditAgreement)
(CreditAgreement)-[:CONTAINS]->(Clause14_2)
(Clause14_2)-[:REQUIRES_CONSENT_FROM]->(BigBank)
```

The materialized edge stores only the metadata required to reconnect it to governed knowledge:

```text
canonical_statement_id
canonical_confidence
valid_from
valid_to
```

It should not duplicate source-document details, evidence text, extraction metadata, or reconciliation history.

Those remain accessible through:

```text
Materialized edge
    |
    v
CanonicalStatement
    |
    v
Claims
    |
    v
Evidence
    |
    v
DocumentFile
```

The materialized domain graph is optimized for:

- graph traversal
- risk-pattern matching
- cross-document reasoning
- exploration and visualization
- graph-assisted retrieval

It is a derived projection and must be rebuildable from Claims, Evidence, the ontology, and reconciliation rules.

## Derived Findings

A Finding represents an application-level interpretation, such as a risk, anomaly, inconsistency, or missing-information signal.

Required fields:

```text
Finding
|-- finding_id
|-- finding_type
|-- finding_status
|-- finding_confidence
|-- ruleset_version
`-- created_at
```

Required relationships:

```text
(Finding)-[:IN_DATA_ROOM]->(DataRoom)
(Finding)-[:DERIVED_FROM]->(CanonicalStatement)
```

A Finding may also link directly to Claims when the finding is specifically about conflict, uncertainty, or source disagreement.

Findings are not source facts. They must remain distinguishable from extracted Claims and CanonicalStatements.

## Required Relationship Summary

| From | Relationship | To | Purpose |
|---|---|---|---|
| DataRoom | `CONTAINS_DOCUMENT` | Document | Data Room scope |
| Document | `HAS_FILE` | DocumentFile | Connect logical document to uploaded files |
| Evidence | `FROM_FILE` | DocumentFile | Exact source provenance |
| Mention | `APPEARS_IN` | Evidence | Preserve raw source form |
| ExtractionRun | `PROCESSED` | DocumentFile | Extraction lineage |
| Entity | `IN_DATA_ROOM` | DataRoom | Room isolation |
| Entity | `INSTANCE_OF` | Concept | Domain typing |
| Claim | `IN_DATA_ROOM` | DataRoom | Room isolation |
| Claim | `HAS_SUBJECT` | Entity | Claim subject |
| Claim | `USES_PREDICATE` | Predicate | Claim meaning |
| Claim | `HAS_OBJECT_ENTITY` | Entity | Entity object |
| Claim | `HAS_OBJECT_VALUE` | Value | Literal object |
| Claim | `SUPPORTED_BY` | Evidence | Source support |
| Claim | `GENERATED_BY` | ExtractionRun | Extraction lineage |
| ResolutionDecision | `RESOLVES_INPUT` | Mention | Resolution input |
| ResolutionDecision | `SELECTED_*` | Entity/Concept/Predicate/Value | Resolution output |
| Concept/Predicate | `DEFINED_IN` | OntologyRelease | Ontology versioning |
| CanonicalStatement | `SUPPORTED_BY_CLAIM` | Claim | Reconciled support |
| CanonicalStatement | `CONTRADICTED_BY_CLAIM` | Claim | Preserved conflict |
| CanonicalStatement | `PRODUCED_BY` | ReconciliationRun | Reconciliation lineage |
| Finding | `DERIVED_FROM` | CanonicalStatement | Explainable application output |

## LadybugDB Physical Model

> The evolving domain projection must use a dedicated open-type graph created with CREATE GRAPH <name> ANY and selected with USE GRAPH <name>. LadybugDB’s default main graph is strictly typed, so undeclared labels and relationship types will fail there.
The production model uses two complementary graph layers.

### Governed Node and Relationship Tables

Use explicit LadybugDB node and relationship tables for:

```text
DataRoom
Document
DocumentFile
Evidence
Mention
Entity
Value
Claim
ExtractionRun
ResolutionDecision
OntologyRelease
Concept
Predicate
TermLabel
OntologyConstraint
OntologyProposal
ReconciliationRun
CanonicalStatement
Finding
```

These tables define stable infrastructure and lineage.

### Evolving Domain Projection

Use the open graph capability for ontology-driven labels and relationships such as:

```text
Company
Agreement
Clause
Patent
Permit
Employee
Obligation
Incident

PARTY_TO
CONTAINS
REQUIRES_CONSENT_FROM
OWNS
AMENDS
EXPIRES_ON
```

The open graph is generated from CanonicalStatements. The LLM does not write directly to it and does not execute schema changes.

## Deletion, Replacement, and Reprocessing

When a DocumentFile is deleted or replaced, all dependent knowledge must be traceable and recomputed.

```text
DocumentFile removed or invalidated
        |
        v
Evidence from that file invalidated
        |
        v
Claims supported only by that Evidence invalidated
        |
        v
CanonicalStatements reconciled again
        |
        v
Materialized domain graph updated
        |
        v
Affected Findings recomputed
```

If another DocumentFile independently supports the same Claim, the canonical knowledge may remain valid.

A new DocumentFile uploaded to an existing Document is processed as a new source. It does not automatically supersede prior knowledge unless source metadata or extracted domain relationships establish that supersession.

## Versioning

The following versions are independent and must remain separately identifiable:

```text
core_schema_version
ontology_release_id
extraction_schema_version
extractor_version
model_id
prompt_version
resolver_version
normalization_version
reconciliation_ruleset_version
finding_ruleset_version
projection_version
```

A single generic version number is insufficient because each layer can change independently.

## Schema Evolution Rules

### New Entity Instances

New instances of existing Concepts are added continuously without schema changes.

```text
Concept: Company
New Entity: Acme Pty Ltd
```

### New Concepts and Predicates

New domain vocabulary is introduced through OntologyProposal and governance.

```text
New Concept: TakeOrPayObligation
New Predicate: requiresEnvironmentalApproval
```

No change to the governed core schema is required.

### Core Schema Changes

Changes to the following require controlled engineering migrations:

```text
Claim structure
Evidence locator contract
Entity identity rules
DocumentFile provenance rules
CanonicalStatement semantics
Room-isolation rules
```

The LLM must never perform or approve these changes automatically.

## Non-Negotiable Invariants

The production schema must enforce the following invariants:

- every room-derived Entity, Claim, CanonicalStatement, and Finding belongs to exactly one DataRoom
- every Evidence record points to exactly one DocumentFile
- every Claim has exactly one subject, one Predicate, and exactly one object
- every Claim records polarity and assertion mode so that negated or non-factual statements are not materialized as facts
- every Claim has at least one Evidence record and one ExtractionRun
- every Entity has at least one Concept
- every CanonicalStatement has at least one supporting Claim
- every materialized domain edge points back to one CanonicalStatement
- source Claims are never overwritten by reconciliation
- ontology terms have stable identifiers across releases
- room-specific knowledge is never used to resolve entities in another Data Room without an explicit governed feature
- deletion of a DocumentFile can deterministically identify every dependent derived object

## Final Model

The schema separates three concerns:

```text
Existing application data
        |
        | stable references
        v
Evidence-backed claims
        |
        | resolution and reconciliation
        v
Canonical knowledge
        |
        | materialization
        v
Query-optimized domain graph and derived findings
```

The stable core answers:

> How do we trace, validate, reconcile, update, and delete knowledge safely?

The evolving ontology answers:

> What does the knowledge mean?

The materialized domain graph answers:

> How do we query relationships efficiently?

The LLM may extract knowledge and propose ontology changes, but it does not control the core schema, canonical truth, or governance lifecycle.
