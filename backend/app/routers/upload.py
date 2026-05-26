"""Multipart upload orchestration for Role 1 document-to-reconciliation flow."""

import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import ReconcileRequest, ReconciliationResult
from app.routers.reconcile import ReconciliationInputError, run_reconciliation
from app.services.bank_statement_parser import BankStatementParseError, parse_bank_statement
from app.services.morpheus_extractor import MorpheusExtractor


router = APIRouter(prefix="/api/upload", tags=["upload"])
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "data" / "uploads"
DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
BANK_EXTENSIONS = {".csv", ".xlsx"}


def _demo_mode_enabled() -> bool:
    return os.getenv("DEMO_MODE", "true").lower() != "false"


def _used_local_extraction_fallback(*warnings: list[str]) -> bool:
    return any(
        "fallback" in warning.lower() and "morpheus extraction failed" in warning.lower()
        for warning_list in warnings
        for warning in warning_list
    )


def _safe_filename(field_name: str, filename: str, allowed_extensions: set[str]) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must use one of these file types: {allowed}.",
        )
    stem = Path(filename).stem or field_name
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._") or field_name
    return f"{field_name}_{cleaned[:80]}{suffix}"


async def _save_upload(
    job_dir: Path, field_name: str, upload: UploadFile, allowed_extensions: set[str]
) -> Path:
    filename = _safe_filename(field_name, upload.filename or field_name, allowed_extensions)
    destination = job_dir / filename
    content = await upload.read()
    if not content:
        raise HTTPException(status_code=400, detail=f"{field_name} file is empty.")
    destination.write_bytes(content)
    return destination


@router.post("", response_model=ReconciliationResult)
async def upload_and_reconcile(
    invoice: UploadFile = File(...),
    payment_proof: UploadFile = File(...),
    bank_statement: UploadFile = File(...),
) -> ReconciliationResult:
    """Save uploaded files, parse bank rows, extract fields, and reconcile safely."""

    job_id = f"upload_{uuid4().hex}"
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)

    invoice_path = await _save_upload(job_dir, "invoice", invoice, DOCUMENT_EXTENSIONS)
    payment_path = await _save_upload(
        job_dir, "payment_proof", payment_proof, DOCUMENT_EXTENSIONS
    )
    bank_path = await _save_upload(job_dir, "bank_statement", bank_statement, BANK_EXTENSIONS)

    try:
        bank_rows = parse_bank_statement(bank_path)
        extractor = MorpheusExtractor()
        extracted_invoice = extractor.extract_invoice(document_path=invoice_path)
        extracted_payment = extractor.extract_payment_proof(document_path=payment_path)
        if not _demo_mode_enabled() and (
            extractor.fallback_mode
            or _used_local_extraction_fallback(
                extracted_invoice.warnings, extracted_payment.warnings
            )
        ):
            raise ReconciliationInputError(
                "Morpheus extraction is unavailable; uploaded financial documents "
                "cannot be safely reconciled in live mode."
            )
        request = ReconcileRequest(
            job_id=job_id,
            invoice=extracted_invoice,
            payment=extracted_payment,
            bank_rows=bank_rows,
        )
        return run_reconciliation(request)
    except BankStatementParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ReconciliationInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

