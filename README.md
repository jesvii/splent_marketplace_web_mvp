# Marketplace Web MVP

A small web app to explore SPLENT packages and their dependencies, now served with Flask and connected to `splent-api`.

## What It Does

- Shows a list of packages.
- Lets you search by name, description, or tags.
- When you select a package, it shows:
  - version
  - description
  - dependencies
  - packages that depend on it
  - relationship lines like `A -> B`
- Includes a button to copy the install command.
- Exposes a JSON API at `/api/packages`.
- Fetches package data from the external SPLENT API instead of reading a local JSON file.

## How To Run It

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the server:

```bash
python3 app.py
```

If your API is not running on the default URL, set:

```bash
export SPLENT_API_BASE_URL=http://127.0.0.1:5000
```

Then open:

```text
http://localhost:8080
```

## Structure

- `app.py`: Flask entry point
- `marketplace-web-mvp/templates/index.html`: main template
- `marketplace-web-mvp/static/`: static frontend assets
- `SPLENT_API_BASE_URL`: base URL for `splent-api`
