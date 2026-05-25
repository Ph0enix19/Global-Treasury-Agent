# Treasury AI Reconciliation Agent: Team Handoff And Demo Rescue Plan

**Status date:** May 26, 2026 (MYT)
**Team:** Hemdan, Tawila, Youssef, Shafey
**Immediate objective:** Turn a stable technical proof into a convincing treasury demo.

## Executive Message

We have a working deterministic reconciliation pipeline, but we should not describe the
current demo as a complete treasury solution yet. It proves one invoice flow and three
matching outcomes, while all three outcomes currently reuse the same invoice
(`INV-2026-0412`).

The right rescue move is **not** to spend time searching Kaggle for an unrelated large
dataset. We need a small, controlled, realistic reconciliation portfolio that can be
explained confidently during judging:

- Five or six synthetic but realistic invoices across USD, SGD, and EUR.
- Corresponding payment-proof records and one consolidated MYR bank statement.
- Clear examples of matched, needs-review, and unmatched decisions.
- PDF/CSV evidence for selected cases.
- Offline fallback as the reliable demo path, with live FX as an optional integration proof.

This is achievable quickly because the calculation engine, API response contract,
artifact generation, and initial frontend already exist.

## Current Repository Status

| Area | Status Today | Evidence |
|---|---|---|
| FastAPI backend | Working | `/api/health`, `/api/demo`, `/api/reconcile`, artifact routes |
| Response contract | Frozen and working | `ReconciliationResult` used by demo and reconcile |
| Matching decisions | Working | `matched`, `needs_review`, `unmatched` named backend cases |
| FX and bank fees | Working deterministically | FX trace and fee trace in every result |
| PDF/CSV artifacts | Working | Report and audit downloads for named cases |
| Bank import parser | Completed in Role 2 PR | CSV/XLSX parsing into `BankStatementRow` values |
| Live FX with fallback | Completed in Role 2 PR | Dated Frankfurter lookup plus local fallback |
| Frontend dashboard | Working for default case | Displays `/api/demo` matched result and downloads |
| Frontend case switcher | Not implemented yet | Youssef task |
| Uploaded-file orchestration | Not implemented yet | Hemdan task |
| Real Morpheus/Chutes calls | Placeholder only | Optional if stable before submission |

## GitHub Integration Status

| Pull Request | State | What It Contains |
|---|---|---|
| PR #1: deterministic demo cases | Merged to `main` | Named outcome endpoints and initial Role 2 tests |
| PR #2: real bank statements and FX fallback | Open for review | CSV/XLSX parser, live FX fallback, safer supplied-input handling, expanded tests |

PR #2: <https://github.com/AliTawila/treasury_hackathon/pull/2>

## What Works In The Demo Right Now

The backend can currently demonstrate:

| Backend Call | Result |
|---|---|
| `GET /api/demo?case=matched` | Exact payment match with high confidence |
| `GET /api/demo?case=needs_review` | Same reference/date with amount discrepancy |
| `GET /api/demo?case=unmatched` | No credible bank candidate |
| `GET /api/report/{job_id}` | Downloadable reconciliation PDF |
| `GET /api/export/{job_id}` | Downloadable audit CSV |
| `POST /api/reconcile` | Structured invoice/payment/bank-row reconciliation |

Verified Role 2 behavior:

- `20` backend tests pass.
- Frontend production build succeeds.
- All three named outcomes produce PDF and CSV artifacts.
- A valid submitted bank-row result matches correctly.
- Unsupported real FX inputs return a clear error instead of a fake successful demo result.
- Live dated FX can be used when configured; local stored rates preserve offline reliability.

## The Main Weakness

Today the application changes bank rows to show three statuses, but it does not yet
show multiple actual invoice journeys. A judge may reasonably ask:

- Can it reconcile a portfolio rather than one hardcoded invoice?
- Can it handle more than one currency?
- What happens with delayed credits, missing references, fee variances, or duplicates?
- Can a user upload a bank statement, or is all input preloaded?
- Where does AI participate, beyond a mocked explanation boundary?

We should answer those questions with a small scenario portfolio and a crisp scope
statement, rather than trying to claim broad production readiness.

## Decision: Do Not Wait For Kaggle

No Kaggle dataset is required for the MVP demo. A Kaggle download is likely to create
format-cleaning work without guaranteeing invoice, remittance, FX, and bank-credit
relationships that fit our reconciliation story.

Use a declared synthetic demo portfolio instead:

- It contains no confidential customer data.
- Every amount can be validated manually.
- The expected outcome for each case is defensible.
- It can be stored locally and demonstrated without internet.
- It gives the frontend a better story than one golden invoice.

If a teammate already has an anonymized bank CSV/XLSX export, use it as an additional
parser proof, not as a dependency for submission.

## Minimum Convincing Demo Portfolio

The next Role 2 increment should add at least five invoice scenarios. Keep the shared
response contract unchanged and expose each scenario as a deterministic demo selection.

| Scenario ID | Business Story | Currency | Expected Status | Judge Value |
|---|---|---:|---|---|
| `matched_usd_wire` | Existing invoice paid exactly after FX and incoming-wire fee | USD | `matched` | Establishes the golden path |
| `matched_sgd_wire` | Second customer payment converts from SGD into MYR correctly | SGD | `matched` | Proves multi-currency behavior |
| `review_fee_variance` | Reference/date match, but received amount differs from expected fee outcome | EUR or SGD | `needs_review` | Shows exception handling |
| `review_missing_reference` | Amount and date are plausible, but bank narrative lacks invoice reference | USD | `needs_review` | Shows traceable uncertainty |
| `unmatched_missing_credit` | Invoice/payment proof exists, but no credible bank credit appears | EUR | `unmatched` | Shows control and escalation |

Useful stretch case after the five above:

| Scenario ID | Business Story | Expected Behavior |
|---|---|---|
| `review_duplicate_candidates` | Two similar incoming bank credits could match one invoice | Flag manual review rather than auto-match |

The duplicate-candidate case requires matcher enhancement and should not delay the
minimum five-scenario portfolio.

## Required Demo Data Assets

For each scenario, prepare:

| Asset | Purpose |
|---|---|
| Invoice fixture | Supplier/customer, invoice number, original currency, amount, date |
| Payment proof fixture | Sender, transfer reference, amount sent, currency, payment date |
| Bank row or consolidated bank statement | MYR credit used by the matcher |
| Expected calculation note | FX rate, fee rule, expected MYR credit, expected status |

Recommended structure:

```text
data/demo/portfolio/
|-- invoices/
|-- payments/
|-- statements/
|-- expected_results/
`-- portfolio_cases.json
```

For submission, say clearly that these are **synthetic treasury test transactions**
created to demonstrate deterministic reconciliation safely.

## Demo Narrative Worth Showing

A strong three-minute walkthrough can be:

1. Open the dashboard and explain: AI extracts/explains; code performs money decisions.
2. Run `matched_usd_wire` and show FX, fees, confidence, and report download.
3. Switch to `review_fee_variance` and show why human review is required.
4. Switch to `unmatched_missing_credit` and show that the system refuses to fabricate a match.
5. Download one PDF report and one CSV audit record.
6. Briefly show the offline fallback guarantee and mention that live FX is available when configured.

That story is more credible than trying to demo many incomplete integrations.

## Work Plan By Role

### Tawila: Role 2, Data And Deterministic Logic

Must deliver next:

- Expand demo fixtures from one invoice to at least five portfolio scenarios.
- Add USD, SGD, and EUR examples using traceable stored dated FX rates.
- Keep fee calculations, thresholds, statuses, and report values deterministic.
- Add tests covering each portfolio scenario and every expected outcome.
- Keep PDF/CSV generation working per selected case.
- Merge PR #2 after Hemdan reviews the real-input safety behavior.

Do not spend time on:

- Large external dataset ingestion.
- Machine-learning matching.
- Complex duplicate handling before the five-case portfolio works.

### Hemdan: Role 1, Orchestration And Provider Boundary

Must deliver next:

- Review and merge PR #2 if the response contract and `422` behavior are acceptable.
- Add a bank-statement upload route or orchestration flow that calls
  `parse_bank_statement(path)` for CSV/XLSX inputs.
- Preserve deterministic money logic in Role 2 services.
- Connect real Morpheus/Chutes only if it does not put the offline demo at risk.

### Youssef: Role 3, Dashboard

Must deliver next:

- Add a scenario selector to the UI.
- Call `/api/demo?case=...` and render the unchanged response model.
- Keep PDF/CSV download buttons visible for every selected scenario.
- Make statuses visually clear: Matched, Needs Review, Unmatched.

Youssef can begin now using the already merged three status endpoints, then add the
larger portfolio case labels after the Role 2 fixture expansion lands.

### Shafey: Role 4, Submission And QA

Must deliver next:

- Create a short demo script centered on one success and two control exceptions.
- Capture screenshots after the selector and expanded portfolio are merged.
- Document that synthetic transactions are used for privacy-safe demonstration.
- Rehearse offline mode and maintain a screenshot/video fallback.

## Stable Interface For Parallel Work

Do not change the fields in `ReconciliationResult` during the rescue sprint:

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

Youssef can safely build against that result shape. Hemdan owns approval for any later
schema change.

## Acceptance Checklist Before Submission

| Requirement | Owner | Done When |
|---|---|---|
| PR #2 reviewed and merged | Hemdan + Tawila | Parser/live-FX changes are on `main` |
| Five-scenario portfolio fixtures | Tawila | At least five distinct invoices return expected decisions |
| Multi-currency proof | Tawila | USD, SGD, and EUR results show correct MYR traces |
| Scenario selector | Youssef | Judge can switch scenarios in the dashboard |
| Upload demonstration or honest scope statement | Hemdan | Upload works, or team clearly presents preloaded scenario mode |
| Reports and audit exports | Tawila + Youssef | PDF/CSV download works from UI for demo cases |
| Submission script and evidence | Shafey | Screenshots/slides/video reflect verified behavior |
| Offline rehearsal | Entire team | Demo runs with no provider keys and no internet |

## Recommended Merge Order From Here

1. Hemdan reviews and merges PR #2.
2. Tawila adds the five-scenario portfolio and tests in a small follow-up PR.
3. Youssef merges the selector UI against stable named scenarios.
4. Hemdan merges upload/provider improvements only if they are stable.
5. Shafey finalizes slides, screenshots, and demo recording from merged `main`.

## Message To Send The Team

> Current status: the backend pipeline is stable and already proves matched,
> needs-review, unmatched, PDF report, CSV audit, and deterministic FX/fee reasoning.
> Our honest gap is that the present cases reuse one invoice. We should not waste time
> searching Kaggle. We will build a five-scenario synthetic treasury portfolio across
> USD, SGD, and EUR, expose it through the unchanged API result shape, and let the UI
> switch between success and exception stories. Hemdan reviews/merges the Role 2
> real-data PR and wires uploads if time permits; Youssef builds the selector; Shafey
> prepares the judged walkthrough and offline evidence.

## Bottom Line

The current project is a valid technical foundation, not a finished judging story.
It becomes hackathon-worthy when we show a small but credible multi-invoice portfolio,
visible reasoning for exceptions, reliable downloads, and a demo that remains stable
offline. That is a focused expansion of what is already built, not a rewrite.
