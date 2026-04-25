# Module 10 — Decision Log

**Status:** `ACTIVE` (this module is open from day one and never closes)
**Depends on:** All modules (decision log entries reference the module outputs on which decisions are based)
**Consumed by:** *(terminal — this module is not an input to any other module)*

---

## Purpose

This is an append-only log of every material strategic decision made over the life of the venture. It is the single most important folder in this repository because it is the only mechanism that prevents memory from rewriting history in the decision-maker's favour after the fact.

Human beings systematically remember their predictions as more accurate than they were. When a decision turns out well, they remember that they were confident. When a decision turns out badly, they remember that they had reservations. This is not dishonesty — it is how memory works. The decision log destroys this mechanism by recording the actual state of mind, the actual assumptions, and the actual confidence level at the moment of decision, before the outcome is known.

Ray Dalio built Bridgewater's "error log" on this principle. This is ENIGMA's version of it.

---

## Immutability Rule

**No entry in this log may ever be edited or deleted after it is written.**

New entries may amend, supersede, or contradict prior entries. When they do, they must explicitly reference the prior entry by its Decision ID. The prior entry remains fully visible. The reader can always see the original decision and the subsequent revision side by side.

Enforcement of this rule is structural: each entry is committed to the repository with a timestamp, and the git commit history serves as the tamper-evidence mechanism. Any attempt to alter a prior entry will be visible in the commit history.

---

## Entry Format

Every decision entry must use the following template exactly. No field may be left blank. If a field is unknown, write "UNKNOWN — [reason]". If a field is not applicable, write "N/A — [reason]".

```
---
Decision ID: D-[sequential number, e.g. D-001]
Date: [YYYY-MM-DD]
Time: [HH:MM IST]
Decision-Maker(s): [full names of everyone who made or ratified this decision]
Decision: [one sentence — what was decided, stated as an action, not a consideration]

Context:
[Two to five sentences describing the situation that prompted this decision. What was the problem being solved? What options were available? Why was a decision required now rather than later?]

Assumptions:
[Numbered list of every empirical belief on which this decision rests. Each assumption must be stated as a falsifiable claim, e.g. "Mumbai residential prices in the ₹2–4 crore segment will appreciate at not less than 8% per annum over the next 36 months." Not: "real estate prices will go up."]
1.
2.
3.
[continue as needed]

Module References:
[List every ENIGMA INTEL module whose output informed this decision, with the specific section or finding cited.]

Confidence Level: [HIGH / MEDIUM / LOW]
Confidence Basis: [Why this confidence level? What would move it higher or lower?]

Tripwire Conditions:
[What specific, observable events would indicate that this decision was wrong and should be revisited? Each tripwire must be measurable.]
1.
2.

Tripwire Review Date: [The date by which tripwires will be assessed, even if no tripwire has fired]

Outcome Record: [LEFT BLANK AT ENTRY — to be completed only after the outcome is known]
---
```

---

## What Constitutes a Material Strategic Decision

The following categories of decisions require a log entry. This list is not exhaustive — any decision that, if it turns out to be wrong, would materially affect fund returns, LP relationships, or regulatory standing, requires a log entry.

- Any decision to enter or exit a market segment
- Any decision to hire or terminate a senior employee (Director level and above)
- Any decision to raise or decline to raise a new fund
- Any decision to accept or reject an LP commitment
- Any decision on fund structure, fee terms, or regulatory vehicle
- Any asset acquisition decision (including decisions not to acquire an asset that was in active diligence)
- Any asset disposition decision
- Any decision involving a related party
- Any decision to engage or terminate an external adviser (legal, accounting, placement agent, fund administrator)
- Any decision to respond to (or not respond to) a regulatory inquiry
- Any decision to depart from the ENIGMA compliance wall defined in Module 07

---

## Quarterly Review

On the first working day of each calendar quarter, the founder reviews:

1. Every open tripwire condition across all active decision entries
2. Every decision whose Tripwire Review Date falls in the current quarter
3. The outcome record for any decision where the outcome is now knowable

For each reviewed entry, a new entry is created (not an edit to the original) recording:
- Which prior decision is being reviewed (reference by Decision ID)
- Whether tripwires have fired, are approaching, or remain inactive
- The current assessment of the decision's accuracy
- Any revised assumptions

---

## Seed Entry

The first entry in this log, to be written immediately upon this scaffolding being finalised and reviewed, is the decision to build the ENIGMA CORP platform in the first instance — the founding decision. That entry should document, with the level of specificity this template requires, the actual assumptions on which the founder is betting several years of his working life. If those assumptions cannot be written down in falsifiable form, the founding decision itself has not yet been made rigorously.

---

## This module is wrong if: any entry is found to have been edited, backdated, or deleted after its original commit timestamp, or if the log fails to contain a dated entry corresponding to every material strategic decision made by the founder as defined in the categories above, or if any tripwire condition is not reviewed within 30 days of its designated Tripwire Review Date.
