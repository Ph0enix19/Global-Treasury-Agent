# Team Context: Treasury AI Reconciliation Agent

## Goal And Guardrail

Build a stable AI Marathon 2026 Global Treasury Agent MVP that reconciles invoice,
payment proof, and bank statement data. Morpheus and Chutes are visible integration
boundaries, but the demo works without keys or internet.

**Locked rule:** AI extracts and explains; deterministic code calculates FX conversion,
bank fees, match scores, status, and reported values.

## Team Roles

| Role | Member | Branch | Primary Ownership |
|---|---|---|---|
| Role 1 | Hemdan | `backend/extraction` | FastAPI orchestration, Morpheus/Chutes wrappers, schema approval |
| Role 2 | Tawila | `backend/matching` | FX, fees, matcher, demo cases, PDF/CSV artifacts, tests |
| Role 3 | Youssef | `frontend/dashboard` | Dashboard, case selector, upload-ready UI, API calls |
| Role 4 | Shafey | `demo/docs` | README/deck polish, screenshots, demo script, QA |

## Branch Ownership

The role-to-member mapping above identifies each owner; this locked branch matrix remains
the integration reference:

| Branch | Owner | Work |
|---|---|---|
| backend/extraction | Role 1 | Morpheus, Chutes, FastAPI orchestration |
| backend/matching | Role 2 | FX, fees, matcher, report, demo data |
| frontend/dashboard | Role 3 | UI components and API calls |
| demo/docs | Role 4 | deck, README, screenshots, demo script |

## Current Progress

Baseline complete on `main`:
- FastAPI boots locally with health, demo, reconcile, PDF report, and CSV export routes.
- The shared `ReconciliationResult` contract and deterministic FX/fee/matcher path work.
- Demo fixtures and fallback mode run without Morpheus, Chutes, or FX network access.
- Named matched, needs-review, and unmatched cases with focused backend tests are merged.
- The React dashboard consumes `/api/demo` and exposes PDF/CSV download actions.
- README setup instructions and the architecture diagram are committed.

Role 1 update on `backend/hemdan`:
- `POST /api/upload` accepts multipart `invoice`, `payment_proof`, and `bank_statement`.
- Uploaded files are saved under ignored runtime job folders in `data/uploads/`.
- Bank CSV/XLSX rows are parsed through `parse_bank_statement(path)`.
- Invoice and payment proof extraction goes through `MorpheusExtractor`; `DEMO_MODE=true`
  and provider failures preserve local fallback extraction.
- Uploaded data is submitted as a `ReconcileRequest` to the existing deterministic
  `run_reconciliation` pipeline, preserving the frozen `ReconciliationResult` shape.
- The frontend-compatible handoff is supported: `/api/upload` stores the upload result,
  and `/api/reconcile` returns that stored result when called with only the upload
  `job_id`.
- Provider env placeholders are documented without secrets:
  `MORPHEUS_BASE_URL`, `MORPHEUS_MODEL`, `MORPHEUS_FAST_MODEL`, `CHUTES_BASE_URL`,
  `CHUTES_MODEL`, and `CHUTES_REASONING_MODEL`.

Role 1 local verification on `backend/hemdan`:
- Backend dependencies were installed into `backend/.venv`; `backend/.env` was not
  printed or committed.
- Backend tests passed with the repo-local pytest temp directory:
  `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp .tmp\pytest`
  returned `21 passed`.
- FastAPI was started locally with uvicorn and smoke-tested successfully:
  `/api/health` returned `ok`, `/api/demo?case=matched` returned `matched`, and
  multipart `/api/upload` returned a matched upload result.
- The frontend-compatible upload handoff was smoke-tested: posting the upload `job_id`
  back to `/api/reconcile` returned the stored upload reconciliation.
- Frontend dependencies were installed locally and `npm run build` completed
  successfully.
- `docker-compose.yml` was checked with `docker compose config`; the frontend env var
  was corrected to `VITE_API_URL` so it matches `frontend/src/lib/api.js`.
- Recommendation for day-to-day work: use the local venv and npm workflow for speed;
  use Docker Compose when a clean teammate/demo environment is more important than
  fast iteration.

Immediate branch work:

| Member | In Progress Next | Expected Handoff |
|---|---|---|
| Hemdan | Provider/orchestration integration and API stability review | Approve contract-sensitive PRs and verify routes after merge |
| Tawila | CSV/XLSX bank-export parser plus live dated FX fallback | Typed rows, explicit FX traces, and no fake result substitution for real inputs |
| Youssef | Demo-case switcher using merged case endpoints | UI showing matched, needs review, and unmatched results |
| Shafey | Submission deck, script, screenshots, and QA | Verified demo narrative and final delivery assets |

## API Contract Ownership

Hemdan owns [backend/app/models/schemas.py](../backend/app/models/schemas.py) and approves
contract changes before merge. Tawila implements deterministic values within that contract.
Youssef consumes the contract and must not create alternate result field names. Shafey
documents only behavior confirmed against demo mode.

`GET /api/demo`, `POST /api/upload`, and `POST /api/reconcile` return one
`ReconciliationResult` shape:

```json
{
  "job_id": "",
  "status": "",
  "confidence": 0.0,
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

Endpoint ownership:

| Endpoint | Owner | Contract |
|---|---|---|
| `GET /api/health` | Hemdan | Service readiness response |
| `GET /api/demo?case=matched\|needs_review\|unmatched` | Hemdan + Tawila | `ReconciliationResult`; omitted `case` defaults to `matched` |
| `POST /api/upload` | Hemdan | Multipart upload orchestration returning/storing `ReconciliationResult` |
| `POST /api/reconcile` | Hemdan + Tawila | `ReconciliationResult` from supplied or fallback data |
| `GET /api/report/{job_id}` | Tawila | PDF artifact |
| `GET /api/export/{job_id}` | Tawila | CSV audit artifact |

## Responsibilities And Outputs

| Member | Immediate Responsibility | Handoff |
|---|---|---|
| Hemdan | Freeze schemas and keep application bootable | API contract and endpoint smoke results |
| Tawila | Keep all money math deterministic and normalize real bank rows | Parser, FX fallback, matching tests, artifacts |
| Youssef | Make demo response legible and presentation-ready | Working UI and report/download actions |
| Shafey | Keep delivery materials accurate and tested | Deck, screenshots, timed demo script |

## Integration Checkpoints

Checkpoint 1:
- backend boots successfully
- /api/demo works

Checkpoint 2:
- frontend displays demo response

Checkpoint 3:
- matcher integrated
- named matched, needs-review, and unmatched cases covered by pytest

Checkpoint 4:
- PDF/export generation works
- bank CSV/XLSX export parsing and live-FX fallback covered by pytest

Checkpoint 5:
- final demo walkthrough stable

## Merge Strategy

1. This named-team handoff is published to `main`, then each owner branches from current `main`.
2. Owners commit small working changes and open pull requests into `main`.
3. Schema field changes are discussed before implementation and approved by Hemdan.
4. Each pull request must preserve demo mode and document any new environment variable.
5. Hemdan merges only after endpoint smoke checks; Shafey verifies README/demo wording after integration.

Merge order for the submission path:

1. Tawila: real bank-export parsing and live-FX fallback after merged case support.
2. Youssef: frontend case selector against the already merged result contract.
3. Hemdan: upload/provider orchestration only if the fallback path remains stable.
4. Shafey: final screenshots, demo script, and documentation polish.

## Pull Strategy

Before opening or updating a pull request:

```bash
git checkout main
git pull origin main
git checkout <your-branch>
git merge main
```

Resolve conflicts on the feature branch and re-run the affected checkpoint before pushing.

## Initial Branch Commands

```bash
git checkout main
git pull origin main
git checkout -b backend/extraction     # Hemdan
git checkout -b backend/matching main  # Tawila
git checkout -b frontend/dashboard main # Youssef
git checkout -b demo/docs main         # Shafey
```

Each teammate runs only the command for their assigned branch.

## Start Here Today

- Hemdan: pull `main`, create `backend/extraction`, keep `ReconciliationResult` stable, and review backend PRs.
- Tawila: continue Role 2 work on `backend/matching-real-data`, delivering CSV/XLSX normalization and live FX fallback without changing response fields.
- Youssef: pull `main`, create `frontend/dashboard`, and implement the case-selector UI against the merged named-case URLs.
- Shafey: pull `main`, create `demo/docs`, prepare slides/script and capture matched and needs-review screenshots.
- Team: merge only when demo mode works without API keys.

## Immediate Delivery Sequence

1. Everyone pulls current `main`; named demo cases are already available there.
2. Tawila delivers bank export parsing and live-FX fallback through a reviewed pull request.
3. Youssef consumes the merged named case endpoints in the dashboard in parallel.
4. Hemdan integrates file upload/Morpheus/Chutes orchestration while keeping all monetary calculations in code.
5. Shafey captures the verified matched and needs-review workflow for submission.
