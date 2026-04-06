# Marketplace Web MVP

A small frontend project to browse SPLENT packages and their dependencies.

## What It Does

- Shows a list of packages.
- You can search by name, description, or tags.
- When you select one, you can see:
	- version
	- description
	- dependencies
	- packages that use it
	- relation lines like `A -> B`
- Includes a button to copy the install command.

## How To Run It

From this folder:

```bash
python3 -m http.server 8080
```

Then open in your browser:

```text
http://localhost:8080
```

## How To Use It

1. In the left column, you have the package list.
2. Use the search box to filter.
3. Click a package to see its details.
4. If you want, click `Copy` to copy the command.

Command example:

```bash
splent install splent_feature_public
```

## Data

Data is loaded from:

`data/packages.json`
