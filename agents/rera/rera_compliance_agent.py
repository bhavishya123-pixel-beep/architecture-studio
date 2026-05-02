"""
RERA Compliance Agent
──────────────────────
Analyzes RERA records for a project or developer and produces a structured
compliance report: delays, complaints, risk flags, and regulatory status.
"""

from __future__ import annotations

import time
from typing import Optional
from uuid import UUID

from agents.base import BaseAgent, AgentOutput
from api.schemas import RERARecord, RERAStatus, DeveloperRecord
from etl.validators.schema_validator import validate_rera


class RERAComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__("RERAComplianceAgent")

    async def run(
        self,
        rera_records: list[RERARecord],
        developer: Optional[DeveloperRecord] = None,
    ) -> AgentOutput:
        t0 = time.perf_counter()

        try:
            flagged: list[dict] = []
            clean: list[dict] = []
            evidence_ids = [r.id for r in rera_records]

            for r in rera_records:
                vr = validate_rera(r)
                issues = {
                    "rera_number": r.rera_registration_number,
                    "project": r.project_name,
                    "developer": r.developer_name,
                    "status": r.rera_status.value,
                    "city": r.city,
                    "possession_delay_days": r.possession_delay_days,
                    "complaint_count": r.complaint_count,
                    "active_complaints": r.active_complaints,
                    "validation_passed": vr.passed,
                    "validation_issues": [
                        {"field": i.field, "severity": i.severity, "msg": i.message}
                        for i in vr.issues
                    ],
                    "freshness_score": vr.freshness_score,
                }

                risk_flags = self._derive_risk_flags(r)
                issues["risk_flags"] = risk_flags

                if risk_flags or not vr.passed:
                    flagged.append(issues)
                else:
                    clean.append(issues)

            summary = self._summarize(rera_records)
            ms = (time.perf_counter() - t0) * 1000

            return self._ok(
                result={
                    "total_projects": len(rera_records),
                    "flagged_projects": len(flagged),
                    "clean_projects": len(clean),
                    "flagged": flagged,
                    "clean": clean,
                    "summary": summary,
                },
                evidence_ids=evidence_ids,
                sources=list({r.source_id for r in rera_records}),
                confidence=0.90,
                processing_ms=ms,
            )

        except Exception as e:
            return self._fail(str(e))

    def _derive_risk_flags(self, r: RERARecord) -> list[str]:
        flags = []
        if r.rera_status == RERAStatus.REVOKED:
            flags.append("RERA_REVOKED")
        if r.rera_status == RERAStatus.EXPIRED:
            flags.append("RERA_EXPIRED")
        if r.possession_delay_days and r.possession_delay_days > 365:
            flags.append(f"POSSESSION_DELAY_{r.possession_delay_days}D")
        if r.complaint_count and r.total_units:
            if r.complaint_count / max(r.total_units, 1) > 0.15:
                flags.append("HIGH_COMPLAINT_RATE")
        if r.active_complaints and r.active_complaints > 5:
            flags.append("ACTIVE_COMPLAINTS")
        if r.rera_status == RERAStatus.UNKNOWN:
            flags.append("RERA_STATUS_UNKNOWN")
        return flags

    def _summarize(self, records: list[RERARecord]) -> dict:
        if not records:
            return {}
        delays = [r.possession_delay_days for r in records if r.possession_delay_days]
        revoked = sum(1 for r in records if r.rera_status == RERAStatus.REVOKED)
        registered = sum(1 for r in records if r.rera_status == RERAStatus.REGISTERED)
        return {
            "revoked_count": revoked,
            "registered_count": registered,
            "avg_possession_delay_days": sum(delays) / len(delays) if delays else None,
            "max_delay_days": max(delays) if delays else None,
            "projects_with_delay": len(delays),
        }
