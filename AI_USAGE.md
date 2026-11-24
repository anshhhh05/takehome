# AI / coding tool use

**Tools used:** Claude chat helped plan the QA approach and draft an initial test file. Codex was used to inspect the contract and app, produce and run the final tests, replay requests, and draft the reports. Claude Code was not used.

**Accepted and validated:** The test areas covered tenant ownership, explicit and missing years, comparison math and citations, payload validation, insufficient evidence, and unknown IDs. I checked expected behavior against `REQUIREMENTS.md` and checked values against the seed data; for example, 1000 → 1200 is +20.00% using the baseline denominator. I reported suspected defects only after a test or replay reproduced them.

**Rejected or corrected:** No AI suggestion was rejected. I added checks for no-year/latest selection and unknown IDs as contract coverage; both passed, so they were not reported as defects. Review feedback prompted a separate comparison-citation test and defect report because the response cites only one of the two sources. No app code or requirements were modified.

**How expectations were checked:** I compared assertions to the acceptance contract, hand-checked the reference calculation, and ran pytest. Current result: 10 passed and 11 failed, including parameterized cases. `BUG_REPORTS.md` contains exact replay requests and representative actual responses.
