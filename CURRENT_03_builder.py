#!/usr/bin/env python3
"""
mog_atlas.py — Australian Machinery of Government Atlas builder (single-file)

Reads:   mog_entities.csv, mog_connections.csv  (source-of-truth CSVs)
Writes:  mog_atlas.html                         (self-contained, 5-view atlas)

Usage:
    python3 mog_atlas.py
    python3 mog_atlas.py --entities ENT.csv --connections CONN.csv --out atlas.html

The output HTML is fully self-contained: no server, no external data files.
External deps loaded from CDN at runtime: D3.js (graph + circle), Leaflet (map).

Views:
    1. Graph    — ring-based force layout by legal_class
    2. Map      — Leaflet map, all 1,729 entities geocoded
    3. Circle   — concentric rings, legal_class ordered outward
    4. Registry — filterable sortable table
    5. Stats    — counts, budget, distributions

Author: Kristen Foster
Version: v2.4 (April 2026)
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

# Ring ordering (inner -> outer). These are the canonical ring numbers from
# mog_entities.csv. Labels match the legal_class in each ring.
RING_ORDER = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 99]

RING_LABELS = {
    -1: "Constitutional",
    0:  "Ministry",
    1:  "State Dept",
    2:  "NCA",
    3:  "CCE",
    4:  "GBE",
    5:  "State Statutory",
    6:  "State SOC",
    7:  "State Integrity",
    9:  "Statutory Office",
    10: "Advisory",
    11: "IGA / Min Forum",
    12: "LGA Association",
    13: "Council",
    14: "Subsidiary / Industry / Investment",
    99: "Federal Court",
}

# Tier colours (used in graph, map markers, stats)
TIER_COLOURS = {
    "Federal":    "#5ba3f5",
    "State":      "#e07a5f",
    "Territory":  "#f4a261",
    "Local":      "#74c69d",
    "Cross-tier": "#bc6c25",
}

# Connection type colours
CONN_COLOURS = {
    "parent_of":           "#5ba3f5",
    "member_of":           "#9b2335",
    "funds":               "#2d6a4f",
    "has_interest_in":     "#d4a017",
    "shareholder_of":      "#e07a5f",
    "regulates":           "#6b4c7a",
    "overlaps_with":       "#7b6b8a",
    "constitutional_role": "#bc6c25",
}

# Sector colours (15 sectors in dataset)
SECTOR_COLOURS = {
    "Local Government":                "#74c69d",
    "Economy & Finance":               "#2e86ab",
    "Transport & Infrastructure":      "#1d3557",
    "Parliament & Accountability":     "#5b7fa6",
    "Health":                          "#2d6a4f",
    "Environment & Energy":            "#606c38",
    "Justice & Safety":                "#e07a5f",
    "Agriculture & Resources":         "#8b9467",
    "Defence":                         "#6c757d",
    "Intergovernmental":               "#9b2335",
    "Recreation, Culture & Heritage":  "#6b4c7a",
    "Education":                       "#40916c",
    "Industry & Science":              "#e9c46a",
    "Housing & Community":             "#bc6c25",
    "Social Services":                 "#74c69d",
}

# Fields kept in the JS-embedded payload (trimmed to reduce HTML size).
# 'description' is dropped from payload — pulled on-demand via registry click
# would require a server, so for a single-file atlas we include a truncated
# version. Full description kept in registry detail panel.
ENTITY_PAYLOAD_FIELDS = [
    "id", "label", "full_name", "tier", "jurisdiction", "legal_class",
    "accountability", "portfolio", "sector", "ring",
    "lat", "lon", "budget_000s", "budget_type", "financial_year",
    "data_quality", "legislation", "established", "parent_id",
    "data_source", "lga_code", "geographic_scope",
]

CONN_PAYLOAD_FIELDS = [
    "id", "from", "to", "type", "label", "amount_aud",
    "financial_year", "data_quality",
]

# ─────────────────────────────────────────────────────────────────────────────
# CSV LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_entities(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        # Numeric coercion (but keep strings where the value is blank)
        for fld in ("lat", "lon"):
            v = r.get(fld, "").strip()
            r[fld] = float(v) if v else None
        v = r.get("budget_000s", "").strip()
        try:
            r["budget_000s"] = float(v) if v else None
        except ValueError:
            r["budget_000s"] = None
        v = r.get("ring", "").strip()
        try:
            r["ring"] = int(v) if v else None
        except ValueError:
            r["ring"] = None
        # Truncate description for tooltip — full text goes in registry detail
        desc = r.get("description", "")
        r["description"] = (desc[:400] + "…") if len(desc) > 400 else desc
    return rows


def load_connections(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        v = r.get("amount_aud", "").strip()
        try:
            r["amount_aud"] = float(v) if v else None
        except ValueError:
            r["amount_aud"] = None
    return rows


def slim_entity(e: dict) -> dict:
    return {k: e.get(k) for k in ENTITY_PAYLOAD_FIELDS}


def slim_connection(c: dict) -> dict:
    return {k: c.get(k) for k in CONN_PAYLOAD_FIELDS}


# ─────────────────────────────────────────────────────────────────────────────
# STATS PRECOMPUTE
# ─────────────────────────────────────────────────────────────────────────────

def compute_stats(entities: list[dict], connections: list[dict]) -> dict:
    tier_counts = Counter(e["tier"] for e in entities if e.get("tier"))
    jur_counts = Counter(e["jurisdiction"] for e in entities if e.get("jurisdiction"))
    sector_counts = Counter(e["sector"] for e in entities if e.get("sector"))
    legal_counts = Counter(e["legal_class"] for e in entities if e.get("legal_class"))
    acc_counts = Counter(e["accountability"] for e in entities if e.get("accountability"))
    dq_counts = Counter(e["data_quality"] for e in entities if e.get("data_quality"))
    conn_counts = Counter(c["type"] for c in connections if c.get("type"))

    # Budget by tier (entities with budget)
    budget_by_tier = defaultdict(float)
    budget_by_jur = defaultdict(float)
    budget_by_sector = defaultdict(float)
    n_with_budget = 0
    total_budget = 0.0
    for e in entities:
        b = e.get("budget_000s")
        if b is not None:
            n_with_budget += 1
            total_budget += b
            budget_by_tier[e.get("tier", "?")] += b
            budget_by_jur[e.get("jurisdiction", "?")] += b
            budget_by_sector[e.get("sector", "?")] += b

    return {
        "n_entities": len(entities),
        "n_connections": len(connections),
        "n_with_budget": n_with_budget,
        "total_budget_000s": total_budget,
        "tier_counts": dict(tier_counts),
        "jur_counts": dict(jur_counts),
        "sector_counts": dict(sector_counts),
        "legal_counts": dict(legal_counts),
        "acc_counts": dict(acc_counts),
        "dq_counts": dict(dq_counts),
        "conn_counts": dict(conn_counts),
        "budget_by_tier": dict(budget_by_tier),
        "budget_by_jur": dict(budget_by_jur),
        "budget_by_sector": dict(budget_by_sector),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Australian MoG Atlas — __N_ENTITIES__ entities · __N_CONNECTIONS__ connections</title>

<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700;9..144,800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
:root {
  --bg: #0a0e1a;
  --bg-alt: #111827;
  --surface: #1a2234;
  --surface-hi: #243049;
  --border: #2a3650;
  --border-hi: #3a4a6b;
  --text: #e6edf7;
  --text-dim: #8ba0bd;
  --text-mute: #5a6b87;
  --accent: #f5b841;       /* ochre */
  --accent-alt: #e07a5f;   /* terracotta */
  --blue: #5ba3f5;
  --green: #74c69d;
  --red: #e07a5f;
  --purple: #9b6cbf;
  --header-h: 52px;
  --tabs-h: 40px;
  --filter-h: 38px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
  font-size: 13px;
  line-height: 1.4;
  -webkit-font-smoothing: antialiased;
}

/* ══ HEADER ══ */
#header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 500;
  height: var(--header-h);
  background: linear-gradient(to right, var(--bg) 0%, var(--bg-alt) 100%);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 18px; gap: 16px;
}
#header h1 {
  font-family: 'Fraunces', serif;
  font-size: 18px; font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}
#header h1 .sub {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px; font-weight: 500;
  color: var(--accent);
  margin-left: 8px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
#header-stats {
  margin-left: auto;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px; color: var(--text-dim);
  display: flex; gap: 18px;
}
#header-stats b { color: var(--accent); font-weight: 600; }

/* ══ TABS ══ */
#tabs {
  position: fixed; top: var(--header-h); left: 0; right: 0; z-index: 490;
  height: var(--tabs-h);
  background: var(--bg-alt); border-bottom: 1px solid var(--border);
  display: flex; padding: 0 12px;
}
.tab {
  padding: 0 18px; height: 100%;
  display: flex; align-items: center; gap: 8px;
  font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  color: var(--text-dim); cursor: pointer;
  border-bottom: 2px solid transparent;
  text-transform: uppercase; letter-spacing: 0.1em;
  transition: all 0.15s ease;
}
.tab:hover { color: var(--text); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; opacity: 0.6; }

/* ══ FILTER BAR ══ */
#filters {
  position: fixed;
  top: calc(var(--header-h) + var(--tabs-h));
  left: 0; right: 0; z-index: 480;
  height: var(--filter-h);
  background: var(--surface); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px; padding: 0 12px;
  overflow-x: auto; overflow-y: hidden;
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}
#filters::-webkit-scrollbar { height: 4px; }
#filters::-webkit-scrollbar-thumb { background: var(--border); }
.filter-group { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.filter-group label {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--text-mute); text-transform: uppercase; letter-spacing: 0.08em;
}
.filter-group select, .filter-group input {
  background: var(--bg); color: var(--text);
  border: 1px solid var(--border); border-radius: 3px;
  padding: 4px 8px; font-size: 12px; font-family: 'IBM Plex Sans', sans-serif;
  min-width: 110px;
}
.filter-group select:focus, .filter-group input:focus {
  outline: none; border-color: var(--accent);
}
#filter-clear {
  background: none; border: 1px solid var(--border); border-radius: 3px;
  color: var(--text-dim); font-family: 'IBM Plex Mono', monospace;
  font-size: 10px; padding: 4px 10px; cursor: pointer;
  text-transform: uppercase; letter-spacing: 0.08em;
}
#filter-clear:hover { color: var(--accent); border-color: var(--accent); }
#filter-count {
  margin-left: auto; flex-shrink: 0;
  font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  color: var(--text-dim);
}
#filter-count b { color: var(--accent); }

/* ══ VIEW CONTAINERS ══ */
.view {
  position: fixed;
  top: calc(var(--header-h) + var(--tabs-h) + var(--filter-h));
  left: 0; right: 0; bottom: 0;
  display: none;
  background: var(--bg);
}
.view.active { display: block; }

/* ══ GRAPH ══ */
#graph-svg { width: 100%; height: 100%; cursor: grab; }
#graph-svg:active { cursor: grabbing; }
.node circle { stroke: #0a0e1a; stroke-width: 1.5; cursor: pointer; }
.node circle:hover { stroke: var(--accent); stroke-width: 2.5; }
.node.highlight circle { stroke: var(--accent); stroke-width: 3; }
.node text {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; fill: var(--text-dim);
  pointer-events: none; text-anchor: middle;
}
.link { stroke-opacity: 0.35; fill: none; }
.link.highlight { stroke-opacity: 0.9; }
.ring-label {
  font-family: 'Fraunces', serif; font-size: 10px;
  fill: var(--text-mute); text-anchor: middle;
  font-style: italic;
}
.ring-guide { fill: none; stroke: var(--border); stroke-dasharray: 2 4; stroke-width: 0.5; }

/* ══ MAP ══ */
#map { width: 100%; height: 100%; background: var(--bg); }
.leaflet-container { background: var(--bg-alt); font-family: 'IBM Plex Sans', sans-serif; }
.leaflet-popup-content-wrapper, .leaflet-popup-tip {
  background: var(--surface); color: var(--text);
  border: 1px solid var(--border);
}
.leaflet-popup-content { margin: 10px 14px; font-size: 12px; }
.leaflet-popup-content strong { color: var(--accent); }
.leaflet-control-attribution { background: rgba(10,14,26,0.8) !important; color: var(--text-mute) !important; }
.leaflet-control-attribution a { color: var(--text-dim) !important; }
.leaflet-control-zoom a {
  background: var(--surface) !important; color: var(--text) !important;
  border-color: var(--border) !important;
}

/* ══ CIRCLE ══ */
#circle-svg { width: 100%; height: 100%; }
.ring-arc { fill: none; stroke-width: 1; }

/* ══ REGISTRY ══ */
#registry-wrap { height: 100%; overflow: auto; }
#registry-wrap table {
  width: 100%; border-collapse: collapse;
  font-family: 'IBM Plex Sans', sans-serif; font-size: 12px;
}
#registry-wrap th {
  position: sticky; top: 0;
  background: var(--bg-alt); color: var(--accent);
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
  padding: 10px 12px; text-align: left;
  border-bottom: 1px solid var(--border);
  cursor: pointer; user-select: none;
}
#registry-wrap th:hover { color: var(--text); }
#registry-wrap th .sort-ind { color: var(--text-mute); margin-left: 4px; }
#registry-wrap td {
  padding: 8px 12px; border-bottom: 1px solid var(--border);
  color: var(--text); vertical-align: top;
}
#registry-wrap tr { cursor: pointer; }
#registry-wrap tr:hover td { background: var(--surface); }
#registry-wrap td.id { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-dim); }
#registry-wrap td.budget { font-family: 'IBM Plex Mono', monospace; text-align: right; color: var(--green); }
.tier-tag, .dq-tag {
  display: inline-block; padding: 1px 6px; border-radius: 2px;
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
}

/* ══ STATS ══ */
#stats-wrap { height: 100%; overflow: auto; padding: 28px; }
.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px; margin-bottom: 32px;
}
.stat-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 4px; padding: 18px;
}
.stat-card .num {
  font-family: 'Fraunces', serif; font-size: 38px; font-weight: 700;
  color: var(--accent); line-height: 1; letter-spacing: -0.02em;
}
.stat-card .lbl {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em;
  margin-top: 8px;
}
.stat-card .sub {
  font-size: 11px; color: var(--text-mute); margin-top: 4px;
}
.chart-section {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 4px; padding: 20px; margin-bottom: 20px;
}
.chart-section h3 {
  font-family: 'Fraunces', serif; font-size: 16px; font-weight: 600;
  color: var(--text); margin-bottom: 16px;
}
.chart-section h3 .sub {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--text-mute); font-weight: 400; margin-left: 10px;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.bar-row {
  display: grid; grid-template-columns: 180px 1fr 80px;
  align-items: center; gap: 12px; padding: 4px 0;
  font-size: 12px;
}
.bar-row .lbl { color: var(--text); font-size: 12px; }
.bar-row .bar { height: 18px; background: var(--bg); border-radius: 2px; overflow: hidden; position: relative; }
.bar-row .fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
.bar-row .val {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  color: var(--text-dim); text-align: right;
}

/* ══ DETAIL PANEL ══ */
#detail {
  position: fixed; top: 0; right: -460px;
  width: 440px; max-width: 90vw; height: 100vh;
  background: var(--bg-alt); border-left: 1px solid var(--border);
  box-shadow: -8px 0 40px rgba(0,0,0,0.5);
  z-index: 600; transition: right 0.25s ease;
  overflow-y: auto; padding: 24px;
}
#detail.open { right: 0; }
#detail-close {
  position: absolute; top: 16px; right: 16px;
  background: none; border: none; color: var(--text-dim);
  font-size: 20px; cursor: pointer; line-height: 1;
}
#detail-close:hover { color: var(--accent); }
#detail h2 {
  font-family: 'Fraunces', serif; font-size: 22px; font-weight: 700;
  color: var(--text); line-height: 1.2; padding-right: 30px;
  margin-bottom: 4px;
}
#detail .id {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--text-mute); letter-spacing: 0.05em;
  margin-bottom: 16px;
}
#detail .detail-block {
  border-top: 1px solid var(--border); padding: 14px 0;
}
#detail .detail-block:first-of-type { border-top: none; padding-top: 0; }
#detail .detail-row {
  display: grid; grid-template-columns: 120px 1fr; gap: 12px;
  padding: 4px 0; font-size: 12px;
}
#detail .detail-row .k {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--text-mute); text-transform: uppercase;
  letter-spacing: 0.08em; padding-top: 2px;
}
#detail .detail-row .v { color: var(--text); }
#detail .desc {
  font-size: 13px; color: var(--text-dim); line-height: 1.55;
  font-style: italic;
}
#detail h3 {
  font-family: 'Fraunces', serif; font-size: 14px; color: var(--accent);
  margin: 16px 0 8px;
}
#detail .conn-list { font-size: 12px; }
#detail .conn-item {
  padding: 6px 0; border-bottom: 1px dotted var(--border);
  display: grid; grid-template-columns: 80px 1fr; gap: 10px;
}
#detail .conn-item .typ {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.05em;
  padding-top: 2px;
}
#detail .conn-item .to {
  color: var(--text); cursor: pointer;
}
#detail .conn-item .to:hover { color: var(--accent); }

/* ══ TOOLTIP ══ */
#tooltip {
  position: fixed; z-index: 1000; pointer-events: none;
  background: var(--surface-hi); border: 1px solid var(--border-hi);
  border-radius: 3px; padding: 8px 12px;
  font-size: 11px; color: var(--text);
  max-width: 280px; opacity: 0;
  transition: opacity 0.15s;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
#tooltip.show { opacity: 1; }
#tooltip b { color: var(--accent); display: block; margin-bottom: 2px; font-family: 'Fraunces', serif; font-size: 13px; }
#tooltip .meta { color: var(--text-dim); font-size: 10px; font-family: 'IBM Plex Mono', monospace; }
</style>
</head>
<body>

<div id="header">
  <h1>MoG Atlas<span class="sub">v2.4 · April 2026</span></h1>
  <div id="header-stats">
    <span><b>__N_ENTITIES__</b> entities</span>
    <span><b>__N_CONNECTIONS__</b> connections</span>
    <span><b>__N_WITH_BUDGET__</b> with budget</span>
  </div>
</div>

<div id="tabs">
  <div class="tab active" data-view="graph"><span class="dot"></span>Graph</div>
  <div class="tab" data-view="map"><span class="dot"></span>Map</div>
  <div class="tab" data-view="circle"><span class="dot"></span>Circle</div>
  <div class="tab" data-view="registry"><span class="dot"></span>Registry</div>
  <div class="tab" data-view="stats"><span class="dot"></span>Stats</div>
</div>

<div id="filters">
  <div class="filter-group">
    <label>Tier</label>
    <select id="f-tier"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Jurisdiction</label>
    <select id="f-jur"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Sector</label>
    <select id="f-sector"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Legal Class</label>
    <select id="f-legal"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Accountability</label>
    <select id="f-acc"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Search</label>
    <input type="text" id="f-search" placeholder="name or id…" style="min-width:160px">
  </div>
  <button id="filter-clear">Clear</button>
  <div id="filter-count"><b>0</b> visible</div>
</div>

<!-- ══ VIEWS ══ -->
<div class="view active" id="view-graph"><svg id="graph-svg"></svg></div>
<div class="view" id="view-map"><div id="map"></div></div>
<div class="view" id="view-circle"><svg id="circle-svg"></svg></div>
<div class="view" id="view-registry"><div id="registry-wrap"></div></div>
<div class="view" id="view-stats"><div id="stats-wrap"></div></div>

<!-- ══ DETAIL PANEL ══ -->
<div id="detail">
  <button id="detail-close">✕</button>
  <div id="detail-body"></div>
</div>

<!-- ══ TOOLTIP ══ -->
<div id="tooltip"></div>

<script>
// ═══════════════════════════════════════════════════════════════════════════
// PAYLOAD — injected at build time
// ═══════════════════════════════════════════════════════════════════════════
const PAYLOAD = __PAYLOAD__;
const ENTITIES = PAYLOAD.entities;
const CONNECTIONS = PAYLOAD.connections;
const STATS = PAYLOAD.stats;
const CFG = PAYLOAD.config;

// Entity index for fast lookup
const ENT_BY_ID = {};
ENTITIES.forEach(e => ENT_BY_ID[e.id] = e);

// Connection adjacency (both directions)
const ADJ = {};
CONNECTIONS.forEach(c => {
  (ADJ[c.from] = ADJ[c.from] || []).push({dir: 'out', ...c});
  (ADJ[c.to] = ADJ[c.to] || []).push({dir: 'in', ...c});
});

// ═══════════════════════════════════════════════════════════════════════════
// FILTER STATE
// ═══════════════════════════════════════════════════════════════════════════
const FILTER = { tier: '', jur: '', sector: '', legal: '', acc: '', search: '' };

function populateFilter(id, values) {
  const el = document.getElementById(id);
  const sorted = [...values].sort();
  sorted.forEach(v => {
    if (!v) return;
    const o = document.createElement('option');
    o.value = v; o.textContent = v;
    el.appendChild(o);
  });
}

populateFilter('f-tier',   Object.keys(STATS.tier_counts));
populateFilter('f-jur',    Object.keys(STATS.jur_counts));
populateFilter('f-sector', Object.keys(STATS.sector_counts));
populateFilter('f-legal',  Object.keys(STATS.legal_counts));
populateFilter('f-acc',    Object.keys(STATS.acc_counts));

['tier','jur','sector','legal','acc'].forEach(k => {
  document.getElementById('f-'+k).addEventListener('change', e => {
    FILTER[k] = e.target.value;
    applyFilters();
  });
});
document.getElementById('f-search').addEventListener('input', e => {
  FILTER.search = e.target.value.toLowerCase();
  applyFilters();
});
document.getElementById('filter-clear').addEventListener('click', () => {
  Object.keys(FILTER).forEach(k => FILTER[k] = '');
  document.querySelectorAll('#filters select').forEach(s => s.value = '');
  document.getElementById('f-search').value = '';
  applyFilters();
});

function entityMatchesFilter(e) {
  if (FILTER.tier   && e.tier !== FILTER.tier) return false;
  if (FILTER.jur    && e.jurisdiction !== FILTER.jur) return false;
  if (FILTER.sector && e.sector !== FILTER.sector) return false;
  if (FILTER.legal  && e.legal_class !== FILTER.legal) return false;
  if (FILTER.acc    && e.accountability !== FILTER.acc) return false;
  if (FILTER.search) {
    const s = FILTER.search;
    if (!(e.id || '').toLowerCase().includes(s) &&
        !(e.label || '').toLowerCase().includes(s) &&
        !(e.full_name || '').toLowerCase().includes(s)) return false;
  }
  return true;
}

function filteredEntities() {
  return ENTITIES.filter(entityMatchesFilter);
}

function applyFilters() {
  const vis = filteredEntities();
  document.getElementById('filter-count').innerHTML = '<b>' + vis.length + '</b> visible';
  if (CURRENT_VIEW === 'graph')    renderGraph();
  if (CURRENT_VIEW === 'map')      renderMap();
  if (CURRENT_VIEW === 'circle')   renderCircle();
  if (CURRENT_VIEW === 'registry') renderRegistry();
  if (CURRENT_VIEW === 'stats')    renderStats();
}

// ═══════════════════════════════════════════════════════════════════════════
// VIEW SWITCHING
// ═══════════════════════════════════════════════════════════════════════════
let CURRENT_VIEW = 'graph';

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const v = tab.dataset.view;
    CURRENT_VIEW = v;
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === tab));
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.getElementById('view-' + v).classList.add('active');
    if (v === 'graph')    renderGraph();
    if (v === 'map')      renderMap();
    if (v === 'circle')   renderCircle();
    if (v === 'registry') renderRegistry();
    if (v === 'stats')    renderStats();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// TOOLTIP
// ═══════════════════════════════════════════════════════════════════════════
const tooltip = document.getElementById('tooltip');
function showTip(html, ev) {
  tooltip.innerHTML = html;
  tooltip.classList.add('show');
  tooltip.style.left = (ev.clientX + 12) + 'px';
  tooltip.style.top  = (ev.clientY + 12) + 'px';
}
function hideTip() { tooltip.classList.remove('show'); }

function entTip(e) {
  return '<b>' + (e.label || e.id) + '</b>' +
    '<div>' + (e.full_name || '') + '</div>' +
    '<div class="meta">' + (e.tier || '') + ' · ' + (e.jurisdiction || '') +
    ' · ' + (e.legal_class || '') + '</div>' +
    (e.sector ? '<div class="meta">' + e.sector + '</div>' : '');
}

// ═══════════════════════════════════════════════════════════════════════════
// DETAIL PANEL
// ═══════════════════════════════════════════════════════════════════════════
const detail = document.getElementById('detail');
const detailBody = document.getElementById('detail-body');
document.getElementById('detail-close').addEventListener('click', () => detail.classList.remove('open'));

function fmtBudget(v) {
  if (!v && v !== 0) return '—';
  // budget_000s is in thousands. Output as AUD billions/millions.
  const dollars = v * 1000;
  if (dollars >= 1e9) return '$' + (dollars / 1e9).toFixed(2) + 'B';
  if (dollars >= 1e6) return '$' + (dollars / 1e6).toFixed(1) + 'M';
  if (dollars >= 1e3) return '$' + (dollars / 1e3).toFixed(0) + 'K';
  return '$' + dollars.toFixed(0);
}

function detailRow(k, v) {
  if (!v && v !== 0) return '';
  return '<div class="detail-row"><div class="k">' + k + '</div><div class="v">' + v + '</div></div>';
}

function openDetail(id) {
  const e = ENT_BY_ID[id];
  if (!e) return;
  const conns = (ADJ[id] || []).map(c => {
    const other = c.dir === 'out' ? c.to : c.from;
    const arrow = c.dir === 'out' ? '→' : '←';
    const oe = ENT_BY_ID[other];
    const oLabel = oe ? (oe.label || other) : other;
    return '<div class="conn-item">' +
      '<div class="typ" style="color:' + (CFG.conn_colours[c.type] || '#888') + '">' + arrow + ' ' + c.type + '</div>' +
      '<div class="to" data-id="' + other + '">' + oLabel + '</div>' +
    '</div>';
  }).join('');

  detailBody.innerHTML =
    '<h2>' + (e.full_name || e.label || e.id) + '</h2>' +
    '<div class="id">' + e.id + '</div>' +
    '<div class="detail-block">' +
      detailRow('Tier',           e.tier) +
      detailRow('Jurisdiction',   e.jurisdiction) +
      detailRow('Legal class',    e.legal_class) +
      detailRow('Accountability', e.accountability) +
      detailRow('Portfolio',      e.portfolio) +
      detailRow('Sector',         e.sector) +
      detailRow('Ring',           e.ring != null ? e.ring + ' — ' + (CFG.ring_labels[e.ring] || '') : null) +
    '</div>' +
    '<div class="detail-block">' +
      detailRow('Budget',         fmtBudget(e.budget_000s) + (e.financial_year ? ' (' + e.financial_year + ')' : '')) +
      detailRow('Budget type',    e.budget_type) +
      detailRow('Legislation',    e.legislation) +
      detailRow('Established',    e.established) +
      detailRow('Geographic',     e.geographic_scope) +
      detailRow('LGA code',       e.lga_code) +
      detailRow('Data quality',   e.data_quality) +
      detailRow('Data source',    e.data_source) +
    '</div>' +
    (conns ? '<h3>Connections (' + (ADJ[id] || []).length + ')</h3><div class="conn-list">' + conns + '</div>' : '');

  // Wire connection click-throughs
  detailBody.querySelectorAll('.to[data-id]').forEach(el => {
    el.addEventListener('click', () => openDetail(el.dataset.id));
  });
  detail.classList.add('open');
}

// ═══════════════════════════════════════════════════════════════════════════
// GRAPH VIEW — ring-based force layout
// ═══════════════════════════════════════════════════════════════════════════
let GRAPH_SIM = null, GRAPH_Z = null;

function renderGraph() {
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();

  const W = svg.node().clientWidth;
  const H = svg.node().clientHeight;
  const cx = W / 2, cy = H / 2;
  const R = Math.min(W, H) * 0.45;

  // Root group for zoom/pan
  const root = svg.append('g');

  GRAPH_Z = d3.zoom()
    .scaleExtent([0.15, 8])
    .on('zoom', ev => root.attr('transform', ev.transform));
  svg.call(GRAPH_Z);

  // Ring positions — ring -1 innermost, 99 outermost
  const rings = CFG.ring_order;
  const ringRadius = {};
  rings.forEach((r, i) => {
    ringRadius[r] = (i + 1) / rings.length * R;
  });

  // Ring guide circles + labels
  rings.forEach(r => {
    root.append('circle')
      .attr('class', 'ring-guide')
      .attr('cx', cx).attr('cy', cy)
      .attr('r', ringRadius[r]);
    root.append('text')
      .attr('class', 'ring-label')
      .attr('x', cx).attr('y', cy - ringRadius[r] - 4)
      .text(CFG.ring_labels[r] || ('ring ' + r));
  });

  // Build filtered node/link sets
  const nodes = filteredEntities().map(e => ({
    id: e.id, e: e,
    ring: e.ring != null ? e.ring : 14,
  }));
  const nodeIds = new Set(nodes.map(n => n.id));
  const links = CONNECTIONS
    .filter(c => nodeIds.has(c.from) && nodeIds.has(c.to))
    .map(c => ({source: c.from, target: c.to, type: c.type}));

  // Simulation: radial force by ring, weak charge, small link
  if (GRAPH_SIM) GRAPH_SIM.stop();
  GRAPH_SIM = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-12))
    .force('collide', d3.forceCollide().radius(4))
    .force('r', d3.forceRadial(d => ringRadius[d.ring] || R * 0.9, cx, cy).strength(1.2))
    .force('link', d3.forceLink(links).id(d => d.id).distance(25).strength(0.05))
    .alpha(0.6).alphaDecay(0.04);

  // Links
  const linkSel = root.append('g').selectAll('line')
    .data(links).enter().append('line')
    .attr('class', 'link')
    .attr('stroke', d => CFG.conn_colours[d.type] || '#888')
    .attr('stroke-width', 0.8);

  // Nodes
  const nodeSel = root.append('g').selectAll('g.node')
    .data(nodes).enter().append('g')
    .attr('class', 'node');

  nodeSel.append('circle')
    .attr('r', d => {
      const b = d.e.budget_000s;
      if (!b) return 3;
      return Math.min(10, 3 + Math.log10(b) * 0.6);
    })
    .attr('fill', d => CFG.tier_colours[d.e.tier] || '#888')
    .on('mouseover', (ev, d) => showTip(entTip(d.e), ev))
    .on('mousemove', ev => showTip(tooltip.innerHTML, ev))
    .on('mouseout', hideTip)
    .on('click', (ev, d) => { ev.stopPropagation(); openDetail(d.id); });

  // Labels only for large-budget entities (keeps graph readable)
  nodeSel.filter(d => d.e.budget_000s && d.e.budget_000s > 1e6)
    .append('text')
    .attr('dy', -8)
    .text(d => d.e.label);

  GRAPH_SIM.on('tick', () => {
    linkSel
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    nodeSel.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// MAP VIEW — Leaflet
// ═══════════════════════════════════════════════════════════════════════════
let MAP = null, MAP_LAYER = null;

function renderMap() {
  if (!MAP) {
    MAP = L.map('map', {
      center: [-25.5, 134], zoom: 4, minZoom: 3, maxZoom: 14,
      preferCanvas: true,
    });
    // Dark Carto tiles — free, OSM-based
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      subdomains: 'abcd', maxZoom: 19,
    }).addTo(MAP);
  }
  if (MAP_LAYER) MAP.removeLayer(MAP_LAYER);

  MAP_LAYER = L.layerGroup();
  filteredEntities().forEach(e => {
    if (e.lat == null || e.lon == null) return;
    const col = CFG.tier_colours[e.tier] || '#888';
    const r = e.budget_000s
      ? Math.min(14, 3 + Math.log10(e.budget_000s) * 0.9)
      : 4;
    const m = L.circleMarker([e.lat, e.lon], {
      radius: r,
      fillColor: col, color: '#0a0e1a', weight: 1,
      opacity: 1, fillOpacity: 0.75,
    });
    m.bindPopup(
      '<strong>' + (e.label || e.id) + '</strong><br>' +
      (e.full_name || '') + '<br>' +
      '<em>' + (e.tier || '') + ' · ' + (e.jurisdiction || '') + '</em><br>' +
      (e.sector || '') + '<br>' +
      '<small>' + e.id + '</small>'
    );
    m.on('click', () => openDetail(e.id));
    MAP_LAYER.addLayer(m);
  });
  MAP_LAYER.addTo(MAP);
  setTimeout(() => MAP.invalidateSize(), 50);
}

// ═══════════════════════════════════════════════════════════════════════════
// CIRCLE VIEW — concentric rings, entities as dots on arcs
// ═══════════════════════════════════════════════════════════════════════════
function renderCircle() {
  const svg = d3.select('#circle-svg');
  svg.selectAll('*').remove();
  const W = svg.node().clientWidth;
  const H = svg.node().clientHeight;
  const cx = W / 2, cy = H / 2;
  const R = Math.min(W, H) * 0.42;

  const root = svg.append('g');
  const z = d3.zoom().scaleExtent([0.3, 8]).on('zoom', ev => root.attr('transform', ev.transform));
  svg.call(z);

  const rings = CFG.ring_order;
  const entsByRing = {};
  rings.forEach(r => entsByRing[r] = []);
  filteredEntities().forEach(e => {
    const r = e.ring != null ? e.ring : 14;
    (entsByRing[r] = entsByRing[r] || []).push(e);
  });

  rings.forEach((r, i) => {
    const rad = (i + 1) / rings.length * R;
    const ents = entsByRing[r] || [];
    // Ring guide
    root.append('circle')
      .attr('class', 'ring-guide')
      .attr('cx', cx).attr('cy', cy).attr('r', rad);
    // Ring label — position on right side
    root.append('text')
      .attr('class', 'ring-label')
      .attr('x', cx + rad + 6).attr('y', cy + 3)
      .attr('text-anchor', 'start')
      .text((CFG.ring_labels[r] || ('ring ' + r)) + ' (' + ents.length + ')');
    // Entities distributed around ring
    ents.forEach((e, j) => {
      const theta = (j / Math.max(ents.length, 1)) * 2 * Math.PI - Math.PI / 2;
      const x = cx + rad * Math.cos(theta);
      const y = cy + rad * Math.sin(theta);
      const col = CFG.tier_colours[e.tier] || '#888';
      const g = root.append('g').attr('class', 'node');
      g.append('circle')
        .attr('cx', x).attr('cy', y)
        .attr('r', e.budget_000s ? Math.min(8, 2.5 + Math.log10(e.budget_000s) * 0.45) : 2.5)
        .attr('fill', col)
        .attr('stroke', '#0a0e1a').attr('stroke-width', 0.5)
        .on('mouseover', ev => showTip(entTip(e), ev))
        .on('mousemove', ev => showTip(tooltip.innerHTML, ev))
        .on('mouseout', hideTip)
        .on('click', ev => { ev.stopPropagation(); openDetail(e.id); });
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// REGISTRY VIEW
// ═══════════════════════════════════════════════════════════════════════════
let REG_SORT = { field: 'label', dir: 1 };

function renderRegistry() {
  const vis = filteredEntities();
  const sorted = vis.slice().sort((a, b) => {
    const va = a[REG_SORT.field], vb = b[REG_SORT.field];
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * REG_SORT.dir;
    return String(va).localeCompare(String(vb)) * REG_SORT.dir;
  });

  const cols = [
    { k: 'id',             lbl: 'ID',           cls: 'id' },
    { k: 'label',          lbl: 'Label' },
    { k: 'full_name',      lbl: 'Full Name' },
    { k: 'tier',           lbl: 'Tier',         fmt: tierTag },
    { k: 'jurisdiction',   lbl: 'Jur' },
    { k: 'legal_class',    lbl: 'Legal Class' },
    { k: 'sector',         lbl: 'Sector' },
    { k: 'accountability', lbl: 'Accountability' },
    { k: 'budget_000s',    lbl: 'Budget',       fmt: fmtBudget, cls: 'budget' },
    { k: 'data_quality',   lbl: 'DQ',           fmt: dqTag },
  ];

  const ind = (k) => REG_SORT.field === k ? (REG_SORT.dir === 1 ? '▲' : '▼') : '';

  let html = '<table><thead><tr>';
  cols.forEach(c => {
    html += '<th data-k="' + c.k + '">' + c.lbl + ' <span class="sort-ind">' + ind(c.k) + '</span></th>';
  });
  html += '</tr></thead><tbody>';

  // Only render first 500 rows for performance; rest accessible via filters
  const CAP = 500;
  const shown = sorted.slice(0, CAP);
  shown.forEach(e => {
    html += '<tr data-id="' + e.id + '">';
    cols.forEach(c => {
      const raw = e[c.k];
      const v = c.fmt ? c.fmt(raw) : (raw != null ? raw : '');
      html += '<td class="' + (c.cls || '') + '">' + v + '</td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  if (sorted.length > CAP) {
    html += '<div style="padding:18px;text-align:center;color:var(--text-mute);font-family:\'IBM Plex Mono\',monospace;font-size:11px">' +
      'Showing first ' + CAP + ' of ' + sorted.length + ' matches. Narrow filters to see the rest.</div>';
  }

  const wrap = document.getElementById('registry-wrap');
  wrap.innerHTML = html;

  wrap.querySelectorAll('th').forEach(th => {
    th.addEventListener('click', () => {
      const k = th.dataset.k;
      if (REG_SORT.field === k) REG_SORT.dir *= -1;
      else { REG_SORT.field = k; REG_SORT.dir = 1; }
      renderRegistry();
    });
  });
  wrap.querySelectorAll('tr[data-id]').forEach(tr => {
    tr.addEventListener('click', () => openDetail(tr.dataset.id));
  });
}

function tierTag(t) {
  if (!t) return '';
  return '<span class="tier-tag" style="background:' + (CFG.tier_colours[t] || '#888') + '22;color:' + (CFG.tier_colours[t] || '#888') + '">' + t + '</span>';
}
function dqTag(d) {
  if (!d) return '';
  const c = d === 'HIGH' ? 'var(--green)' : 'var(--accent)';
  return '<span class="dq-tag" style="background:' + c + '22;color:' + c + '">' + d + '</span>';
}

// ═══════════════════════════════════════════════════════════════════════════
// STATS VIEW
// ═══════════════════════════════════════════════════════════════════════════
function renderStats() {
  const vis = filteredEntities();
  const visIds = new Set(vis.map(e => e.id));
  const visConn = CONNECTIONS.filter(c => visIds.has(c.from) && visIds.has(c.to));

  // Recompute counts from filtered set
  const tierC = count(vis, 'tier');
  const jurC  = count(vis, 'jurisdiction');
  const secC  = count(vis, 'sector');
  const legC  = count(vis, 'legal_class');
  const accC  = count(vis, 'accountability');
  const connC = count(visConn, 'type');
  const dqC   = count(vis, 'data_quality');

  let totBudget = 0, nBudget = 0;
  vis.forEach(e => { if (e.budget_000s) { totBudget += e.budget_000s; nBudget++; } });

  const html =
    '<div class="stats-grid">' +
      statCard(vis.length.toLocaleString(), 'Entities', nBudget + ' with budget data') +
      statCard(visConn.length.toLocaleString(), 'Connections', Object.keys(connC).length + ' types') +
      statCard(fmtBudget(totBudget), 'Total budget', 'Across ' + nBudget + ' entities') +
      statCard(Object.keys(jurC).length, 'Jurisdictions', 'Tiers: ' + Object.keys(tierC).length) +
    '</div>' +
    chartSection('By tier', tierC, CFG.tier_colours) +
    chartSection('By jurisdiction', jurC, null) +
    chartSection('By sector', secC, CFG.sector_colours) +
    chartSection('By legal class', legC, null) +
    chartSection('By accountability', accC, null) +
    chartSection('Connection types', connC, CFG.conn_colours) +
    chartSection('Data quality', dqC, {HIGH: 'var(--green)', MEDIUM: 'var(--accent)'});

  document.getElementById('stats-wrap').innerHTML = html;
}

function count(arr, fld) {
  const c = {};
  arr.forEach(x => { const v = x[fld]; if (v) c[v] = (c[v] || 0) + 1; });
  return c;
}

function statCard(num, lbl, sub) {
  return '<div class="stat-card">' +
    '<div class="num">' + num + '</div>' +
    '<div class="lbl">' + lbl + '</div>' +
    (sub ? '<div class="sub">' + sub + '</div>' : '') +
  '</div>';
}

function chartSection(title, obj, colours) {
  const entries = Object.entries(obj).sort((a, b) => b[1] - a[1]);
  const max = entries.length ? entries[0][1] : 1;
  let rows = '';
  entries.forEach(([k, v]) => {
    const col = colours && colours[k] ? colours[k] : 'var(--blue)';
    const pct = (v / max) * 100;
    rows += '<div class="bar-row">' +
      '<div class="lbl">' + k + '</div>' +
      '<div class="bar"><div class="fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<div class="val">' + v.toLocaleString() + '</div>' +
    '</div>';
  });
  return '<div class="chart-section">' +
    '<h3>' + title + '<span class="sub">' + entries.length + ' values</span></h3>' + rows +
  '</div>';
}

// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════
applyFilters();
window.addEventListener('resize', () => {
  if (CURRENT_VIEW === 'graph')  renderGraph();
  if (CURRENT_VIEW === 'circle') renderCircle();
  if (CURRENT_VIEW === 'map' && MAP) MAP.invalidateSize();
});
// Initial graph render
renderGraph();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def build(entities_path: Path, connections_path: Path, out_path: Path) -> None:
    print(f"Reading {entities_path} …")
    entities = load_entities(entities_path)
    print(f"  {len(entities):,} entities, {len(entities[0].keys())} fields")

    print(f"Reading {connections_path} …")
    connections = load_connections(connections_path)
    print(f"  {len(connections):,} connections, {len(connections[0].keys())} fields")

    # Validate referential integrity
    ent_ids = {e["id"] for e in entities}
    orphans = [c for c in connections if c["from"] not in ent_ids or c["to"] not in ent_ids]
    if orphans:
        print(f"  WARNING: {len(orphans)} connections reference missing entity ids")
        for c in orphans[:3]:
            print(f"    {c['id']}: {c['from']} -> {c['to']}")

    # Compute stats
    stats = compute_stats(entities, connections)

    # Build payload
    payload = {
        "entities":    [slim_entity(e)    for e in entities],
        "connections": [slim_connection(c) for c in connections],
        "stats":       stats,
        "config": {
            "ring_order":      RING_ORDER,
            "ring_labels":     {str(k): v for k, v in RING_LABELS.items()},
            "tier_colours":    TIER_COLOURS,
            "conn_colours":    CONN_COLOURS,
            "sector_colours":  SECTOR_COLOURS,
        },
    }

    # JSON with compact separators; default=str handles any stray non-serialisable
    payload_json = json.dumps(payload, separators=(",", ":"), default=str, ensure_ascii=False)

    html = (HTML_TEMPLATE
            .replace("__PAYLOAD__", payload_json)
            .replace("__N_ENTITIES__", f"{len(entities):,}")
            .replace("__N_CONNECTIONS__", f"{len(connections):,}")
            .replace("__N_WITH_BUDGET__", f"{stats['n_with_budget']:,}"))

    out_path.write_text(html, encoding="utf-8")
    print(f"\nWritten: {out_path}")
    print(f"  Size: {out_path.stat().st_size / 1024:.0f} KB")
    print(f"  Stats: {stats['n_entities']:,} entities · {stats['n_connections']:,} connections · "
          f"{stats['n_with_budget']:,} with budget · "
          f"total ${stats['total_budget_000s'] * 1000 / 1e9:.1f}B")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build mog_atlas.html from canonical CSVs")
    ap.add_argument("--entities",    default="mog_entities.csv",    help="Path to entities CSV")
    ap.add_argument("--connections", default="mog_connections.csv", help="Path to connections CSV")
    ap.add_argument("--out",         default="mog_atlas.html",      help="Output HTML path")
    args = ap.parse_args()

    for p in (args.entities, args.connections):
        if not Path(p).exists():
            print(f"ERROR: {p} not found", file=sys.stderr)
            return 1

    build(Path(args.entities), Path(args.connections), Path(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
