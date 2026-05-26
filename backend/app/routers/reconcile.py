"""Shared reconciliation pipeline and POST API route."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    BankStatementRow,
    InvoiceData,
    PaymentProofData,
    ReconcileRequest,
    ReconciliationResult,
)
from app.services.audit_exporter import export_audit_log
from app.services.bank_statement_parser import parse_bank_statement
from app.services.chutes_agent import generate_explanation
from app.services.fee_engine import apply_bank_fees
from app.services.fx_service import fetch_fx_rate
from app.services.matcher import match_transactions
from app.services.morpheus_extractor import MorpheusExtractor
from app.services.report_generator import generate_reconciliation_report
from app.utils.validators import collect_input_warnings


router = APIRouter(prefix="/api/reconcile", tags=["reconciliation"])
DEMO_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "demo"
JOB_STORE: Dict[str, ReconciliationResult] = {}


class ReconciliationInputError(ValueError):
    """Raised when supplied financial inputs cannot be calculated safely."""


def _load_bank_rows() -> List[BankStatementRow]:
    return parse_bank_statement(DEMO_DATA_DIR / "sample_bank_statement.csv")


def _emergency_result(job_id: str) -> ReconciliationResult:
    with (DEMO_DATA_DIR / "demo_results.json").open("r", encoding="utf-8") as fixture:
        payload = json.load(fixture)
    payload["job_id"] = job_id
    payload["warnings"] = payload.get("warnings", []) + [
        "Prebuilt demo result used because a pipeline service was unavailable."
    ]
    return ReconciliationResult(**payload)


def _store_artifacts(result: ReconciliationResult) -> None:
    generate_reconciliation_report(result)
    export_audit_log(result)
    JOB_STORE[result.job_id] = result


def _contains_supplied_data(payload: ReconcileRequest) -> bool:
    return any(
        (payload.invoice is not None, payload.payment is not None, payload.bank_rows is not None)
    )


def run_reconciliation(
    request: Optional[ReconcileRequest] = None,
    job_id: Optional[str] = None,
    allow_emergency_fallback: bool = False,
) -> ReconciliationResult:
    """Execute the deterministic MVP pipeline using caller data or demo fixtures."""

    payload = request or ReconcileRequest()
    resolved_job_id = job_id or payload.job_id or "job_reconcile_001"
    if (
        request is not None
        and payload.job_id
        and not _contains_supplied_data(payload)
        and payload.job_id in JOB_STORE
    ):
        return JOB_STORE[payload.job_id]
    try:
        extractor = MorpheusExtractor()
        invoice: InvoiceData = payload.invoice or extractor.extract_invoice()
        payment: PaymentProofData = payload.payment or extractor.extract_payment_proof()
        bank_rows = payload.bank_rows if payload.bank_rows is not None else _load_bank_rows()
        amount = invoice.amount or 0.0
        transaction_date = payment.date or invoice.date or "2026-05-20"
        fx_trace = fetch_fx_rate(
            invoice.currency or "USD",
            bank_rows[0].currency if bank_rows else "MYR",
            transaction_date,
            amount,
        )
        fee_trace = apply_bank_fees(
            fx_trace.converted_amount, fx_trace.target_currency, payload.fee_rule
        )
        match = match_transactions(invoice, payment, bank_rows, fee_trace)
        result = ReconciliationResult(
            job_id=resolved_job_id,
            status=match.status,
            confidence=match.confidence,
            invoice=invoice,
            payment=payment,
            best_match=match.best_match,
            fx_trace=fx_trace,
            fee_trace=fee_trace,
            score_breakdown={
                "date_score": match.date_score,
                "reference_score": match.reference_score,
                "amount_score": match.amount_score,
                "date_weight": 0.30,
                "reference_weight": 0.30,
                "amount_weight": 0.40,
            },
            explanation=generate_explanation(invoice, match),
            warnings=collect_input_warnings(invoice, payment),
        )
    except Exception as exc:
        if _contains_supplied_data(payload) and not allow_emergency_fallback:
            raise ReconciliationInputError(
                f"Unable to safely reconcile supplied inputs: {exc}"
            ) from exc
        result = _emergency_result(resolved_job_id)
    _store_artifacts(result)
    return result


def find_result(job_id: str) -> Optional[ReconciliationResult]:
    return JOB_STORE.get(job_id)


@router.post("", response_model=ReconciliationResult)
def reconcile(request: Optional[ReconcileRequest] = None) -> ReconciliationResult:
    try:
        return run_reconciliation(request)
    except ReconciliationInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
