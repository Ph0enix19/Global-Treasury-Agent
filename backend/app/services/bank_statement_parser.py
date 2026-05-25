"""Parse real bank statement CSV/XLSX exports into normalized matching rows."""

import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from app.models.schemas import BankStatementRow
from app.utils.normalizer import normalize_currency, normalize_date, round_money


class BankStatementParseError(ValueError):
    """Raised when an uploaded statement cannot be normalized safely."""


COLUMN_ALIASES: Dict[str, tuple] = {
    "row_id": ("row_id", "transaction_id", "reference_id", "id"),
    "date": ("date", "transaction_date", "value_date", "posting_date"),
    "description": ("description", "details", "narrative", "transaction_description"),
    "credit_amount": ("credit_amount", "credit", "amount_received", "deposit_amount"),
    "debit_amount": ("debit_amount", "debit", "withdrawal_amount"),
    "currency": ("currency", "ccy", "currency_code"),
}
REQUIRED_COLUMNS = ("date", "description", "credit_amount", "currency")


def _clean_header(header: object) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", str(header).strip().lower())).strip("_")


def _read_statement(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise BankStatementParseError(f"Bank statement file not found: {path.name}.")
    try:
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        if path.suffix.lower() == ".xlsx":
            return pd.read_excel(path)
    except Exception as exc:
        raise BankStatementParseError(f"Could not read bank statement file: {path.name}.") from exc
    raise BankStatementParseError("Bank statement must be a CSV or XLSX file.")


def _resolve_columns(frame: pd.DataFrame) -> Dict[str, str]:
    clean_to_original = {_clean_header(column): column for column in frame.columns}
    resolved: Dict[str, str] = {}
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in clean_to_original:
                resolved[field] = clean_to_original[alias]
                break
    missing = [field for field in REQUIRED_COLUMNS if field not in resolved]
    if missing:
        raise BankStatementParseError(
            "Missing required bank statement columns: " + ", ".join(missing) + "."
        )
    return resolved


def _text(value: object, label: str, row_number: int) -> str:
    if pd.isna(value) or not str(value).strip():
        raise BankStatementParseError(f"Row {row_number}: {label} is missing.")
    return str(value).strip()


def _date(value: object, row_number: int) -> str:
    if pd.isna(value):
        raise BankStatementParseError(f"Row {row_number}: date is missing.")
    if isinstance(value, (pd.Timestamp, date)):
        normalized = (
            value.date().isoformat() if isinstance(value, pd.Timestamp) else value.isoformat()
        )
    else:
        normalized = normalize_date(_text(value, "date", row_number))
    try:
        date.fromisoformat(normalized)
    except (TypeError, ValueError) as exc:
        raise BankStatementParseError(
            f"Row {row_number}: date must be a valid date."
        ) from exc
    return normalized


def _money(value: object, label: str, row_number: int, optional: bool = False) -> Optional[float]:
    if pd.isna(value) or str(value).strip() == "":
        if optional:
            return None
        raise BankStatementParseError(f"Row {row_number}: {label} is missing.")
    cleaned = str(value).replace(",", "").replace("RM", "").strip()
    try:
        amount = float(cleaned)
    except ValueError as exc:
        raise BankStatementParseError(f"Row {row_number}: {label} must be numeric.") from exc
    if amount < 0:
        raise BankStatementParseError(f"Row {row_number}: {label} cannot be negative.")
    return round_money(amount)


def parse_bank_statement(file_path: Union[str, Path]) -> List[BankStatementRow]:
    """Return normalized rows from a common bank CSV/XLSX export."""

    frame = _read_statement(Path(file_path))
    if frame.empty:
        raise BankStatementParseError("Bank statement does not contain any transaction rows.")
    columns = _resolve_columns(frame)
    rows: List[BankStatementRow] = []

    for index, row in frame.iterrows():
        row_number = int(index) + 2
        row_id = (
            _text(row[columns["row_id"]], "row_id", row_number)
            if "row_id" in columns
            else f"uploaded_{len(rows) + 1:03d}"
        )
        rows.append(
            BankStatementRow(
                row_id=row_id,
                date=_date(row[columns["date"]], row_number),
                description=_text(row[columns["description"]], "description", row_number),
                credit_amount=_money(row[columns["credit_amount"]], "credit_amount", row_number) or 0.0,
                debit_amount=(
                    _money(row[columns["debit_amount"]], "debit_amount", row_number, optional=True)
                    if "debit_amount" in columns
                    else None
                ),
                currency=normalize_currency(_text(row[columns["currency"]], "currency", row_number)),
            )
        )
    return rows
