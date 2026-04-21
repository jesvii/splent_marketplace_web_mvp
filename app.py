from __future__ import annotations

import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "marketplace-web-mvp"
DEFAULT_SPLENT_API_BASE_URL = "http://127.0.0.1:5000"


def get_splent_api_base_url() -> str:
    return os.getenv("SPLENT_API_BASE_URL", DEFAULT_SPLENT_API_BASE_URL).rstrip("/")


def fetch_packages() -> tuple[dict, int]:
    api_url = f"{get_splent_api_base_url()}/api/packages"

    try:
        with urlopen(api_url) as response:
            payload = response.read().decode("utf-8")
            return {"packages": jsonify_response_to_python(payload)}, response.status
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


def jsonify_response_to_python(payload: str) -> list:
    import json

    data = json.loads(payload)
    if isinstance(data, list):
        return data

    return data.get("packages", [])


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

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "splent_api_base_url": get_splent_api_base_url(),
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8080)
