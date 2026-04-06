const state = {
  packages: [],
  selected: null,
};

const dom = {
  packageList: document.getElementById("packageList"),
  packageCount: document.getElementById("packageCount"),
  searchInput: document.getElementById("searchInput"),
  emptyState: document.getElementById("emptyState"),
  detail: document.getElementById("packageDetail"),
  detailName: document.getElementById("detailName"),
  detailVersion: document.getElementById("detailVersion"),
  detailDescription: document.getElementById("detailDescription"),
  installCommand: document.getElementById("installCommand"),
  copyBtn: document.getElementById("copyBtn"),
  dependenciesList: document.getElementById("dependenciesList"),
  reverseDependenciesList: document.getElementById("reverseDependenciesList"),
  edgesList: document.getElementById("edgesList"),
};

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function getReverseDependencies(targetName) {
  return state.packages
    .filter((pkg) => pkg.dependencies.includes(targetName))
    .map((pkg) => pkg.name);
}

function renderSimpleList(container, values, emptyText = "(none)") {
  container.innerHTML = "";

  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    container.appendChild(li);
    return;
  }

  values.forEach((v) => {
    const li = document.createElement("li");
    li.textContent = v;
    container.appendChild(li);
  });
}

function packageMatchesQuery(pkg, query) {
  if (!query) return true;

  return (
    normalize(pkg.name).includes(query) ||
    normalize(pkg.description).includes(query) ||
    pkg.tags.some((tag) => normalize(tag).includes(query))
  );
}

function renderPackageList(query = "") {
  const normalizedQuery = normalize(query);
  const filtered = state.packages.filter((pkg) => packageMatchesQuery(pkg, normalizedQuery));

  dom.packageCount.textContent = String(filtered.length);
  dom.packageList.innerHTML = "";

  filtered.forEach((pkg) => {
    const li = document.createElement("li");
    li.className = "package-item";

    const btn = document.createElement("button");
    if (state.selected?.name === pkg.name) btn.classList.add("active");

    btn.innerHTML = `
      <span class="name">${pkg.name}</span>
      <span class="meta">v${pkg.version} · ${pkg.dependencies.length} dependencias</span>
    `;
    btn.addEventListener("click", () => selectPackage(pkg.name));

    li.appendChild(btn);
    dom.packageList.appendChild(li);
  });
}

function renderEdges(pkgName, deps, reverseDeps) {
  const edges = [
    ...deps.map((dep) => `${pkgName} -> ${dep}`),
    ...reverseDeps.map((source) => `${source} -> ${pkgName}`),
  ];

  renderSimpleList(dom.edgesList, edges, "No dependency relations");
}

async function copyCommand(command) {
  try {
    await navigator.clipboard.writeText(command);
    dom.copyBtn.textContent = "Copiado";
    dom.copyBtn.classList.add("copied");

    setTimeout(() => {
      dom.copyBtn.textContent = "Copiar";
      dom.copyBtn.classList.remove("copied");
    }, 1200);
  } catch (_) {
    // Fallback for restricted contexts.
    window.prompt("Copia el comando:", command);
  }
}

function selectPackage(name) {
  const pkg = state.packages.find((p) => p.name === name);
  if (!pkg) return;

  state.selected = pkg;
  renderPackageList(dom.searchInput.value);

  dom.emptyState.classList.add("hidden");
  dom.detail.classList.remove("hidden");

  dom.detailName.textContent = pkg.name;
  dom.detailVersion.textContent = `v${pkg.version}`;
  dom.detailDescription.textContent = pkg.description;

  const cmd = `splent install ${pkg.name}`;
  dom.installCommand.textContent = cmd;

  const deps = [...pkg.dependencies];
  const reverseDeps = getReverseDependencies(pkg.name);

  renderSimpleList(dom.dependenciesList, deps);
  renderSimpleList(dom.reverseDependenciesList, reverseDeps);
  renderEdges(pkg.name, deps, reverseDeps);

  dom.copyBtn.onclick = () => copyCommand(cmd);
}

async function init() {
  const response = await fetch("./data/packages.json");
  const data = await response.json();
  state.packages = data.packages;

  renderPackageList();

  if (state.packages.length) {
    selectPackage(state.packages[0].name);
  }

  dom.searchInput.addEventListener("input", (ev) => {
    renderPackageList(ev.target.value);
  });
}

init().catch((error) => {
  dom.emptyState.classList.remove("hidden");
  dom.emptyState.innerHTML = `<h3>Error cargando datos</h3><p>${error.message}</p>`;
});
