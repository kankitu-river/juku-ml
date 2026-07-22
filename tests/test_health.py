import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ML_API_TOKEN", "test-token")

from main import app  # noqa: E402

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_auth_required():
    """認証なしのリクエストは401"""
    res = client.post("/shift/forecast", json={"teachers": []})
    assert res.status_code == 422 or res.status_code == 401


def test_auth_valid_token():
    """正しいトークンでアクセスできる"""
    res = client.post(
        "/shift/forecast",
        json={"teachers": []},
        headers={"x-api-token": "test-token"},
    )
    assert res.status_code == 200
