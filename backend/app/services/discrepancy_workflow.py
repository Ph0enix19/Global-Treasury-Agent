"""Structured action packs for non-clean reconciliation outcomes."""

from typing import List, Optional

from app.models.schemas import (
    DiscrepancyActionPack,
    FXTrace,
    FeeTrace,
    InvoiceData,
    MatchResult,
    PaymentProofData,
)
from app.utils.normalizer import round_money


def _money(currency: str, amount: Optional[float]) -> str:
    if amount is None:
        return f"{currency} N/A"
    return f"{currency} {amount:.2f}"


def _invoice_label(invoice: InvoiceData) -> str:
    return invoice.invoice_number or "the invoice"


def _difference(match: MatchResult) -> Optional[float]:
    if match.difference is not None:
        return match.difference
    if match.actual_credit is None:
        return None
    return round_money(abs(match.actual_credit - match.expected_credit))


def _classify_discrepancy(match: MatchResult) -> str:
    weak_date = match.date_score < 0.5
    weak_reference = match.reference_score < 0.65
    weak_amount = match.amount_score < 0.70

    if match.status == "needs_review":
        if weak_amount and not weak_reference:
            return "amount_variance_after_fx_and_fees"
        if weak_reference and not weak_amount:
            return "weak_or_missing_reference"
        if weak_date:
            return "settlement_timing_variance"
        return "mixed_review_signals"

    if not match.best_match:
        return "missing_bank_credit"
    if weak_reference and weak_amount:
        return "no_credible_bank_match"
    if weak_date:
        return "settlement_window_gap"
    if weak_reference:
        return "weak_or_missing_reference"
    if weak_amount:
        return "amount_outside_tolerance"
    return "low_confidence_bank_match"


def _likely_reason(category: str, invoice: InvoiceData, match: MatchResult, fee_trace: FeeTrace) -> str:
    invoice_number = _invoice_label(invoice)
    difference = _difference(match)
    if category == "amount_variance_after_fx_and_fees":
        return (
            f"{invoice_number} has a plausible reference/date match, but the closest bank "
            f"credit differs from the deterministic expected credit by "
            f"{_money(fee_trace.currency, difference)}. A possible extra bank charge, "
            "intermediary deduction, or fee-policy variance should be verified."
        )
    if category == "weak_or_missing_reference":
        return (
            f"The closest bank credit does not carry a strong reference match for "
            f"{invoice_number}, so the system cannot safely post it without remittance evidence."
        )
    if category == "settlement_timing_variance":
        return (
            "The strongest candidate falls outside the expected settlement-date window, "
            "which may indicate a delayed credit or an unrelated payment."
        )
    if category == "missing_bank_credit":
        return (
            f"No local bank statement credit was available for the expected credit from "
            f"{invoice_number}."
        )
    if category == "no_credible_bank_match":
        return (
            "The closest bank row is weak on both reference and amount agreement, so it is "
            "not credible enough for automated reconciliation."
        )
    if category == "amount_outside_tolerance":
        return (
            "The closest bank credit is outside the amount tolerance after deterministic FX "
            "and fee calculation."
        )
    if category == "settlement_window_gap":
        return (
            "The closest row is not within the expected payment settlement window, even if "
            "some other attributes partially align."
        )
    return (
        "The available bank evidence is mixed, so the result should remain in manual review "
        "until finance confirms the underlying payment evidence."
    )


def _recommended_action(category: str) -> str:
    if category in {"amount_variance_after_fx_and_fees", "amount_outside_tolerance"}:
        return (
            "Ask finance to obtain the bank advice or remittance fee breakdown before posting "
            "the receipt."
        )
    if category == "weak_or_missing_reference":
        return (
            "Request remittance advice that links the bank credit to the invoice reference."
        )
    if category in {"settlement_timing_variance", "settlement_window_gap"}:
        return (
            "Check the bank statement for the next settlement window and confirm the value "
            "date with the payer."
        )
    if category == "missing_bank_credit":
        return (
            "Hold the invoice open and request an updated bank statement or proof that the "
            "transfer has settled."
        )
    return "Route to finance review with the calculated FX, fee, and match-score evidence."


def _missing_evidence(
    category: str,
    invoice: InvoiceData,
    payment: PaymentProofData,
) -> List[str]:
    invoice_number = _invoice_label(invoice)
    checklist = [
        "Original payment proof with sender, date, amount, currency, and reference visible.",
    ]
    if category in {"amount_variance_after_fx_and_fees", "amount_outside_tolerance"}:
        checklist.append("Bank advice or SWIFT/remittance details showing deducted charges.")
        checklist.append("Confirmation of the receiving bank fee rule used for this account.")
    if category == "weak_or_missing_reference" or not payment.reference:
        checklist.append(f"Remittance advice or bank narrative containing {invoice_number}.")
    if category in {"settlement_timing_variance", "settlement_window_gap", "missing_bank_credit"}:
        checklist.append("Updated bank statement covering the expected settlement window.")
    if payment.warnings:
        checklist.append("Clean payment proof image/PDF without obscured extracted fields.")
    checklist.append("Finance approval note before ledger posting.")
    return list(dict.fromkeys(checklist))


def _notification_message(
    invoice: InvoiceData,
    match: MatchResult,
    fx_trace: FXTrace,
    fee_trace: FeeTrace,
    recommended_action: str,
) -> str:
    invoice_number = _invoice_label(invoice)
    status = match.status.replace("_", " ").title()
    fee = _money(fee_trace.currency, fee_trace.total_fee)
    expected = _money(fee_trace.currency, fee_trace.expected_credit)
    if match.best_match:
        row = match.best_match
        difference = _money(fee_trace.currency, _difference(match))
        candidate = (
            f"Closest bank row {row.row_id} credited {_money(row.currency, row.credit_amount)} "
            f"on {row.date}; variance versus expected is {difference}."
        )
    else:
        candidate = "No local bank credit reached the minimum match threshold."
    return (
        f"Subject: Finance review required for {invoice_number}\n\n"
        f"{invoice_number} is marked {status}. Expected local credit is {expected} after "
        f"{fx_trace.base_currency}/{fx_trace.target_currency} {fx_trace.rate:.4f} on "
        f"{fx_trace.rate_date} and {fee_trace.rule_name} fees of {fee}. {candidate} "
        f"Recommended action: {recommended_action}"
    )


def _audit_safe_explanation(
    match: MatchResult,
    fx_trace: FXTrace,
    fee_trace: FeeTrace,
) -> str:
    row_summary = (
        f"best bank row {match.best_match.row_id}"
        if match.best_match
        else "no candidate bank row"
    )
    return (
        "This action pack uses only extracted invoice/payment fields, the FX trace "
        f"({fx_trace.base_currency}/{fx_trace.target_currency} {fx_trace.rate:.4f}), "
        f"the fee trace ({_money(fee_trace.currency, fee_trace.total_fee)} total fee), "
        f"{row_summary}, and deterministic match scores "
        f"(date {match.date_score:.2f}, reference {match.reference_score:.2f}, "
        f"amount {match.amount_score:.2f}). It does not assume unobserved bank charges "
        "or fabricate missing credits."
    )


def _evidence_basis(match: MatchResult, fx_trace: FXTrace, fee_trace: FeeTrace) -> List[str]:
    basis = [
        f"fx_rate={fx_trace.rate:.4f}",
        f"fx_rate_date={fx_trace.rate_date}",
        f"fee_rule={fee_trace.rule_name}",
        f"expected_credit={fee_trace.currency} {fee_trace.expected_credit:.2f}",
        f"confidence={match.confidence:.4f}",
        f"date_score={match.date_score:.4f}",
        f"reference_score={match.reference_score:.4f}",
        f"amount_score={match.amount_score:.4f}",
    ]
    if match.best_match:
        basis.append(f"best_match_row_id={match.best_match.row_id}")
        basis.append(f"actual_credit={match.best_match.currency} {match.best_match.credit_amount:.2f}")
    return basis


def build_discrepancy_action_pack(
    invoice: InvoiceData,
    payment: PaymentProofData,
    match: MatchResult,
    fx_trace: FXTrace,
    fee_trace: FeeTrace,
) -> Optional[DiscrepancyActionPack]:
    """Create an audit-safe next-action pack for review and unmatched outcomes."""

    if match.status == "matched":
        return None

    category = _classify_discrepancy(match)
    recommended_action = _recommended_action(category)
    return DiscrepancyActionPack(
        category=category,
        likely_reason=_likely_reason(category, invoice, match, fee_trace),
        recommended_next_action=recommended_action,
        missing_evidence_checklist=_missing_evidence(category, invoice, payment),
        mock_notification_message=_notification_message(
            invoice, match, fx_trace, fee_trace, recommended_action
        ),
        audit_safe_explanation=_audit_safe_explanation(match, fx_trace, fee_trace),
        evidence_basis=_evidence_basis(match, fx_trace, fee_trace),
    )
