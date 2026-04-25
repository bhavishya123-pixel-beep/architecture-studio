# Module 03 — Indian Real-Asset Market Map

**Status:** `SCAFFOLDED`
**Depends on:** Modules 02 (for mechanism-feasibility filter), 04 (for demand-side substrate)
**Consumed by:** Modules 05, 08, 09

---

## Research Question

Which Indian real-asset segments will grow at greater than 15 percent compound annual growth rate over the next seven years, and why — expressed as a specific, enumerated set of assumptions that downstream modules can stress-test independently?

The 15 percent CAGR threshold is not arbitrary: it is the minimum growth rate at which a new entrant can capture market share, build a track record, and generate the carry economics required to support Fund I's LP commitments. Any segment projected below 15 percent CAGR must still be included in the analysis with its actual projected growth rate, so that the white-space map in Module 05 can correctly identify which segments are contested by incumbents with structural advantages.

---

## Segments to Be Analysed

Every segment below must be analysed with the same four-part structure: (1) current size in INR crore with source, (2) seven-year CAGR projection with explicit assumption set, (3) primary growth driver, and (4) primary growth risk.

**Residential Redevelopment**
- Mumbai island city and inner suburbs redevelopment (cluster redevelopment, Section 33/34 FSI framework)
- Delhi-NCR unauthorised colony regularisation and redevelopment
- Bengaluru old BDA layout redevelopment

**Senior Living**
- Independent senior living (age-restricted, not healthcare)
- Assisted living and memory care
- Continuing care retirement communities (CCRC) — absent in India at scale; project when they will exist
- Geography: Mumbai Metropolitan Region, Delhi-NCR, Bengaluru, Pune, Hyderabad separately

**Industrial and Logistics**
- Tier-2 industrial corridors (DMIC, Chennai-Bengaluru corridor, Vizag-Chennai corridor)
- Grade A warehousing and logistics parks
- Cold chain and temperature-controlled warehousing (separate from ambient)

**Emerging Segments**
- Data centres (MW capacity and implied real estate demand)
- Student housing (purpose-built, Grade A)
- Branded co-living (not PG; organised, amenitised, professionally managed)
- Last-mile fulfilment real estate (dark stores, urban micro-warehouses)

---

## Assumption Set Requirement

Every CAGR projection must be accompanied by a numbered assumption set. Example structure (not the actual content — that is for the research phase):

```
Segment: Senior Living — Mumbai Metropolitan Region
Projected 7-year CAGR: [X]%
Assumption set:
  A1. Mumbai MMR population aged 60+ grows from [X] to [Y] by [year] — source: Census 2011 projection / NFHS-5
  A2. Penetration of organised senior living among 60+ cohort reaches [Z]% by [year] — [basis for assumption]
  A3. Average unit realisation grows at [X]% per annum — [basis]
  A4. Supply-side: [N] new projects are developed by [existing players] — [basis]
If A1 is wrong by more than [threshold], the CAGR projection changes to [revised range].
If A2 is wrong by more than [threshold], the CAGR projection changes to [revised range].
```

This structure is mandatory for every segment. It is what makes this module's outputs usable by Module 08 (capital formation) and Module 09 (risk register).

---

## Required Sources

Claims about current market size must cite at minimum one of: CBRE India, Knight Frank India, Anarock, JLL India, ICRA sector reports, CRISIL Research reports.

Claims about demographic drivers must cite at minimum one of: Census 2011 (and 2026 when available), NFHS-5 (National Family Health Survey), Periodic Labour Force Survey (PLFS), RBI Household Finance and Consumption Survey, NSS consumption expenditure surveys.

Claims about policy-driven demand must cite the primary policy instrument (e.g., the PM Awas Yojana targets and actuals, the National Logistics Policy, the Production-Linked Incentive scheme allocations).

---

## What This Module Does Not Do

This module projects market growth. It does not:
- Identify which competitors control which segments (that is Module 05)
- Explain why consumers behave as the projections assume (that is Module 04, which this module depends on)
- Specify how ENIGMA will access these markets (that is Module 08)
- Specify what can go wrong (that is Module 09)

All cross-references to other modules must be explicit: "the demographic assumption underlying A2 is derived from Module 04, Section [X]."

---

## This module is wrong if: any enumerated segment that was projected to exceed 15 percent CAGR fails to reach that growth rate over the seven-year window, or if any primary assumption in any segment's numbered assumption set is contradicted by subsequent primary data published by Census 2026, NFHS-6, or any of the named real estate research firms.
