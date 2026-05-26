"""Chutes-compatible explanation boundary with deterministic offline responses."""

import os

from app.models.schemas import InvoiceData, MatchResult


class ChutesAgent:
    """Create business-language explanations only from already-calculated results."""

    def __init__(self) -> None:
        self.api_key = os.getenv("CHUTES_API_KEY", "")
        self.base_url = (os.getenv("CHUTES_BASE_URL") or "https://llm.chutes.ai/v1").rstrip("/")
        self.model = os.getenv("CHUTES_MODEL") or "Qwen/Qwen3-32B-TEE"
        self.reasoning_model = os.getenv("CHUTES_REASONING_MODEL") or "zai-org/GLM-5.1-TEE"
        self.fallback_mode = os.getenv("DEMO_MODE", "true").lower() != "false" or not self.api_key

    def explain_reconciliation(self, invoice: InvoiceData, match: MatchResult) -> str:
        invoice_number = invoice.invoice_number or "the invoice"
        if match.status == "matched" and match.best_match:
            row = match.best_match
            return (
                f"{invoice_number} was matched to a {row.currency} {row.credit_amount:.2f} "
                f"bank credit on {row.date} after the recorded FX and fee adjustments."
            )
        if match.status == "needs_review" and match.best_match:
            return (
                f"{invoice_number} needs review because the closest bank credit differs "
                f"from the expected amount by {match.difference:.2f} after FX and fees."
            )
        return (
            f"{invoice_number} could not be matched to a bank credit with sufficient "
            "date, reference, and amount agreement."
        )


def generate_explanation(invoice: InvoiceData, match: MatchResult) -> str:
    return ChutesAgent().explain_reconciliation(invoice, match)
