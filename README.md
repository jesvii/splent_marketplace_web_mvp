# SPLENT Marketplace Web MVP

A small Flask web app to browse SPLENT packages from `splent-api`.

The marketplace does not store packages. It serves the web UI and proxies `GET /api/packages` to the configured SPLENT API using a bearer token.

## Features

- Lists SPLENT packages/features.
- Searches by `full_name`, `repository`, `name`, or contract description.
- Shows package details, dependencies, reverse dependencies, and dependency edges.
- Opens the GitHub repository using `repo_url`.
- Copies the install command using `full_name`.

## Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Set the API URL and token:

```env
SPLENT_API_URL=https://api.splent.io
SPLENT_API_TOKEN=replace-with-the-splent-api-token
```

`SPLENT_API_TOKEN` is sent to the API and is also used by the marketplace endpoints that require authentication:

```http
Authorization: Bearer <token>
```

The CLI stores SPLENT_API_URL and SPLENT_API_TOKEN for the Splent API.
The marketplace web UI only displays packages by proxying the API.

Do not commit `.env`. Only `.env.example` should be versioned.

## CLI Marketplace Endpoints

The marketplace exposes small JSON endpoints for the SPLENT CLI:

- `GET /api/packages`: returns packages for `splent feature:search`.
- `POST /api/marketplace/login`: validates a token if the CLI wants to check login against the server.
- `POST /api/marketplace/logout`: returns `ok`; the CLI removes the stored local session.
- `GET /api/search?q=<query>`: optional server-side package search endpoint.

Login accepts either a JSON body:

```json
{"token":"<splent-api-token>"}
```

or an `Authorization` header:

```http
Authorization: Bearer <splent-api-token>
```

`/api/search` requires the same Bearer token and matches `full_name`, `repository`, `name`, or contract description.

## Local Development

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the development server:

```bash
python3 app.py
```

Open:

```text
http://localhost:8080
```

## Unit Tests

The unit tests are located in `tests/unit` and use `pytest`.

- `tests/unit/test_app.py` tests the Flask app, API proxy, token header, CLI login/search endpoints, and upstream error handling.
- `tests/unit/conftest.py` defines reusable pytest fixtures for the Flask app and test client.

Run the tests with:

```bash
python3 -m pytest tests/unit
```

The tests use fake package data and mocks. They do not call the real Splent API.

## GitHub Actions

This repository includes three workflows:

- `CI_pytest.yml`: runs the Flask route, page render, and mocked API proxy tests with `pytest`.
- `CI_codacy.yml`: runs Codacy code quality analysis for the web codebase.
- `CD_render.yml`: triggers a Render deployment after `CI pytest` passes on `main` or `master`.

Configure these repository secrets in GitHub:

```text
CODACY_PROJECT_TOKEN
RENDER_DEPLOY_HOOK_URL
```

`CODACY_PROJECT_TOKEN` comes from the Codacy project settings. `RENDER_DEPLOY_HOOK_URL` comes from the Render service deploy hook.

## Docker Deployment

The production deployment must run with Docker Compose. The service listens on container port `80`, maps host port `80`, and uses `restart: always`.

On the marketplace VM:

```bash
git clone <this-repository-url>
cd splent_marketplace_web_mvp
cp .env.example .env
```

Edit `.env` with the real API URL and bearer token:

```bash
nano .env
```

Build and start the service:

```bash
docker compose up -d --build
```

Check the container:

```bash
docker compose ps
docker compose logs -f marketplace
```

Check the app health endpoint:

```bash
curl http://localhost/health
```

The public domain should point to the VM and resolve to:

```text
http://marketplace.splent.io
```

## Updating The Deployment

On the VM:

```bash
git pull
docker compose up -d --build
```

## Project Structure

- `app.py`: Flask entry point and API proxy.
- `marketplace-web-mvp/templates/index.html`: main HTML template.
- `marketplace-web-mvp/static/`: frontend assets.
- `Dockerfile`: production image.
- `docker-compose.yml`: production Compose service.
- `.env.example`: environment variable template.
