<div align="center">

# 🛠️ aas-digital-twin-Afriso

### Digital twins for Afriso industrial products, powered by Eclipse BaSyx
### 🔁 A reusable pipeline — one guide, any product

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Podman](https://img.shields.io/badge/Podman-container%20engine-892CA0?logo=podman&logoColor=white)
![BaSyx](https://img.shields.io/badge/Eclipse%20BaSyx-2.0-2C2255?logo=eclipseide&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248?logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/status-in%20development-yellow)

</div>

---

This project builds and manages **Asset Administration Shells (AAS)** — standardized digital twins — for Afriso industrial products. It's designed as a reusable template: swap in a new product's Excel data and JSON template, and the same pipeline and infrastructure will generate and publish its AAS package.

> Throughout this guide, `<PRODUCT_ID>` is a placeholder for your product's identifier (e.g. `LAG14ER`, `PrimoVent77766`, etc.) — replace it with the actual `id_short` of the product you're working with.

It combines:
- 🧩 A **BaSyx-based AAS infrastructure** (repositories, registries, discovery, and a web UI) running in containers.
- 🐍 A **Python conversion pipeline** that reads product data from an Excel sheet, fills in an AAS JSON template, packages it as an `.aasx` file, and uploads it to the running AAS environment.

<br>

## 📑 Table of Contents

1. [What this project does](#1-what-this-project-does)
2. [Prerequisites](#2-prerequisites)
3. [Install Podman](#3-install-podman)
4. [Set up the Python environment](#4-set-up-the-python-environment)
5. [Configure environment variables](#5-configure-environment-variables)
6. [Expected project structure](#6-expected-project-structure)
7. [Running the project](#7-running-the-project)
8. [Makefile & helper script reference](#8-makefile--helper-script-reference)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. What this project does

### 🪪 Asset Administration Shell (AAS)
- **id_short**: `<PRODUCT_ID>` — the product's unique short identifier (e.g. `LAG14ER`).
- **id**: `https://www.afriso.com/aas/<PRODUCT_ID>` — globally unique URI, also usable directly as an API endpoint (HTTP GET) on the Afriso AAS registry server.
- **display_name**: Multi-language name (`en`, `de`).
- **description**: Product designation, typically in German and English.
- **asset_kind**: `AssetKind.TYPE`
- **global_asset_id**: Link to the Afriso product details page.
- **administration**: AAS metadata versioning, initialized at `1.0`.
- **Submodel references** (typical set — adjust per product):
  - 🏷️ `Digital Nameplate`
  - 📄 `Handover Documentation`
  - ⚙️ `Technical Data`
  - 🌱 `Carbon Footprint`
  - 🔧 `Maintenance Instructions`

### 🔄 Data pipeline (`<PRODUCT_ID>.py`)

```mermaid
flowchart LR
    A[📊 <PRODUCT_ID>.xlsx] --> B[🐍 <PRODUCT_ID>.py]
    T[📋 <PRODUCT_ID>_Template.json] --> B
    B --> C[📝 <PRODUCT_ID>_output.json]
    C --> D[📦 <PRODUCT_ID>.aasx]
    D --> E[☁️ Upload to BaSyx<br/>localhost:8081/upload]
```

1. Reads product data from an Excel workbook (`../xlsx/<PRODUCT_ID>.xlsx`), matching rows by `Element Name (idShort)` / `Actual Value`.
2. Loads the empty AAS template (`../json_template/<PRODUCT_ID>_Template.json`).
3. Recursively walks the template and injects the Excel values into matching `idShort` fields (handling `Property`, `File`, and `MultiLanguageProperty` elements, including `@de` / `@en` language tags). Fields without matching Excel data are cleared out.
4. Writes the filled JSON to `../output_json/<PRODUCT_ID>_output.json`.
5. Packages the result into an AASX package at `../aasx/<PRODUCT_ID>.aasx` using the `basyx-python-sdk`.
6. Uploads the `.aasx` package to a running BaSyx AAS environment (`http://localhost:8081/upload` by default).

> 💡 **Tip:** re-running the script after updating the Excel sheet regenerates the JSON and AASX package from scratch — no manual cleanup needed.

> 🆕 **Adding a new product:** to onboard a new product, create `<PRODUCT_ID>.xlsx`, `<PRODUCT_ID>_Template.json`, and a `<PRODUCT_ID>.py` (or generalize the script to accept `<PRODUCT_ID>` as an argument) following the same pattern as an existing product.

### 🏗️ Infrastructure (`docker-compose.yml`)
The stack is based on [Eclipse BaSyx](https://www.eclipse.org/basyx/) and consists of:

| Service | Purpose | Port |
|---|---|---|
| 🍃 `mongo` | MongoDB backing store | internal |
| 🏭 `machine1-aas` | AAS environment for machine 1 | `8081` |
| 🏭 `machine2-aas` | AAS environment for machine 2 | `8082` |
| 📇 `aas-registry` | AAS registry (control tower) | `8083` |
| 🔍 `submodel-registry` | Submodel registry / discovery | `8084` |
| 🖥️ `aas-ui` | Web UI for browsing/editing AAS data | `3000` |

---

## 2. 📋 Prerequisites

- 🐧 A Linux, macOS, or WSL2 environment
- 🦭 [Podman](https://podman.io/) as the container engine, orchestrated via `podman-compose`
- 🐍 Python 3.9+
- 🔨 `make`

---

## 3. 🦭 Install Podman

`podman-compose` is what actually drives the containers here (the `Makefile` calls it directly — no Docker shim needed). You still need the `podman` engine itself installed at the system level; `podman-compose` is then installed automatically into the project's virtual environment by `make venv` (see next section).

### Debian / Ubuntu
```bash
sudo apt update
sudo apt install -y podman
```

### Fedora / RHEL / CentOS
```bash
sudo dnf install -y podman
```

### macOS (via Homebrew)
```bash
brew install podman
podman machine init
podman machine start
```

### Verify installation
```bash
podman --version
```

> **Note:** the original Makefile comment flagged `# need to change podman version` — double-check the BaSyx image tags in `docker-compose.yml` are compatible with your installed Podman version before running `make up`.

---

## 4. 🐍 Set up the Python environment

The project manages its own virtual environment via `make` — you don't need to create it manually.

### Create the virtual environment & install dependencies
```bash
make venv
```
This creates a `.venv/` folder and installs all required packages into it:

| Package | Purpose |
|---|---|
| `pandas` | Reads and processes the Excel source data |
| `openpyxl` | Excel (`.xlsx`) engine used by `pandas` |
| `basyx-python-sdk` | Reads/writes AAS JSON and builds `.aasx` packages |
| `pyecma376-2` | OPC/ECMA-376 package format support, used when building `.aasx` files |
| `requests` | Uploads the generated `.aasx` file to the AAS environment |
| `podman-compose` | Container orchestration (installed into the venv so it's always available) |

> `make up` and `make run` both depend on `venv`, so it's created automatically the first time you run either — running `make venv` yourself is optional but useful if you just want the environment ready.

### 🔌 Activate / deactivate helper scripts
Two convenience scripts are included so you don't have to remember the `.venv/bin/activate` path:

```bash
source activate_venv.sh      # activates .venv, or tells you to run `make venv` first
```
```bash
source deactivate_venv.sh    # deactivates the current venv
```

> ⚠️ Both scripts must be **sourced**, not executed directly (`./activate_venv.sh` won't work) — sourcing runs them in your current shell, which is required for `activate`/`deactivate` to affect your session.

---

## 5. 🔐 Configure environment variables

Create a `.env` file in the project root (used by `docker-compose.yml`):

```bash
DB_USER=your_mongo_username
DB_PASSWORD=your_mongo_password
CORS_ORIGINS=http://localhost:3000
```

---

## 6. 📁 Expected project structure

The Python script expects the following directory layout relative to its own location:

```
project-root/
├── xlsx/
│   └── <PRODUCT_ID>.xlsx          # source product data
├── json_template/
│   └── <PRODUCT_ID>_Template.json # empty AAS template
├── output_json/
│   └── <PRODUCT_ID>_output.json   # generated after running the script
├── aasx/
│   └── <PRODUCT_ID>.aasx          # generated AASX package
├── scripts/                  # or wherever <PRODUCT_ID>.py lives
│   └── <PRODUCT_ID>.py
├── main.py                   # entry point invoked by `make run`
├── docker-compose.yml
├── Makefile
├── activate_venv.sh
├── deactivate_venv.sh
└── .env
```

Create any missing folders before running the script:

```bash
mkdir -p xlsx json_template output_json aasx
```

---

## 7. 🚀 Running the project

### ▶️ Start the infrastructure
```bash
make up
```
This automatically creates the virtual environment (`venv`, if it doesn't exist yet), creates the required local `data/` and `config/` folders, and starts all containers (`mongo`, `machine1-aas`, `machine2-aas`, `aas-registry`, `submodel-registry`, `aas-ui`) via `podman-compose up -d`.

Check logs:
```bash
make logs
```

Once running, the web UI is available at **[http://localhost:3000](http://localhost:3000)** 🎉

### 📤 Generate and upload the AAS package
Run the conversion pipeline through the Makefile — this uses the venv's Python automatically, no manual activation needed:
```bash
make run
```
This invokes `main.py` with the venv's interpreter, which reads `xlsx/<PRODUCT_ID>.xlsx`, fills the AAS template, writes `output_json/<PRODUCT_ID>_output.json`, builds `aasx/<PRODUCT_ID>.aasx`, and uploads it to `http://localhost:8081/upload` (the `machine1-aas` service).

> 💡 Prefer working inside an activated shell instead? Run `source activate_venv.sh`, then call your product script directly (e.g. `python <PRODUCT_ID>.py`), and `source deactivate_venv.sh` when you're done.

### 🧹 Stop / clean up
```bash
make down     # stop containers
make clean    # stop containers and remove volumes
make fclean   # full clean: remove images, volumes, local mongo data, and the .venv
```

---

## 8. 🔨 Makefile & helper script reference

| Command | What it does |
|---|---|
| `make venv` | Creates `.venv/` and installs `pandas`, `basyx-python-sdk`, `openpyxl`, `pyecma376-2`, `requests`, `podman-compose` |
| `make up` | Depends on `venv`; creates `data/mongodb` and `config/` folders, then runs `podman-compose up -d` |
| `make run` | Depends on `venv`; runs `main.py` using the venv's Python |
| `make logs` | Tails logs from all running containers |
| `make down` | Stops all containers |
| `make clean` | Stops containers and removes volumes |
| `make fclean` | Full reset: removes images, volumes, orphan containers, local Mongo data, **and** `.venv` |
| `source activate_venv.sh` | Activates `.venv` in your current shell (prompts you to run `make venv` if it's missing) |
| `source deactivate_venv.sh` | Deactivates the currently active virtual environment |

---

## 9. 🆘 Troubleshooting

| Problem | Fix |
|---|---|
| ❌ **Upload fails / connection refused** | Make sure `make up` has finished starting `machine1-aas` (check `make logs`) before running `make run`. |
| ❌ **Excel columns not found** | The script expects a header row at Excel row 5 (`header=4`) with columns named `Element Name (idShort)` and `Actual Value`. |
| ❌ **`podman-compose: command not found`** | It's installed inside `.venv`, not system-wide — run `make venv` first, or activate the venv with `source activate_venv.sh` before calling `podman-compose` manually. |
| ❌ **`activate_venv.sh` says the venv doesn't exist** | Run `make venv` (or `make up` / `make run`, which create it automatically) before sourcing the script. |
| ❌ **Activating/deactivating seems to do nothing** | Make sure you `source` the script rather than executing it (`source activate_venv.sh`, not `./activate_venv.sh`). |

<div align="center">

---
Made for the Afriso digital twin initiative 🔧

</div>
