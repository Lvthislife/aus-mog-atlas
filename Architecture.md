# Architecture

**Version:** 4.1
**Status:** Build-ready — under active architectural review

---

## 1. Project Scope

This project is a federated constitutional and governance atlas — broader than a narrow executive machinery of government model. The term "Machinery of Government" is retained for accessibility but the scope covers:

- Commonwealth, State, Territory and Local government
- Parliamentary institutions
- Judicial institutions
- Government-owned entities and statutory authorities
- Intergovernmental bodies and ministerial councils
- Native title holders and prescribed bodies corporate
- Legislation, authority pathways, and accountability structures
- Spatial overlays and financial flows
- Temporal changes and entity lifecycle

---

## 2. Object Model

The v4.1 schema defines the following first-class objects:

| Object | Purpose |
|---|---|
| `Entity` | Any actor in the graph: polity, body, office holder, court, council, committee |
| `Authority` | Explicit legal source of any power, function, status or existence |
| `Delegation` | Legally sourced transfer of power from delegating entity to delegate |
| `Relationship` | Enduring structural link between entities |
| `Interaction` | Discrete action, decision or event by an accountable actor |
| `Function` | What an authority empowers an entity to do |
| `Legislation` | Act, regulation or instrument — first-class object (v4.1) |
| `IntergovernmentalAgreement` | IGA — first-class object (v4.1) |
| `CourtDecision` | Court determination — first-class object (v4.1) |
| `FinancialFlow` | Financial transfer between entities |
| `Program` | Government program — first-class object (v4.1) |
| `SpatialReference` | Spatial area — LGA, state, native title determination area, cadastral parcel |
| `NativeTitleStatus` | Native title determination record |
| `Constraint` | Legal constraint on a function within a spatial area |

---

## 3. Entity Types

```
polity
parliament
executive_council
minister
department
agency
statutory_authority
corporate_commonwealth_entity
non_corporate_commonwealth_entity
government_business_enterprise
local_government_council
court
tribunal
independent_officer
accountable_authority
office_holder
native_title_holder_group
prescribed_body_corporate
recognised_body
cabinet_committee
cabinet_subcommittee
intergovernmental_body
ministerial_council
cross_government_committee
```

---

## 4. Authority Sources

```
constitution                    — Commonwealth Constitution
state_constitution              — State/Territory constitutions
statute                         — Act of Parliament
court_determination             — Court decision (e.g. native title)
recognised_right                — Recognised rights
executive                       — Cabinet/Executive Council/PM/Premier directive
intergovernmental_agreement     — IGA between polities
administrative_instrument       — AAO, terms of reference, executive instrument
```

**Core rule:** Authority is never inferred. Every entity's existence and every power it exercises must trace to an explicit Authority record citing a legal instrument.

---

## 5. Relationship Types

| Relationship | Direction | Description |
|---|---|---|
| `portfolio_membership` | entity → portfolio | Entity is part of a ministerial portfolio |
| `regulatory_authority` | entity → entity | Entity regulates another |
| `coordination` | bidirectional | Intergovernmental coordination relationship |
| `funding_relationship` | payer → recipient | Financial flow between entities |
| `membership` | entity → body | Entity is a member of a body or committee |
| `controlled_entity` | controller → controlled | Entity controls another |
| `shareholder_entity` | shareholder → entity | Shareholder relationship |
| `constitutional_basis` | entity → constitution | Entity's constitutional grounding |
| `supported_by` | body → entity | Secretariat or support function |

**Key distinction:** Relationships are enduring structural links. Interactions are discrete events. These must not be conflated.

---

## 6. View Architecture

### Relationship View
- Primary exploration view
- Radial cluster layout — no single central node
- Clustered by jurisdiction and entity type
- Default edges: portfolio membership, regulatory authority, coordination
- Toggleable: funding, controlled entity, shareholder, membership, constitutional basis

### Map View
- Spatial view
- Commonwealth entities: national overlay or floating node — not pinned to Canberra
- State/Territory entities: polygon highlight + capital city anchor
- Local government: clustered within state polygon
- Intergovernmental bodies: connectors between member polities — not inside any single jurisdiction
- Non-spatial entities: floating layer / panel only

### Authority View
- Chain: Entity → Authority → Legislation / IGA / Instrument
- Grouped by jurisdiction
- Shows authority summary, legislation list, and functions

### Funding View
- Financial flows between entities
- 232 of 240 flows currently provisional (authority unresolved)
- Renders with warning indicators on provisional flows

### Coordination View
- Intergovernmental coordination relationships
- IGA overlay
- Bidirectional for coordination relationships

### Portfolio View
- Tree layout
- Root: department nodes
- Branches: portfolio entities

---

## 7. Status Model

| Status | Rendering | Visible by default |
|---|---|---|
| `normal` | Solid border | Yes |
| `provisional` | Dashed border + warning badge | Yes |
| `deprecated` | 40% opacity | No — requires explicit filter |

---

## 8. Key Design Principles

### No central node
The graph has no administrative root. Commonwealth entities do not sit above state entities. The model reflects constitutional federation.

### Authority is not geography
Spatial coverage describes where an entity operates or has effect. It does not determine legal authority. Authority is held in Authority records, never inferred from the map.

### Westminster responsible government
The model correctly represents the fusion of executive and legislature in Westminster systems. Ministers are members of Parliament and the Executive simultaneously. This is not a defect — it is a constitutional fact that the model must represent accurately.

### Judicial separation
Courts are modelled as constitutionally separate from the executive. Visual architecture must not imply executive authority over judicial institutions.

### Federation
Commonwealth authority does not derive from superiority over States. Each polity is constitutionally grounded. Cross-jurisdiction relationships are modelled as coordination or intergovernmental agreement — not hierarchy.

### Functions and Legislation as first-class objects (v4.1)
Free-text references to functions and Acts are deprecated. All references must use `function_id` and `legislation_id` pointing to first-class objects.

---

## 9. Validation Rules (Key)

- `aao_reference` must not be populated where `jurisdiction ≠ commonwealth`
- `legal_basis_id` must resolve to an existing Authority record
- For `local_government_council`, Authority source must be `state_constitution` or `statute` with State jurisdiction
- For `cabinet_committee`, Authority source must be `executive`
- For `ministerial_council`, Authority source must be `intergovernmental_agreement`
- Where `authority_mechanism = delegated`, a Delegation record must exist
- `function_id` must be populated — `power_or_function` (free text) is deprecated
- Where `authority_source = statute`, `legislation_id` must be populated
- `delegation_instrument` must cite a specific instrument — not generic

---

## 10. Temporal Model

All objects carry `valid_from` and `valid_to` fields (ISO 8601). `valid_to: null` means current.

Temporal scope covers:
- AAO changes and portfolio reassignment
- Entity establishment and abolition
- Ministerial appointment and cessation
- Legislation commencement and repeal
- IGA execution and termination
- Court determinations

Identifiers are stable across temporal changes — a new AAO does not create a new entity record; it creates a new relationship or updates `valid_to` on the existing one.

---

## 11. Spatial Model

Spatial references are geographic only. They do not determine authority.

| Spatial type | Description |
|---|---|
| `local_government_area` | LGA boundary (ABS ASGS) |
| `state_polygon` | State/Territory boundary |
| `native_title_determination_area` | NNTT registered determination area |
| `cadastral_parcel` | Individual land parcel |
| `electoral_boundary` | Electoral division |

Native title determination areas trigger Constraint records under the Native Title Act 1993 (Cth) where future acts are proposed.

