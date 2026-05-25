"""Named deterministic demo cases using the shared reconciliation response contract."""

import json
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import ReconcileRequest, ReconciliationResult
from app.routers.reconcile import run_reconciliation


router = APIRouter(prefix="/api/demo", tags=["demo"])
DEMO_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "demo"
SUPPORTED_DEMO_CASES = ("matched", "needs_review", "unmatched")


def _load_demo_request(case_name: str) -> ReconcileRequest:
    with (DEMO_DATA_DIR / "demo_cases.json").open("r", encoding="utf-8") as fixture:
        cases: Dict[str, dict] = json.load(fixture)
    return ReconcileRequest(**cases[case_name])


@router.get("", response_model=ReconciliationResult)
def demo_result(
    case: str = Query(default="matched", description="Deterministic scenario to demonstrate.")
) -> ReconciliationResult:
    if case not in SUPPORTED_DEMO_CASES:
        supported = ", ".join(SUPPORTED_DEMO_CASES)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported demo case '{case}'. Supported cases: {supported}.",
        )
    return run_reconciliation(_load_demo_request(case))
