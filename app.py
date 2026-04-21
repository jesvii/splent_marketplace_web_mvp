from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "marketplace-web-mvp"
DATA_FILE = FRONTEND_DIR / "data" / "packages.json"


def load_packages() -> dict:
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


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
        return jsonify(load_packages())

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8080)
