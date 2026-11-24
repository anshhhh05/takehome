# Release decision

Recommendation (GO / CONDITIONAL GO / NO-GO): **NO-GO** for any release handling tenant data.

Three most consequential risks and why:

1. **Cross-tenant disclosure (P0):** `/ask` returns Beacon's confidential metric to Northstar when given the foreign document ID.
2. **Wrong-year answers (P1):** an explicit year may return the first document's year, and a missing requested year can return another year's data as success.
3. **Incorrect, unauditable comparisons (P1):** percentage uses the wrong denominator and the result cites only one source document.

Required fixes before release: enforce tenant ownership before reading selected IDs; select the exact requested year or return insufficient evidence; compute percentage against baseline and cite both documents; validate nonblank strings, required values, nonempty ID arrays, plausible year, and page >= 1. Rerun the contract suite after fixes.

PR/merge regression gate: deterministic pytest suite, including all contract tests and existing smoke tests; no failures on protected tenant, answer correctness, citations, or payload validation.

Pre-release regression gate: full suite against release candidate, verify representative upload/list/ask flow and OpenAPI payload behavior. Validate security with real authentication and data store separately before production because the supplied tenant header is only a test identity.

Residual risks / open questions: in-memory storage and simulated identity do not represent production persistence or authorization. The toy parser supports only documented question forms and simple metric phrases; no claims are made about real LLM/RAG quality, OCR, load, or concurrency.
