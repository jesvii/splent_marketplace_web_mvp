import json
from urllib.error import URLError

import app as marketplace_app


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_health_ok(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_json_payload_accepts_list_or_packages_object():
    packages = [{"name": "splent_feature_auth"}]

    assert marketplace_app.jsonify_response_to_python(json.dumps(packages)) == packages
    assert (
        marketplace_app.jsonify_response_to_python(json.dumps({"packages": packages}))
        == packages
    )


def test_fetch_packages_uses_configured_api(monkeypatch):
    packages = [{"name": "splent_feature_auth"}]
    monkeypatch.setenv("SPLENT_API_URL", "https://api.example.test")

    def fake_urlopen(request):
        assert request.full_url == "https://api.example.test/api/packages"
        return FakeResponse({"packages": packages})

    monkeypatch.setattr(marketplace_app, "urlopen", fake_urlopen)

    payload, status = marketplace_app.fetch_packages()

    assert status == 200
    assert payload == packages


def test_fetch_packages_sends_bearer_token(monkeypatch):
    monkeypatch.setenv("SPLENT_API_TOKEN", "secret-token")

    def fake_urlopen(request):
        assert request.get_header("Authorization") == "Bearer secret-token"
        return FakeResponse([])

    monkeypatch.setattr(marketplace_app, "urlopen", fake_urlopen)

    payload, status = marketplace_app.fetch_packages()

    assert status == 200
    assert payload == []


def test_fetch_packages_returns_502_when_api_is_down(monkeypatch):
    def fake_urlopen(request):
        raise URLError("connection refused")

    monkeypatch.setattr(marketplace_app, "urlopen", fake_urlopen)

    payload, status = marketplace_app.fetch_packages()

    assert status == 502
    assert payload["error"] == "Could not connect to Splent API"


def test_marketplace_login_with_valid_token(client, monkeypatch):
    monkeypatch.setenv("SPLENT_API_TOKEN", "marketplace-token")

    res = client.post(
        "/api/marketplace/login",
        json={"token": "marketplace-token"},
    )

    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_marketplace_login_uses_marketplace_api_token(client, monkeypatch):
    monkeypatch.setenv("SPLENT_API_TOKEN", "splent-token")
    monkeypatch.setenv("MARKETPLACE_API_TOKEN", "marketplace-token")

    res = client.post(
        "/api/marketplace/login",
        json={"token": "marketplace-token"},
    )

    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_marketplace_login_rejects_invalid_token(client, monkeypatch):
    monkeypatch.setenv("SPLENT_API_TOKEN", "marketplace-token")

    res = client.post(
        "/api/marketplace/login",
        json={"token": "wrong-token"},
    )

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"


def test_marketplace_logout_ok(client):
    res = client.post("/api/marketplace/logout")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_search_needs_valid_token(client, monkeypatch):
    monkeypatch.setenv("SPLENT_API_TOKEN", "marketplace-token")

    res = client.get("/api/search?q=auth")

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"


def test_search_filters_marketplace_packages(client, monkeypatch):
    packages = [
        {
            "full_name": "splent/splent_feature_auth",
            "name": "splent_feature_auth",
            "repository": "splent/splent_feature_auth",
            "contract": {"description": "Authentication feature"},
        },
        {
            "full_name": "splent/splent_feature_mail",
            "name": "splent_feature_mail",
            "repository": "splent/splent_feature_mail",
            "contract": {"description": "Email feature"},
        },
    ]
    monkeypatch.setenv("SPLENT_API_TOKEN", "marketplace-token")
    monkeypatch.setattr(marketplace_app, "fetch_packages", lambda: (packages, 200))

    res = client.get(
        "/api/search?q=auth",
        headers={"Authorization": "Bearer marketplace-token"},
    )

    assert res.status_code == 200
    assert res.get_json() == [packages[0]]
