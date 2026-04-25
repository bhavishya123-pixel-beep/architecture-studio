# ENIGMA CORP — Intelligence & Strategy Repository

## Purpose

This repository is the single source of analytical truth for ENIGMA CORP's investment and operating platform. It exists to produce decisions, not documents. Every module inside it must answer a specific falsifiable question, cite primary sources or flag claims as speculation, and connect its outputs explicitly to the modules that consume them.

The corporate architecture being analysed is:

```
Singapore HoldCo (ENIGMA CORP)
├── Enigma Certification   — Passive House and EnerPHit retrofit
├── Enigma Realty          — net-zero redevelopment
└── Enigma Living          — senior living
```

The strategic target is approximately ₹120 crore per year of personal net worth accretion to the founder by age 30, generated primarily through carried interest and sponsor unit appreciation.

---

## Source Citation Rule

Every factual claim in a finalised module must either:

1. Cite a named primary source (regulatory text, SEBI filing, fund LP agreement, RBI master direction, government survey, disclosed financial statement), **or**
2. Be explicitly prefixed with `[SPECULATION]` and accompanied by the reasoning chain that produced it.

Claims that are neither cited nor flagged are defective and must be revised before the module can be marked complete.

---

## Module Dependency Graph

The table below shows which modules must be finalised before a downstream module can be finalised. A module may be *drafted* once its upstream modules are finalised, but cannot be *marked complete* until its own review cycle is closed.

| Module | Depends On | Consumed By |
|--------|-----------|-------------|
| 01 — Regulatory Perimeter | *(none — foundational)* | 07, 08, 09 |
| 02 — Blackstone Deconstruction | *(none — foundational)* | 03, 05, 07, 08 |
| 03 — Indian Market Map | 02, 04 | 05, 08, 09 |
| 04 — Consumer & Cultural Substrate | *(none — foundational)* | 03, 09 |
| 05 — Competitor Intelligence | 02, 03 | 06, 07, 08, 09 |
| 06 — Vendor Absorption Playbook | 05 | 09 |
| 07 — Information & Relationship Architecture | 01, 02, 05 | 09 |
| 08 — Capital Formation Roadmap | 01, 02, 03, 05 | 09 |
| 09 — Risk Register | 01–08 | 10 |
| 10 — Decision Log | *(all modules; ongoing)* | *(terminal — consumed by no module)* |

**Recommended completion order** (resolves dependencies with minimum blocking):
`04 → 02 → 01 → 03 → 05 → 06 → 07 → 08 → 09 → 10 (ongoing)`

Note: The prompt author recommends beginning with Module 02 rather than Module 01, because knowing which Blackstone mechanisms you are replicating makes the regulatory constraint-mapping in Module 01 a sharper, more targeted exercise.

---

## Review Protocol

No module transitions from `DRAFT` to `FINAL` until the following steps are complete:

1. **Founder review**: The founder reads the module in full and annotates every substantive claim as one of:
   - `ACCEPTED` — claim is believed to be accurate and is adopted as a working premise
   - `REJECTED` — claim is believed to be inaccurate; reason must be stated
   - `INVESTIGATE FURTHER` — claim is plausible but requires additional evidence before adoption

2. **Written sign-off**: The founder records the review date, the module version, and the aggregate annotation counts in `10-decision-log/` before the module status changes to `FINAL`.

3. **Downstream release**: Only after written sign-off may downstream modules that depend on this module be finalised. Downstream drafts in progress are not invalidated, but must be reconciled with the now-final upstream output before their own sign-off.

4. **Falsification monitoring**: Each module's falsification condition (the final line of every module README) must be reviewed at each quarterly review cycle. If the falsification condition has been triggered, the module reverts to `DRAFT` and must be re-researched.

---

## Module Status Tracker

| Module | Status | Last Reviewed | Signed Off By |
|--------|--------|--------------|--------------|
| 01 — Regulatory Perimeter | `SCAFFOLDED` | — | — |
| 02 — Blackstone Deconstruction | `SCAFFOLDED` | — | — |
| 03 — Indian Market Map | `SCAFFOLDED` | — | — |
| 04 — Consumer & Cultural Substrate | `SCAFFOLDED` | — | — |
| 05 — Competitor Intelligence | `SCAFFOLDED` | — | — |
| 06 — Vendor Absorption Playbook | `SCAFFOLDED` | — | — |
| 07 — Information & Relationship Architecture | `SCAFFOLDED` | — | — |
| 08 — Capital Formation Roadmap | `SCAFFOLDED` | — | — |
| 09 — Risk Register | `SCAFFOLDED` | — | — |
| 10 — Decision Log | `ACTIVE` | — | — |

---

## What This Repository Does Not Contain

This repository contains no actual research, market data, financial models, competitor profiles, or legal opinions until each module is formally commissioned and reviewed. The scaffolding defines the questions. The research answers them.
