# QA Lead take-home — generic Document Q&A Service

## Scenario

A B2B software team maintains an enterprise **document Q&A** feature. Users upload already-extracted text from ordinary operations reports, view documents for their workspace, and ask questions about orders completed or support-ticket counts. A deterministic simulator answers with structured facts and citations.

The application is functional enough to demonstrate, but **not necessarily correct**. Your job is to assess release readiness with evidence. You do **not** need to repair it.

**Recommended timebox:** 90–120 minutes maximum. Tool-assisted coding is allowed, including ChatGPT, Copilot and Claude Code, if you verify results and can explain decisions. Correctly failing tests are valuable.

## Setup

Python 3.10+ recommended (3.11+ preferred). From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Visit `/docs` for OpenAPI, `/demo` for a minimal browser interface. No real LLM, external API, paid tool or PDF parser is needed. You can use FastAPI `TestClient` and skip starting the server.

## Required deliverables

1. **QA_STRATEGY.md:** Top 8–10 test scenarios, P0/P1/P2, why your top three are highest risk, and test-layer choices (one page maximum).
2. **Automated tests:** At least 5 meaningful checks in `tests/`: include (a) upload → list → ask → verify, (b) tenant isolation, (c) correct year or metric selection, and (d) one negative-input or insufficient-evidence case. API-level E2E receives full credit; browser Playwright is optional.
3. **BUG_REPORTS.md:** At least 3 reproduced defects with severity, exact request/steps, expected and observed results, evidence, and hypothesis distinguished from observation.
4. **RELEASE_DECISION.md:** GO, CONDITIONAL GO or NO-GO, key user risks, PR gates, periodic regression strategy.
5. **AI_USAGE.md:** tools used, examples of AI-generated ideas/code you verified or rejected, and how you verified expected results. No AI use is also fine.

Keep tests deterministic and isolated. Explain gaps you didn't address. If editing product code, submit separately and show behavior before/after. Don't silently modify requirements to pass tests.

## Project boundaries

`X-Tenant-ID` is simulated identity only; do not treat it as production authorization. True SSO, live model calls, embedding search, OCR, streaming, async workers and load testing are outside this small starter implementation. The **contract in `REQUIREMENTS.md` takes precedence over observed implementation behavior**. Browser testing via `/demo` is optional.

## Submission

Send repository/ZIP including added tests, the four requested Markdown reports and short run instructions. Be ready for 20-minute review of priorities and any tests that failed.
