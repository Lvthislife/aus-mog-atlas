# Australian Machinery of Government — v4.1 Build Schema

**Version:** 4.1
**Status:** Build-ready
**Scope:** Commonwealth, States, Territories, Local Government, Native Title, statutory bodies, courts, Cabinet committees, National Cabinet, Ministerial Councils, cross-government committees, accountable actors, spatial regimes, financial flows, programs, legislation, intergovernmental agreements, court decisions.

This is a build schema. It defines the objects, fields, allowed values, required/optional status, and validation rules required to instantiate a graph-capable model of Australian government structure, authority, delegation, interactions, constraints, spatial applicability, financial flows, programs, legislation, court decisions, and intergovernmental governance.

v4.1 is a strict upgrade of v4.0. All v4.0 objects are preserved; deprecated fields are explicitly marked. New objects are inserted as new sections.

---

## 1. Schema-wide conventions

### 1.1 Identifiers

- All objects have `id` (string, globally unique, snake_case or URI-safe).
- All cross-references use `id`.
- Time-bounded fields use ISO 8601 dates: `valid_from`, `valid_to`. `valid_to: null` means current.

### 1.2 Field status

- **Required (R):** must be populated for the record to validate.
- **Conditional (C):** required only when stated trigger condition is met.
- **Optional (O):** may be omitted.
- **Deprecated (D):** retained for backward compatibility. MUST NOT be populated in new v4.1 records. Validators MUST flag any active use.

### 1.3 Authority is never inferred

Authority must be explicit on the relevant object. The model does not derive authority from:
- the entity's name or institutional label
- the function the entity performs
- the entity's spatial location
- the label of any relationship
- committee membership

Authority is asserted via the `Authority` object and referenced by other objects.

### 1.4 Relationships vs Interactions

- **Relationship:** enduring structural link (e.g. Department administers Act; Minister is member of Cabinet committee).
- **Interaction:** discrete action, decision or event (e.g. Minister approves grant; Committee endorses recommendation).

These are modelled as separate objects and must not be conflated.

### 1.5 Functions, Legislation, Programs as first-class objects (v4.1)

Functions, Legislation and Programs are first-class objects. Free-text references to functions, Acts and programs are deprecated and MUST be replaced by `function_id`, `legislation_id` and `program_id` references.

---

## 2. Object: Entity

### 2.1 Purpose

Represents any actor in the MoG graph: a polity, jurisdiction, body, office holder, court, statutory authority, council, recognised group, or committee.

### 2.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique identifier. |
| `name` | string | R | Display name. |
| `entity_type` | enum | R | See allowed values below. |
| `jurisdiction` | enum | R | `commonwealth` \| `nsw` \| `vic` \| `qld` \| `wa` \| `sa` \| `tas` \| `act` \| `nt` \| `local` \| `cross_jurisdiction` \| `non_government`. |
| `parent_entity_id` | string | O | Parent entity. |
| `portfolio_id` | string | C | Required where `entity_type = department` or `agency` and a portfolio exists. |
| `legal_basis_id` | string | R | Reference to `Authority.id` establishing this entity's existence. |
| `aao_reference` | string | C | Required only for Commonwealth entities mapped under the AAO. Must not be populated for State, Territory or Local entities. |
| `state_admin_arrangement_ref` | string | C | Required for State/Territory entities where responsibilities are set by State administrative arrangements. |
| `valid_from` | date | R | Establishment / commencement date. |
| `valid_to` | date | O | Abolition / cessation date. Null = current. |

### 2.3 Allowed `entity_type` values

- `polity` (Commonwealth, State, Territory)
- `parliament`
- `executive_council`
- `minister`
- `department`
- `agency`
- `statutory_authority`
- `corporate_commonwealth_entity`
- `non_corporate_commonwealth_entity`
- `government_business_enterprise`
- `local_government_council`
- `court`
- `tribunal`
- `independent_officer`
- `accountable_authority`
- `office_holder`
- `native_title_holder_group`
- `prescribed_body_corporate`
- `recognised_body`
- **`cabinet_committee`** *(v4.1)*
- **`cabinet_subcommittee`** *(v4.1)*
- **`intergovernmental_body`** *(v4.1 — e.g. National Cabinet, COAG-successor bodies)*
- **`ministerial_council`** *(v4.1)*
- **`cross_government_committee`** *(v4.1 — senior officials committees, taskforces, interdepartmental committees)*

### 2.4 Validation rules

- `aao_reference` MUST NOT be populated where `jurisdiction` ≠ `commonwealth`.
- `legal_basis_id` MUST resolve to an existing `Authority` record.
- For `entity_type = local_government_council`, the referenced `Authority` MUST have `authority_source = state_constitution` or `authority_source = statute` with a State `jurisdiction`.
- For `entity_type = cabinet_committee` or `cabinet_subcommittee`, the referenced `Authority` MUST have `authority_source = executive`.
- For `entity_type = ministerial_council`, the referenced `Authority` MUST have `authority_source = intergovernmental_agreement`.
- For `entity_type = intergovernmental_body` (e.g. National Cabinet), the referenced `Authority` MUST have `authority_source ∈ {executive, intergovernmental_agreement}`. Where the body holds both, assert two `Authority` records.
- For `entity_type = cross_government_committee`, the referenced `Authority` MUST have `authority_source ∈ {executive, administrative_instrument}`. `statute` is not permitted unless explicitly justified per Validation Rule 8 (Section 19).

### 2.5 Example

```json
{
  "id": "ent_qld_dept_education",
  "name": "Queensland Department of Education",
  "entity_type": "department",
  "jurisdiction": "qld",
  "parent_entity_id": "ent_qld_polity",
  "portfolio_id": "port_qld_education",
  "legal_basis_id": "auth_qld_public_service_act_2008",
  "state_admin_arrangement_ref": "qld_aao_2024_education",
  "valid_from": "1957-12-10",
  "valid_to": null
}
```

---

## 3. Object: Authority

### 3.1 Purpose

Captures the explicit legal source of any power, function, status or existence. Every assertion of capacity in the graph traces to an Authority record.

### 3.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `holder_entity_id` | string | R | Entity that holds the authority. |
| `authority_source` | enum | R | See allowed values. |
| `authority_mechanism` | enum | R | See allowed values. |
| `authority_instrument` | string | R | Citation: Act + section, regulation, instrument number, determination ID, IGA name, executive instrument. Retained as the citation field. |
| `legislation_id` | string | C | *(v4.1)* Required where `authority_source ∈ {statute, state_constitution}`. References `Legislation.id`. |
| `iga_id` | string | C | *(v4.1)* Required where `authority_source = intergovernmental_agreement`. References `IntergovernmentalAgreement.id`. |
| `court_decision_id` | string | C | *(v4.1)* Required where `authority_source = court_determination`. References `CourtDecision.id`. |
| `power_or_function` | string | D | *(deprecated v4.1)* Free-text description. Replaced by `function_id`. |
| `function_id` | string | R | *(v4.1)* Reference to `Function.id` describing what the authority empowers. |
| `subject_matter` | string | O | Domain. |
| `spatial_scope_id` | string | C | Required where authority is spatially limited. |
| `valid_from` | date | R | Commencement. |
| `valid_to` | date | O | Repeal / sunset. |
| `notes` | string | O | Free text. |

### 3.3 Allowed values

**`authority_source` (extended in v4.1):**
- `constitution` — Commonwealth Constitution
- `state_constitution`
- `statute`
- `court_determination`
- `recognised_right`
- **`executive`** *(v4.1 — Cabinet/Executive Council/Premier or Prime Minister directive establishing a body or power)*
- **`intergovernmental_agreement`** *(v4.1)*
- **`administrative_instrument`** *(v4.1 — administrative arrangement orders, terms of reference issued under executive authority where no statute or IGA applies)*

**`authority_mechanism`:**
- `direct`
- `delegated`
- `recognised`

### 3.4 Validation rules

- `authority_instrument` must not be empty or generic. It must cite an instrument.
- Where `authority_mechanism = delegated`, a corresponding `Delegation` record MUST exist.
- Where `authority_mechanism = recognised`, the `authority_source` MUST be `recognised_right` or `court_determination`.
- Authority MUST NOT be inferred from `function_id` alone; the field describes what the authority does, it does not establish it.
- Where `authority_source = statute`, `legislation_id` MUST be populated.
- Where `authority_source = intergovernmental_agreement`, `iga_id` MUST be populated.
- Where `authority_source = court_determination`, `court_decision_id` MUST be populated.
- `function_id` MUST be populated. `power_or_function` is deprecated and MUST NOT be populated in new records.

### 3.5 Example

```json
{
  "id": "auth_cwlth_education_minister_grants",
  "holder_entity_id": "ent_cwlth_minister_education",
  "authority_source": "statute",
  "authority_mechanism": "direct",
  "authority_instrument": "Australian Education Act 2013 (Cth) s23",
  "legislation_id": "leg_cwlth_aea_2013",
  "function_id": "fn_grant_approval_school_funding",
  "subject_matter": "school_education",
  "valid_from": "2014-01-01",
  "valid_to": null
}
```

---

## 4. Object: Delegation

### 4.1 Purpose

Models the legally sourced transfer of a power or function from a delegating entity to a delegate entity. Delegation is never generic; the legal source is required.

### 4.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `delegating_entity_id` | string | R | Entity holding the original authority. |
| `delegate_entity_id` | string | R | Entity receiving the delegated power. |
| `delegation_source_type` | enum | R | See allowed values. |
| `delegation_instrument` | string | R | Citation. |
| `legislation_id` | string | C | *(v4.1)* Required where `delegation_source_type ∈ {pgpa_finance_law, enabling_legislation, portfolio_legislation, state_legislation, local_government_legislation}`. |
| `delegated_power` | string | D | *(deprecated v4.1)* Replaced by `function_id`. |
| `function_id` | string | R | *(v4.1)* Reference to `Function.id`. |
| `function` | string | D | *(deprecated v4.1)* Replaced by `function_id`. |
| `upstream_authority_id` | string | R | Reference to the `Authority` record. |
| `conditions` | string | O | |
| `subdelegation_permitted` | boolean | O | Defaults to false. |
| `valid_from` | date | R | |
| `valid_to` | date | O | |

### 4.3 Allowed `delegation_source_type` values

- `pgpa_finance_law`
- `enabling_legislation`
- `portfolio_legislation`
- `state_legislation`
- `local_government_legislation`

### 4.4 Validation rules

- `delegation_instrument` must not be empty or generic.
- Commonwealth finance/resource delegations MUST use `delegation_source_type = pgpa_finance_law`.
- Substantive statutory powers MUST use `enabling_legislation` or `portfolio_legislation`.
- `upstream_authority_id` MUST resolve and the resolved `Authority.holder_entity_id` MUST equal `delegating_entity_id`.
- Local government delegations MUST use `local_government_legislation` or `state_legislation`.
- `function_id` MUST be populated; `delegated_power` and `function` are deprecated.
- `legislation_id` MUST resolve to a `Legislation` record consistent with `delegation_source_type`.

### 4.5 Example

```json
{
  "id": "del_cwlth_secretary_education_grant_approvals",
  "delegating_entity_id": "ent_cwlth_accountable_authority_education",
  "delegate_entity_id": "ent_cwlth_sesb1_grants_branch_head",
  "delegation_source_type": "pgpa_finance_law",
  "delegation_instrument": "Education Department Accountable Authority Instructions 2024, Sch 2 Item 14",
  "legislation_id": "leg_cwlth_pgpa_act_2013",
  "function_id": "fn_grant_approval_school_funding",
  "upstream_authority_id": "auth_cwlth_education_aa_pgpa",
  "conditions": "Subject to AAIs and financial threshold; cannot delegate to APS5 or below.",
  "subdelegation_permitted": false,
  "valid_from": "2024-07-01",
  "valid_to": null
}
```

---

## 5. Object: Interaction

### 5.1 Purpose

Represents a discrete action, decision or event undertaken by an accountable actor.

### 5.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `interaction_type` | enum | R | See allowed values. |
| `interaction_outcome_type` | enum | R | *(v4.1)* See allowed values. |
| `accountable_actor_id` | string | R | Entity legally accountable for the interaction. |
| `decision_maker_id` | string | R | *(v4.1)* Entity that actually made the decision. May equal `accountable_actor_id`; for committee outcomes, references the committee or the chair as appropriate. |
| `acting_under_authority_id` | string | R | The `Authority` under which the actor acts. |
| `acting_under_delegation_id` | string | C | Required where the actor is exercising a delegated power. |
| `counterparties` | array<string> | O | Other entities involved. |
| `subject_matter` | string | R | What the interaction concerns. |
| `function_id` | string | R | *(v4.1)* Function exercised. |
| `instrument_produced` | string | O | Document, decision notice, contract, approval, communiqué. |
| `spatial_reference_id` | string | O | If spatially specific. |
| `financial_flow_id` | string | O | Linked financial flow, if any. |
| `program_id` | string | C | *(v4.1)* Required where `interaction_type = grant_action`. |
| `constraints_engaged` | array<string> | O | Constraint IDs. |
| `event_date` | date | R | |

### 5.3 Allowed values

**`interaction_type`:**
- `decision`
- `approval`
- `direction`
- `appointment`
- `determination`
- `appropriation_action`
- `procurement_action`
- `grant_action`
- `regulatory_action`
- `enforcement_action`
- `intergovernmental_agreement_action`
- `consultation_event`
- `notification`
- `report_tabling`

**`interaction_outcome_type` (v4.1):**
- `statutory_decision` — exercises a statutory power producing legal effect
- `executive_decision` — exercises executive power (Cabinet/Executive Council, ministerial directive without statutory power)
- `intergovernmental_agreement` — produces or amends an IGA, communiqué, or council decision
- `advisory` — recommendation or advice without binding legal effect

### 5.4 Validation rules

- `accountable_actor_id` MUST be populated.
- `decision_maker_id` MUST be populated.
- `interaction_outcome_type` MUST be populated.
- `acting_under_authority_id` MUST resolve and link (directly or via Delegation) back to the `accountable_actor_id`.
- Where `acting_under_delegation_id` is populated, the delegation's `delegate_entity_id` MUST equal `accountable_actor_id`.
- Where `interaction_type = grant_action`, `program_id` MUST be populated.
- Committees (`cabinet_committee`, `cabinet_subcommittee`, `intergovernmental_body`, `ministerial_council`, `cross_government_committee`) MUST NOT produce `interaction_outcome_type = statutory_decision` unless an explicit `Authority` record with `authority_source = statute` and `legislation_id` populated exists for the committee and is referenced by `acting_under_authority_id`.
- `function_id` MUST be populated.

### 5.5 Example

```json
{
  "id": "int_qld_council_da_2025_00471",
  "interaction_type": "approval",
  "interaction_outcome_type": "statutory_decision",
  "accountable_actor_id": "ent_redland_city_council",
  "decision_maker_id": "ent_redland_city_council",
  "acting_under_authority_id": "auth_qld_planning_act_2016_assessment_manager",
  "subject_matter": "Material change of use — multi-unit dwelling, 12 Smith St",
  "function_id": "fn_planning_assessment_decision",
  "instrument_produced": "Decision notice DA-2025-00471",
  "spatial_reference_id": "sp_lga_redland_parcel_12_smith_st",
  "constraints_engaged": ["con_qld_planning_scheme_residential_zone"],
  "event_date": "2025-08-14"
}
```

---

## 6. Object: Constraint

### 6.1 Purpose

Represents a practical legal or administrative constraint on an action. Limited to MoG-relevant decision constraints.

Stare decisis is out of scope. The Kable principle is out of scope unless the use case is constitutional litigation.

### 6.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `constraint_effect` | enum | R | `blocks` \| `conditions` \| `requires` \| `enables`. |
| `constraint_source` | enum | R | See allowed values. |
| `constraint_instrument` | string | R | Citation. |
| `legislation_id` | string | C | *(v4.1)* Required where `constraint_source ∈ {statute, regulation}`. |
| `court_decision_id` | string | C | *(v4.1)* Required where `constraint_source = court_decision`. |
| `applies_to_entity_ids` | array<string> | O | |
| `applies_to_function_id` | string | O | *(v4.1)* Reference to `Function.id`. |
| `applies_to_function` | string | D | *(deprecated v4.1)* Replaced by `applies_to_function_id`. |
| `applies_to_spatial_id` | string | C | Required where the constraint is spatially scoped. |
| `description` | string | R | |
| `triggering_condition` | string | O | |
| `process_required` | string | O | |
| `valid_from` | date | R | |
| `valid_to` | date | O | |

### 6.3 Allowed `constraint_source` values

- `constitution`
- `state_constitution`
- `statute`
- `regulation`
- `court_decision`
- `administrative_instrument`

### 6.4 Validation rules

- `constraint_effect` MUST be one of the four enumerated values.
- `constraint_instrument` must cite an instrument or decision.
- Where `constraint_source = court_decision`, `court_decision_id` MUST be populated.
- Where `constraint_source ∈ {statute, regulation}`, `legislation_id` MUST be populated.
- Spatially scoped constraints MUST populate `applies_to_spatial_id`.
- `applies_to_function_id` is the active field; `applies_to_function` is deprecated.

### 6.5 Example

```json
{
  "id": "con_cwlth_native_title_future_act",
  "constraint_effect": "requires",
  "constraint_source": "statute",
  "constraint_instrument": "Native Title Act 1993 (Cth) Pt 2 Div 3",
  "legislation_id": "leg_cwlth_nta_1993",
  "applies_to_function_id": "fn_land_dealing",
  "applies_to_spatial_id": "sp_nt_determination_area_generic",
  "description": "Future acts affecting native title rights and interests must follow the future act regime.",
  "triggering_condition": "Proposed act affecting determined or claimed native title rights and interests.",
  "process_required": "Future act process: notification, right to negotiate, ILUA, or alternative procedure as applicable.",
  "valid_from": "1994-01-01",
  "valid_to": null
}
```

---

## 7. Object: SpatialReference

### 7.1 Purpose

Identifies a spatial regime relevant to authority, constraints, interactions or status. References authoritative external datasets; geometry is not stored.

Spatial reference indicates which legal regimes apply but does not override law.

### 7.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `spatial_type` | enum | R | See allowed values. |
| `name` | string | R | Display name. |
| `external_dataset` | string | R | Authoritative dataset. |
| `external_id` | string | R | Identifier within that dataset. |
| `parent_spatial_id` | string | O | |
| `applicable_jurisdiction` | enum | R | Same enum as `Entity.jurisdiction`. |
| `valid_from` | date | O | |
| `valid_to` | date | O | |

### 7.3 Allowed `spatial_type` values

- `state_or_territory`
- `local_government_area`
- `native_title_determination_area`
- `ilua_area`
- `national_park`
- `state_park_or_reserve`
- `marine_park`
- `resource_tenement`
- `planning_zone`
- `cadastral_parcel`
- `electoral_division`
- `other`

### 7.4 Validation rules

- `external_dataset` and `external_id` MUST be populated; geometry must NOT be embedded.
- Spatial reference alone MUST NOT be used to assert authority.

### 7.5 Example

```json
{
  "id": "sp_nntt_qcd2014_001",
  "spatial_type": "native_title_determination_area",
  "name": "Quandamooka People Determination Area",
  "external_dataset": "NNTT_Register_of_Native_Title_Determinations",
  "external_id": "QCD2011/001",
  "applicable_jurisdiction": "qld",
  "valid_from": "2011-07-04",
  "valid_to": null
}
```

---

## 8. Object: FinancialFlow

### 8.1 Purpose

Represents financial (or non-financial transfer) movement. Revenue and expenditure are separate. Rates, fees, royalties and levies are revenue, not tax expenditure.

### 8.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `flow_direction` | enum | R | `inbound` \| `outbound` \| `non_financial`. |
| `flow_class` | enum | R | See allowed values. |
| `payer_entity_id` | string | R | |
| `recipient_entity_id` | string | R | |
| `amount` | number | C | Required where `flow_direction ≠ non_financial` and known. |
| `currency` | string | C | Default `AUD`. |
| `financial_authority_source` | enum | R | See allowed values. |
| `financial_authority_instrument` | string | R | Citation. |
| `authority_id` | string | R | *(v4.1)* Reference to the `Authority` record authorising the flow. |
| `program_id` | string | C | *(v4.1)* Required where `flow_class ∈ {grant, subsidy, transfer_payment}`. |
| `linked_interaction_id` | string | O | |
| `period_start` | date | O | |
| `period_end` | date | O | |
| `notes` | string | O | |

### 8.3 Allowed values

**`flow_direction`:** `inbound` | `outbound` | `non_financial`.

**`flow_class`:**
- `appropriation`
- `grant`
- `transfer_payment`
- `procurement`
- `subsidy`
- `loan`
- `equity`
- `rates_revenue`
- `taxation_revenue`
- `regulatory_fee`
- `royalty`
- `levy`
- `penalty`
- `in_kind`
- `non_financial`

**`financial_authority_source`:**
- `constitution`
- `state_constitution`
- `appropriation_act`
- `statute`
- `regulation`
- `pgpa_finance_law`
- `state_finance_law`
- `local_government_legislation`
- `court_order`

### 8.4 Validation rules

- `flow_class` MUST be drawn from the enumerated list. `tax_expenditure` is NOT permitted.
- Revenue classes (`rates_revenue`, `regulatory_fee`, `royalty`, `levy`, `taxation_revenue`, `penalty`) MUST have `flow_direction = inbound` from the levying entity's perspective.
- `appropriation` MUST have `financial_authority_source = appropriation_act`.
- Commonwealth `procurement`, `grant`, `subsidy`, `loan`, `equity` MUST cite `pgpa_finance_law` plus substantive program legislation if applicable.
- `non_financial` flows MUST NOT populate `amount`.
- `authority_id` MUST resolve.
- Where `flow_class ∈ {grant, subsidy, transfer_payment}`, `program_id` MUST be populated.

### 8.5 Examples

**Outbound grant (Commonwealth):**

```json
{
  "id": "fin_cwlth_education_recurrent_2024_qld",
  "flow_direction": "outbound",
  "flow_class": "grant",
  "payer_entity_id": "ent_cwlth_dept_education",
  "recipient_entity_id": "ent_qld_polity",
  "amount": 8123456789,
  "currency": "AUD",
  "financial_authority_source": "appropriation_act",
  "financial_authority_instrument": "Australian Education Act 2013 (Cth); Appropriation Act (No. 1) 2024-25",
  "authority_id": "auth_cwlth_education_minister_grants",
  "program_id": "prog_cwlth_recurrent_school_funding",
  "period_start": "2024-07-01",
  "period_end": "2025-06-30"
}
```

**Inbound rates (council):**

```json
{
  "id": "fin_redland_general_rates_2024_25",
  "flow_direction": "inbound",
  "flow_class": "rates_revenue",
  "payer_entity_id": "ent_ratepayers_redland",
  "recipient_entity_id": "ent_redland_city_council",
  "amount": 215000000,
  "currency": "AUD",
  "financial_authority_source": "local_government_legislation",
  "financial_authority_instrument": "Local Government Act 2009 (Qld) Ch 4 Pt 1; Council resolution 2024-06-26",
  "authority_id": "auth_qld_redland_rating_power",
  "period_start": "2024-07-01",
  "period_end": "2025-06-30"
}
```

---

## 9. Object: NativeTitleStatus

### 9.1 Purpose

Models recognised Native Title rights and interests as status, not as ordinary delegated authority.

### 9.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `holder_group_entity_id` | string | R | |
| `prescribed_body_corporate_id` | string | C | Required where a PBC is registered under NTA s56/s57. |
| `status` | enum | R | `determined` \| `extinguished` \| `not_determined` \| `claim_registered`. |
| `determination_instrument` | string | C | Required where `status = determined` or `extinguished`. |
| `court_decision_id` | string | C | *(v4.1)* Required where `status ∈ {determined, extinguished}` and the determination is a court determination. |
| `spatial_reference_id` | string | R | |
| `rights_and_interests` | string | O | |
| `triggers_constraints` | array<string> | O | |
| `valid_from` | date | C | Required where `status ∈ {determined, extinguished}`. |
| `valid_to` | date | O | |

### 9.3 Validation rules

- Native Title MUST NOT be modelled via `Authority.authority_mechanism = delegated`.
- Where used in an `Authority` record, `authority_mechanism` MUST be `recognised` and `authority_source` MUST be `recognised_right` or `court_determination`.
- `determination_instrument` MUST be populated where `status ∈ {determined, extinguished}`.
- `spatial_reference_id` MUST resolve to a SpatialReference of `spatial_type = native_title_determination_area` or `ilua_area`.

### 9.4 Example

```json
{
  "id": "nts_quandamooka_2011",
  "holder_group_entity_id": "ent_quandamooka_people",
  "prescribed_body_corporate_id": "ent_qyac",
  "status": "determined",
  "determination_instrument": "Federal Court determination QUD6128/1998 (4 July 2011)",
  "court_decision_id": "cd_quandamooka_v_qld_2011",
  "spatial_reference_id": "sp_nntt_qcd2014_001",
  "rights_and_interests": "Mix of exclusive and non-exclusive rights as set out in the determination.",
  "triggers_constraints": ["con_cwlth_native_title_future_act"],
  "valid_from": "2011-07-04",
  "valid_to": null
}
```

---

## 10. Object: Relationship

### 10.1 Purpose

Represents an enduring structural link between entities. Relationships are not events.

### 10.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `relationship_type` | enum | R | See allowed values. |
| `from_entity_id` | string | R | |
| `to_entity_id` | string | R | |
| `subject_matter` | string | O | |
| `legislation_id` | string | C | *(v4.1)* Required where `relationship_type = administers_legislation`. |
| `member_role` | string | C | *(v4.1)* Required where `relationship_type = membership`. E.g. `chair`, `deputy_chair`, `member`, `observer`, `secretariat_lead`. |
| `legal_basis_id` | string | R | Authority establishing the relationship. |
| `valid_from` | date | R | |
| `valid_to` | date | O | |

### 10.3 Allowed `relationship_type` values (extended in v4.1)

- `administers_legislation`
- `portfolio_membership`
- `reports_to`
- `accountable_to`
- `oversight_of`
- `appointment_relationship`
- `funding_relationship`
- `service_delivery_relationship`
- `intergovernmental_agreement_party`
- `recognised_partnership`
- `controlled_entity`
- `shareholder_entity`
- **`membership`** *(v4.1 — committee/council/body membership)*
- **`supported_by`** *(v4.1 — secretariat or supporting entity)*

`reports_to` is retained from v4.0 and is permitted for committee reporting links (e.g. subcommittee reports_to parent committee).

### 10.4 Validation rules

- A `Relationship` MUST NOT model an action, decision or event.
- `legal_basis_id` MUST resolve to an `Authority` record.
- `relationship_type = administers_legislation` requires `subject_matter` and `legislation_id` to be populated.
- `relationship_type = membership` requires `member_role` to be populated and `to_entity_id` MUST resolve to an entity of `entity_type ∈ {cabinet_committee, cabinet_subcommittee, intergovernmental_body, ministerial_council, cross_government_committee}` (or, in legacy cases, another committee-class entity).
- `relationship_type = supported_by` is used for secretariat relationships; the `to_entity_id` is the supporting entity (typically a department).

### 10.5 Example

```json
{
  "id": "rel_cwlth_dept_education_administers_aea2013",
  "relationship_type": "administers_legislation",
  "from_entity_id": "ent_cwlth_dept_education",
  "to_entity_id": "ent_legislation_aea_2013",
  "subject_matter": "Australian Education Act 2013 (Cth)",
  "legislation_id": "leg_cwlth_aea_2013",
  "legal_basis_id": "auth_cwlth_aao_education_2024",
  "valid_from": "2024-07-29",
  "valid_to": null
}
```

---

## 11. Object: Function *(new in v4.1)*

### 11.1 Purpose

First-class representation of a government function, power or capability. Replaces all free-text function fields elsewhere in the schema.

### 11.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `name` | string | R | Display name. |
| `function_class` | enum | R | See allowed values. |
| `description` | string | R | Plain-language description. |
| `parent_function_id` | string | O | For taxonomic hierarchy. |
| `subject_domain` | string | O | E.g. education, health, water, justice. |
| `valid_from` | date | O | |
| `valid_to` | date | O | |

### 11.3 Allowed `function_class` values

- `policy_development`
- `legislative_drafting`
- `regulatory_decision`
- `licensing`
- `enforcement`
- `grant_administration`
- `procurement`
- `service_delivery`
- `revenue_collection`
- `appointments_and_governance`
- `intergovernmental_coordination`
- `oversight_and_assurance`
- `advisory`
- `planning_assessment`
- `land_dealing`
- `other`

### 11.4 Validation rules

- `function_class` MUST be populated.
- `description` MUST NOT be empty.
- Function MUST NOT itself assert authority. It is descriptive only and is referenced from `Authority`, `Delegation`, `Interaction` and `Constraint`.

### 11.5 Example

```json
{
  "id": "fn_grant_approval_school_funding",
  "name": "Approve recurrent school funding grants",
  "function_class": "grant_administration",
  "description": "Approval of recurrent funding to approved authorities under the Australian Education Act 2013.",
  "subject_domain": "school_education"
}
```

---

## 12. Object: Legislation *(new in v4.1)*

### 12.1 Purpose

First-class representation of an Act, regulation, or statutory instrument. Referenced wherever a legislative basis is asserted.

### 12.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `short_title` | string | R | E.g. "Australian Education Act 2013". |
| `citation` | string | R | Full citation. |
| `legislation_type` | enum | R | See allowed values. |
| `jurisdiction` | enum | R | Same enum as `Entity.jurisdiction`. |
| `administering_entity_ids` | array<string> | O | Entities administering the legislation. |
| `commenced` | date | O | Commencement date. |
| `repealed` | date | O | Repeal date, if any. |
| `parent_legislation_id` | string | C | Required for regulations and instruments made under a parent Act. |

### 12.3 Allowed `legislation_type` values

- `act`
- `regulation`
- `legislative_instrument`
- `subordinate_instrument`
- `proclamation`
- `appropriation_act`

### 12.4 Validation rules

- `citation` MUST be specific (Act + year + jurisdiction).
- Where `legislation_type ∈ {regulation, legislative_instrument, subordinate_instrument, proclamation}`, `parent_legislation_id` MUST be populated.

### 12.5 Example

```json
{
  "id": "leg_cwlth_aea_2013",
  "short_title": "Australian Education Act 2013",
  "citation": "Australian Education Act 2013 (Cth)",
  "legislation_type": "act",
  "jurisdiction": "commonwealth",
  "administering_entity_ids": ["ent_cwlth_dept_education"],
  "commenced": "2014-01-01",
  "repealed": null
}
```

---

## 13. Object: Program *(new in v4.1)*

### 13.1 Purpose

Represents a defined government program through which grants, subsidies or transfer payments flow. Required for grant flows and grant interactions.

### 13.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `name` | string | R | |
| `program_type` | enum | R | `grant_program` \| `subsidy_program` \| `transfer_payment_program` \| `service_delivery_program` \| `other`. |
| `administering_entity_id` | string | R | Entity administering the program. |
| `legislation_id` | string | C | Required where the program is created or governed by legislation. |
| `iga_id` | string | C | Required where the program is established or funded under an IGA. |
| `authority_id` | string | R | Reference to the `Authority` for the program. |
| `subject_domain` | string | O | |
| `valid_from` | date | R | |
| `valid_to` | date | O | |

### 13.3 Validation rules

- `administering_entity_id` MUST resolve.
- `authority_id` MUST resolve.
- For programs funded under an IGA (e.g. National Health Reform Agreement), `iga_id` MUST be populated.
- Program MUST be referenced by every `FinancialFlow` of `flow_class ∈ {grant, subsidy, transfer_payment}` and every `Interaction` of `interaction_type = grant_action`.

### 13.4 Example

```json
{
  "id": "prog_cwlth_recurrent_school_funding",
  "name": "Recurrent funding for schools",
  "program_type": "grant_program",
  "administering_entity_id": "ent_cwlth_dept_education",
  "legislation_id": "leg_cwlth_aea_2013",
  "authority_id": "auth_cwlth_education_minister_grants",
  "subject_domain": "school_education",
  "valid_from": "2014-01-01",
  "valid_to": null
}
```

---

## 14. Object: IntergovernmentalAgreement *(new in v4.1)*

### 14.1 Purpose

Represents an agreement between two or more polities (Commonwealth/States/Territories) or the constitutive instrument of an intergovernmental body. Required for all `ministerial_council` entities and for any authority asserted as `intergovernmental_agreement`.

### 14.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `name` | string | R | E.g. "National Health Reform Agreement". |
| `iga_type` | enum | R | See allowed values. |
| `parties` | array<string> | R | Entity IDs of party polities. |
| `instrument_citation` | string | R | Full citation / version reference. |
| `subject_matter` | string | R | |
| `signed_date` | date | C | Required for fixed-form agreements. |
| `effective_from` | date | R | |
| `effective_to` | date | O | |
| `successor_iga_id` | string | O | Where superseded. |

### 14.3 Allowed `iga_type` values

- `national_agreement`
- `national_partnership_agreement`
- `intergovernmental_agreement`
- `ministerial_council_terms_of_reference`
- `national_cabinet_constitutive_arrangement`
- `bilateral_agreement`
- `multilateral_agreement`

### 14.4 Validation rules

- Every `Entity` of `entity_type = ministerial_council` MUST have an `Authority` record with `authority_source = intergovernmental_agreement` referencing an IGA via `iga_id`.
- `parties` MUST contain at least two distinct polities for `iga_type ∈ {national_agreement, national_partnership_agreement, intergovernmental_agreement, bilateral_agreement, multilateral_agreement}`.
- For `iga_type = ministerial_council_terms_of_reference`, parties are the polities whose ministers participate.

### 14.5 Example

```json
{
  "id": "iga_council_federal_financial_relations_tor",
  "name": "Council on Federal Financial Relations — Terms of Reference",
  "iga_type": "ministerial_council_terms_of_reference",
  "parties": [
    "ent_cwlth_polity",
    "ent_nsw_polity", "ent_vic_polity", "ent_qld_polity",
    "ent_wa_polity", "ent_sa_polity", "ent_tas_polity",
    "ent_act_polity", "ent_nt_polity"
  ],
  "instrument_citation": "Council on Federal Financial Relations Terms of Reference (current version)",
  "subject_matter": "Federal financial relations; Federation Funding Agreements oversight.",
  "effective_from": "2020-05-29",
  "effective_to": null
}
```

---

## 15. Object: CourtDecision *(new in v4.1)*

### 15.1 Purpose

Represents a specific court determination. Required where `authority_source = court_determination` or where a constraint or Native Title status references a court determination.

### 15.2 Fields

| Field | Type | Status | Notes |
|---|---|---|---|
| `id` | string | R | Unique. |
| `case_name` | string | R | |
| `citation` | string | R | Neutral and/or report citation. |
| `court` | string | R | E.g. "Federal Court of Australia", "High Court of Australia". |
| `jurisdiction` | enum | R | |
| `decision_date` | date | R | |
| `subject_matter` | string | R | |
| `binding_effect` | enum | O | `determination` \| `declaration` \| `injunction` \| `other`. |

### 15.3 Validation rules

- `citation` MUST be specific (case name + court + year + identifier).
- `court` MUST be populated.

### 15.4 Example

```json
{
  "id": "cd_quandamooka_v_qld_2011",
  "case_name": "Quandamooka People #1 v State of Queensland",
  "citation": "[2011] FCA 675",
  "court": "Federal Court of Australia",
  "jurisdiction": "commonwealth",
  "decision_date": "2011-07-04",
  "subject_matter": "Native title determination — Quandamooka People",
  "binding_effect": "determination"
}
```

---

## 16. National Committee Dataset (FIXED)

The following bodies MUST be modelled as Entities of the indicated `entity_type`. This list is fixed for v4.1.

### 16.1 Cabinet Committees (`entity_type = cabinet_committee`)

- Expenditure Review Committee
- National Security Committee of Cabinet
- Parliamentary Business Committee
- Priority and Delivery Committee
- Net Zero Economy Committee

### 16.2 Cabinet Subcommittees (`entity_type = cabinet_subcommittee`)

- Government Communications Subcommittee
- National Security Investment Subcommittee

### 16.3 National Cabinet System

- **National Cabinet** — `entity_type = intergovernmental_body`

Reform Committees (`entity_type = intergovernmental_body`, reporting to National Cabinet):
- Health Reform Committee
- Energy Reform Committee
- Infrastructure and Transport Reform Committee
- Skills Reform Committee
- Regional Reform Committee

### 16.4 Ministerial Councils (`entity_type = ministerial_council`)

- Agriculture Ministers' Meeting
- Attorneys-General Meeting
- Community Services Ministers' Meeting
- Council on Federal Financial Relations
- Data and Digital Ministers' Meeting
- Disability Reform Ministers' Meeting
- Education Ministers' Meeting
- Emergency Management Ministers' Meeting
- Energy and Climate Change Ministers' Meeting
- Environment Ministers' Meeting
- Health Ministers' Meeting
- Housing and Homelessness Ministers' Meeting
- Infrastructure and Transport Ministers' Meeting
- Joint Council on Closing the Gap
- Planning Ministers' Meeting
- Skills and Workforce Ministers' Meeting
- Trade and Investment Ministers' Meeting
- Veterans' Affairs Ministers' Meeting
- Water Ministers' Meeting
- Women and Women's Safety Ministers' Meeting

### 16.5 Modelling rules for committees

- Cabinet committees and subcommittees: `Authority.authority_source = executive` (Prime Ministerial / Cabinet establishment).
- National Cabinet: requires two `Authority` records — one with `authority_source = executive` and one with `authority_source = intergovernmental_agreement`.
- National Cabinet Reform Committees: `Authority.authority_source = intergovernmental_agreement` (established by National Cabinet) supplemented by `executive` where appropriate.
- Ministerial Councils: `Authority.authority_source = intergovernmental_agreement` referencing terms of reference.
- Cross-government committees: `Authority.authority_source ∈ {executive, administrative_instrument}`. `statute` is permitted only with explicit justification per Validation Rule 8.
- Committee membership MUST be modelled as `Relationship.relationship_type = membership` with `member_role` populated.
- Subcommittees report to parent committees via `Relationship.relationship_type = reports_to`.
- Secretariat support is modelled as `Relationship.relationship_type = supported_by`.

---

## 17. Visual graph implementation notes

Recommended mapping:

- **Nodes:** `Entity`, `Authority`, `SpatialReference`, `NativeTitleStatus`, `Constraint`, `FinancialFlow`, `Interaction`, `Function`, `Legislation`, `Program`, `IntergovernmentalAgreement`, `CourtDecision`.
- **Edges:**
  - `Relationship` — typed edge between two `Entity` nodes (including `membership`, `reports_to`, `supported_by`).
  - `Delegation` — typed edge between two `Entity` nodes.
  - `Authority.holder_entity_id` — edge from `Authority` to `Entity`.
  - `Authority.legislation_id` / `iga_id` / `court_decision_id` — edges from `Authority` to the relevant nodes.
  - `Interaction.accountable_actor_id`, `decision_maker_id`, `acting_under_authority_id`, `acting_under_delegation_id`, `function_id`, `program_id` — edges from `Interaction`.
  - `FinancialFlow.payer_entity_id` / `recipient_entity_id` / `authority_id` / `program_id` — edges from `FinancialFlow`.
  - `Program.administering_entity_id` / `legislation_id` / `iga_id` / `authority_id` — edges from `Program`.
  - `Constraint.applies_to_*` and `triggers_constraints` from `NativeTitleStatus`.
  - `SpatialReference.parent_spatial_id`.

Recommended visual conventions:

- Distinguish `direct`, `delegated` and `recognised` authority by edge style.
- Distinguish revenue vs expenditure financial flows by colour.
- Render Native Title as a distinct node class.
- Render committees in a dedicated layer, with cabinet committees, intergovernmental bodies, ministerial councils and cross-government committees colour-coded.
- Render `Function`, `Legislation`, `Program`, `IntergovernmentalAgreement` and `CourtDecision` as taxonomy/reference nodes that other entities and authorities link to.

---

## 18. Minimum viable instantiation checklist

A working v4.1 graph instance should include, at minimum:

- One `Entity` per polity (Commonwealth + 6 States + 2 Territories).
- `Entity` records for at least one Department, Minister and Accountable Authority per polity covered by the use case.
- `Authority` records for the constitutive basis of each `Entity`.
- `Function`, `Legislation`, `Program`, `IntergovernmentalAgreement` and `CourtDecision` records as referenced by the use case.
- `Relationship` records for portfolio membership, legislation administration, committee membership and reporting lines.
- `Delegation` records for any modelled exercise of delegated power.
- `SpatialReference` and `NativeTitleStatus` records as engaged.
- `Constraint` records for practical decision constraints.
- `FinancialFlow` records, correctly classified, with `authority_id` and (where required) `program_id`.
- `Interaction` records, each with `accountable_actor_id`, `decision_maker_id`, `interaction_outcome_type` and `function_id`.
- For every cabinet committee, intergovernmental body, ministerial council, and modelled cross-government committee in scope: an `Entity`, an `Authority` of correct `authority_source`, membership `Relationship` records with `member_role`, and (where applicable) an `IntergovernmentalAgreement`.

---

## 19. Schema-wide validation rules

A v4.1 instance MUST satisfy all of the following rules. These are normative.

1. **Authority is explicit and never inferred.** Every assertion of capacity references an `Authority` record. Authority is not derived from `entity_type`, `name`, `relationship_type`, `interaction_type`, `function_id`, `SpatialReference`, or committee membership.

2. **Delegation cites legal source.** Every `Delegation` populates `delegation_source_type`, `delegation_instrument` and `legislation_id`.

3. **Commonwealth finance/resource delegations cite PGPA finance law.**

4. **Substantive delegations cite enabling or portfolio legislation.**

5. **Local government traces to State legislation.**

6. **Native Title is status, not delegation.**

7. **Spatial does not override law.**

8. **Constraints are practical and bounded.** Stare decisis and the Kable principle are out of scope.

9. **Revenue is not tax expenditure.** `tax_expenditure` is not a permitted `flow_class`. Rates, fees, royalties and levies are revenue.

10. **Every interaction has an accountable actor and a decision maker.** `accountable_actor_id`, `decision_maker_id` and `interaction_outcome_type` MUST be populated.

11. **Relationships are enduring; interactions are events.**

12. **AAO is Commonwealth-only.**

13. **Temporal integrity.** `valid_to ≥ valid_from` where both are populated.

14. **Referential integrity.** Every `*_id` must resolve to a record of the correct object type.

15. **No active free-text function fields.** `power_or_function`, `delegated_power`, `function`, and `applies_to_function` are deprecated. `function_id` MUST be used.

16. **All legislation references use `legislation_id`.** `authority_instrument` is retained as the citation field but the authoritative reference is `legislation_id` where applicable.

17. **Programs required for grant flows.** `FinancialFlow` of `flow_class ∈ {grant, subsidy, transfer_payment}` and `Interaction` of `interaction_type = grant_action` MUST populate `program_id`.

18. **Committees MUST have an authority source.**
    - `cabinet_committee` and `cabinet_subcommittee` → `executive`.
    - `intergovernmental_body` (incl. National Cabinet) → `executive` and/or `intergovernmental_agreement`.
    - `ministerial_council` → `intergovernmental_agreement` (with `iga_id` populated).
    - `cross_government_committee` → `executive` or `administrative_instrument`. `statute` is not permitted unless explicitly justified by an Authority record citing the specific statutory provision establishing the committee, in which case `legislation_id` MUST be populated and the justification recorded in `Authority.notes`.

19. **Committee membership is explicit.** Membership is asserted via `Relationship.relationship_type = membership` with `member_role` populated. Membership MUST NOT be inferred from any other field.

20. **Committees do not produce statutory decisions by default.** Committees MUST NOT produce `interaction_outcome_type = statutory_decision` unless an explicit `Authority` with `authority_source = statute` exists for the committee.

21. **Authority must not be inferred** from membership, function or relationship. (Restated for prominence.)

22. **`cross_government_committee` cannot use `statute`** as `authority_source` unless explicitly justified per Rule 18.

---

## 20. v4.1 Change Log

| Change | Description |
|---|---|
| Object added: `Function` | First-class function object; replaces all free-text function fields. |
| Object added: `Legislation` | First-class legislation object; referenced from `Authority`, `Relationship`, `Constraint`, `Delegation`, `Program`. |
| Object added: `Program` | Required for grant/subsidy/transfer-payment financial flows and grant interactions. |
| Object added: `IntergovernmentalAgreement` | Required for ministerial councils and any `intergovernmental_agreement` authority source. |
| Object added: `CourtDecision` | Required where `authority_source = court_determination` or constraints/Native Title reference court decisions. |
| Enum extended: `Authority.authority_source` | Added `executive`, `intergovernmental_agreement`, `administrative_instrument`. |
| Enum extended: `Entity.entity_type` | Added `cabinet_committee`, `cabinet_subcommittee`, `intergovernmental_body`, `ministerial_council`, `cross_government_committee`. |
| Enum extended: `Relationship.relationship_type` | Added `membership`, `supported_by` (and clarified use of `reports_to`). |
| Field added: `Relationship.member_role` | Required for `membership` relationships. |
| Field added: `Relationship.legislation_id` | Required for `administers_legislation` relationships. |
| Field added: `Interaction.decision_maker_id` | Required. |
| Field added: `Interaction.interaction_outcome_type` | Required; enum: `statutory_decision`, `executive_decision`, `intergovernmental_agreement`, `advisory`. |
| Field added: `Interaction.function_id`, `program_id` | `program_id` required for `grant_action`. |
| Field added: `FinancialFlow.program_id`, `authority_id` | `program_id` required for grant/subsidy/transfer-payment classes. |
| Field added: `Authority.legislation_id`, `iga_id`, `court_decision_id`, `function_id` | Required conditionally. |
| Field added: `Delegation.legislation_id`, `function_id` | |
| Field added: `Constraint.legislation_id`, `court_decision_id`, `applies_to_function_id` | |
| Field added: `NativeTitleStatus.court_decision_id` | |
| Fields deprecated | `Authority.power_or_function`, `Delegation.delegated_power`, `Delegation.function`, `Constraint.applies_to_function`. |
| Validation rules | Restated; new rules 15–22 added covering function/legislation/program references, committee authority, membership, decision typing, and `cross_government_committee` statute restriction. |
| National Committee Dataset | Fixed list of cabinet committees, cabinet subcommittees, National Cabinet system bodies, and ministerial councils added (Section 16). |
| Appendix A | Validation instances added (Appendix A). |

---

## Appendix A — Validation Instances

The following five instances are fully populated against the v4.1 schema. Records reference one another by `id`. Records relied on across instances (e.g. `ent_cwlth_polity`) are defined in the first instance that uses them and reused.

---

### A.1 Instance 1 — National Security Committee of Cabinet

```json
{
  "Entity": [
    {
      "id": "ent_cwlth_polity",
      "name": "Commonwealth of Australia",
      "entity_type": "polity",
      "jurisdiction": "commonwealth",
      "legal_basis_id": "auth_cwlth_constitution",
      "valid_from": "1901-01-01",
      "valid_to": null
    },
    {
      "id": "ent_cwlth_pm",
      "name": "Prime Minister",
      "entity_type": "minister",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "legal_basis_id": "auth_cwlth_pm_office",
      "valid_from": "1901-01-01",
      "valid_to": null
    },
    {
      "id": "ent_cwlth_dpmc",
      "name": "Department of the Prime Minister and Cabinet",
      "entity_type": "department",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "portfolio_id": "port_cwlth_pmc",
      "legal_basis_id": "auth_cwlth_dpmc_aao",
      "aao_reference": "AAO_2024_PMC",
      "valid_from": "1971-12-22",
      "valid_to": null
    },
    {
      "id": "ent_cwlth_nsc_cabinet",
      "name": "National Security Committee of Cabinet",
      "entity_type": "cabinet_committee",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "legal_basis_id": "auth_nsc_cabinet_executive",
      "valid_from": "1996-03-11",
      "valid_to": null
    }
  ],
  "Authority": [
    {
      "id": "auth_cwlth_constitution",
      "holder_entity_id": "ent_cwlth_polity",
      "authority_source": "constitution",
      "authority_mechanism": "direct",
      "authority_instrument": "Commonwealth of Australia Constitution Act",
      "function_id": "fn_polity_existence",
      "valid_from": "1901-01-01"
    },
    {
      "id": "auth_cwlth_pm_office",
      "holder_entity_id": "ent_cwlth_pm",
      "authority_source": "executive",
      "authority_mechanism": "direct",
      "authority_instrument": "Commission from the Governor-General under s64 of the Constitution",
      "function_id": "fn_head_of_government",
      "valid_from": "1901-01-01"
    },
    {
      "id": "auth_cwlth_dpmc_aao",
      "holder_entity_id": "ent_cwlth_dpmc",
      "authority_source": "administrative_instrument",
      "authority_mechanism": "direct",
      "authority_instrument": "Administrative Arrangements Order (current)",
      "function_id": "fn_cabinet_secretariat_support",
      "valid_from": "2024-07-29"
    },
    {
      "id": "auth_nsc_cabinet_executive",
      "holder_entity_id": "ent_cwlth_nsc_cabinet",
      "authority_source": "executive",
      "authority_mechanism": "direct",
      "authority_instrument": "Cabinet Handbook (current edition); Prime Ministerial determination of Cabinet committee structure",
      "function_id": "fn_national_security_coordination",
      "valid_from": "1996-03-11",
      "notes": "Cabinet committee established under the executive authority of the Prime Minister; not a statutory body."
    }
  ],
  "Function": [
    {
      "id": "fn_polity_existence",
      "name": "Polity existence",
      "function_class": "other",
      "description": "Existence and capacity of a polity under its constitutional instrument."
    },
    {
      "id": "fn_head_of_government",
      "name": "Head of Government",
      "function_class": "appointments_and_governance",
      "description": "Leadership of the Government of the Commonwealth, advising the Governor-General."
    },
    {
      "id": "fn_cabinet_secretariat_support",
      "name": "Cabinet secretariat and coordination",
      "function_class": "intergovernmental_coordination",
      "description": "Secretariat, coordination and policy support to Cabinet and Cabinet committees."
    },
    {
      "id": "fn_national_security_coordination",
      "name": "National security policy coordination",
      "function_class": "policy_development",
      "description": "Cabinet-level coordination of national security and intelligence policy.",
      "subject_domain": "national_security"
    }
  ],
  "Relationship": [
    {
      "id": "rel_pm_chairs_nsc",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_pm",
      "to_entity_id": "ent_cwlth_nsc_cabinet",
      "member_role": "chair",
      "legal_basis_id": "auth_nsc_cabinet_executive",
      "valid_from": "1996-03-11",
      "valid_to": null
    },
    {
      "id": "rel_dpmc_supports_nsc",
      "relationship_type": "supported_by",
      "from_entity_id": "ent_cwlth_nsc_cabinet",
      "to_entity_id": "ent_cwlth_dpmc",
      "legal_basis_id": "auth_cwlth_dpmc_aao",
      "valid_from": "1996-03-11",
      "valid_to": null
    }
  ],
  "Interaction": [
    {
      "id": "int_nsc_endorses_strategy",
      "interaction_type": "decision",
      "interaction_outcome_type": "executive_decision",
      "accountable_actor_id": "ent_cwlth_nsc_cabinet",
      "decision_maker_id": "ent_cwlth_nsc_cabinet",
      "acting_under_authority_id": "auth_nsc_cabinet_executive",
      "subject_matter": "Endorsement of national security strategy update",
      "function_id": "fn_national_security_coordination",
      "instrument_produced": "NSC Cabinet record of decision (classified)",
      "event_date": "2025-03-12"
    }
  ]
}
```

---

### A.2 Instance 2 — National Cabinet

```json
{
  "Entity": [
    {
      "id": "ent_nsw_polity",
      "name": "State of New South Wales",
      "entity_type": "polity",
      "jurisdiction": "nsw",
      "legal_basis_id": "auth_nsw_state_constitution",
      "valid_from": "1901-01-01"
    },
    {
      "id": "ent_vic_polity", "name": "State of Victoria",
      "entity_type": "polity", "jurisdiction": "vic",
      "legal_basis_id": "auth_vic_state_constitution", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_qld_polity", "name": "State of Queensland",
      "entity_type": "polity", "jurisdiction": "qld",
      "legal_basis_id": "auth_qld_state_constitution", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_wa_polity", "name": "State of Western Australia",
      "entity_type": "polity", "jurisdiction": "wa",
      "legal_basis_id": "auth_wa_state_constitution", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_sa_polity", "name": "State of South Australia",
      "entity_type": "polity", "jurisdiction": "sa",
      "legal_basis_id": "auth_sa_state_constitution", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_tas_polity", "name": "State of Tasmania",
      "entity_type": "polity", "jurisdiction": "tas",
      "legal_basis_id": "auth_tas_state_constitution", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_act_polity", "name": "Australian Capital Territory",
      "entity_type": "polity", "jurisdiction": "act",
      "legal_basis_id": "auth_act_self_government", "valid_from": "1989-05-11"
    },
    {
      "id": "ent_nt_polity", "name": "Northern Territory",
      "entity_type": "polity", "jurisdiction": "nt",
      "legal_basis_id": "auth_nt_self_government", "valid_from": "1978-07-01"
    },
    {
      "id": "ent_national_cabinet",
      "name": "National Cabinet",
      "entity_type": "intergovernmental_body",
      "jurisdiction": "cross_jurisdiction",
      "legal_basis_id": "auth_national_cabinet_executive",
      "valid_from": "2020-03-13",
      "valid_to": null
    }
  ],
  "Authority": [
    {
      "id": "auth_nsw_state_constitution",
      "holder_entity_id": "ent_nsw_polity",
      "authority_source": "state_constitution",
      "authority_mechanism": "direct",
      "authority_instrument": "Constitution Act 1902 (NSW)",
      "legislation_id": "leg_nsw_constitution_act_1902",
      "function_id": "fn_polity_existence",
      "valid_from": "1902-12-19"
    },
    {
      "id": "auth_national_cabinet_executive",
      "holder_entity_id": "ent_national_cabinet",
      "authority_source": "executive",
      "authority_mechanism": "direct",
      "authority_instrument": "Joint executive determination by First Ministers (March 2020); Prime Ministerial announcement",
      "function_id": "fn_national_first_ministers_coordination",
      "valid_from": "2020-03-13",
      "notes": "National Cabinet is established under the executive authority of First Ministers; it is not a statutory body."
    },
    {
      "id": "auth_national_cabinet_iga",
      "holder_entity_id": "ent_national_cabinet",
      "authority_source": "intergovernmental_agreement",
      "authority_mechanism": "direct",
      "authority_instrument": "National Cabinet operating arrangements (current)",
      "iga_id": "iga_national_cabinet_arrangements",
      "function_id": "fn_national_first_ministers_coordination",
      "valid_from": "2020-05-29"
    }
  ],
  "Function": [
    {
      "id": "fn_national_first_ministers_coordination",
      "name": "First Ministers' national coordination",
      "function_class": "intergovernmental_coordination",
      "description": "Coordination of national policy priorities by Commonwealth, State and Territory First Ministers."
    }
  ],
  "IntergovernmentalAgreement": [
    {
      "id": "iga_national_cabinet_arrangements",
      "name": "National Cabinet — Operating Arrangements",
      "iga_type": "national_cabinet_constitutive_arrangement",
      "parties": [
        "ent_cwlth_polity", "ent_nsw_polity", "ent_vic_polity", "ent_qld_polity",
        "ent_wa_polity", "ent_sa_polity", "ent_tas_polity",
        "ent_act_polity", "ent_nt_polity"
      ],
      "instrument_citation": "National Cabinet Operating Arrangements (current version)",
      "subject_matter": "Constitutive arrangements for National Cabinet meetings, agenda setting, and decision-making.",
      "effective_from": "2020-05-29",
      "effective_to": null
    }
  ],
  "Relationship": [
    {
      "id": "rel_pm_chairs_nc",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_pm",
      "to_entity_id": "ent_national_cabinet",
      "member_role": "chair",
      "legal_basis_id": "auth_national_cabinet_executive",
      "valid_from": "2020-03-13",
      "valid_to": null
    },
    {
      "id": "rel_nsw_premier_member_nc",
      "relationship_type": "membership",
      "from_entity_id": "ent_nsw_polity",
      "to_entity_id": "ent_national_cabinet",
      "member_role": "member",
      "legal_basis_id": "auth_national_cabinet_iga",
      "valid_from": "2020-03-13",
      "valid_to": null
    },
    {
      "id": "rel_dpmc_supports_nc",
      "relationship_type": "supported_by",
      "from_entity_id": "ent_national_cabinet",
      "to_entity_id": "ent_cwlth_dpmc",
      "legal_basis_id": "auth_cwlth_dpmc_aao",
      "valid_from": "2020-03-13",
      "valid_to": null
    }
  ],
  "Interaction": [
    {
      "id": "int_nc_communique_2025_q1",
      "interaction_type": "intergovernmental_agreement_action",
      "interaction_outcome_type": "intergovernmental_agreement",
      "accountable_actor_id": "ent_national_cabinet",
      "decision_maker_id": "ent_national_cabinet",
      "acting_under_authority_id": "auth_national_cabinet_iga",
      "subject_matter": "National Cabinet communiqué — health and housing reform priorities",
      "function_id": "fn_national_first_ministers_coordination",
      "instrument_produced": "National Cabinet Communiqué Q1 2025",
      "event_date": "2025-02-21"
    }
  ]
}
```

---

### A.3 Instance 3 — Council on Federal Financial Relations

```json
{
  "Entity": [
    {
      "id": "ent_cwlth_treasurer",
      "name": "Treasurer of the Commonwealth",
      "entity_type": "minister",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "legal_basis_id": "auth_cwlth_treasurer_office",
      "valid_from": "1901-01-01"
    },
    {
      "id": "ent_cwlth_treasury",
      "name": "Department of the Treasury",
      "entity_type": "department",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "portfolio_id": "port_cwlth_treasury",
      "legal_basis_id": "auth_cwlth_treasury_aao",
      "aao_reference": "AAO_2024_Treasury",
      "valid_from": "1901-01-01"
    },
    {
      "id": "ent_nsw_treasurer", "name": "Treasurer of New South Wales",
      "entity_type": "minister", "jurisdiction": "nsw",
      "parent_entity_id": "ent_nsw_polity",
      "legal_basis_id": "auth_nsw_treasurer_office", "valid_from": "1901-01-01"
    },
    {
      "id": "ent_cffr",
      "name": "Council on Federal Financial Relations",
      "entity_type": "ministerial_council",
      "jurisdiction": "cross_jurisdiction",
      "legal_basis_id": "auth_cffr_iga",
      "valid_from": "2009-01-01",
      "valid_to": null
    }
  ],
  "Authority": [
    {
      "id": "auth_cwlth_treasurer_office",
      "holder_entity_id": "ent_cwlth_treasurer",
      "authority_source": "executive",
      "authority_mechanism": "direct",
      "authority_instrument": "Commission under s64 of the Constitution",
      "function_id": "fn_treasury_portfolio_leadership",
      "valid_from": "1901-01-01"
    },
    {
      "id": "auth_cwlth_treasury_aao",
      "holder_entity_id": "ent_cwlth_treasury",
      "authority_source": "administrative_instrument",
      "authority_mechanism": "direct",
      "authority_instrument": "Administrative Arrangements Order (current)",
      "function_id": "fn_treasury_portfolio_leadership",
      "valid_from": "2024-07-29"
    },
    {
      "id": "auth_cffr_iga",
      "holder_entity_id": "ent_cffr",
      "authority_source": "intergovernmental_agreement",
      "authority_mechanism": "direct",
      "authority_instrument": "Council on Federal Financial Relations Terms of Reference (current); Intergovernmental Agreement on Federal Financial Relations 2008",
      "iga_id": "iga_council_federal_financial_relations_tor",
      "function_id": "fn_federal_financial_relations_coordination",
      "valid_from": "2009-01-01"
    }
  ],
  "Function": [
    {
      "id": "fn_treasury_portfolio_leadership",
      "name": "Treasury portfolio leadership",
      "function_class": "policy_development",
      "description": "Leadership of fiscal, taxation and federal financial relations policy."
    },
    {
      "id": "fn_federal_financial_relations_coordination",
      "name": "Federal financial relations coordination",
      "function_class": "intergovernmental_coordination",
      "description": "Oversight and coordination of Federation Funding Agreements and federal financial arrangements between the Commonwealth and the States and Territories."
    }
  ],
  "IntergovernmentalAgreement": [
    {
      "id": "iga_council_federal_financial_relations_tor",
      "name": "Council on Federal Financial Relations — Terms of Reference",
      "iga_type": "ministerial_council_terms_of_reference",
      "parties": [
        "ent_cwlth_polity","ent_nsw_polity","ent_vic_polity","ent_qld_polity",
        "ent_wa_polity","ent_sa_polity","ent_tas_polity",
        "ent_act_polity","ent_nt_polity"
      ],
      "instrument_citation": "Council on Federal Financial Relations Terms of Reference (current version); Intergovernmental Agreement on Federal Financial Relations 2008",
      "subject_matter": "Federal financial relations; oversight of Federation Funding Agreements.",
      "effective_from": "2009-01-01",
      "effective_to": null
    }
  ],
  "Program": [
    {
      "id": "prog_cwlth_ffa_health",
      "name": "Federation Funding Agreement — Health",
      "program_type": "transfer_payment_program",
      "administering_entity_id": "ent_cwlth_treasury",
      "iga_id": "iga_council_federal_financial_relations_tor",
      "authority_id": "auth_cffr_iga",
      "subject_domain": "health_financing",
      "valid_from": "2020-07-01",
      "valid_to": null
    }
  ],
  "Relationship": [
    {
      "id": "rel_cwlth_treasurer_chairs_cffr",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_treasurer",
      "to_entity_id": "ent_cffr",
      "member_role": "chair",
      "legal_basis_id": "auth_cffr_iga",
      "valid_from": "2009-01-01"
    },
    {
      "id": "rel_nsw_treasurer_member_cffr",
      "relationship_type": "membership",
      "from_entity_id": "ent_nsw_treasurer",
      "to_entity_id": "ent_cffr",
      "member_role": "member",
      "legal_basis_id": "auth_cffr_iga",
      "valid_from": "2009-01-01"
    },
    {
      "id": "rel_treasury_supports_cffr",
      "relationship_type": "supported_by",
      "from_entity_id": "ent_cffr",
      "to_entity_id": "ent_cwlth_treasury",
      "legal_basis_id": "auth_cwlth_treasury_aao",
      "valid_from": "2009-01-01"
    }
  ],
  "Interaction": [
    {
      "id": "int_cffr_endorse_ffa_health_2025",
      "interaction_type": "intergovernmental_agreement_action",
      "interaction_outcome_type": "intergovernmental_agreement",
      "accountable_actor_id": "ent_cffr",
      "decision_maker_id": "ent_cffr",
      "acting_under_authority_id": "auth_cffr_iga",
      "subject_matter": "Endorsement of Federation Funding Agreement — Health 2025 schedule",
      "function_id": "fn_federal_financial_relations_coordination",
      "instrument_produced": "CFFR Communiqué (March 2025)",
      "program_id": null,
      "event_date": "2025-03-21"
    }
  ],
  "FinancialFlow": [
    {
      "id": "fin_cwlth_ffa_health_nsw_2025",
      "flow_direction": "outbound",
      "flow_class": "transfer_payment",
      "payer_entity_id": "ent_cwlth_treasury",
      "recipient_entity_id": "ent_nsw_polity",
      "amount": 9500000000,
      "currency": "AUD",
      "financial_authority_source": "appropriation_act",
      "financial_authority_instrument": "Federal Financial Relations Act 2009 (Cth); Appropriation Act (No. 1) 2024-25",
      "authority_id": "auth_cffr_iga",
      "program_id": "prog_cwlth_ffa_health",
      "linked_interaction_id": "int_cffr_endorse_ffa_health_2025",
      "period_start": "2025-07-01",
      "period_end": "2026-06-30"
    }
  ]
}
```

---

### A.4 Instance 4 — Cross-government senior officials committee

This instance models a **Secretaries' Board on Indigenous Affairs Coordination** as a cross-government senior officials committee established under executive authority.

```json
{
  "Entity": [
    {
      "id": "ent_cwlth_niaa",
      "name": "National Indigenous Australians Agency",
      "entity_type": "agency",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "legal_basis_id": "auth_niaa_executive_order",
      "valid_from": "2019-07-01"
    },
    {
      "id": "ent_secretaries_board_indigenous",
      "name": "Secretaries' Board on Indigenous Affairs Coordination",
      "entity_type": "cross_government_committee",
      "jurisdiction": "commonwealth",
      "parent_entity_id": "ent_cwlth_polity",
      "legal_basis_id": "auth_secretaries_board_indigenous_executive",
      "valid_from": "2020-07-30",
      "valid_to": null
    }
  ],
  "Authority": [
    {
      "id": "auth_niaa_executive_order",
      "holder_entity_id": "ent_cwlth_niaa",
      "authority_source": "executive",
      "authority_mechanism": "direct",
      "authority_instrument": "Executive Order establishing the National Indigenous Australians Agency (29 May 2019)",
      "function_id": "fn_indigenous_affairs_coordination",
      "valid_from": "2019-07-01"
    },
    {
      "id": "auth_secretaries_board_indigenous_executive",
      "holder_entity_id": "ent_secretaries_board_indigenous",
      "authority_source": "administrative_instrument",
      "authority_mechanism": "direct",
      "authority_instrument": "Terms of Reference issued by the Secretary of PM&C (administrative instrument, current)",
      "function_id": "fn_indigenous_affairs_coordination",
      "valid_from": "2020-07-30",
      "notes": "Cross-government senior officials committee. Authority is administrative; no statutory basis is asserted."
    }
  ],
  "Function": [
    {
      "id": "fn_indigenous_affairs_coordination",
      "name": "Indigenous affairs cross-portfolio coordination",
      "function_class": "intergovernmental_coordination",
      "description": "Cross-portfolio coordination of Closing the Gap implementation and Indigenous affairs policy across Commonwealth departments."
    }
  ],
  "Relationship": [
    {
      "id": "rel_niaa_ceo_chairs_secretaries_board",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_niaa",
      "to_entity_id": "ent_secretaries_board_indigenous",
      "member_role": "chair",
      "legal_basis_id": "auth_secretaries_board_indigenous_executive",
      "valid_from": "2020-07-30"
    },
    {
      "id": "rel_dpmc_member_secretaries_board",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_dpmc",
      "to_entity_id": "ent_secretaries_board_indigenous",
      "member_role": "member",
      "legal_basis_id": "auth_secretaries_board_indigenous_executive",
      "valid_from": "2020-07-30"
    },
    {
      "id": "rel_treasury_member_secretaries_board",
      "relationship_type": "membership",
      "from_entity_id": "ent_cwlth_treasury",
      "to_entity_id": "ent_secretaries_board_indigenous",
      "member_role": "member",
      "legal_basis_id": "auth_secretaries_board_indigenous_executive",
      "valid_from": "2020-07-30"
    },
    {
      "id": "rel_niaa_supports_secretaries_board",
      "relationship_type": "supported_by",
      "from_entity_id": "ent_secretaries_board_indigenous",
      "to_entity_id": "ent_cwlth_niaa",
      "legal_basis_id": "auth_niaa_executive_order",
      "valid_from": "2020-07-30"
    }
  ],
  "Interaction": [
    {
      "id": "int_secretaries_board_advice_2025",
      "interaction_type": "consultation_event",
      "interaction_outcome_type": "advisory",
      "accountable_actor_id": "ent_secretaries_board_indigenous",
      "decision_maker_id": "ent_secretaries_board_indigenous",
      "acting_under_authority_id": "auth_secretaries_board_indigenous_executive",
      "subject_matter": "Senior officials advice on Closing the Gap implementation",
      "function_id": "fn_indigenous_affairs_coordination",
      "instrument_produced": "Secretaries' Board minute and advice to ministers",
      "event_date": "2025-04-08"
    }
  ]
}
```

---

### A.5 Instance 5 — Local government + ministerial council scenario

This instance models a Queensland local government interaction (planning approval) intersecting a ministerial council scenario (Planning Ministers' Meeting endorsement of national planning principles), with a Native Title constraint engaged.

```json
{
  "Entity": [
    {
      "id": "ent_qld_minister_planning",
      "name": "Queensland Minister for Planning",
      "entity_type": "minister",
      "jurisdiction": "qld",
      "parent_entity_id": "ent_qld_polity",
      "legal_basis_id": "auth_qld_minister_planning_office",
      "valid_from": "2017-12-12"
    },
    {
      "id": "ent_planning_ministers_meeting",
      "name": "Planning Ministers' Meeting",
      "entity_type": "ministerial_council",
      "jurisdiction": "cross_jurisdiction",
      "legal_basis_id": "auth_pmm_iga",
      "valid_from": "2021-06-04",
      "valid_to": null
    },
    {
      "id": "ent_redland_city_council",
      "name": "Redland City Council",
      "entity_type": "local_government_council",
      "jurisdiction": "local",
      "parent_entity_id": "ent_qld_polity",
      "legal_basis_id": "auth_redland_lg_act",
      "valid_from": "2008-03-15"
    },
    {
      "id": "ent_quandamooka_people",
      "name": "Quandamooka People",
      "entity_type": "native_title_holder_group",
      "jurisdiction": "qld",
      "legal_basis_id": "auth_quandamooka_recognised",
      "valid_from": "2011-07-04"
    },
    {
      "id": "ent_qyac",
      "name": "Quandamooka Yoolooburrabee Aboriginal Corporation",
      "entity_type": "prescribed_body_corporate",
      "jurisdiction": "qld",
      "legal_basis_id": "auth_qyac_pbc",
      "valid_from": "2011-09-22"
    }
  ],
  "Authority": [
    {
      "id": "auth_qld_state_constitution",
      "holder_entity_id": "ent_qld_polity",
      "authority_source": "state_constitution",
      "authority_mechanism": "direct",
      "authority_instrument": "Constitution of Queensland 2001",
      "legislation_id": "leg_qld_constitution_2001",
      "function_id": "fn_polity_existence",
      "valid_from": "2002-06-06"
    },
    {
      "id": "auth_qld_minister_planning_office",
      "holder_entity_id": "ent_qld_minister_planning",
      "authority_source": "statute",
      "authority_mechanism": "direct",
      "authority_instrument": "Planning Act 2016 (Qld); Constitution of Queensland 2001",
      "legislation_id": "leg_qld_planning_act_2016",
      "function_id": "fn_planning_policy_leadership",
      "valid_from": "2017-07-03"
    },
    {
      "id": "auth_pmm_iga",
      "holder_entity_id": "ent_planning_ministers_meeting",
      "authority_source": "intergovernmental_agreement",
      "authority_mechanism": "direct",
      "authority_instrument": "Planning Ministers' Meeting Terms of Reference (current)",
      "iga_id": "iga_pmm_tor",
      "function_id": "fn_planning_intergovernmental_coordination",
      "valid_from": "2021-06-04"
    },
    {
      "id": "auth_redland_lg_act",
      "holder_entity_id": "ent_redland_city_council",
      "authority_source": "statute",
      "authority_mechanism": "direct",
      "authority_instrument": "Local Government Act 2009 (Qld)",
      "legislation_id": "leg_qld_local_government_act_2009",
      "function_id": "fn_local_government_general_competence",
      "valid_from": "2008-03-15"
    },
    {
      "id": "auth_qld_planning_act_2016_assessment_manager",
      "holder_entity_id": "ent_redland_city_council",
      "authority_source": "statute",
      "authority_mechanism": "direct",
      "authority_instrument": "Planning Act 2016 (Qld) — assessment manager functions",
      "legislation_id": "leg_qld_planning_act_2016",
      "function_id": "fn_planning_assessment_decision",
      "valid_from": "2017-07-03"
    },
    {
      "id": "auth_quandamooka_recognised",
      "holder_entity_id": "ent_quandamooka_people",
      "authority_source": "court_determination",
      "authority_mechanism": "recognised",
      "authority_instrument": "Quandamooka People #1 v State of Queensland [2011] FCA 675",
      "court_decision_id": "cd_quandamooka_v_qld_2011",
      "function_id": "fn_native_title_rights_holder",
      "valid_from": "2011-07-04"
    },
    {
      "id": "auth_qyac_pbc",
      "holder_entity_id": "ent_qyac",
      "authority_source": "statute",
      "authority_mechanism": "direct",
      "authority_instrument": "Native Title Act 1993 (Cth) ss56-57; CATSI Act 2006 (Cth)",
      "legislation_id": "leg_cwlth_nta_1993",
      "function_id": "fn_pbc_management",
      "valid_from": "2011-09-22"
    }
  ],
  "Function": [
    {
      "id": "fn_planning_policy_leadership",
      "name": "State planning policy leadership",
      "function_class": "policy_development",
      "description": "Leadership of State planning policy and the State planning framework.",
      "subject_domain": "planning"
    },
    {
      "id": "fn_planning_intergovernmental_coordination",
      "name": "National planning coordination",
      "function_class": "intergovernmental_coordination",
      "description": "Coordination of national planning policy directions across Commonwealth, State and Territory planning ministers.",
      "subject_domain": "planning"
    },
    {
      "id": "fn_local_government_general_competence",
      "name": "Local government general competence",
      "function_class": "service_delivery",
      "description": "General local government powers and functions under State local government legislation."
    },
    {
      "id": "fn_planning_assessment_decision",
      "name": "Planning assessment decision",
      "function_class": "planning_assessment",
      "description": "Assessment and decision on development applications under the Planning Act 2016 (Qld).",
      "subject_domain": "planning"
    },
    {
      "id": "fn_native_title_rights_holder",
      "name": "Holding recognised native title rights",
      "function_class": "other",
      "description": "Holding native title rights and interests recognised by court determination."
    },
    {
      "id": "fn_pbc_management",
      "name": "PBC management of native title",
      "function_class": "appointments_and_governance",
      "description": "Holding and managing native title rights on behalf of the common law holders."
    },
    {
      "id": "fn_land_dealing",
      "name": "Land dealing",
      "function_class": "land_dealing",
      "description": "Decisions and acts dealing with land, including grants of interests, approvals and disposals."
    }
  ],
  "Legislation": [
    {
      "id": "leg_qld_constitution_2001",
      "short_title": "Constitution of Queensland 2001",
      "citation": "Constitution of Queensland 2001 (Qld)",
      "legislation_type": "act",
      "jurisdiction": "qld",
      "commenced": "2002-06-06"
    },
    {
      "id": "leg_qld_planning_act_2016",
      "short_title": "Planning Act 2016",
      "citation": "Planning Act 2016 (Qld)",
      "legislation_type": "act",
      "jurisdiction": "qld",
      "commenced": "2017-07-03"
    },
    {
      "id": "leg_qld_local_government_act_2009",
      "short_title": "Local Government Act 2009",
      "citation": "Local Government Act 2009 (Qld)",
      "legislation_type": "act",
      "jurisdiction": "qld",
      "commenced": "2010-07-01"
    },
    {
      "id": "leg_cwlth_nta_1993",
      "short_title": "Native Title Act 1993",
      "citation": "Native Title Act 1993 (Cth)",
      "legislation_type": "act",
      "jurisdiction": "commonwealth",
      "commenced": "1994-01-01"
    },
    {
      "id": "leg_cwlth_pgpa_act_2013",
      "short_title": "Public Governance, Performance and Accountability Act 2013",
      "citation": "Public Governance, Performance and Accountability Act 2013 (Cth)",
      "legislation_type": "act",
      "jurisdiction": "commonwealth",
      "commenced": "2014-07-01"
    },
    {
      "id": "leg_cwlth_aea_2013",
      "short_title": "Australian Education Act 2013",
      "citation": "Australian Education Act 2013 (Cth)",
      "legislation_type": "act",
      "jurisdiction": "commonwealth",
      "commenced": "2014-01-01"
    }
  ],
  "IntergovernmentalAgreement": [
    {
      "id": "iga_pmm_tor",
      "name": "Planning Ministers' Meeting — Terms of Reference",
      "iga_type": "ministerial_council_terms_of_reference",
      "parties": [
        "ent_cwlth_polity","ent_nsw_polity","ent_vic_polity","ent_qld_polity",
        "ent_wa_polity","ent_sa_polity","ent_tas_polity",
        "ent_act_polity","ent_nt_polity"
      ],
      "instrument_citation": "Planning Ministers' Meeting Terms of Reference (current version)",
      "subject_matter": "National planning policy coordination.",
      "effective_from": "2021-06-04"
    }
  ],
  "CourtDecision": [
    {
      "id": "cd_quandamooka_v_qld_2011",
      "case_name": "Quandamooka People #1 v State of Queensland",
      "citation": "[2011] FCA 675",
      "court": "Federal Court of Australia",
      "jurisdiction": "commonwealth",
      "decision_date": "2011-07-04",
      "subject_matter": "Native title determination — Quandamooka People",
      "binding_effect": "determination"
    }
  ],
  "SpatialReference": [
    {
      "id": "sp_lga_redland",
      "spatial_type": "local_government_area",
      "name": "Redland City local government area",
      "external_dataset": "ABS_ASGS_LGA",
      "external_id": "LGA36720",
      "applicable_jurisdiction": "qld"
    },
    {
      "id": "sp_lga_redland_parcel_12_smith_st",
      "spatial_type": "cadastral_parcel",
      "name": "12 Smith Street, Cleveland — Lot 4 RP123456",
      "external_dataset": "QLD_Cadastre",
      "external_id": "L4RP123456",
      "parent_spatial_id": "sp_lga_redland",
      "applicable_jurisdiction": "qld"
    },
    {
      "id": "sp_nntt_qcd2014_001",
      "spatial_type": "native_title_determination_area",
      "name": "Quandamooka People Determination Area",
      "external_dataset": "NNTT_Register_of_Native_Title_Determinations",
      "external_id": "QCD2011/001",
      "applicable_jurisdiction": "qld",
      "valid_from": "2011-07-04"
    }
  ],
  "NativeTitleStatus": [
    {
      "id": "nts_quandamooka_2011",
      "holder_group_entity_id": "ent_quandamooka_people",
      "prescribed_body_corporate_id": "ent_qyac",
      "status": "determined",
      "determination_instrument": "Federal Court determination QUD6128/1998 (4 July 2011)",
      "court_decision_id": "cd_quandamooka_v_qld_2011",
      "spatial_reference_id": "sp_nntt_qcd2014_001",
      "rights_and_interests": "Mix of exclusive and non-exclusive rights as set out in the determination.",
      "triggers_constraints": ["con_cwlth_native_title_future_act"],
      "valid_from": "2011-07-04"
    }
  ],
  "Constraint": [
    {
      "id": "con_cwlth_native_title_future_act",
      "constraint_effect": "requires",
      "constraint_source": "statute",
      "constraint_instrument": "Native Title Act 1993 (Cth) Pt 2 Div 3",
      "legislation_id": "leg_cwlth_nta_1993",
      "applies_to_function_id": "fn_land_dealing",
      "applies_to_spatial_id": "sp_nntt_qcd2014_001",
      "description": "Future acts affecting native title rights and interests must follow the future act regime.",
      "triggering_condition": "Proposed act affecting determined or claimed native title rights and interests.",
      "process_required": "Future act process: notification, right to negotiate, ILUA, or alternative procedure as applicable.",
      "valid_from": "1994-01-01"
    },
    {
      "id": "con_qld_planning_scheme_residential_zone",
      "constraint_effect": "conditions",
      "constraint_source": "statute",
      "constraint_instrument": "Planning Act 2016 (Qld); Redland City Plan 2018 — Residential zone code",
      "legislation_id": "leg_qld_planning_act_2016",
      "applies_to_function_id": "fn_planning_assessment_decision",
      "applies_to_spatial_id": "sp_lga_redland",
      "description": "Assessable development within the residential zone is conditioned on compliance with the residential zone code.",
      "valid_from": "2018-10-08"
    }
  ],
  "Relationship": [
    {
      "id": "rel_qld_planning_minister_member_pmm",
      "relationship_type": "membership",
      "from_entity_id": "ent_qld_minister_planning",
      "to_entity_id": "ent_planning_ministers_meeting",
      "member_role": "member",
      "legal_basis_id": "auth_pmm_iga",
      "valid_from": "2021-06-04"
    }
  ],
  "Interaction": [
    {
      "id": "int_pmm_endorse_national_planning_principles_2025",
      "interaction_type": "intergovernmental_agreement_action",
      "interaction_outcome_type": "intergovernmental_agreement",
      "accountable_actor_id": "ent_planning_ministers_meeting",
      "decision_maker_id": "ent_planning_ministers_meeting",
      "acting_under_authority_id": "auth_pmm_iga",
      "subject_matter": "Endorsement of National Planning Principles (2025)",
      "function_id": "fn_planning_intergovernmental_coordination",
      "instrument_produced": "Planning Ministers' Meeting communiqué, 14 February 2025",
      "event_date": "2025-02-14"
    },
    {
      "id": "int_redland_da_2025_00471",
      "interaction_type": "approval",
      "interaction_outcome_type": "statutory_decision",
      "accountable_actor_id": "ent_redland_city_council",
      "decision_maker_id": "ent_redland_city_council",
      "acting_under_authority_id": "auth_qld_planning_act_2016_assessment_manager",
      "subject_matter": "Material change of use — multi-unit dwelling, 12 Smith Street, Cleveland",
      "function_id": "fn_planning_assessment_decision",
      "instrument_produced": "Decision notice DA-2025-00471",
      "spatial_reference_id": "sp_lga_redland_parcel_12_smith_st",
      "constraints_engaged": [
        "con_qld_planning_scheme_residential_zone"
      ],
      "event_date": "2025-08-14"
    }
  ]
}
```

End of v4.1 Build Schema.


