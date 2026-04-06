# SPLENT Marketplace Web MVP

This is an independent frontend MVP for a Marketplace-like experience.

## Features

- List available packages.
- Inspect dependency and reverse-dependency relations for each package.
- Copy a ready-to-use install command:

`splent install <package_name>`

## Run locally

From this folder:

```bash
python3 -m http.server 8080
```

Then open:

`http://localhost:8080`

## Data source

Package data is loaded from `data/packages.json`.
