# Treasury AI Reconciliation Agent

An offline-capable cross-border reconciliation agent built for **AI Marathon 2026**,
Track 3: **Global Treasury Agent**. It turns invoice data, payment proof data, and
local bank statement rows into a traceable reconciliation result and exportable artifacts.

## Project Overview

Small and medium businesses receive cross-border payments in a different currency from
the invoice currency. A USD invoice may appear as a MYR bank credit after an exchange
rate and incoming-wire fees. This MVP demonstrates a reliable workflow for identifying
the best bank match, exposing every money calculation, and producing an audit artifact.

The design follows one trust rule:

> AI extracts and explains; deterministic code calculates and validates all money logic.

## Problem Statement

Manual reconciliation requires finance teams to read payment proofs, verify invoice
references, find dated FX rates, account for fees, compare bank credits, and document
discrepancies. The process is slow and vulnerable to transcription errors, especially
for small teams without treasury tooling.

## Solution Architecture

The application implements this path:

1. The dashboard triggers a demo reconciliation or uploaded-document flow.
2. A Morpheus-compatible extractor returns typed invoice and payment fields, using
   committed JSON fixtures when a live provider is unavailable.
3. Deterministic Python code applies dated FX rates with local fallback and a named
   bank fee rule.
4. The matcher scores bank rows using date, payment reference, and amount proximity.
5. A Chutes-compatible explanation wrapper produces a concise business explanation
   from calculated facts only.
6. The backend generates a PDF reconciliation report and CSV audit log.

![Agent architecture](docs/architecture_diagram.png)

## Tech Stack

| Layer | Technology | MVP Purpose |
|---|---|---|
| Backend | FastAPI, Pydantic, Uvicorn | Modular typed API and shared response contract |
| Frontend | React, Vite | Single-page demo dashboard and API integration |
| Extraction | Morpheus-compatible vision wrapper | Live invoice/payment extraction with safe demo fallback |
| Explanation | Chutes wrapper placeholder | Deterministic offline-friendly explanations |
| Matching | Python, RapidFuzz fallback support | Explainable scoring and decisions |
| FX and fees | Python, Frankfurter v2 + local JSON | Live dated rates with traceable offline fallback |
| Bank imports | pandas, openpyxl | Normalize CSV/XLSX exports into typed statement rows |
| Artifacts | ReportLab, CSV | PDF reconciliation report and audit export |

## Team Structure

| Role | Member | Branch | Primary Ownership |
|---|---|---|---|
| Role 1 | Hemdan | `backend/extraction` | FastAPI orchestration, Morpheus/Chutes wrappers, schema approval |
| Role 2 | Tawila | `backend/matching` | FX, fees, matcher, demo cases, PDF/CSV artifacts, tests |
| Role 3 | Youssef | `frontend/dashboard` | Dashboard, case selector, upload-ready UI, API calls |
| Role 4 | Shafey | `demo/docs` | README/deck polish, screenshots, demo script, QA |

See [docs/context.md](docs/context.md) for branch ownership, checkpoints, and the
locked API contract.

## Current Baseline

The shared `main` baseline already includes:

- FastAPI health, demo, reconciliation, PDF report, and CSV audit endpoints.
- Multipart upload orchestration for invoice, payment proof, and bank statement files.
- Deterministic USD/MYR FX conversion, fee calculation, and transaction scoring.
- Local extraction, FX, and complete-result fallback fixtures for offline demo mode.
- Named `matched`, `needs_review`, and `unmatched` demo cases with pytest coverage.
- A React/Vite dashboard with named scenarios, upload flow, artifact downloads, and
  dark/light mode.
- A committed architecture diagram and local run instructions.

Current Role 1/2 integration: CSV/XLSX bank-export parsing, live dated FX lookup with
safe local fallback, multipart upload orchestration, Morpheus vision extraction, PDF
reports, and CSV audit exports are wired into the shared API contract. The frontend
upload flow posts files to `/api/upload`, receives a stored `job_id`, and can call
`/api/reconcile` with that `job_id` to retrieve the same result.

## Branch Workflow

`main` is the shared integration branch. Pull this coordination baseline before creating
your assigned branch:

```bash
git checkout main
git pull origin main
git checkout -b backend/extraction
```

Use only your branch command:

```bash
# Tawila
git checkout -b backend/matching main

# Youssef
git checkout -b frontend/dashboard main

# Shafey
git checkout -b demo/docs main
```

Commit in small working units and open pull requests into `main`. Hemdan reviews and
merges integration or contract-sensitive work after endpoint smoke checks pass. Before
updating a pull request:

```bash
git checkout main
git pull origin main
git checkout <your-branch>
git merge main
```

Merge order for the remaining submission path: Role 2 real-data parsing and FX
fallback, Role 3 case switcher, Role 1 upload/provider orchestration only when stable,
then Role 4 final screenshots and documentation polish.

## Folder Structure

```text
treasury_hackathon/
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- models/schemas.py
|   |   |-- routers/{health,demo,reconcile,report}.py
|   |   |-- services/
|   |   `-- utils/
|   |-- tests/
|   |-- requirements.txt
|   `-- .env.example
|-- frontend/
|   |-- src/{components,lib}/
|   |-- src/App.jsx
|   `-- package.json
|-- data/
|   |-- demo/
|   `-- outputs/{reports,exports}/
|-- docs/
|   |-- architecture_diagram.png
|   `-- context.md
|-- .gitignore
`-- docker-compose.yml
```

## Setup Instructions

Requirements:

- Python 3.9 or later
- Node.js 18 or later and npm
- Optional: Docker Desktop for one-command service startup

On macOS, if `npm` is not available:

```bash
brew install node
node --version
npm --version
```

Backend setup:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The default `DEMO_MODE=true` makes provider keys optional and keeps all results local.
For live FX integration testing, set `DEMO_MODE=false`; if the provider cannot be
reached, the response FX trace records use of the local dated fallback:

```bash
DEMO_MODE=false
MORPHEUS_API_KEY=
MORPHEUS_BASE_URL=
MORPHEUS_MODEL=
MORPHEUS_FAST_MODEL=
CHUTES_API_KEY=
CHUTES_BASE_URL=
CHUTES_MODEL=
CHUTES_REASONING_MODEL=
FX_API_URL=https://api.frankfurter.dev/v2
FX_API_TIMEOUT_SECONDS=3
```

Recommended Morpheus defaults for live document upload:

```bash
MORPHEUS_BASE_URL=https://api.mor.org/api/v1
MORPHEUS_MODEL=gemma-4-31b
MORPHEUS_FAST_MODEL=gemma-4-26b-a4b
```

Frontend setup:

```bash
cd frontend
npm install
```

## Backend Run Commands

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Open API documentation at `http://localhost:8000/docs`.

Backend verification:

```bash
cd backend
source .venv/bin/activate
pytest
```

## Frontend Run Commands

In a second terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. Set `VITE_API_URL` only if the backend is hosted
somewhere other than `http://localhost:8000`.

Docker alternative:

```bash
docker compose up
```

## API Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Backend status and active mode |
| GET | `/api/demo` | Run the offline matched golden-path reconciliation |
| GET | `/api/demo?case=matched\|needs_review\|unmatched` | Run a named deterministic demo outcome |
| POST | `/api/upload` | Upload invoice, payment proof, and CSV/XLSX bank statement files |
| POST | `/api/reconcile` | Reconcile optional structured inputs or default fixtures |
| GET | `/api/report/{job_id}` | Download the generated PDF report |
| GET | `/api/export/{job_id}` | Download the generated CSV audit log |

`GET /api/demo`, `POST /api/upload`, and `POST /api/reconcile` return
`ReconciliationResult`:

```json
{
  "job_id": "demo_001",
  "status": "matched",
  "confidence": 1.0,
  "invoice": {},
  "payment": {},
  "best_match": {},
  "fx_trace": {},
  "fee_trace": {},
  "score_breakdown": {},
  "explanation": "",
  "warnings": []
}
```

The `ReconciliationResult` shape is frozen for parallel development. Hemdan approves
any contract change before another branch depends on it.

Named demo calls:

```bash
curl http://localhost:8000/api/demo?case=matched
curl http://localhost:8000/api/demo?case=needs_review
curl http://localhost:8000/api/demo?case=unmatched
```

Structured POST example:

```bash
curl -X POST http://localhost:8000/api/reconcile \
  -H "Content-Type: application/json" \
  -d '{}'
```

Multipart upload example in offline demo mode:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "invoice=@data/demo/sample_invoice.pdf" \
  -F "payment_proof=@data/demo/sample_payment_proof.pdf" \
  -F "bank_statement=@data/demo/sample_bank_statement.csv"
```

Then post the returned `job_id` back to `/api/reconcile`:

```bash
curl -X POST http://localhost:8000/api/reconcile \
  -H "Content-Type: application/json" \
  -d '{"job_id":"upload_job_id_here"}'
```

Live Morpheus + FX sample upload:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "invoice=@data/demo/live_fx_upload_test/invoice_INV-LIVE-2026-0526.png" \
  -F "payment_proof=@data/demo/live_fx_upload_test/payment_proof_INV-LIVE-2026-0526.png" \
  -F "bank_statement=@data/demo/live_fx_upload_test/bank_statement_live_fx.csv"
```

Expected live sample result when `DEMO_MODE=false`, Morpheus is configured, and
Frankfurter is reachable:

- `status`: `matched`
- `confidence`: `1.0`
- `invoice.invoice_number`: `INV-LIVE-2026-0526`
- `fx_trace.source`: `frankfurter_live`
- `fx_trace.rate`: `3.955`
- `fx_trace.fallback_used`: `false`
- `fee_trace.expected_credit`: `968.92`
- `best_match.row_id`: `live_row_002`

## Postman Smoke Tests

Import [docs/postman/treasury-ai-reconciliation-agent.postman_collection.json](docs/postman/treasury-ai-reconciliation-agent.postman_collection.json)
into Postman and run it against `http://localhost:8000` with `DEMO_MODE=true`.

The upload request uses these repo-local demo files:

- `data/demo/sample_invoice.pdf`
- `data/demo/sample_payment_proof.pdf`
- `data/demo/sample_bank_statement.csv`

Screenshot placeholder: add the Postman collection runner result screenshot at
`docs/screenshots/postman-smoke-test.png` before submission.

## Demo Flow

1. Start backend and frontend, then click **Run Demo Mode**.
2. The fallback extraction fixtures produce invoice `INV-2026-0412` for `USD 100.00`.
3. Stored FX rate `USD/MYR 4.3300` converts the invoice to `MYR 433.00`.
4. The incoming-wire rule applies `1.5% + MYR 5.00`, yielding `MYR 421.50`.
5. Row `row_003` in the bank statement credits `MYR 421.50`, producing a match.
6. Download the PDF report and audit CSV directly from the result panel.
7. Use `?case=needs_review` and `?case=unmatched` for exception-handling scenes.

For the live upload GUI flow, open `http://localhost:5173`, upload the three files in
`data/demo/live_fx_upload_test/`, and click **Run Reconciliation**. The document upload
cards truncate long file names, the theme toggle switches dark/light mode, and artifact
buttons download the stored job report/export.

Named demo scenarios remain deterministic even when the backend is running with
`DEMO_MODE=false`; live FX is used for real uploaded/supplied financial inputs, while
`/api/demo` keeps the fixture FX values needed for repeatable presentation outcomes.

## Fallback Strategy

The demo does not rely on an external network or an API key:

- `fallback_extracted_invoice.json` replaces unavailable invoice extraction.
- `fallback_extracted_payment.json` replaces unavailable payment proof extraction.
- `fallback_fx_rates.json` replaces unavailable live dated FX lookup.
- `demo_cases.json` supplies deterministic matched, needs-review, and unmatched scenarios.
- `demo_results.json` is an emergency complete response if the pipeline fails.
- PDF generation has a basic built-in output path if ReportLab is unavailable.

In live mode, real uploaded documents do not silently fall back to fake extraction. If
Morpheus cannot safely extract invoice/payment fields, `/api/upload` returns a clear
422 instead of producing a fake successful match.

## Role 2 Real-Data Handoff

Role 2 provides `parse_bank_statement(path)`, which reads `.csv` or `.xlsx` bank
exports and returns normalized `BankStatementRow` objects. Supported common column
names include `transaction_date`/`value_date`, `description`/`narrative`,
`credit_amount`/`amount_received`, and `currency`/`currency_code`.

Hemdan can call this parser after an uploaded bank file is saved, then submit its rows
through `ReconcileRequest.bank_rows`; the public `ReconciliationResult` response shape
does not change. `fetch_fx_rate()` requests a live dated Frankfurter rate only when
`DEMO_MODE=false`, falls back to stored dated rates on provider failure, and raises an
error if no trustworthy fallback pair exists. Supplied financial rows return a clear
validation error rather than being replaced silently with a prebuilt demo outcome.

## Future Improvements

- Multi-invoice batch reconciliation and persistent job storage.
- Chutes API-backed explanation behind the existing deterministic explanation boundary.
- Configurable treasury rate/fee policies, batch reconciliation, and human approval workflow.
- Accounting integrations and secure document storage.

## Integration Checklist

- Confirm `GET /api/health` returns `status: ok`.
- Confirm `GET /api/demo` and each named `case` return the expected deterministic status.
- Confirm `POST /api/reconcile` returns the same field structure as demo.
- Confirm PDF and CSV links download generated artifacts.
- Confirm live upload with `data/demo/live_fx_upload_test/` returns a matched result
  only when Morpheus extraction succeeds.
- Confirm `pytest` passes before merging backend changes.
- Record the final demo in `DEMO_MODE=true` after the above checks pass.

## Start Here Today

| Member | First Task | Handoff Required |
|---|---|---|
| Hemdan | Keep schemas/routes stable and review backend PRs | Confirm API smoke checks after merges |
| Tawila | Deliver bank export parser and live FX fallback tests | Provide typed rows and traceable FX behavior |
| Youssef | Use the merged named-case endpoints | Add case switch UI and retain downloads |
| Shafey | Prepare deck/script against the verified baseline | Capture matched and needs-review flow after integration |

Immediate sequence:

1. Pull `main` and create only your assigned branch.
2. Tawila delivers the real bank-export parser and live-FX fallback pull request.
3. Youssef connects the already available named cases in the UI.
4. Hemdan connects uploads/provider work without moving money calculations into AI.
5. Shafey captures the stable offline walkthrough and final materials.
