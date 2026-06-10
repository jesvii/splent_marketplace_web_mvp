from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

from click.testing import CliRunner
import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
API_REPO = WORKSPACE_ROOT / "splent-api"
CLI_SRC = WORKSPACE_ROOT / "splent_cli" / "src"


def _add_import_path(path: Path) -> None:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)


def _create_api_app(packages_file: Path, token: str, monkeypatch):
    monkeypatch.setenv("PACKAGES_FILE", str(packages_file))
    monkeypatch.setenv("PACKAGE_SOURCES", "registry")
    monkeypatch.setenv("SPLENT_API_TOKEN", token)

    _add_import_path(API_REPO)

    from src.config import Config
    from src.services import package_service
    from src.app import create_app

    Config.PACKAGES_FILE = str(packages_file)
    Config.SPLENT_API_TOKEN = token
    package_service.PACKAGES_FILE = str(packages_file)

    app = create_app()
    app.config.update(TESTING=True)
    return app


class RequestsResponse:
    def __init__(self, flask_response):
        self._response = flask_response
        self.status_code = flask_response.status_code
        self.content = flask_response.data

    def raise_for_status(self):
        if self.status_code < 400:
            return

        error = requests.exceptions.HTTPError()
        error.response = self
        raise error

    def json(self):
        return self._response.get_json()


class UrlopenResponse:
    def __init__(self, flask_response):
        self._response = flask_response
        self.status = flask_response.status_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self._response.data


def _patch_http_clients(api_app, monkeypatch):
    api_client = api_app.test_client()

    def fake_requests_request(method, url, timeout=None, headers=None, json=None):
        parsed = urlparse(url)
        path = parsed.path
        if parsed.query:
            path = f"{path}?{parsed.query}"

        response = api_client.open(
            path,
            method=method,
            headers=headers or {},
            json=json,
        )
        return RequestsResponse(response)

    def fake_urlopen(request):
        parsed = urlparse(request.full_url)
        path = parsed.path
        if parsed.query:
            path = f"{path}?{parsed.query}"

        response = api_client.open(
            path,
            method="GET",
            headers=dict(request.header_items()),
        )
        return UrlopenResponse(response)

    monkeypatch.setattr(requests, "request", fake_requests_request)

    import app as marketplace_app

    monkeypatch.setattr(marketplace_app, "urlopen", fake_urlopen)


def test_cli_published_package_is_visible_through_api_and_marketplace(
    tmp_path, monkeypatch
):
    token = "e2e-token"
    packages_file = tmp_path / "packages.json"
    api_app = _create_api_app(packages_file, token, monkeypatch)
    api_url = "http://splent-api.test"
    _patch_http_clients(api_app, monkeypatch)

    cli_env = tmp_path / "cli.env"
    cli_env.write_text(
        f"SPLENT_API_URL={api_url}\n"
        f"SPLENT_API_TOKEN={token}\n"
        "SPLENT_MARKETPLACE_AUTH=true\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("SPLENT_CLI_ENV_FILE", str(cli_env))
    monkeypatch.setenv("SPLENT_API_URL", api_url)
    monkeypatch.setenv("SPLENT_API_TOKEN", token)
    monkeypatch.setenv("SPLENT_MARKETPLACE_AUTH", "true")

    _add_import_path(CLI_SRC)

    from splent_cli.commands.feature.feature_search import feature_search
    from splent_cli.services import api_client

    package_payload = {
        "full_name": "splent-io/splent_feature_e2e@v1",
        "owner": "splent-io",
        "name": "splent_feature_e2e",
        "description": "Feature published during the E2E flow",
        "provides": {"services": ["E2EService"]},
        "requires": {"features": []},
        "repo_url": "https://github.com/splent-io/splent_feature_e2e",
        "repository": "splent-io/splent_feature_e2e",
        "contract": {
            "description": "Feature published during the E2E flow",
            "provides": {"services": ["E2EService"]},
            "requires": {"features": []},
        },
        "metadata": {"source": "e2e-test"},
    }

    published = api_client.post("/api/packages", json=package_payload)

    assert published["name"] == "splent_feature_e2e"

    result = CliRunner().invoke(feature_search, ["e2e"])

    assert result.exit_code == 0
    assert "splent_feature_e2e" in result.output

    monkeypatch.setenv("SPLENT_API_URL", api_url)
    monkeypatch.setenv("SPLENT_API_TOKEN", token)

    import app as marketplace_app

    marketplace = marketplace_app.create_app()
    marketplace.config.update(TESTING=True)
    response = marketplace.test_client().get(
        "/api/search?q=e2e",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    packages = response.get_json()
    assert any(package["name"] == "splent_feature_e2e" for package in packages)
