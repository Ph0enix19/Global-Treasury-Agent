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

1. The dashboard triggers a demo reconciliation or future uploaded-document flow.
2. A Morpheus-compatible extractor returns typed invoice and payment fields, using
   committed JSON fixtures when a live provider is unavailable.
3. Deterministic Python code applies fallback FX rates and a named bank fee rule.
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
| Extraction | Morpheus wrapper placeholder | Mocked structured invoice/payment extraction |
| Explanation | Chutes wrapper placeholder | Deterministic offline-friendly explanations |
| Matching | Python, RapidFuzz fallback support | Explainable scoring and decisions |
| FX and fees | Python + local JSON | Deterministic calculations with no network dependency |
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
- Deterministic USD/MYR FX conversion, fee calculation, and transaction scoring.
- Local extraction, FX, and complete-result fallback fixtures for offline demo mode.
- A React/Vite dashboard that loads the golden-path result and downloads artifacts.
- A committed architecture diagram and local run instructions.

Next integration target: Tawila adds deterministic `matched`, `needs_review`, and
`unmatched` demo cases on `backend/matching`; after review and merge, Youssef exposes
those cases in the dashboard without changing the response model.

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

Merge order for the submission path: Role 2 deterministic cases and tests, Role 3 case
switcher, Role 1 live provider enhancements only when stable, then Role 4 final
screenshots and documentation polish.

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

Open `http://localhost:5173`. Set `VITE_API_BASE_URL` only if the backend is hosted
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
| POST | `/api/reconcile` | Reconcile optional structured inputs or default fixtures |
| GET | `/api/report/{job_id}` | Download the generated PDF report |
| GET | `/api/export/{job_id}` | Download the generated CSV audit log |

`GET /api/demo` and `POST /api/reconcile` both return `ReconciliationResult`:

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

## Demo Flow

1. Start backend and frontend, then click **Run Demo Mode**.
2. The fallback extraction fixtures produce invoice `INV-2026-0412` for `USD 100.00`.
3. Stored FX rate `USD/MYR 4.3300` converts the invoice to `MYR 433.00`.
4. The incoming-wire rule applies `1.5% + MYR 5.00`, yielding `MYR 421.50`.
5. Row `row_003` in the bank statement credits `MYR 421.50`, producing a match.
6. Download the PDF report and audit CSV directly from the result panel.
7. Use `?case=needs_review` and `?case=unmatched` for exception-handling scenes.

## Fallback Strategy

The demo does not rely on an external network or an API key:

- `fallback_extracted_invoice.json` replaces unavailable invoice extraction.
- `fallback_extracted_payment.json` replaces unavailable payment proof extraction.
- `fallback_fx_rates.json` replaces unavailable live dated FX lookup.
- `demo_cases.json` supplies deterministic matched, needs-review, and unmatched scenarios.
- `demo_results.json` is an emergency complete response if the pipeline fails.
- PDF generation has a basic built-in output path if ReportLab is unavailable.

The mock provider boundaries are intentionally stable so real Morpheus and Chutes
adapters can be connected later without changing the API contract.

## Future Improvements

- Multipart invoice/payment uploads and CSV/XLSX parsing routes.
- Live Morpheus extraction and Chutes explanation behind the existing wrappers.
- Live FX lookup with cached dated-rate fallback.
- Needs-review case toggles, batch reconciliation, and human approval workflow.
- Accounting integrations and secure document storage.

## Integration Checklist

- Confirm `GET /api/health` returns `status: ok`.
- Confirm `GET /api/demo` and each named `case` return the expected deterministic status.
- Confirm `POST /api/reconcile` returns the same field structure as demo.
- Confirm PDF and CSV links download generated artifacts.
- Confirm `pytest` passes before merging backend changes.
- Record the final demo in `DEMO_MODE=true` after the above checks pass.

## Start Here Today

| Member | First Task | Handoff Required |
|---|---|---|
| Hemdan | Keep schemas/routes stable and review backend PRs | Confirm API smoke checks after merges |
| Tawila | Add and test deterministic match/review/unmatched cases | Provide stable demo case URLs and artifacts |
| Youssef | Keep current dashboard usable while waiting for case URLs | Add case switch UI after Role 2 merges |
| Shafey | Prepare deck/script against the verified baseline | Capture matched and needs-review flow after integration |

Immediate sequence:

1. Pull `main` and create only your assigned branch.
2. Tawila completes the deterministic demo-case pull request.
3. Youssef connects the named cases in the UI.
4. Hemdan integrates provider work without moving money calculations into AI.
5. Shafey captures the stable offline walkthrough and final materials.
