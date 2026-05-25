"""Regression coverage for Role 2 deterministic matching and artifact behavior."""

import csv
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import BankStatementRow
from app.services.fee_engine import apply_bank_fees
from app.services.fx_service import fetch_fx_rate
from app.services.matcher import match_transactions
from app.services.morpheus_extractor import MorpheusExtractor


DEMO_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "demo"
RESULT_FIELDS = {
    "job_id",
    "status",
    "confidence",
    "invoice",
    "payment",
    "best_match",
    "fx_trace",
    "fee_trace",
    "score_breakdown",
    "explanation",
    "warnings",
}
client = TestClient(app)


def _case_rows(case_name: str):
    with (DEMO_DATA_DIR / "demo_cases.json").open("r", encoding="utf-8") as fixture:
        payload = json.load(fixture)[case_name]
    return [BankStatementRow(**row) for row in payload["bank_rows"]]


def test_fx_uses_dated_local_fallback_trace() -> None:
    trace = fetch_fx_rate("USD", "MYR", "2026-05-20", 100.0)

    assert trace.rate == 4.33
    assert trace.converted_amount == 433.0
    assert trace.source == "local_fallback_fx_rates"
    assert trace.fallback_used is True


@pytest.mark.parametrize(
    ("rule_name", "expected_fee", "expected_credit"),
    [
        ("incoming_wire", 11.50, 421.50),
        ("flat_fee_only", 5.00, 428.00),
        ("no_fee", 0.00, 433.00),
    ],
)
def test_fee_rules_are_deterministic(
    rule_name: str, expected_fee: float, expected_credit: float
) -> None:
    trace = apply_bank_fees(433.0, "MYR", rule_name)

    assert trace.total_fee == expected_fee
    assert trace.expected_credit == expected_credit


@pytest.mark.parametrize(
    ("case_name", "expected_status"),
    [
        ("matched", "matched"),
        ("needs_review", "needs_review"),
        ("unmatched", "unmatched"),
    ],
)
def test_matcher_produces_each_review_status(case_name: str, expected_status: str) -> None:
    extractor = MorpheusExtractor()
    invoice = extractor.extract_invoice()
    payment = extractor.extract_payment_proof()
    fx_trace = fetch_fx_rate(invoice.currency or "USD", "MYR", payment.date or "", invoice.amount or 0.0)
    fee_trace = apply_bank_fees(fx_trace.converted_amount, "MYR")

    result = match_transactions(invoice, payment, _case_rows(case_name), fee_trace)

    assert result.status == expected_status
    if case_name == "matched":
        assert result.confidence >= 0.85
    elif case_name == "needs_review":
        assert 0.65 <= result.confidence < 0.85
    else:
        assert result.confidence < 0.65


def test_demo_defaults_to_matched_shared_contract() -> None:
    demo = client.get("/api/demo")
    reconcile = client.post("/api/reconcile", json={})

    assert demo.status_code == 200
    assert demo.json()["status"] == "matched"
    assert demo.json()["job_id"] == "demo_001"
    assert set(demo.json()) == RESULT_FIELDS
    assert set(reconcile.json()) == RESULT_FIELDS


@pytest.mark.parametrize(
    ("case_name", "status", "job_id"),
    [
        ("matched", "matched", "demo_001"),
        ("needs_review", "needs_review", "demo_needs_review_001"),
        ("unmatched", "unmatched", "demo_unmatched_001"),
    ],
)
def test_named_demo_cases_generate_downloadable_artifacts(
    case_name: str, status: str, job_id: str
) -> None:
    result = client.get("/api/demo", params={"case": case_name})
    report = client.get(f"/api/report/{job_id}")
    export = client.get(f"/api/export/{job_id}")

    assert result.status_code == 200
    assert result.json()["status"] == status
    assert set(result.json()) == RESULT_FIELDS
    assert report.status_code == 200
    assert report.headers["content-type"].startswith("application/pdf")
    assert report.content.startswith(b"%PDF")
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")
    exported_rows = list(csv.DictReader(export.text.splitlines()))
    assert exported_rows[0]["job_id"] == job_id
    assert exported_rows[0]["status"] == status


def test_unknown_demo_case_returns_supported_values() -> None:
    response = client.get("/api/demo", params={"case": "missing"})

    assert response.status_code == 400
    assert "matched, needs_review, unmatched" in response.json()["detail"]
