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
  detailRepoLink: document.getElementById("detailRepoLink"),
  detailUpdatedAt: document.getElementById("detailUpdatedAt"),
  installCommand: document.getElementById("installCommand"),
  copyBtn: document.getElementById("copyBtn"),
  dependenciesList: document.getElementById("dependenciesList"),
  reverseDependenciesList: document.getElementById("reverseDependenciesList"),
  edgesList: document.getElementById("edgesList"),
};

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function getDescription(pkg) {
  return pkg.contract?.description || "No description available yet.";
}

function getDependencies(pkg) {
  return pkg.contract?.requires?.features || [];
}

function getVersionLabel(pkg) {
  if (pkg.full_name?.includes("@")) {
    return pkg.full_name.split("@").pop();
  }

  return pkg.metadata?.feature_version || pkg.metadata?.version || "from contract";
}

function getPackageId(pkg) {
  if (!pkg) return "";
  return pkg.full_name || pkg.repository || pkg.name;
}

function getUpdatedAt(pkg) {
  return pkg.metadata?.updated_at || pkg.updated_at;
}

function formatUpdatedAt(value) {
  if (!value) return "Unknown";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function getReverseDependencies(targetName) {
  return state.packages
    .filter((pkg) => getDependencies(pkg).includes(targetName))
    .map((pkg) => getPackageId(pkg));
}

function renderSimpleList(container, values, emptyText = "(none)") {
  container.innerHTML = "";

  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    container.appendChild(li);
    return;
  }

  values.forEach((value) => {
    const li = document.createElement("li");
    li.textContent = value;
    container.appendChild(li);
  });
}

function packageMatchesQuery(pkg, query) {
  if (!query) return true;

  const values = [
    pkg.full_name,
    pkg.repository,
    pkg.name,
    getDescription(pkg),
  ];

  return values.some((value) => normalize(value).includes(query));
}

function renderPackageList(query = "") {
  const normalizedQuery = normalize(query);
  const filtered = state.packages.filter((pkg) => packageMatchesQuery(pkg, normalizedQuery));

  dom.packageCount.textContent = `${filtered.length} packages`;
  dom.packageList.innerHTML = "";

  filtered.forEach((pkg) => {
    const li = document.createElement("li");
    li.className = "package-item";

    const btn = document.createElement("button");
    if (getPackageId(state.selected) === getPackageId(pkg)) btn.classList.add("active");

    btn.innerHTML = `
      <span class="name">${pkg.name}</span>
      <span class="meta">${getVersionLabel(pkg)} · ${getDependencies(pkg).length} dependencies</span>
    `;
    btn.addEventListener("click", () => selectPackage(getPackageId(pkg)));

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
    dom.copyBtn.textContent = "Copied";
    dom.copyBtn.classList.add("copied");

    setTimeout(() => {
      dom.copyBtn.textContent = "Copy";
      dom.copyBtn.classList.remove("copied");
    }, 1200);
  } catch (_) {
    window.prompt("Copy the command:", command);
  }
}

function selectPackage(featureRef) {
  const pkg = state.packages.find((item) => getPackageId(item) === featureRef);
  if (!pkg) return;

  state.selected = pkg;
  renderPackageList(dom.searchInput.value);

  dom.emptyState.classList.add("hidden");
  dom.detail.classList.remove("hidden");

  dom.detailName.textContent = pkg.name;
  dom.detailVersion.textContent = getVersionLabel(pkg);
  dom.detailDescription.textContent = getDescription(pkg);
  dom.detailRepoLink.href = pkg.repo_url || "#";
  dom.detailRepoLink.textContent = pkg.repository || pkg.name;
  dom.detailUpdatedAt.textContent = formatUpdatedAt(getUpdatedAt(pkg));

  const command = `splent feature:install ${getPackageId(pkg)}`;
  dom.installCommand.textContent = command;

  const deps = [...getDependencies(pkg)];
  const reverseDeps = getReverseDependencies(getPackageId(pkg));

  renderSimpleList(dom.dependenciesList, deps);
  renderSimpleList(dom.reverseDependenciesList, reverseDeps);
  renderEdges(getPackageId(pkg), deps, reverseDeps);

  dom.copyBtn.onclick = () => copyCommand(command);
}

async function init() {
  const response = await fetch("/api/packages");
  if (!response.ok) {
    throw new Error(`Could not load packages (${response.status})`);
  }

  const data = await response.json();
  state.packages = Array.isArray(data) ? data : data.packages || [];

  renderPackageList();

  if (state.packages.length) {
    selectPackage(getPackageId(state.packages[0]));
  }

  dom.searchInput.addEventListener("input", (event) => {
    renderPackageList(event.target.value);
  });
}

init().catch((error) => {
  dom.emptyState.classList.remove("hidden");
  dom.emptyState.innerHTML = `<h3>Could not load registry</h3><p>${error.message}</p>`;
});
