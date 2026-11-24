# Defect reports

## BUG-001: Ask returns another tenant's document data

Severity / release impact: **P0 — release blocker.** A request identified as Northstar can query a known foreign document ID and receive its metric and citation.

Preconditions and exact reproduction request:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":"How many orders were completed in FY2024?","document_ids":["beacon_fy24"]}
```

Expected: HTTP 403, with no foreign facts or source data in the response.

Actual: HTTP 200 with body:

```json
{"status":"success","answer":"orders completed were 7777 in FY2024.","facts":{"metric":"orders_completed","fiscal_year":2024,"value":7777,"baseline_year":null,"baseline_value":null,"change_pct":null},"citations":[{"document_id":"beacon_fy24","page":7}]}
```

Evidence (test ID / response / log): `test_CT02_tenant_list_and_ask_isolation` fails (200 received, expected 403); exact replay above. The list endpoint remains tenant-scoped, so list filtering does not prevent direct-ID disclosure.

Suspected component (hypothesis, not confirmed root cause): `/api/v1/ask` fetches by ID without checking the fetched document's `tenant_id` against `X-Tenant-ID`.

## BUG-002: Explicit requested year is ignored when it is not first

Severity / release impact: **P1 — incorrect business answer.** The service returns a valid-looking metric for the wrong year.

Preconditions and exact reproduction request:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":"How many orders were completed in FY2024?","document_ids":["atlas_fy23","atlas_fy24"]}
```

Expected: HTTP 200 success, `facts.fiscal_year=2024`, `facts.value=1200`, citation `atlas_fy24` page 14.

Actual: HTTP 200 with body:

```json
{"status":"success","answer":"orders completed were 1000 in FY2023.","facts":{"metric":"orders_completed","fiscal_year":2023,"value":1000,"baseline_year":null,"baseline_value":null,"change_pct":null},"citations":[{"document_id":"atlas_fy23","page":11}]}
```

Evidence (test ID / response / log): `test_CT03_explicit_year_ignores_document_order_and_returns_metric` fails because year 2023 is returned; exact replay above.

Suspected component (hypothesis, not confirmed root cause): single-year resolution chooses `docs[0]` whenever a year appears in the question rather than finding the selected document for that year.

## BUG-003: Comparison percentage divides by target value

Severity / release impact: **P1 — incorrect trend calculation.** The supplied example should report a 20% increase, but the result understates it.

Preconditions and exact reproduction request:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":"How did orders completed change from FY2023 to FY2024?","document_ids":["atlas_fy24","atlas_fy23"]}
```

Expected: baseline 1000, target 1200, and `(1200 - 1000) / 1000 * 100 = 20.00`.

Actual: HTTP 200 with body:

```json
{"status":"success","answer":"orders completed changed by +16.67% from FY2023 (1000) to FY2024 (1200).","facts":{"metric":"orders_completed","fiscal_year":2024,"value":1200,"baseline_year":2023,"baseline_value":1000,"change_pct":16.67},"citations":[{"document_id":"atlas_fy24","page":14}]}
```

Evidence (test ID / response / log): `test_CT05_comparison_uses_baseline_denominator` fails because `change_pct` is 16.67 rather than 20.00.

Suspected component (hypothesis, not confirmed root cause): comparison calculation uses the target value as the denominator.

## BUG-004: Comparison cites only one source document

Severity / release impact: **P1 — comparison is not fully auditable.** The response omits one document that supports the reported comparison.

Preconditions and exact reproduction request:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":"How did orders completed change from FY2023 to FY2024?","document_ids":["atlas_fy24","atlas_fy23"]}
```

Expected: HTTP 200 success with citations for both `atlas_fy23` page 11 and `atlas_fy24` page 14, independent of input order.

Actual: HTTP 200 with body:

```json
{"status":"success","answer":"orders completed changed by +16.67% from FY2023 (1000) to FY2024 (1200).","facts":{"metric":"orders_completed","fiscal_year":2024,"value":1200,"baseline_year":2023,"baseline_value":1000,"change_pct":16.67},"citations":[{"document_id":"atlas_fy24","page":14}]}
```

Evidence (test ID / response / log): `test_CT06_comparison_cites_both_documents_in_any_input_order` fails; only `atlas_fy24` is present in the actual citation list.

Suspected component (hypothesis, not confirmed root cause): comparison citation construction appears to use only the first selected document instead of both year-specific sources.

## BUG-005: Missing requested year falls back to another year

Severity / release impact: **P1 — unsupported answer.** Users may believe the requested year was present when it was not selected.

Preconditions and exact reproduction request:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":"How many orders were completed in FY2025?","document_ids":["atlas_fy24"]}
```

Expected: HTTP 200 `status=insufficient_evidence`, `facts=null`, `citations=[]`.

Actual: HTTP 200 with body:

```json
{"status":"success","answer":"orders completed were 1200 in FY2024.","facts":{"metric":"orders_completed","fiscal_year":2024,"value":1200,"baseline_year":null,"baseline_value":null,"change_pct":null},"citations":[{"document_id":"atlas_fy24","page":14}]}
```

Evidence (test ID / response / log): `test_CT07_missing_requested_year_is_insufficient_evidence` fails because it receives `success`; exact replay above.

Suspected component (hypothesis, not confirmed root cause): when the explicit year is not found, the resolver retains the first selected document rather than returning insufficient evidence.

## BUG-006: Invalid ask payloads are accepted

Severity / release impact: **P1 — input contract violation.** Blank questions and empty document ID arrays are processed instead of rejected.

Preconditions and exact reproduction requests:

```http
POST /api/v1/ask
X-Tenant-ID: northstar
Content-Type: application/json

{"question":" ","document_ids":["atlas_fy24"]}
```

Expected: HTTP 422 because the question must be nonblank. An empty `document_ids` array must also return HTTP 422.

Actual: blank ask returned HTTP 200 `{"status":"insufficient_evidence","answer":"Insufficient evidence in the selected documents.","facts":null,"citations":[]}`. Empty `document_ids` also returned HTTP 200 with the same insufficient-evidence body.

Evidence (test ID / response / log): `test_CT09_invalid_ask_payload_returns_422[payload0]` and `[payload1]` fail. Missing mandatory question (`payload2`) correctly returns 422.

Suspected component (hypothesis, not confirmed root cause): the ask payload model does not constrain question whitespace or require a nonempty ID array.

## BUG-007: Invalid upload metadata is accepted

Severity / release impact: **P1 — input contract violation.** Invalid source records can be stored and reported as complete.

Preconditions and exact reproduction request:

```http
POST /api/v1/documents
X-Tenant-ID: northstar
Content-Type: application/json

{"company":"Acme","filename":"f.txt","fiscal_year":2025,"page":0,"extracted_text":"text"}
```

Expected: HTTP 422 because page must be at least 1. The contract also requires nonempty company, filename, and extracted text, plus a plausible four-digit year.

Actual: HTTP 201 with body `{"id":"upload_0001","filename":"f.txt","fiscal_year":2025,"status":"complete"}`. Blank `company`, blank `extracted_text`, and fiscal year 99 each also returned HTTP 201 in parameterized reproductions.

Evidence (test ID / response / log): `test_CT10_invalid_upload_payload_returns_422[overrides0]` through `[overrides3]` fail. Missing mandatory filename (`overrides4`) correctly returns 422.

Suspected component (hypothesis, not confirmed root cause): the upload payload model declares basic types but does not constrain whitespace, minimum page, or plausible year range.
