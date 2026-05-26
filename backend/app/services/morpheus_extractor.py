"""Morpheus-compatible extraction wrapper with deterministic local fallback data."""

import base64
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx
from pydantic import ValidationError

from app.models.schemas import InvoiceData, PaymentProofData


DEMO_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "demo"
T = TypeVar("T", InvoiceData, PaymentProofData)
JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)


def _load_json(filename: str) -> Dict[str, Any]:
    with (DEMO_DATA_DIR / filename).open("r", encoding="utf-8") as fixture:
        return json.load(fixture)


def _parse_provider_json(content: str) -> Dict[str, Any]:
    """Parse provider JSON even when a model wraps it in a Markdown fence."""

    candidate = content.strip()
    fenced = JSON_FENCE_RE.search(candidate)
    if fenced:
        candidate = fenced.group(1).strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(candidate[start : end + 1])


class MorpheusExtractor:
    """Stable interface that can later call Morpheus without affecting routes."""

    def __init__(self) -> None:
        self.api_key = os.getenv("MORPHEUS_API_KEY", "")
        self.base_url = (os.getenv("MORPHEUS_BASE_URL") or "https://api.mor.org/api/v1").rstrip("/")
        self.model = os.getenv("MORPHEUS_MODEL") or "gemma-4-31b"
        self.fast_model = os.getenv("MORPHEUS_FAST_MODEL") or "gemma-4-26b-a4b"
        self.fallback_mode = os.getenv("DEMO_MODE", "true").lower() != "false" or not self.api_key

    def _fallback_invoice(self, warning: Optional[str] = None) -> InvoiceData:
        invoice = InvoiceData(**_load_json("fallback_extracted_invoice.json"))
        if warning:
            invoice.warnings.append(warning)
        return invoice

    def _fallback_payment(self, warning: Optional[str] = None) -> PaymentProofData:
        payment = PaymentProofData(**_load_json("fallback_extracted_payment.json"))
        if warning:
            payment.warnings.append(warning)
        return payment

    def _extract_with_provider(
        self,
        document_type: str,
        schema: Type[T],
        document_path: Optional[Union[str, Path]],
        model: str,
    ) -> T:
        if not document_path:
            raise ValueError("No document path supplied for provider extraction.")
        path = Path(document_path)
        media_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
        }.get(path.suffix.lower(), "application/octet-stream")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        fields = (
            "invoice_number, payer, payee, amount, currency, date, due_date"
            if document_type == "invoice"
            else "sender, receiver, amount_sent, currency_sent, date, reference, method"
        )
        prompt = (
            "You are a financial document extraction specialist. "
            "Extract only values visibly present in the supplied document. "
            f"For {document_type}, return JSON with these fields: {fields}. "
            "Set missing fields to null. Do not calculate, infer, or explain."
        )
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{encoded}",
                                },
                            },
                        ],
                    }
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        payload = _parse_provider_json(content)
        return schema(**payload)

    def extract_invoice(
        self,
        structured_input: Optional[Union[InvoiceData, Dict[str, Any]]] = None,
        document_path: Optional[Union[str, Path]] = None,
    ) -> InvoiceData:
        if isinstance(structured_input, InvoiceData):
            return structured_input
        if structured_input:
            return InvoiceData(**structured_input)
        if self.fallback_mode:
            return self._fallback_invoice()
        try:
            return self._extract_with_provider("invoice", InvoiceData, document_path, self.model)
        except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            try:
                return self._extract_with_provider(
                    "invoice", InvoiceData, document_path, self.fast_model
                )
            except (
                httpx.HTTPError,
                KeyError,
                json.JSONDecodeError,
                ValidationError,
                ValueError,
            ):
                return self._fallback_invoice(
                    f"Morpheus extraction failed; local invoice fallback used: {exc}"
                )

    def extract_payment_proof(
        self,
        structured_input: Optional[Union[PaymentProofData, Dict[str, Any]]] = None,
        document_path: Optional[Union[str, Path]] = None,
    ) -> PaymentProofData:
        if isinstance(structured_input, PaymentProofData):
            return structured_input
        if structured_input:
            return PaymentProofData(**structured_input)
        if self.fallback_mode:
            return self._fallback_payment()
        try:
            return self._extract_with_provider("payment proof", PaymentProofData, document_path, self.model)
        except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            try:
                return self._extract_with_provider(
                    "payment proof", PaymentProofData, document_path, self.fast_model
                )
            except (
                httpx.HTTPError,
                KeyError,
                json.JSONDecodeError,
                ValidationError,
                ValueError,
            ):
                return self._fallback_payment(
                    f"Morpheus extraction failed; local payment fallback used: {exc}"
                )


def extract_document_fields(document_type: str) -> Union[InvoiceData, PaymentProofData]:
    """Mock the extraction tool while keeping a future provider-friendly interface."""

    extractor = MorpheusExtractor()
    if document_type == "invoice":
        return extractor.extract_invoice()
    if document_type == "payment":
        return extractor.extract_payment_proof()
    raise ValueError(f"Unsupported document type: {document_type}")
