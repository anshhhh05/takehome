import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def reset_test_data():
    # Keeps uploaded documents from leaking between individual tests.
    store.reset_store()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def tenant_headers():
    return {"X-Tenant-ID": "northstar"}
