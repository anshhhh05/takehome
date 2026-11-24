# Acceptance contract — synthetic Document Q&A Service

## Intended behavior

1. `GET /health` returns 200 and `{"status":"ok"}`.
2. `GET /api/v1/documents` shows only the requesting tenant's documents. `X-Tenant-ID` is a simplified test identity.
3. `POST /api/v1/documents` accepts JSON with nonempty `company`, `filename`, `extracted_text`, plausible four-digit `fiscal_year`, `page >= 1`; return 201 with unique ID, `status: "complete"`, and metadata. Uploaded data is immediately listable/queryable by the same tenant.
4. `POST /api/v1/ask` requires a nonblank `question` and nonempty `document_ids`. It may read evidence **only from selected IDs** and must never return another tenant's data. Unauthorized selected ID → **403**, no leaked facts; unknown ID → **404**.
5. Single-year question uses its explicit year regardless of document order; absent year uses the latest selected year. Supported metrics are **orders completed** (`orders_completed`) and **support tickets received** (`support_tickets`). Different metrics must not be mixed.
6. Comparison `% change = (target − baseline) / baseline × 100`, rounded to two decimals. Both years must exist; answers must cite **both source documents/pages**, independent of input order.
7. Successful request returns `status: "success"`, answer text, structured facts (see example), and correct citations. Assert structured values/citations rather than exact response wording.
8. Missing source for requested year/metric → HTTP 200 `status: "insufficient_evidence"`, `facts: null`, `citations: []`. Do not invent numbers from other years or tenants.
9. Invalid payloads (blank question/text, missing mandatory fields, empty ID array, wrong types, page < 1) → 422. Errors must not leak secrets, raw source text from other tenants, or stack traces.
10. Upload/list/ask works as a complete flow; tests are isolated and repeatable.

## Example

**Request** (`X-Tenant-ID: northstar`):

```json
{"question":"How many orders were completed in FY2024?","document_ids":["atlas_fy23","atlas_fy24"]}
```

**Expected response**:

```json
{
  "status":"success",
  "answer":"orders completed were 1200 in FY2024.",
  "facts":{"metric":"orders_completed","fiscal_year":2024,"value":1200,
           "baseline_year":null,"baseline_value":null,"change_pct":null},
  "citations":[{"document_id":"atlas_fy24","page":14}]
}
```

**Known reference data**:

| Metric | FY2023 | FY2024 | Change |
|---|---:|---:|---:|
| Orders completed | 1,000 | 1,200 | +20.00% |
| Support tickets received | 2,400 | 2,100 | −12.50% |

## Supported question forms for this toy simulator

- `How many orders were completed in FY2024?`
- `How many support tickets were received in FY2024?`
- `How did orders completed change from FY2023 to FY2024?`
- `How did support tickets change from FY2023 to FY2024?`

This is a deterministic simulator, **not** a real natural-language model. Testing real RAG infrastructure would require different components and data.

## Optional UI

`/demo` supports selecting workspace, listing/uploading documents, and sending a question. A Playwright flow is optional. API E2E is sufficient for full credit. Production authentication, OCR, real retrieval embeddings, model streaming, caching and rate limiting are not in scope.
