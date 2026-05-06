# Data

**Version:** 4.1
**Status:** Partially populated — significant provisional content

---

## Dataset Overview

| File | Description | Format |
|---|---|---|
| `CURRENT_01_entities.csv` | Entity records | CSV |
| `CURRENT_02_connections.csv` | Relationship records | CSV |
| `ux_spatial_nodes_v41.csv` | Spatial node data for map view | CSV |
| `ux_panels_v41.json` | Authority panel content | JSON |
| `ux_filters_v41.json` | Filter configuration | JSON |
| `ux_views_v41.json` | View configuration | JSON |
| `ux_map_rules_v41.json` | Map rendering rules | JSON |
| `ux_map_connectors_v41.json` | Map connector rendering rules | JSON |

---

## Data Sources

Entity and relationship data was sourced from:

- **Commonwealth Budget Statements** (2025-26) — portfolio structure, entity lists, financial flows
- **Administrative Arrangements Orders** — Commonwealth portfolio and function assignments
- **Safe Work Australia / agency websites** — entity existence and legislative basis
- **Australian Government organisations register** — PGPA entity classification
- **State and Territory government websites** — state entity structure
- **Federal Register of Legislation** — Act citations and commencement dates
- **NNTT Register of Native Title Determinations** — native title spatial data
- **ABS Australian Statistical Geography Standard** — LGA and state boundary identifiers

Data was extracted through a combination of PDF scraping, structured web extraction, and manual curation. Budget Statements were processed as Word documents via the Claude project context.

---

## Data Quality and Status

### Confirmed records
Records marked `status: normal` have been cross-referenced against at least one primary source and are considered reliable for the current version.

### Provisional records
Records marked `status: provisional` are present in the model but have not been fully validated against primary sources. Common reasons for provisional status:

- Authority instrument not yet cited to a specific section
- Entity existence confirmed but legislative basis not yet verified
- Financial flow amount confirmed but authority source not yet resolved
- Relationship inferred from organisational context rather than confirmed from instrument

**232 of 240 financial flow records are currently provisional** — amounts are drawn from Budget Statements but the specific authority instruments (appropriation act references, program IDs) are not yet fully resolved.

### Deprecated records
Records marked `status: deprecated` represent entities or relationships that no longer exist. They are hidden by default in the interface but retained in the dataset for temporal completeness.

---

## Known Gaps

- **Commonwealth**: AAO references partially populated; some non-corporate Commonwealth entities lack `legal_basis_id` resolution to specific statutory sections
- **States/Territories**: Coverage is partial — Queensland and NSW are more complete than other states
- **Local government**: Placeholder coverage only — 537 local government councils are not individually modelled at this stage
- **Legislation dataset**: Referenced throughout the model but a complete `Legislation` object dataset is not yet built
- **IntergovernmentalAgreement dataset**: Key IGAs modelled (CFFR, National Cabinet, Planning Ministers' Meeting) but coverage is incomplete
- **Financial flows**: Authority resolution pending for 232 of 240 records
- **Native title**: Key determinations modelled as examples; national coverage not yet attempted

---

## Temporal Coverage

The current dataset primarily reflects the structure of Australian government as at **mid-2025**. Historical records (prior AAOs, abolished entities, superseded relationships) are partially present but not systematically populated for earlier periods.

---

## Data Maintenance

This dataset requires ongoing governance as:
- AAOs change with ministerial reshuffles and machinery of government changes
- Entities are established and abolished by legislation
- Financial flows change with each Budget
- Native title determinations are registered on an ongoing basis
- Legislation is amended

The `valid_from` / `valid_to` temporal model is designed to support incremental updates without requiring full rebuilds.

---

## Provenance

All Authority records are required to cite a specific instrument (`authority_instrument` field). Free-text or generic citations are validation failures under the v4.1 schema. Where provenance is uncertain, the record is marked `provisional`.

Dataset provenance is tracked at the record level through the `valid_from` date and the `authority_instrument` citation. A formal provenance log is a planned addition for v4.2.

