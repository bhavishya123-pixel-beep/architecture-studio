# India Real Estate Intelligence OS — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     INDIA REAL ESTATE INTELLIGENCE OS                        │
│                       (Production-Grade AI Agent System)                     │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  INGESTION LAYER                                                              ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  ║
║  │ NHAI/MoRTH   │ │ RERA Portals │ │ RBI / MOSPI  │ │ News + Listings  │  ║
║  │ Connectors   │ │ Scrapers     │ │ API Clients  │ │ Enrichment Feed  │  ║
║  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘  ║
║         │                │                │                   │             ║
║  ┌──────▼───────────────▼────────────────▼───────────────────▼──────────┐ ║
║  │              PDF Parser + Change Detector + Deduplicator              │ ║
║  └──────────────────────────────────────┬──────────────────────────────-─┘ ║
╚═══════════════════════════════════════════╪════════════════════════════════╝
                                            │
╔═══════════════════════════════════════════▼════════════════════════════════╗
║  DATA LAKE                                                                   ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ ║
║  │  RAW ZONE   │  │CLEANED ZONE │  │ANALYTICS    │  │ VECTOR STORE     │ ║
║  │ (immutable  │─▶│(normalized  │─▶│ZONE         │  │ (FAISS/Chroma)   │ ║
║  │  snapshots) │  │ schemas)    │  │(scores,     │  │ Semantic search  │ ║
║  └─────────────┘  └─────────────┘  │ features)   │  │ across docs      │ ║
║                                     └─────────────┘  └──────────────────┘ ║
║  ┌───────────────────────────────────────────────────────────────────────┐ ║
║  │         PostgreSQL + PostGIS | DuckDB (fast analytics)                │ ║
║  └───────────────────────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════════════╝
                                            │
╔═══════════════════════════════════════════▼════════════════════════════════╗
║  SCORING ENGINE                                                               ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  ║
║  │Infrastructure│ │ Connectivity │ │ Affordability│ │   Rental Yield   │  ║
║  │ Uplift Score │ │    Score     │ │    Score     │ │     Score        │  ║
║  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘  ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  ║
║  │  Liquidity   │ │  Regulatory  │ │  Developer   │ │  Execution Risk  │  ║
║  │    Score     │ │ Safety Score │ │ Trust Score  │ │     Score        │  ║
║  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘  ║
║  ┌──────────────┐ ┌───────────────────────────────────────────────────────┐ ║
║  │ Appreciation │ │         FINAL INVESTMENT ATTRACTIVENESS SCORE         │ ║
║  │ Potential    │ │  (weighted composite, deterministic, evidence-cited)   │ ║
║  └──────────────┘ └───────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════════════╝
                                            │
╔═══════════════════════════════════════════▼════════════════════════════════╗
║  AI AGENT LAYER  (LLM for synthesis only, code for all calculations)         ║
║                                                                               ║
║  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐   ║
║  │ Market   │ │Infrastructure│ │  RERA   │ │  Macro  │ │  Valuation   │   ║
║  │ Data     │ │  Watch     │ │Compliance│ │ Signal  │ │    Agent     │   ║
║  │ Agent    │ │  Agent     │ │  Agent   │ │  Agent  │ │              │   ║
║  └────┬─────┘ └─────┬──────┘ └────┬─────┘ └────┬────┘ └──────┬───────┘   ║
║       │             │              │             │             │            ║
║  ┌────▼─────┐ ┌─────▼──────┐ ┌────▼─────────────▼─────────────▼───────┐  ║
║  │  Risk    │ │Neighborhood│ │           ORCHESTRATOR AGENT             │  ║
║  │  Agent   │ │  Research  │ │   (coordinates, resolves conflicts,      │  ║
║  └──────────┘ │   Agent    │ │    produces final memos + alerts)        │  ║
║               └────────────┘ └──────────────────────────────────────────┘  ║
║  ┌──────────┐ ┌────────────┐                                                ║
║  │Portfolio │ │  Alerting  │                                                ║
║  │Allocation│ │   Agent    │                                                ║
║  └──────────┘ └────────────┘                                                ║
╚════════════════════════════════════════════════════════════════════════════╝
                                            │
╔═══════════════════════════════════════════▼════════════════════════════════╗
║  API LAYER (FastAPI)                                                          ║
║  /api/v1/markets  /api/v1/corridors  /api/v1/projects  /api/v1/alerts       ║
║  /api/v1/scores   /api/v1/memos      /api/v1/watchlist  /api/v1/map         ║
╚════════════════════════════════════════════════════════════════════════════╝
                                            │
╔═══════════════════════════════════════════▼════════════════════════════════╗
║  DASHBOARD (Streamlit)                                                        ║
║  City Dashboard | Corridor View | Project Due-Diligence | Map View          ║
║  Alert Feed     | Watchlist     | Comparison View       | Memo Generator    ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Data Flow

```
Official Sources
     │
     ▼
Ingestion (scheduled, idempotent, source-tagged)
     │
     ▼
Raw Zone (immutable, timestamped, provenance-stored)
     │
     ▼
ETL / Normalization (unified schema, confidence scored)
     │
     ▼
Cleaned Zone (deduplicated, validated, freshness-scored)
     │
     ▼
Analytics Zone (scores, features, geo-enriched)
     │
     ▼
Agent Layer (specialist agents → orchestrator → output)
     │
     ▼
API + Dashboard + Alerts
```

## Geo-Influence Zone Model

```
Project/Location Point
    │
    ├── 0–3 km    →  Direct Influence Zone     (highest uplift weight)
    ├── 3–7 km    →  Secondary Influence Zone  (moderate uplift weight)
    ├── 7–15 km   →  Corridor Spill Zone       (low-moderate uplift weight)
    └── Metro/Airport special cases:
         ├── Metro: 0–1 km walkable = 1.5× multiplier
         └── Airport: 0–10 km logistics zone = 1.2× multiplier
```

## Agent Responsibility Matrix

| Agent              | Input Sources         | Output                    | LLM Used? |
|--------------------|-----------------------|---------------------------|-----------|
| MarketDataAgent    | Price/rent feeds      | Market snapshot JSON      | Summary   |
| InfraWatchAgent    | NHAI, Metro, Airport  | Infra event JSON          | Summary   |
| RERAAgent          | RERA portals          | Compliance report JSON    | Summary   |
| MacroAgent         | RBI, MOSPI, Budget    | Macro signal JSON         | Summary   |
| ValuationAgent     | Price+infra+macro     | Valuation model JSON      | No        |
| RiskAgent          | RERA+legal+developer  | Risk score JSON           | Summary   |
| NeighborhoodAgent  | Geo+POI data          | Neighborhood profile JSON | Summary   |
| PortfolioAgent     | All scores            | Allocation recommendation | Summary   |
| AlertingAgent      | All change events     | Alert payloads            | No        |
| OrchestratorAgent  | All agent outputs     | Investment memo           | Yes       |

## Key Design Decisions

1. **LLM boundary**: LLM is used ONLY for summarization, narrative, and document
   parsing. All scores are computed deterministically in Python.

2. **Source hierarchy**: Official govt sources > verified listing feeds > news.
   Every record stores `source_tier` (1=official, 2=listing, 3=news).

3. **Confidence decay**: Scores decay over time. A 90-day-old price observation
   scores at 70% confidence. Controlled via `freshness_score`.

4. **No hallucination guard**: If data is missing, scores return `None` with
   `data_gap=True` flag. The system never fills gaps with invented values.

5. **Evidence chain**: Every recommendation links to `evidence_ids[]`, which
   map to records in the cleaned zone with full provenance.
