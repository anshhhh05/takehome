# QA strategy (max one page)

## Top risk areas

| Rank | Scenario | Priority P0/P1/P2 | Why it matters | Test layer |
|---|---|---|---|---|
| 1 | Foreign document is denied in ask; no data leaks | P0 | Confidentiality | API / TestClient |
| 2 | Tenant listing is isolated | P0 | Workspace privacy | API / TestClient |
| 3 | Explicit year, missing year, and no-year latest selection | P1 | Prevents wrong or unsupported numbers | API / TestClient |
| 4 | Comparison math and both citations, either input order | P1 | Correct, auditable trends | API / TestClient |
| 5 | Upload → list → ask returns the uploaded result | P1 | Core workflow | API / TestClient |
| 6 | Invalid ask/upload payloads return 422 | P1 | Rejects malformed data | API validation |
| 7 | Unknown ID returns 404; absent metric evidence is insufficient | P1 | Prevents invented evidence | API negative cases |
| 8 | Orders and tickets remain distinct metrics | P1 | Avoids mixing measures | API / TestClient |
| 9 | Health endpoint returns expected status | P2 | Basic availability signal | API smoke |

The top three protect customer data and prevent plausible but incorrect answers. These are API tests because the contract is expressed in HTTP status codes and JSON; TestClient makes them fast and deterministic without browser timing or UI flakiness.

## CI / release split

PR / merge: run deterministic pytest API tests for isolation, validation, selection, calculations, citations, and the upload flow. Reset fixtures between tests.

Pre-release: rerun the suite against the release candidate and manually check `/demo` if UI code changes. This simulator does not establish production identity, storage, or RAG quality.

Deliberately not automated: browser flow, production SSO, live model behavior, load, OCR, and persistence across restarts; these are outside the starter app and contract.
