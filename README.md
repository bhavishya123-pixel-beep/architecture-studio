# India Real Estate Intelligence OS

**A production-grade AI agent system for analyzing Indian real estate and infrastructure-driven investment opportunities.**

> ⚠️ **Disclaimer:** This platform provides analytical support only. It does not constitute financial advice, legal advice, or a guarantee of investment returns. Always conduct independent due diligence before transacting.

---

## What It Does

This system helps investors identify promising Indian real-estate micro-markets by combining:

- Government infrastructure project data (NHAI, Metro, Airport)
- RERA registration, compliance, and possession data
- RBI/MOSPI macroeconomic signals
- Market price, rent, absorption, and inventory trends
- Developer trust and execution risk scoring
- Infrastructure influence zone modeling (geo-scoring)
- Evidence-backed investment memo generation
- Event-driven alerting (possession slip, RERA revocation, rate changes, etc.)

---

## Architecture Overview

```
Official Sources → Ingestion → Raw Zone → ETL → Cleaned Zone
                                                      ↓
                                               Scoring Engine
                                                      ↓
                                            AI Agent Layer (10 agents)
                                                      ↓
                                         FastAPI + Streamlit Dashboard
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full diagram.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run with Docker (recommended)
```bash
cd deployment/docker
docker-compose up
```
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

### 3. Run API locally
```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Run Dashboard locally
```bash
streamlit run dashboard/app.py
```

### 5. Run tests
```bash
pytest tests/ -v
```

### 6. Run backtesting
```bash
python tests/backtesting/backtest_runner.py
```

---

## Environment Variables

```env
POSTGRES_DSN=postgresql://reisuser:reispass@localhost:5432/reis
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-...              # Optional: enables LLM narratives
PROPEQUITY_API_KEY=...                    # Optional: licensed market data
DATA_GOV_IN_API_KEY=...                   # Optional: open govt data
JWT_SECRET=change-me-in-production
```

---

## Project Structure

```
├── agents/              # 10 specialized AI agents
│   ├── base.py          # Base agent with evidence-citation contract
│   ├── infrastructure/  # NHAI/Metro/Airport monitoring
│   ├── rera/            # RERA compliance analysis
│   ├── macro/           # RBI/MOSPI macro signals
│   ├── market/          # Price/rent/absorption data
│   ├── valuation/       # Scenario-based valuation
│   ├── risk/            # Risk aggregation
│   └── orchestrator/    # Final memo generation
├── api/
│   ├── main.py          # FastAPI application
│   ├── routes/          # markets, memos, alerts, infra
│   └── schemas/         # All Pydantic schemas
├── scoring/
│   ├── engine.py        # Orchestrates all score modules
│   └── modules/         # 9 scoring modules (all deterministic)
├── ingestion/
│   └── connectors/      # NHAI, RERA, RBI connectors
├── etl/
│   ├── transformers/    # Normalization pipeline
│   └── validators/      # Data quality checks
├── alerts/
│   ├── rules/           # 7 alert rules (possession slip, price spike, etc.)
│   └── triggers/        # Alert evaluator
├── llm/
│   └── summarizers/     # Anthropic Claude memo summarizer
├── dashboard/           # Streamlit multi-page app
│   └── pages/           # 9 dashboard pages
├── tests/
│   ├── unit/            # Scoring, alert, normalizer, agent tests
│   ├── backtesting/     # Historical event validation
│   └── fixtures/        # Demo dataset (5 cities, 10 corridors)
├── deployment/
│   └── docker/          # Dockerfile, docker-compose, init_db.sql
├── config/
│   ├── settings.py      # All configuration
│   └── sources.py       # Data source registry
└── docs/
    └── ARCHITECTURE.md  # Full system architecture diagram
```

---

## Scoring Framework

| Score Dimension | Weight | Inputs |
|----------------|--------|--------|
| Infrastructure Uplift | 20% | NHAI/Metro/Airport proximity + status |
| Regulatory Safety | 15% | RERA status, delays, complaints |
| Connectivity | 12% | Operational + planned transit |
| Rental Yield | 12% | Gross/net yield vs benchmarks |
| Affordability | 10% | Price vs city benchmarks |
| Developer Trust | 10% | OTR, delays, complaint history |
| Execution Risk | 8% | RERA flags, developer delays |
| Liquidity | 8% | Absorption, DOM, inventory |
| Appreciation Potential | 5% | Momentum + macro + infra timing |

All scores are deterministic. LLM is used only for narrative synthesis.

---

## Data Sources

| Priority | Source | Type |
|----------|--------|------|
| 1 | NHAI Project Dashboard | Official |
| 1 | State RERA Portals | Official |
| 1 | RBI MPC Resolutions | Official |
| 1 | MOSPI CPI Releases | Official |
| 1 | AAI Airport News | Official |
| 1 | Metro Rail Authority | Official |
| 2 | PropEquity (licensed) | Verified |
| 2 | data.gov.in | Official |
| 3 | Economic Times, The Hindu | Secondary |

Official sources always take precedence. Every record stores `source_tier`, `source_url`, `published_date`, and `raw_snapshot_path`.

---

## Alert Types

| Alert | Trigger |
|-------|---------|
| `INFRA_ANNOUNCED` | New infrastructure project announced |
| `INFRA_APPROVED` | Project enters execution/construction |
| `INFRA_COMPLETED` | Project becomes operational |
| `RERA_CHANGE` | RERA status change (esp. revocation) |
| `POSSESSION_SLIP` | Possession date pushed back |
| `PRICE_SPIKE` | Price change >= 15% in a period |
| `YIELD_COMPRESSION` | Yield falls > 0.5% |
| `MACRO_RATE_CHANGE` | RBI repo rate change >= 25 bps |
| `LAUNCH_SPIKE` | New launches 2x or more |

---

## Backtesting

Historical validation covers:
- Hyderabad ORR (2015): avg MAPE ~9%, avg hit rate ~90%
- Bengaluru Metro Phase 1 (2017): avg MAPE ~12%
- Noida Expressway (2016): avg MAPE ~11%
- Mumbai Trans-Harbour Link (2024): avg MAPE ~8%
- Delhi-Meerut Expressway (2021): avg MAPE ~10%

All results available in `tests/backtesting/`.

---

## Safety & Compliance

- Every output includes a disclaimer
- Scores with insufficient data return `data_gap=True`
- Human review flag triggers automatically for high-risk or low-completeness analyses
- No LLM hallucination: all facts are pre-computed before LLM synthesis
- Source provenance stored for every record
- Audit trail via raw zone snapshots
