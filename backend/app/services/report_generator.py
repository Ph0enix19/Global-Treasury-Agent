"""PDF report artifact generation with a dependency-free emergency fallback."""

from pathlib import Path
from textwrap import wrap
from typing import List, Optional

from app.models.schemas import ReconciliationResult


REPORT_DIR = Path(__file__).resolve().parents[3] / "data" / "outputs" / "reports"


def _append_wrapped(lines: List[str], label: str, text: str, width: int = 94) -> None:
    wrapped = wrap(text, width=width) or [""]
    lines.append(f"{label}: {wrapped[0]}")
    for continuation in wrapped[1:]:
        lines.append(f"  {continuation}")


def _report_lines(result: ReconciliationResult) -> List[str]:
    bank_row = result.best_match
    invoice_currency = result.invoice.currency or "N/A"
    invoice_amount = result.invoice.amount or 0.0
    matched_credit = (
        f"{bank_row.currency} {bank_row.credit_amount:.2f} on {bank_row.date}"
        if bank_row
        else "No matching bank credit"
    )
    lines = [
        "Treasurer.ai - Reconciliation Report",
        f"Job ID: {result.job_id}",
        f"Status: {result.status.upper()}",
        f"Confidence: {result.confidence:.1%}",
        f"Invoice: {result.invoice.invoice_number or 'Unknown'}",
        f"Invoice Amount: {invoice_currency} {invoice_amount:.2f}",
        f"FX Trace: {result.fx_trace.base_currency}/{result.fx_trace.target_currency} "
        f"{result.fx_trace.rate:.4f} on {result.fx_trace.rate_date}",
        f"Converted Amount: {result.fx_trace.target_currency} {result.fx_trace.converted_amount:.2f}",
        f"Fee Trace: {result.fee_trace.rule_name}, total {result.fee_trace.currency} "
        f"{result.fee_trace.total_fee:.2f}",
        f"Expected Credit: {result.fee_trace.currency} {result.fee_trace.expected_credit:.2f}",
        f"Matched Credit: {matched_credit}",
        f"Explanation: {result.explanation}",
        "Calculation rule: AI extracts and explains; deterministic code calculates and validates.",
    ]
    if result.action_pack:
        lines.append(f"Discrepancy Category: {result.action_pack.category}")
        _append_wrapped(
            lines,
            "Recommended Next Action",
            result.action_pack.recommended_next_action,
        )
        _append_wrapped(
            lines,
            "Missing Evidence Checklist",
            "; ".join(result.action_pack.missing_evidence_checklist),
        )
        _append_wrapped(
            lines,
            "Audit-Safe Explanation",
            result.action_pack.audit_safe_explanation,
        )
    return lines


def _write_with_reportlab(path: Path, lines: List[str]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    document = canvas.Canvas(str(path), pagesize=A4)
    text = document.beginText(48, A4[1] - 56)
    text.setFont("Helvetica", 10)
    for line in lines:
        text.textLine(line)
    document.drawText(text)
    document.save()


def _write_minimal_pdf(path: Path, lines: List[str]) -> None:
    """Write a simple valid PDF when ReportLab is unavailable in a fresh checkout."""

    safe_lines = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in lines]
    commands = ["BT", "/F1 10 Tf", "48 790 Td"]
    for index, line in enumerate(safe_lines):
        if index:
            commands.append("0 -16 Td")
        commands.append(f"({line}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    path.write_bytes(pdf)


def generate_reconciliation_report(
    result: ReconciliationResult, output_dir: Optional[Path] = None
) -> Path:
    """Generate a PDF artifact for a reconciliation result."""

    target_dir = output_dir or REPORT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{result.job_id}_reconciliation_report.pdf"
    lines = _report_lines(result)
    try:
        _write_with_reportlab(path, lines)
    except ImportError:
        _write_minimal_pdf(path, lines)
    return path
