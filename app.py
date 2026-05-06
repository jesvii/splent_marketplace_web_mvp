from __future__ import annotations

import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, render_template


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "marketplace-web-mvp"
DEFAULT_SPLENT_API_URL = "http://127.0.0.1:5000"


def load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


def get_splent_api_base_url() -> str:
    return os.getenv("SPLENT_API_URL", DEFAULT_SPLENT_API_URL).rstrip("/")


def get_splent_api_token() -> str:
    return os.getenv("SPLENT_API_TOKEN", "")


def get_marketplace_api_token() -> str:
    return os.getenv("MARKETPLACE_API_TOKEN") or get_splent_api_token()


def get_splent_api_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    token = get_splent_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if not header.startswith(prefix):
        return ""

    return header[len(prefix) :].strip()


def token_is_valid(token: str) -> bool:
    expected_token = get_marketplace_api_token()
    return bool(expected_token) and token == expected_token


def unauthorized_response():
    return jsonify({"error": "Unauthorized"}), 401


def fetch_packages() -> tuple[list | dict, int]:
    api_url = f"{get_splent_api_base_url()}/api/packages"

    try:
        request = Request(api_url, headers=get_splent_api_headers())
        with urlopen(request) as response:
            payload = response.read().decode("utf-8")
            return jsonify_response_to_python(payload), response.status
    except HTTPError as error:
        return {
            "error": "Splent API returned an error",
            "status_code": error.code,
            "upstream_url": api_url,
        }, 502
    except URLError as error:
        return {
            "error": "Could not connect to Splent API",
            "details": str(error.reason),
            "upstream_url": api_url,
        }, 502


def jsonify_response_to_python(payload: str) -> list | dict:
    import json

    data = json.loads(payload)
    if isinstance(data, list):
        return data

    return data.get("packages", [])


def package_matches_query(package: dict, query: str) -> bool:
    if not query:
        return True

    contract = package.get("contract") or {}
    values = [
        package.get("full_name"),
        package.get("repository"),
        package.get("name"),
        contract.get("description"),
    ]

    normalized_query = query.strip().lower()
    return any(normalized_query in str(value or "").lower() for value in values)


def search_packages(query: str) -> tuple[list | dict, int]:
    packages, status_code = fetch_packages()
    if status_code != 200 or not isinstance(packages, list):
        return packages, status_code

    return [package for package in packages if package_matches_query(package, query)], 200


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/packages")
    def packages():
        payload, status_code = fetch_packages()
        return jsonify(payload), status_code

    @app.post("/api/marketplace/login")
    def marketplace_login():
        data = request.get_json(silent=True) or {}
        token = data.get("token") or get_bearer_token()
        if not token_is_valid(token):
            return unauthorized_response()

        return {
            "status": "ok",
            "marketplace_url": request.host_url.rstrip("/"),
        }

    @app.post("/api/marketplace/logout")
    def marketplace_logout():
        return {"status": "ok"}

    @app.get("/api/search")
    def search():
        if not token_is_valid(get_bearer_token()):
            return unauthorized_response()

        payload, status_code = search_packages(request.args.get("q", ""))
        return jsonify(payload), status_code

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "splent_api_url": get_splent_api_base_url(),
            "splent_api_token_configured": bool(get_splent_api_token()),
            "marketplace_api_token_configured": bool(get_marketplace_api_token()),
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8080)
