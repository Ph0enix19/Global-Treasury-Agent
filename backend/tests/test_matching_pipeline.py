"""Regression coverage for Role 2 deterministic matching and artifact behavior."""

import csv
import json
from pathlib import Path

import httpx
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import BankStatementRow
from app.services import fx_service
from app.services.bank_statement_parser import BankStatementParseError, parse_bank_statement
from app.services.fee_engine import apply_bank_fees
from app.services.fx_service import fetch_fx_rate
from app.services.matcher import match_transactions
from app.services.morpheus_extractor import MorpheusExtractor


DEMO_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "demo"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
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


def test_fx_uses_dated_local_fallback_trace(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    trace = fetch_fx_rate("USD", "MYR", "2026-05-20", 100.0)

    assert trace.rate == 4.33
    assert trace.converted_amount == 433.0
    assert trace.source == "local_fallback_fx_rates"
    assert trace.fallback_used is True


def test_fx_uses_live_dated_rate_when_configured(monkeypatch) -> None:
    class LiveResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self):
            return {"date": "2026-05-20", "base": "USD", "quote": "MYR", "rate": 4.35}

    observed = {}

    def fake_get(url, params, timeout):
        observed.update({"url": url, "params": params, "timeout": timeout})
        return LiveResponse()

    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("FX_API_URL", "https://api.frankfurter.dev/v2")
    monkeypatch.setenv("FX_API_TIMEOUT_SECONDS", "2")
    monkeypatch.setattr(fx_service.httpx, "get", fake_get)

    trace = fetch_fx_rate("USD", "MYR", "2026-05-20", 100.0)

    assert trace.rate == 4.35
    assert trace.converted_amount == 435.0
    assert trace.source == "frankfurter_live"
    assert trace.fallback_used is False
    assert observed == {
        "url": "https://api.frankfurter.dev/v2/rate/USD/MYR",
        "params": {"date": "2026-05-20"},
        "timeout": 2.0,
    }


def test_fx_falls_back_when_live_provider_is_unavailable(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise httpx.TimeoutException("provider timeout")

    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setattr(fx_service.httpx, "get", timeout)

    trace = fetch_fx_rate("USD", "MYR", "2026-05-20", 100.0)

    assert trace.rate == 4.33
    assert trace.source == "local_fallback_fx_rates"
    assert trace.fallback_used is True


def test_fx_rejects_unsupported_fallback_pair(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")

    with pytest.raises(ValueError, match="No fallback FX rate"):
        fetch_fx_rate("AUD", "THB", "2026-05-20", 100.0)


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


def test_parser_normalizes_common_csv_bank_export_headers() -> None:
    rows = parse_bank_statement(FIXTURE_DIR / "bank_statement_export.csv")

    assert len(rows) == 2
    assert rows[0].row_id == "uploaded_001"
    assert rows[0].date == "2026-05-20"
    assert rows[0].description == "Incoming wire INV-2026-0412 Pacific Retail"
    assert rows[0].credit_amount == 421.50
    assert rows[0].currency == "MYR"


def test_parser_reads_xlsx_and_rows_work_with_matcher(tmp_path) -> None:
    statement = tmp_path / "statement.xlsx"
    pd.DataFrame(
        [
            {
                "Transaction ID": "bank_live_001",
                "Value Date": "2026-05-20",
                "Details": "Incoming wire INV-2026-0412 Pacific Retail",
                "Amount Received": 421.50,
                "Currency Code": "MYR",
            }
        ]
    ).to_excel(statement, index=False)

    rows = parse_bank_statement(statement)
    extractor = MorpheusExtractor()
    fee_trace = apply_bank_fees(433.0, "MYR")
    result = match_transactions(
        extractor.extract_invoice(), extractor.extract_payment_proof(), rows, fee_trace
    )

    assert rows[0].row_id == "bank_live_001"
    assert result.status == "matched"


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("date,description,credit_amount\n2026-05-20,payment,421.50\n", "currency"),
        ("date,description,credit_amount,currency\n", "does not contain any"),
    ],
)
def test_parser_rejects_incomplete_csv_statements(tmp_path, content: str, message: str) -> None:
    statement = tmp_path / "invalid_statement.csv"
    statement.write_text(content, encoding="utf-8")

    with pytest.raises(BankStatementParseError, match=message):
        parse_bank_statement(statement)


def test_upload_accepts_files_parses_statement_and_stores_result(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    with (FIXTURE_DIR / "bank_statement_export.csv").open("rb") as statement:
        response = client.post(
            "/api/upload",
            files={
                "invoice": ("invoice.pdf", b"%PDF-1.4\ninvoice fixture", "application/pdf"),
                "payment_proof": (
                    "payment.png",
                    b"\x89PNG\r\npayment fixture",
                    "image/png",
                ),
                "bank_statement": (
                    "bank_statement.csv",
                    statement,
                    "text/csv",
                ),
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == RESULT_FIELDS
    assert payload["job_id"].startswith("upload_")
    assert payload["status"] == "matched"
    assert payload["best_match"]["row_id"] == "uploaded_001"

    stored = client.post("/api/reconcile", json={"job_id": payload["job_id"]})

    assert stored.status_code == 200
    assert stored.json()["job_id"] == payload["job_id"]
    assert stored.json()["best_match"]["row_id"] == "uploaded_001"


def test_supplied_rows_do_not_fall_back_to_fake_demo_results(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    response = client.post(
        "/api/reconcile",
        json={
            "invoice": {
                "invoice_number": "INV-REAL-001",
                "amount": 100.0,
                "currency": "AUD",
                "date": "2026-05-20",
            },
            "payment": {
                "date": "2026-05-20",
                "reference": "INV-REAL-001",
                "currency_sent": "AUD",
            },
            "bank_rows": [
                {
                    "row_id": "uploaded_001",
                    "date": "2026-05-20",
                    "description": "Payment INV-REAL-001",
                    "credit_amount": 250.0,
                    "currency": "THB",
                }
            ],
        },
    )

    assert response.status_code == 422
    assert "No fallback FX rate available for AUD/THB" in response.json()["detail"]
    assert "Prebuilt demo result" not in response.text


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
