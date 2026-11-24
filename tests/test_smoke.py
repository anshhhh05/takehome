"""Small set of passing smoke checks; they do not establish release readiness."""


def test_health(client):
    result = client.get('/health')
    assert result.status_code == 200
    assert result.json() == {'status': 'ok'}


def test_documents_list_is_tenant_scoped(client, tenant_headers):
    result = client.get('/api/v1/documents', headers=tenant_headers)
    assert result.status_code == 200
    assert {d['id'] for d in result.json()['documents']} == {'atlas_fy22','atlas_fy23','atlas_fy24'}


def test_single_document_question(client, tenant_headers):
    result = client.post('/api/v1/ask', headers=tenant_headers, json={
        'question':'How many orders were completed in FY2024?', 'document_ids':['atlas_fy24']})
    assert result.status_code == 200
    payload = result.json()
    assert payload['status'] == 'success'
    assert payload['facts']['value'] == 1200
    assert payload['citations'] == [{'document_id':'atlas_fy24','page':14}]


def test_upload_and_list(client, tenant_headers):
    result = client.post('/api/v1/documents', headers=tenant_headers, json={
        'company':'Atlas Commerce','filename':'FY2025.txt','fiscal_year':2025,'page':4,
        'extracted_text':'FY2025. Orders completed: 1100. Support tickets received: 2000.'})
    assert result.status_code == 201
    uploaded_id = result.json()['id']
    listing = client.get('/api/v1/documents', headers=tenant_headers).json()['documents']
    assert uploaded_id in {d['id'] for d in listing}
