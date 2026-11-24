"""Synthetic enterprise document Q&A API for a QA Lead assessment."""
from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from . import rag, store

app = FastAPI(title="Atlas Document Q&A - QA assessment", version="0.2.0")

class UploadPayload(BaseModel):
    company: str
    filename: str
    fiscal_year: int
    page: int
    extracted_text: str

class AskPayload(BaseModel):
    question: str
    document_ids: list[str]

@app.get("/demo", include_in_schema=False)
def demo():
    return FileResponse(Path(__file__).with_name("demo.html"))

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/api/v1/documents")
def list_documents(x_tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    docs = store.list_for_tenant(x_tenant_id)
    return {"documents": [
        {"id": d["id"], "company": d["company"], "filename": d["filename"],
         "fiscal_year": d["fiscal_year"], "page": d["page"], "status": "complete"}
        for d in docs
    ]}

@app.post("/api/v1/documents", status_code=201)
def upload_document(payload: UploadPayload, x_tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    doc = store.create(x_tenant_id, payload.company, payload.filename,
                       payload.fiscal_year, payload.page, payload.extracted_text)
    return {"id": doc["id"], "filename": doc["filename"],
            "fiscal_year": doc["fiscal_year"], "status": "complete"}

@app.post("/api/v1/ask")
def ask(payload: AskPayload, x_tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    docs = []
    for doc_id in payload.document_ids:
        doc = store.fetch(doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail=f"Unknown document: {doc_id}")
        docs.append(doc)
    return rag.resolve_question(payload.question, docs)
