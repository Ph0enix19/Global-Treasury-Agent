"""Shared API contracts for the treasury reconciliation workflow."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    payer: Optional[str] = None
    payee: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[str] = None
    due_date: Optional[str] = None
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)


class PaymentProofData(BaseModel):
    sender: Optional[str] = None
    receiver: Optional[str] = None
    amount_sent: Optional[float] = None
    currency_sent: Optional[str] = None
    date: Optional[str] = None
    reference: Optional[str] = None
    method: Optional[str] = None
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)


class BankStatementRow(BaseModel):
    row_id: str
    date: str
    description: str
    credit_amount: float
    debit_amount: Optional[float] = None
    currency: str


class FXTrace(BaseModel):
    base_currency: str
    target_currency: str
    rate_date: str
    input_amount: float
    rate: float
    converted_amount: float
    source: str
    fallback_used: bool = True


class FeeTrace(BaseModel):
    rule_name: str
    currency: str
    gross_amount: float
    percentage_rate: float
    percentage_fee: float
    flat_fee: float
    total_fee: float
    expected_credit: float


class MatchResult(BaseModel):
    status: str
    confidence: float
    best_match: Optional[BankStatementRow] = None
    expected_credit: float
    actual_credit: Optional[float] = None
    difference: Optional[float] = None
    date_score: float
    reference_score: float
    amount_score: float


class DiscrepancyActionPack(BaseModel):
    category: str
    likely_reason: str
    recommended_next_action: str
    missing_evidence_checklist: List[str] = Field(default_factory=list)
    mock_notification_message: str
    audit_safe_explanation: str
    evidence_basis: List[str] = Field(default_factory=list)


class ReconciliationResult(BaseModel):
    job_id: str
    status: str
    confidence: float
    invoice: InvoiceData
    payment: PaymentProofData
    best_match: Optional[BankStatementRow] = None
    fx_trace: FXTrace
    fee_trace: FeeTrace
    score_breakdown: Dict[str, float]
    explanation: str
    action_pack: Optional[DiscrepancyActionPack] = None
    warnings: List[str] = Field(default_factory=list)


class ReconcileRequest(BaseModel):
    """Optional structured inputs for upload integration and local testing."""

    job_id: Optional[str] = None
    invoice: Optional[InvoiceData] = None
    payment: Optional[PaymentProofData] = None
    bank_rows: Optional[List[BankStatementRow]] = None
    fee_rule: str = "incoming_wire"


class HealthResponse(BaseModel):
    status: str
    service: str
    mode: str
