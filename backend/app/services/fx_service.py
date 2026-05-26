"""Live-with-fallback FX rate lookup used for deterministic money calculations."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from app.models.schemas import FXTrace
from app.utils.normalizer import normalize_currency, normalize_date, round_money


DEMO_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "demo"


def _rates() -> Dict[str, Any]:
    with (DEMO_DATA_DIR / "fallback_fx_rates.json").open("r", encoding="utf-8") as fixture:
        return json.load(fixture)


def _fallback_rate(base: str, target: str, rate_date: str) -> float:
    fallback_rates = _rates()
    dated_key = f"{rate_date}:{base}_{target}"
    default_key = f"{base}_{target}"
    rate = fallback_rates["dated_rates"].get(
        dated_key, fallback_rates["default_rates"].get(default_key)
    )
    if rate is None:
        raise ValueError(f"No fallback FX rate available for {base}/{target} on {rate_date}.")
    return float(rate)


def _live_rate(base: str, target: str, rate_date: str) -> float:
    api_url = os.getenv("FX_API_URL", "https://api.frankfurter.dev/v2").rstrip("/")
    timeout = float(os.getenv("FX_API_TIMEOUT_SECONDS", "3"))
    response = httpx.get(
        f"{api_url}/rate/{base}/{target}",
        params={"date": rate_date},
        timeout=timeout,
    )
    response.raise_for_status()
    rate = response.json().get("rate")
    if rate is None:
        raise ValueError("FX provider response did not contain a rate.")
    return float(rate)


def fetch_fx_rate(
    base_currency: str,
    target_currency: str,
    transaction_date: str,
    amount: float,
    use_live: Optional[bool] = None,
) -> FXTrace:
    """Use live dated FX outside demo mode, with a traceable local fallback."""

    base = normalize_currency(base_currency)
    target = normalize_currency(target_currency)
    rate_date = normalize_date(transaction_date)
    rate = 1.0
    source = "identity"
    fallback_used = False

    if base != target:
        live_mode = (
            os.getenv("DEMO_MODE", "true").lower() == "false"
            if use_live is None
            else use_live
        )
        if live_mode:
            try:
                rate = _live_rate(base, target, rate_date)
                source = "frankfurter_live"
            except (httpx.HTTPError, ValueError, TypeError, KeyError):
                rate = _fallback_rate(base, target, rate_date)
                source = "local_fallback_fx_rates"
                fallback_used = True
        else:
            rate = _fallback_rate(base, target, rate_date)
            source = "local_fallback_fx_rates"
            fallback_used = True

    return FXTrace(
        base_currency=base,
        target_currency=target,
        rate_date=rate_date,
        input_amount=round_money(amount),
        rate=float(rate),
        converted_amount=round_money(amount * float(rate)),
        source=source,
        fallback_used=fallback_used,
    )
