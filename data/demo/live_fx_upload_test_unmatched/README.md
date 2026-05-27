# Live FX Upload Test - Unmatched

Upload these three files through the dashboard to demonstrate an unmatched live-upload flow:

- `invoice_INV-2026-0412.png`
- `payment_receipt_INV-2026-0412.png`
- `bank_statement_unmatched_live_fx.csv` or `bank_statement_unmatched_live_fx.xlsx`

In the default `DEMO_MODE=true`, the backend uses deterministic fallback extraction for
the visible invoice/payment values and parses this bank statement normally. The statement
intentionally omits a matching `INV-2026-0412` credit near the expected `MYR 421.50`, so
the reconciliation should end as `unmatched`.
