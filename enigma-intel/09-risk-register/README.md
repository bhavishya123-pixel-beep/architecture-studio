# Module 09 — Risk Register

**Status:** `SCAFFOLDED`
**Depends on:** All of Modules 01–08 (the risk register is only complete once all upstream analysis is finalised)
**Consumed by:** Module 10 (decision log references risk register entries when decisions are made)

---

## Research Question

What are all plausible ways this venture fails, and for each failure mode: how likely is it, how bad is it, what would we see before it happened, and what have we committed to doing if we see it?

The risk register is not a compliance document. It is a decision-support document. The difference is that a compliance document lists risks to satisfy an auditor. A decision-support document lists risks to change behaviour before those risks materialise. Every entry in this register must pass the test: "does knowing this risk and its leading indicator change what ENIGMA does today?"

---

## Risk Categories and Mandatory Entries

For each risk below, the research must produce a structured entry with the following fields:

```
Risk ID: [R-XX]
Category: [category name]
Description: [one paragraph — what happens, not just what the risk is called]
Probability: [LOW / MEDIUM / HIGH] with brief quantitative basis where available
Impact: [MINOR / SIGNIFICANT / EXISTENTIAL] with INR crore estimate of fund NAV at risk
Leading Indicator: [the specific, observable, measurable signal that this risk is beginning to materialise]
Monitoring Frequency: [how often the leading indicator is checked and by whom]
Pre-committed Mitigation: [the specific action ENIGMA commits to taking when the leading indicator fires — not a vague intention but an operational action]
Tripwire: [the specific threshold at which the mitigation action becomes mandatory rather than optional]
```

---

**Category 1: Regulatory Reversal**

- R-01: FEMA / FDI policy restricts or prohibits FDI into real estate development, reversing the current permissive framework
- R-02: SEBI AIF regulations are amended to restrict Category II AIF investment in under-construction real estate or impose leverage caps that break the fund's return model
- R-03: GIFT City IFSC framework is modified in a way that eliminates the tax or regulatory advantages on which the offshore fund structure depends
- R-04: The India-Singapore tax treaty is renegotiated, eliminating capital gains treaty benefits currently relied upon by the HoldCo structure
- R-05: RERA is amended at the state level (Maharashtra specifically) in a way that increases compliance cost or restricts joint development agreement structures

**Category 2: Capital Cycle Inversion**

- R-06: Indian residential real estate prices in ENIGMA's target markets decline more than 20 percent, making exit realisations on redevelopment assets insufficient to generate the projected MOIC
- R-07: Construction costs inflate at a rate that compresses project-level IRR below the LP hurdle rate — the specific construction cost escalation threshold at which each fund's return model breaks
- R-08: The domestic interest rate cycle inverts — RBI raises rates sharply, increasing ENIGMA's project-level debt cost and compressing exit cap rates simultaneously (the double-squeeze scenario)

**Category 3: Key-Person Concentration**

- R-09: The founder becomes incapacitated, loses regulatory licences, or exits the business — what happens to fund governance, LP relationships, and investment decision-making in each scenario?
- R-10: A critical early employee with irreplaceable relationships or technical skills (Passive House certification expertise, senior living operations, institutional LP relationships) departs

**Category 4: Governance Breakdown**

- R-11: A related-party transaction is entered into that, in retrospect, constitutes a breach of fiduciary duty to LPs — the specific transaction types that carry this risk in real estate fund management
- R-12: A conflict of interest between the founder's personal investments and the fund's investments is not disclosed or managed adequately, triggering LP withdrawal rights or SEBI investigation

**Category 5: Enforcement and Tax Exposure**

- R-13: An Enforcement Directorate investigation is initiated based on a FEMA violation — the specific FEMA provisions that are most commonly the basis for ED investigations in real estate fund structures
- R-14: An Income Tax reassessment challenges the capital gains treatment of carry income, reclassifying it as ordinary income — the tax exposure quantum and the litigation timeline
- R-15: A money-laundering allegation (PMLA) arises from LP KYC that was inadequate — the specific LP category that carries the highest risk of this outcome

**Category 6: Market Structural Risks**

- R-16: Urbanisation rate slows materially below Module 03's projections — the specific Census or PLFS threshold that would trigger a module-03 reassessment
- R-17: The senior living taboo fails to erode on the timeline assumed — occupancy rates at Enigma Living's first project are below the underwritten assumptions
- R-18: A competing platform (domestic or international) enters ENIGMA's target segments with superior capital and operational infrastructure before ENIGMA achieves scale

**Category 7: Exit Market Illiquidity**

- R-19: The REIT listing market closes — SEBI imposes a moratorium or no new REITs are approved, eliminating the primary institutional exit route at Fund III scale
- R-20: The strategic buyer universe for Indian real estate assets contracts — global funds reduce India exposure due to geopolitical or currency events, eliminating the secondary exit route
- R-21: The AIF secondary market in India remains underdeveloped, eliminating the tertiary exit route and trapping LP capital beyond fund life

---

## Aggregate Risk Exposure

After all individual entries are completed, the research must produce:

1. A heat map plotting all risks by probability and impact
2. The three risks judged to be the highest combined expected-value threats to the venture
3. The correlation matrix for the top-ten risks: which risks tend to occur together (a capital cycle inversion and exit market illiquidity are not independent — they are correlated)
4. The scenario analysis: what happens to the fund's return model if risks R-06, R-08, and R-19 all materialise simultaneously (the "perfect storm" scenario)

---

## This module is wrong if: a risk materialises that was not enumerated in this register and that causes a loss greater than 15 percent of any fund's NAV, or if any pre-committed mitigation action proves operationally unexecutable within 30 days of the corresponding leading indicator firing, or if the leading indicator for any risk fails to provide at least 90 days of warning before the risk fully materialises.
