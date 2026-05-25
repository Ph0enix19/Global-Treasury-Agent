# Copy-Paste Prompt For Teammate Codex Sessions

Send the prompt below to each teammate. Before pasting it, replace only the
`MY_IDENTITY` line with one of:

- `MY_IDENTITY: Hemdan / Role 1 / backend/extraction`
- `MY_IDENTITY: Youssef / Role 3 / frontend/dashboard`
- `MY_IDENTITY: Shafey / Role 4 / demo/docs`

Tawila continues Role 2 work separately on the matching/data pipeline.

```text
MY_IDENTITY: [REPLACE THIS WITH MY NAME / ROLE / BRANCH FROM THE LIST ABOVE]

You are joining an in-progress hackathon repository as my coding agent. Work actively
inside my local clone and continue the project from its current state. Do not just
give me a plan unless a blocker makes implementation impossible.

PROJECT
-------
Project name: Treasury AI Reconciliation Agent
Hackathon: AI Marathon 2026, Global Treasury Agent track
Team:
- Role 1: Hemdan, branch `backend/extraction`
- Role 2: Tawila, branch `backend/matching` / current follow-up branch
  `backend/matching-real-data`
- Role 3: Youssef, branch `frontend/dashboard`
- Role 4: Shafey, branch `demo/docs`

Core product purpose:
Reconcile invoice data, payment proof data, and MYR bank-statement rows for
cross-border payments. The system converts FX, applies bank fees, scores a likely
bank match, explains the result, and generates auditable report/export artifacts.

NON-NEGOTIABLE TRUST RULE
-------------------------
AI may extract structured fields and explain an already-calculated outcome.
Deterministic Python code must calculate all FX conversions, bank fees, match
confidence, status decisions, and monetary values shown in reports or the UI.
Never move financial logic into an LLM/provider response.

DEMO SAFETY RULE
----------------
The application must remain demonstrable offline with `DEMO_MODE=true`, no API keys,
and no internet. Live-provider work is optional unless it is stable and preserves
fallback behavior. Do not remove deterministic fixtures or emergency demo behavior.
For explicitly submitted real financial inputs, do not fabricate a successful result
when a trustworthy calculation cannot be made.

FIRST: READ AND VERIFY BEFORE EDITING
-------------------------------------
1. Locate the repository root, expected to be named `treasury_hackathon`.
2. Read these files before making decisions:
   - `docs/context.md`
   - `docs/team_handoff_demo_rescue_plan.md`
   - `README.md`
   - `backend/app/models/schemas.py`
   - Relevant files for my role listed below.
3. Inspect the working tree and do not discard any existing teammate changes:
   - `git status --short --branch`
   - `git remote -v`
   - `git log --oneline --decorate --max-count=8 --all`
4. Fetch and verify GitHub integration state if network/auth is available:
   - `git fetch origin`
   - `gh pr list --state all --limit 20`
5. Report briefly what is already present, what branch I am on, and the concrete
   change you will make for my role. Then implement it.

KNOWN STATUS AT HANDOFF TIME
----------------------------
This status was verified on May 26, 2026 (MYT). Re-check it before coding because it
may have changed after this prompt was sent.

- `main` contains the baseline FastAPI/React scaffold and merged PR #1:
  deterministic named backend demo cases.
- PR #1 is merged:
  `https://github.com/AliTawila/treasury_hackathon/pull/1`
- PR #2 is currently open from `backend/matching-real-data` into `main`:
  `https://github.com/AliTawila/treasury_hackathon/pull/2`
- PR #2 contains Tawila's Role 2 work:
  - CSV/XLSX bank statement parsing via `parse_bank_statement(path)`
  - live dated FX retrieval with local fallback
  - rejection of unsupported supplied real-input FX rather than fake demo success
  - expanded tests; verified result was `20 passed`
  - `docs/team_handoff_demo_rescue_plan.md`
- The running/default frontend currently displays the default matched demo only.
  It does not yet expose a scenario selector.
- Current backend cases on merged `main` are `matched`, `needs_review`, and
  `unmatched`, but they reuse the same invoice. This proves status behavior, not a
  convincing portfolio.

CURRENT WORKING FUNCTIONALITY
-----------------------------
Already implemented in the project baseline:
- FastAPI app with CORS and modular routers.
- React/Vite dashboard that calls default `GET /api/demo`.
- `GET /api/health`.
- `GET /api/demo` default matched result.
- `GET /api/demo?case=matched|needs_review|unmatched`.
- `POST /api/reconcile` for structured reconciliation data.
- `GET /api/report/{job_id}` for PDF report downloads.
- `GET /api/export/{job_id}` for CSV audit exports.
- Deterministic FX trace, fee trace, matching score, status, explanation boundary,
  and artifact generation.
- Offline fixtures and deterministic fallback behavior.

Stable result contract:
`GET /api/demo` and `POST /api/reconcile` return the same
`ReconciliationResult` shape. Do not add, remove, or rename fields without Hemdan's
explicit schema approval:

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

IMPORTANT PRODUCT GAP AND RESCUE DIRECTION
------------------------------------------
The current three result statuses all reuse one invoice (`INV-2026-0412`). That is a
valid plumbing demonstration, but not yet a persuasive treasury portfolio.

The agreed rescue direction is:
- Do not block on Kaggle or a large external dataset.
- Use five or six clearly labeled synthetic, privacy-safe treasury scenarios.
- Demonstrate USD, SGD, and EUR payments converted to MYR.
- Include matched, needs-review, and unmatched business stories.
- Keep deterministic calculations and offline reliability.
- Make the UI able to switch through the scenarios once available.

Target scenario portfolio being built by Tawila / Role 2:
- `matched_usd_wire`: exact incoming-wire payment after FX and fee.
- `matched_sgd_wire`: successful SGD-to-MYR payment.
- `review_fee_variance`: correct reference/date but fee/amount discrepancy.
- `review_missing_reference`: plausible amount/date but weak narrative reference.
- `unmatched_missing_credit`: no credible bank credit.
- Optional stretch: `review_duplicate_candidates`.

Do not independently modify Role 2 fixture/scoring logic unless Tawila specifically
asks you to resolve an integration conflict.

BRANCH AND MERGE DISCIPLINE
---------------------------
- Work only on my assigned branch, not directly on `main`.
- Do not delete or overwrite changes belonging to another teammate.
- Before coding, update from the latest available integration baseline appropriate for
  my dependency.
- Commit coherent changes and push my branch.
- Open a pull request into `main`; Hemdan reviews contract-sensitive changes.
- Keep the shared result contract intact.

If my branch already exists locally or remotely, inspect it and continue it rather
than blindly recreating it.

ROLE-SPECIFIC INSTRUCTIONS
--------------------------
Read MY_IDENTITY above and execute only the matching role section.

IF I AM HEMDAN / ROLE 1 / `backend/extraction`:
Ownership:
- FastAPI orchestration.
- Morpheus/Chutes provider boundaries.
- Schema approval and backend integration review.

Files to inspect first:
- `backend/app/main.py`
- `backend/app/models/schemas.py`
- `backend/app/routers/reconcile.py`
- `backend/app/routers/demo.py`
- `backend/app/services/morpheus_extractor.py`
- `backend/app/services/chutes_agent.py`
- From PR #2 after merge or local inspection:
  `backend/app/services/bank_statement_parser.py`

Immediate deliverables:
1. Review PR #2 before depending on `parse_bank_statement(path)`.
2. If acceptable, coordinate/merge PR #2 into `main`.
3. Implement a simple bank statement upload/orchestration path for CSV/XLSX input
   that uses Role 2's parser and submits normalized `BankStatementRow` values into
   the existing deterministic reconciliation pipeline.
4. Keep existing JSON reconciliation route and demo routes working.
5. Preserve offline fallback behavior.
6. Only attempt real Morpheus/Chutes provider calls if configuration is present and
   failures safely fall back without breaking the judged walkthrough.

Acceptance criteria:
- Backend starts in `DEMO_MODE=true` without API keys.
- Existing health/demo/reconcile/report/export paths still work.
- A provided CSV/XLSX bank statement can be normalized and reconciled.
- No API response contract break.
- Tests cover the added orchestration behavior.

IF I AM YOUSSEF / ROLE 3 / `frontend/dashboard`:
Ownership:
- React dashboard and API calls.
- Scenario selection UI.
- Clear reconciliation result presentation and download actions.

Files to inspect first:
- `frontend/src/App.jsx`
- `frontend/src/lib/api.js`
- `frontend/src/styles.css`
- `backend/app/routers/demo.py`
- `backend/app/models/schemas.py`

Immediate deliverables:
1. Implement a visible scenario selector for backend cases.
2. Start with merged endpoint values currently on `main`:
   `matched`, `needs_review`, `unmatched`.
3. Design it so new portfolio IDs from Tawila can be added in one small constant/list
   once that follow-up PR merges.
4. Update `getDemoResult` to request `/api/demo?case=<selected-case>`.
5. Preserve existing cards, explanation, raw response display, PDF button, and CSV
   button for every selected result.
6. Display loading/error state clearly and visually distinguish each status.

Acceptance criteria:
- Selecting each existing case retrieves and renders the appropriate result.
- The status visibly changes between Matched, Needs Review, and Unmatched.
- Artifact download links follow the returned `job_id`.
- `npm run build` passes.
- Do not invent new result fields or require PR #2 for the initial selector.

IF I AM SHAFEY / ROLE 4 / `demo/docs`:
Ownership:
- README/deck/demo script/screenshots/QA/submission narrative.

Files to inspect first:
- `README.md`
- `docs/context.md`
- `docs/team_handoff_demo_rescue_plan.md`
- `docs/architecture_diagram.png`
- Backend routes and frontend UI only as needed to verify claims.

Immediate deliverables:
1. Prepare a concise three-minute demo script using the stable functionality:
   one matched case, one needs-review case, one unmatched case, and one artifact
   download.
2. Prepare documentation/slides that honestly state current limitations:
   synthetic data, deterministic calculations, AI extraction/explanation boundary,
   and upload/provider integration status.
3. After Youssef's selector and Tawila's portfolio are merged, capture verified
   screenshots for success and exception cases.
4. Create an offline-demo QA checklist and a fallback recording/screenshot plan.
5. Do not claim functionality you cannot verify in the running app.

Acceptance criteria:
- All presentation claims map to routes/UI behavior that exists on merged `main`.
- Submission explains why synthetic portfolio data is appropriate and safe.
- Demo script works with `DEMO_MODE=true` and no internet.
- Screenshots and docs are updated after feature merges, not before.

VALIDATION EXPECTATIONS FOR ANY ROLE
------------------------------------
Run checks appropriate to your edited surface before opening a PR:

Backend changes:
  cd backend
  source .venv/bin/activate
  pytest -q

Frontend changes:
  cd frontend
  npm install
  npm run build

Documentation/demo changes:
- Verify described routes and visible UI against the current merged implementation.
- Do not state PR #2 functionality is in `main` unless you verify it was merged.

Backend smoke commands when applicable:
  curl http://localhost:8000/api/health
  curl 'http://localhost:8000/api/demo?case=matched'
  curl 'http://localhost:8000/api/demo?case=needs_review'
  curl 'http://localhost:8000/api/demo?case=unmatched'

HOW TO REPORT BACK TO ME
------------------------
After inspecting, tell me:
- Current branch and whether it is up to date with the intended base.
- Current PR/merge state relevant to my work.
- What you will implement for my role.

After implementing, tell me:
- Files changed and behavior added.
- Commands/tests run and their outcomes.
- Branch pushed and PR URL, if created.
- Any dependency on Tawila/Hemdan/Youssef/Shafey before final integration.

Start now by reading the repository documentation and checking git/PR state, then
implement the next deliverable for MY_IDENTITY.
```
