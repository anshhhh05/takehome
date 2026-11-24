"""Acceptance-contract tests for the Document Q&A API (not implementation tests)."""

import pytest


def upload(client, headers, year=2025):
    return client.post("/api/v1/documents", headers=headers, json={
        "company": "Atlas Commerce", "filename": f"FY{year}.txt",
        "fiscal_year": year, "page": 4,
        "extracted_text": f"FY{year}. Orders completed: 1100. Support tickets received: 2000.",
    })


def test_CT01_upload_list_ask_verify_flow(client, tenant_headers):
    created = upload(client, tenant_headers)
    assert created.status_code == 201
    doc_id = created.json()["id"]
    listing = client.get("/api/v1/documents", headers=tenant_headers)
    assert listing.status_code == 200
    assert doc_id in {row["id"] for row in listing.json()["documents"]}
    answer = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many orders were completed in FY2025?",
        "document_ids": [doc_id],
    })
    assert answer.status_code == 200
    result = answer.json()
    assert result["status"] == "success"
    assert result["facts"] == {
        "metric": "orders_completed", "fiscal_year": 2025, "value": 1100,
        "baseline_year": None, "baseline_value": None, "change_pct": None,
    }
    assert result["citations"] == [{"document_id": doc_id, "page": 4}]


def test_CT02_tenant_list_and_ask_isolation(client, tenant_headers):
    listed = client.get("/api/v1/documents", headers=tenant_headers).json()["documents"]
    assert "beacon_fy24" not in {row["id"] for row in listed}
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many orders were completed in FY2024?",
        "document_ids": ["beacon_fy24"],
    })
    assert response.status_code == 403
    assert "7777" not in response.text
    assert "Beacon" not in response.text


def test_CT03_explicit_year_ignores_document_order_and_returns_metric(client, tenant_headers):
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many orders were completed in FY2024?",
        "document_ids": ["atlas_fy23", "atlas_fy24"],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["facts"]["fiscal_year"] == 2024
    assert body["facts"]["value"] == 1200
    assert body["facts"]["metric"] == "orders_completed"
    assert body["citations"] == [{"document_id": "atlas_fy24", "page": 14}]


def test_CT04_no_year_uses_latest_selected_document(client, tenant_headers):
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many support tickets were received?",
        "document_ids": ["atlas_fy23", "atlas_fy24"],
    })
    body = response.json()
    assert body["status"] == "success"
    assert body["facts"]["metric"] == "support_tickets"
    assert body["facts"]["fiscal_year"] == 2024
    assert body["facts"]["value"] == 2100


def test_CT05_comparison_uses_baseline_denominator(client, tenant_headers):
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How did orders completed change from FY2023 to FY2024?",
        "document_ids": ["atlas_fy24", "atlas_fy23"],
    })
    assert response.status_code == 200
    body = response.json()
    facts = body["facts"]
    assert facts["metric"] == "orders_completed"
    assert facts["baseline_year"] == 2023 and facts["baseline_value"] == 1000
    assert facts["fiscal_year"] == 2024 and facts["value"] == 1200
    assert facts["change_pct"] == 20.0


def test_CT06_comparison_cites_both_documents_in_any_input_order(client, tenant_headers):
    for document_ids in (["atlas_fy24", "atlas_fy23"], ["atlas_fy23", "atlas_fy24"]):
        response = client.post("/api/v1/ask", headers=tenant_headers, json={
            "question": "How did orders completed change from FY2023 to FY2024?",
            "document_ids": document_ids,
        })
        assert response.status_code == 200
        body = response.json()
        assert {c["document_id"] for c in body["citations"]} == {"atlas_fy23", "atlas_fy24"}


def test_CT07_missing_requested_year_is_insufficient_evidence(client, tenant_headers):
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many orders were completed in FY2025?",
        "document_ids": ["atlas_fy24"],
    })
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_evidence"
    assert response.json()["facts"] is None
    assert response.json()["citations"] == []


def test_CT08_unknown_document_id_returns_404(client, tenant_headers):
    response = client.post("/api/v1/ask", headers=tenant_headers, json={
        "question": "How many orders were completed in FY2024?",
        "document_ids": ["does_not_exist"],
    })
    assert response.status_code == 404


@pytest.mark.parametrize("payload", [
    {"question": " ", "document_ids": ["atlas_fy24"]},
    {"question": "How many orders?", "document_ids": []},
    {"document_ids": ["atlas_fy24"]},
    {"question": "How many orders?", "document_ids": "atlas_fy24"},
])
def test_CT09_invalid_ask_payload_returns_422(client, tenant_headers, payload):
    response = client.post("/api/v1/ask", headers=tenant_headers, json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize("overrides", [
    {"company": "", "filename": "f.txt", "fiscal_year": 2025, "page": 1, "extracted_text": "text"},
    {"company": "Acme", "filename": "f.txt", "fiscal_year": 2025, "page": 1, "extracted_text": " "},
    {"company": "Acme", "filename": "f.txt", "fiscal_year": 2025, "page": 0, "extracted_text": "text"},
    {"company": "Acme", "filename": "f.txt", "fiscal_year": 99, "page": 1, "extracted_text": "text"},
    {"company": "Acme", "fiscal_year": 2025, "page": 1, "extracted_text": "text"},
])
def test_CT10_invalid_upload_payload_returns_422(client, tenant_headers, overrides):
    response = client.post("/api/v1/documents", headers=tenant_headers, json=overrides)
    assert response.status_code == 422
