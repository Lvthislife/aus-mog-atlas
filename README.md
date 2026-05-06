# aus-mog-atlas

Interactive prototype of a federated Australian Machinery of Government Atlas — mapping Commonwealth, state, territory and local government entities, authority pathways, accountability structures and institutional relationships as a searchable knowledge graph.

---

> **Status: Prototype — v4.1**
> Active development. Architecture and ontology are subject to ongoing review. Data is partially provisional. See [DATA.md](DATA.md) for coverage details.

---

## What This Is

The Australian Machinery of Government Atlas is a federated knowledge graph that maps the structure, authority, accountability and relationships of Australian government — across all jurisdictions, levels, and institutional types.

It is not an org chart. It is not a directory. It is a semantic model of how Australian government is constituted, authorised, and connected — from the Commonwealth Constitution through to local government councils and native title prescribed bodies corporate.

The prototype renders as an interactive browser application with multiple views, filters, and an authority panel showing the legal source of each entity's existence and powers.

---

## What Problem It Solves

Australian government structure is genuinely complex — nine polities, hundreds of entity types, overlapping legislative frameworks, intergovernmental agreements, constitutional constraints, native title regimes, and financial flows that cross jurisdictions. No single publicly accessible resource maps this comprehensively or in machine-readable form.

This project aims to produce:
- A canonical, citable, versioned model of Australian government structure
- A practical tool for policy analysts, governance advisors, researchers, and public administrators
- A foundation for AI-assisted governance reasoning — where models need reliable structured knowledge of institutional relationships, authority chains, and accountability pathways

---

## Current Coverage

| Layer | Status |
|---|---|
| Commonwealth entities | Partially complete — provisional |
| State/Territory entities | Partially complete — provisional |
| Local government | Partially complete — provisional |
| Parliamentary institutions | Partial |
| Judicial institutions | Partial |
| Intergovernmental bodies | Partial |
| Native title | Partial |
| Authority records | Partially populated — many provisional |
| Financial flows | 232 of 240 flows provisional (authority unresolved) |
| Legislation | Referenced; full dataset in progress |

---

## Views

The prototype implements five views:

**Relationship View** — primary exploration. Radial cluster graph organised by jurisdiction and entity type. Nodes represent entities; edges represent structural relationships (portfolio membership, regulatory authority, coordination, funding, constitutional basis). Filterable by jurisdiction, entity type, relationship type, authority source, and status.

**Map View** — spatial view of jurisdiction coverage and funding flows. Commonwealth entities render as national overlays, not Canberra points. Intergovernmental bodies render as connectors between member polities, not inside any single jurisdiction.

**Authority View** — shows the chain Entity → Authority → Legislation / IGA / Instrument. Every entity in the model traces its existence and powers to an explicit legal source.

**Funding View** — shows financial flows between entities. 232 of 240 flows are currently flagged provisional pending authority resolution.

**Coordination View** — shows intergovernmental coordination relationships and IGAs.

**Portfolio View** — tree layout showing portfolio hierarchy: departments and their entities.

---

## Key Design Principles

**Authority is never inferred.** Every entity's existence and powers trace to an explicit Authority record citing a legal instrument — a statute, the Constitution, a state constitution, an intergovernmental agreement, an executive instrument, or a court determination. Authority is never derived from an entity's name, function, location, or relationships.

**No central node.** The graph has no single root. Commonwealth entities are not placed above state entities. The model reflects constitutional federation, not administrative hierarchy.

**Authority is not geography.** Spatial coverage describes where an entity operates. It does not determine legal authority. A Commonwealth entity covering the whole nation is not anchored to Canberra.

**Relationships and interactions are distinct.** A relationship is an enduring structural link (Department administers Act). An interaction is a discrete event (Minister approves grant). These are modelled separately and must not be conflated.

**Confirmed vs provisional.** All records carry a status flag. Provisional records are visible by default but marked with a warning indicator. Deprecated records are hidden by default.

---

## Technology

The prototype is a single self-contained HTML file built from:
- Entity and connection CSV datasets
- A Python builder script (`CURRENT_03_builder.py`) that generates the HTML
- UX specification files (views, filters, map rules, connectors, panels) in JSON
- Spatial node data in CSV

The graph rendering uses a radial cluster layout. The UK Government Digital Service's approach to rendering government structure as an interactive graph was an inspiration for the visual architecture, though the semantic model and ontology are built independently for the Australian constitutional and administrative context.

---

## Repository Structure

```
aus-mog-atlas/
├── README.md
├── ARCHITECTURE.md
├── DATA.md
├── mog_atlas_v41_prototype.html    ← open in browser to run
├── CURRENT_03_builder.py           ← generates HTML from CSV + JSON
├── data/
│   ├── CURRENT_01_entities.csv
│   ├── CURRENT_02_connections.csv
│   └── ux_spatial_nodes_v41.csv
├── ux/
│   ├── ux_views_v41.json
│   ├── ux_filters_v41.json
│   ├── ux_map_rules_v41.json
│   ├── ux_map_connectors_v41.json
│   └── ux_panels_v41.json
└── schema/
    └── australian_mog_v4_1_build_schema.md
```

---

## Running the Prototype

Open `mog_atlas_v41_prototype.html` in a modern browser. No server, no dependencies, no installation required.

---

## Project Context

Built independently as a research and policy tool. The semantic model draws on Australian constitutional law, administrative law, and public administration frameworks including the Westminster system, responsible government, the PGPA Act accountability framework, the SOCI Act, native title law, and intergovernmental agreement structures.

The project is at the intersection of knowledge graph architecture, Australian public administration, and AI-assisted governance reasoning. The structured semantic model is intended as a foundation for governance AI applications that require reliable, citable, machine-readable knowledge of Australian institutional structure.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full semantic model and ontology documentation.
See [DATA.md](DATA.md) for dataset coverage, provenance, and data quality notes.

