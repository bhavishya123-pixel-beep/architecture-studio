"""
Infrastructure Watch Agent
───────────────────────────
Monitors NHAI, metro, airport, and freight corridor announcements.
Identifies new projects, status changes, and corridor openings.
Triggers alert events for downstream processing.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from agents.base import BaseAgent, AgentOutput
from api.schemas import (
    InfrastructureRecord, InfraStatus, InfraType,
    Alert, AlertType, AlertSeverity,
)


class InfraWatchAgent(BaseAgent):
    def __init__(self):
        super().__init__("InfraWatchAgent")

    async def run(
        self,
        new_records: list[InfrastructureRecord],
        existing_records: list[InfrastructureRecord],
        lookback_days: int = 7,
    ) -> AgentOutput:
        t0 = time.perf_counter()

        try:
            alerts: list[dict] = []
            changes: list[dict] = []
            evidence_ids: list[UUID] = []

            existing_by_id = {r.project_id_official: r for r in existing_records if r.project_id_official}
            cutoff = datetime.utcnow() - timedelta(days=lookback_days)

            for record in new_records:
                evidence_ids.append(record.id)

                # Detect net-new projects
                if record.project_id_official not in existing_by_id:
                    alert_type, severity = self._classify_new_project(record)
                    alerts.append(
                        Alert(
                            alert_type=alert_type,
                            severity=severity,
                            title=f"New {record.infra_type.value}: {record.name}",
                            body=self._format_new_project_body(record),
                            city=record.city,
                            affected_infra_ids=[record.id],
                            evidence_ids=[record.id],
                            source_ids=[record.source_id],
                        ).model_dump(mode="json")
                    )
                    changes.append({"change_type": "new_project", "record_id": str(record.id)})
                    continue

                # Detect status changes
                prev = existing_by_id[record.project_id_official]
                if record.status != prev.status:
                    self.logger.info(
                        f"Status change: {record.name} "
                        f"{prev.status.value} → {record.status.value}"
                    )
                    alerts.append(
                        Alert(
                            alert_type=AlertType.INFRA_APPROVED
                            if record.status == InfraStatus.APPROVED
                            else AlertType.INFRA_ANNOUNCED,
                            severity=AlertSeverity.HIGH
                            if record.status == InfraStatus.UNDER_CONSTRUCTION
                            else AlertSeverity.MEDIUM,
                            title=f"Status change: {record.name}",
                            body=(
                                f"{record.name} status updated: "
                                f"{prev.status.value} → {record.status.value}. "
                                f"State: {record.state}. "
                                f"Source: {record.source_id}."
                            ),
                            city=record.city,
                            affected_infra_ids=[record.id],
                            evidence_ids=[record.id],
                            source_ids=[record.source_id],
                        ).model_dump(mode="json")
                    )
                    changes.append({
                        "change_type": "status_change",
                        "record_id": str(record.id),
                        "prev_status": prev.status.value,
                        "new_status": record.status.value,
                    })

                # Detect completion date slippage
                if (
                    prev.expected_completion_date
                    and record.expected_completion_date
                    and record.expected_completion_date > prev.expected_completion_date
                ):
                    slip_days = (record.expected_completion_date - prev.expected_completion_date).days
                    alerts.append(
                        Alert(
                            alert_type=AlertType.POSSESSION_SLIP,
                            severity=AlertSeverity.MEDIUM,
                            title=f"Completion date slipped: {record.name}",
                            body=f"Expected completion pushed by {slip_days} days.",
                            city=record.city,
                            affected_infra_ids=[record.id],
                            evidence_ids=[record.id],
                            source_ids=[record.source_id],
                        ).model_dump(mode="json")
                    )

            ms = (time.perf_counter() - t0) * 1000
            return self._ok(
                result={
                    "new_records_scanned": len(new_records),
                    "changes_detected": len(changes),
                    "alerts_generated": len(alerts),
                    "alerts": alerts,
                    "changes": changes,
                },
                evidence_ids=evidence_ids,
                sources=list({r.source_id for r in new_records}),
                confidence=0.85,
                processing_ms=ms,
            )

        except Exception as e:
            return self._fail(str(e))

    def _classify_new_project(self, r: InfrastructureRecord) -> tuple[AlertType, AlertSeverity]:
        if r.status == InfraStatus.UNDER_CONSTRUCTION:
            return AlertType.INFRA_APPROVED, AlertSeverity.HIGH
        elif r.status in (InfraStatus.APPROVED, InfraStatus.TENDERED):
            return AlertType.INFRA_APPROVED, AlertSeverity.MEDIUM
        else:
            return AlertType.INFRA_ANNOUNCED, AlertSeverity.LOW

    def _format_new_project_body(self, r: InfrastructureRecord) -> str:
        parts = [
            f"New {r.infra_type.value} project detected: {r.name}.",
            f"State: {r.state}.",
            f"Status: {r.status.value}.",
        ]
        if r.length_km:
            parts.append(f"Length: {r.length_km:.1f} km.")
        if r.cost_crore:
            parts.append(f"Cost: ₹{r.cost_crore:,.0f} Cr.")
        if r.expected_completion_date:
            parts.append(f"Expected completion: {r.expected_completion_date}.")
        parts.append(f"Source: {r.source_id} (confidence: {r.confidence:.2f}).")
        return " ".join(parts)
