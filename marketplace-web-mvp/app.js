const state = {
  packages: [],
  selected: null,
};

const packageListEl = document.getElementById("packageList");
const packageCountEl = document.getElementById("packageCount");
const searchInputEl = document.getElementById("searchInput");

const emptyStateEl = document.getElementById("emptyState");
const detailEl = document.getElementById("packageDetail");
const detailNameEl = document.getElementById("detailName");
const detailVersionEl = document.getElementById("detailVersion");
const detailDescriptionEl = document.getElementById("detailDescription");
const installCommandEl = document.getElementById("installCommand");
const copyBtnEl = document.getElementById("copyBtn");
const dependenciesListEl = document.getElementById("dependenciesList");
const reverseDependenciesListEl = document.getElementById("reverseDependenciesList");
const edgesListEl = document.getElementById("edgesList");

function normalize(value) {
  return value.trim().toLowerCase();
}

function reverseDependencies(targetName, packages) {
  return packages
    .filter((pkg) => pkg.dependencies.includes(targetName))
    .map((pkg) => pkg.name);
}

function renderPackageList(query = "") {
  const filtered = state.packages.filter((pkg) => {
    const q = normalize(query);
    if (!q) return true;
    return (
      normalize(pkg.name).includes(q) ||
      normalize(pkg.description).includes(q) ||
      pkg.tags.some((tag) => normalize(tag).includes(q))
    );
  });

  packageCountEl.textContent = String(filtered.length);
  packageListEl.innerHTML = "";

  filtered.forEach((pkg) => {
    const li = document.createElement("li");
    li.className = "package-item";

    const btn = document.createElement("button");
    if (state.selected?.name === pkg.name) {
      btn.classList.add("active");
    }

    btn.innerHTML = `
      <span class="name">${pkg.name}</span>
      <span class="meta">v${pkg.version} · ${pkg.dependencies.length} dependencias</span>
    `;

    btn.addEventListener("click", () => selectPackage(pkg.name));
    li.appendChild(btn);
    packageListEl.appendChild(li);
  });
}

function renderTags(container, values) {
  container.innerHTML = "";
  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = "(none)";
    container.appendChild(li);
    return;
  }
  values.forEach((v) => {
    const li = document.createElement("li");
    li.textContent = v;
    container.appendChild(li);
  });
}

function renderEdges(pkg, deps, reverseDeps) {
  edgesListEl.innerHTML = "";
  const edges = [
    ...deps.map((d) => `${pkg.name} -> ${d}`),
    ...reverseDeps.map((r) => `${r} -> ${pkg.name}`),
  ];

  if (!edges.length) {
    const li = document.createElement("li");
    li.textContent = "No dependency relations";
    edgesListEl.appendChild(li);
    return;
  }

  edges.forEach((edge) => {
    const li = document.createElement("li");
    li.textContent = edge;
    edgesListEl.appendChild(li);
  });
}

function selectPackage(name) {
  const pkg = state.packages.find((p) => p.name === name);
  if (!pkg) return;

  state.selected = pkg;
  renderPackageList(searchInputEl.value);

  emptyStateEl.classList.add("hidden");
  detailEl.classList.remove("hidden");

  detailNameEl.textContent = pkg.name;
  detailVersionEl.textContent = `v${pkg.version}`;
  detailDescriptionEl.textContent = pkg.description;

  const cmd = `splent install ${pkg.name}`;
  installCommandEl.textContent = cmd;

  const deps = [...pkg.dependencies];
  const reverseDeps = reverseDependencies(pkg.name, state.packages);
  renderTags(dependenciesListEl, deps);
  renderTags(reverseDependenciesListEl, reverseDeps);
  renderEdges(pkg, deps, reverseDeps);

  copyBtnEl.onclick = async () => {
    try {
      await navigator.clipboard.writeText(cmd);
      copyBtnEl.textContent = "Copiado";
      copyBtnEl.classList.add("copied");
      setTimeout(() => {
        copyBtnEl.textContent = "Copiar";
        copyBtnEl.classList.remove("copied");
      }, 1200);
    } catch (_) {
      // Fallback for restricted contexts.
      window.prompt("Copia el comando:", cmd);
    }
  };
}

async function init() {
  const response = await fetch("./data/packages.json");
  const data = await response.json();
  state.packages = data.packages;

  renderPackageList();

  if (state.packages.length) {
    selectPackage(state.packages[0].name);
  }

  searchInputEl.addEventListener("input", (ev) => {
    renderPackageList(ev.target.value);
  });
}

init().catch((error) => {
  emptyStateEl.classList.remove("hidden");
  emptyStateEl.innerHTML = `<h3>Error cargando datos</h3><p>${error.message}</p>`;
});
