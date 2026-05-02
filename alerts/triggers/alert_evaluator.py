"""
Alert Evaluator
────────────────
Runs all alert rules against batches of new and existing records.
Returns a list of triggered alerts sorted by severity.
"""

from __future__ import annotations

from api.schemas import Alert, AlertSeverity
from alerts.rules.alert_rules import (
    check_possession_slip,
    check_rera_status_change,
    check_price_spike,
    check_yield_compression,
    check_macro_rate_change,
    check_infra_execution_start,
    check_launch_spike,
)
from api.schemas import RERARecord, MarketPriceRecord, MacroSignalRecord, InfrastructureRecord

SEVERITY_ORDER = {AlertSeverity.HIGH: 0, AlertSeverity.MEDIUM: 1, AlertSeverity.LOW: 2, AlertSeverity.INFO: 3}


class AlertEvaluator:
    def evaluate_rera(
        self,
        current: list[RERARecord],
        previous_map: dict[str, RERARecord],
    ) -> list[Alert]:
        alerts = []
        for r in current:
            prev = previous_map.get(r.rera_registration_number)
            a1 = check_possession_slip(r, prev)
            a2 = check_rera_status_change(r, prev)
            if a1:
                alerts.append(a1)
            if a2:
                alerts.append(a2)
        return alerts

    def evaluate_market(
        self,
        current: list[MarketPriceRecord],
        previous_map: dict[str, MarketPriceRecord],
    ) -> list[Alert]:
        alerts = []
        for r in current:
            key = f"{r.city}:{r.locality}:{r.segment}"
            prev = previous_map.get(key)
            for check in [check_price_spike, check_yield_compression, check_launch_spike]:
                a = check(r, prev)
                if a:
                    alerts.append(a)
        return alerts

    def evaluate_macro(
        self,
        current: list[MacroSignalRecord],
        previous_map: dict[str, MacroSignalRecord],
    ) -> list[Alert]:
        alerts = []
        for r in current:
            prev = previous_map.get(r.signal_type)
            a = check_macro_rate_change(r, prev)
            if a:
                alerts.append(a)
        return alerts

    def evaluate_infra(
        self,
        current: list[InfrastructureRecord],
        previous_map: dict[str, InfrastructureRecord],
    ) -> list[Alert]:
        alerts = []
        for r in current:
            if r.project_id_official:
                prev = previous_map.get(r.project_id_official)
                a = check_infra_execution_start(r, prev)
                if a:
                    alerts.append(a)
        return alerts

    def evaluate_all(
        self,
        current_rera: list[RERARecord] = None,
        current_market: list[MarketPriceRecord] = None,
        current_macro: list[MacroSignalRecord] = None,
        current_infra: list[InfrastructureRecord] = None,
        prev_rera: dict[str, RERARecord] = None,
        prev_market: dict[str, MarketPriceRecord] = None,
        prev_macro: dict[str, MacroSignalRecord] = None,
        prev_infra: dict[str, InfrastructureRecord] = None,
    ) -> list[Alert]:
        all_alerts: list[Alert] = []
        all_alerts += self.evaluate_rera(current_rera or [], prev_rera or {})
        all_alerts += self.evaluate_market(current_market or [], prev_market or {})
        all_alerts += self.evaluate_macro(current_macro or [], prev_macro or {})
        all_alerts += self.evaluate_infra(current_infra or [], prev_infra or {})

        # Sort: HIGH first, then MEDIUM, LOW, INFO
        all_alerts.sort(key=lambda a: SEVERITY_ORDER.get(a.severity, 99))
        return all_alerts
