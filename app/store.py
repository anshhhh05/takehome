"""Very small in-memory document store; reset for test isolation."""
from __future__ import annotations

import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "seed_documents.json"
_DOCS: dict[str, dict] = {}
_NEXT_ID = 1


def reset_store() -> None:
    global _DOCS, _NEXT_ID
    rows = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    _DOCS = {row["id"]: row for row in rows}
    _NEXT_ID = 1


def list_for_tenant(tenant_id: str) -> list[dict]:
    return [dict(d) for d in _DOCS.values() if d["tenant_id"] == tenant_id]


def fetch(document_id: str) -> dict | None:
    row = _DOCS.get(document_id)
    return dict(row) if row else None


def create(tenant_id: str, company: str, filename: str, fiscal_year: int, page: int, extracted_text: str) -> dict:
    global _NEXT_ID
    doc_id = f"upload_{_NEXT_ID:04d}"
    _NEXT_ID += 1
    record = {
        "id": doc_id,
        "tenant_id": tenant_id,
        "company": company,
        "filename": filename,
        "fiscal_year": fiscal_year,
        "page": page,
        "extracted_text": extracted_text,
    }
    _DOCS[doc_id] = record
    return dict(record)


reset_store()
