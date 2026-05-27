"""CSV audit log exports for downstream bookkeeping review."""

import csv
from pathlib import Path
from typing import Optional

from app.models.schemas import ReconciliationResult


EXPORT_DIR = Path(__file__).resolve().parents[3] / "data" / "outputs" / "exports"


def export_audit_log(result: ReconciliationResult, output_dir: Optional[Path] = None) -> Path:
    target_dir = output_dir or EXPORT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{result.job_id}_audit_log.csv"
    row = result.best_match
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "job_id",
                "status",
                "confidence",
                "invoice_number",
                "invoice_amount",
                "invoice_currency",
                "fx_rate",
                "fee_total",
                "expected_credit",
                "bank_row_id",
                "actual_credit",
                "explanation",
                "action_pack_category",
                "recommended_next_action",
                "missing_evidence_checklist",
            ]
        )
        writer.writerow(
            [
                result.job_id,
                result.status,
                result.confidence,
                result.invoice.invoice_number,
                result.invoice.amount,
                result.invoice.currency,
                result.fx_trace.rate,
                result.fee_trace.total_fee,
                result.fee_trace.expected_credit,
                row.row_id if row else "",
                row.credit_amount if row else "",
                result.explanation,
                result.action_pack.category if result.action_pack else "",
                result.action_pack.recommended_next_action if result.action_pack else "",
                " | ".join(result.action_pack.missing_evidence_checklist)
                if result.action_pack
                else "",
            ]
        )
    return path
