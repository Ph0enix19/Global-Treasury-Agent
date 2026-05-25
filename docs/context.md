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
- The React dashboard consumes `/api/demo` and exposes PDF/CSV download actions.
- README setup instructions and the architecture diagram are committed.

Immediate branch work:

| Member | In Progress Next | Expected Handoff |
|---|---|---|
| Hemdan | Provider/orchestration integration and API stability review | Approve contract-sensitive PRs and verify routes after merge |
| Tawila | Three deterministic demo outcomes plus pytest proof | `/api/demo?case=...`, calculation traces, and generated artifacts |
| Youssef | Demo-case switcher after Tawila merges | UI showing matched, needs review, and unmatched results |
| Shafey | Submission deck, script, screenshots, and QA | Verified demo narrative and final delivery assets |

## API Contract Ownership

Hemdan owns [backend/app/models/schemas.py](../backend/app/models/schemas.py) and approves
contract changes before merge. Tawila implements deterministic values within that contract.
Youssef consumes the contract and must not create alternate result field names. Shafey
documents only behavior confirmed against demo mode.

Both `GET /api/demo` and `POST /api/reconcile` return one `ReconciliationResult` shape:

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
| `POST /api/reconcile` | Hemdan + Tawila | `ReconciliationResult` from supplied or fallback data |
| `GET /api/report/{job_id}` | Tawila | PDF artifact |
| `GET /api/export/{job_id}` | Tawila | CSV audit artifact |

## Responsibilities And Outputs

| Member | Immediate Responsibility | Handoff |
|---|---|---|
| Hemdan | Freeze schemas and keep application bootable | API contract and endpoint smoke results |
| Tawila | Keep all money math deterministic and traceable | Demo fixtures, matching tests, artifacts |
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

Checkpoint 5:
- final demo walkthrough stable

## Merge Strategy

1. This named-team handoff is published to `main`, then each owner branches from current `main`.
2. Owners commit small working changes and open pull requests into `main`.
3. Schema field changes are discussed before implementation and approved by Hemdan.
4. Each pull request must preserve demo mode and document any new environment variable.
5. Hemdan merges only after endpoint smoke checks; Shafey verifies README/demo wording after integration.

Merge order for the submission path:

1. Tawila: deterministic cases, artifact reliability, and tests.
2. Youssef: frontend case selector against the unchanged result contract.
3. Hemdan: provider/orchestration additions only if the fallback path remains stable.
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
- Tawila: pull `main`, create `backend/matching`, add `matched`, `needs_review`, and `unmatched` deterministic cases with pytest coverage.
- Youssef: pull `main`, create `frontend/dashboard`, preserve current rendering and prepare the case-selector UI against Tawila's merged URLs.
- Shafey: pull `main`, create `demo/docs`, prepare slides/script now and capture screenshots after named cases merge.
- Team: merge only when demo mode works without API keys.

## Immediate Delivery Sequence

1. Everyone pulls this handoff baseline from `main` and creates only their owned branch.
2. Tawila delivers deterministic case hardening and tests through a pull request.
3. Youssef consumes the named case endpoint in the dashboard after that merge.
4. Hemdan integrates Morpheus/Chutes work while keeping all monetary calculations in code.
5. Shafey captures the verified matched and needs-review workflow for submission.
