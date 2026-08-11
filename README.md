# 🏗️ KCS 표준시방서 자동화 프로젝트 (KCS Automation)

> **Standalone FastAPI Backend Service and CLI Runner for Korean Construction Specification (KCS) HML/HWP Document Generation**

---

## 📌 Project Overview

**KCS Automation (KCS 표준시방서 자동화 프로젝트)** is a standalone FastAPI backend service and CLI runner for Korean Construction Specification (KCS) HML/HWP document generation, parsing, section injection, database storage, and Gemini AI specification recommendation.

The system interacts with standard construction specification databases, connects to the official **KCSC OpenAPI**, utilizes Jinja2 templates and BeautifulSoup XML manipulations for document assembly, and provides both a RESTful Web API and a headless CLI runner.

---

## 🏛️ Directory Tree Architecture

```
KCS_Automation/
├── main.py                     # FastAPI application entry point & REST API routes
├── generate_cli.py             # CLI specification generator runner
├── requirements.txt            # Python dependencies specification
├── run_services.bat            # Windows service launcher script
├── README.md                   # Project overview, directory tree & repository history
├── CONTEXT.md                  # System architecture context & design decisions
├── migration_guide.md          # Migration and deployment guide (PC & Synology NAS Docker)
├── db/                         # Database layer & SQLite storage
│   ├── database.py             # SQLite connection & query wrapper module
│   ├── kcs.db                  # KCS standards database
│   ├── kcs_documents.db        # KCS document metadata database
│   └── kcsc.db                 # KCSC standards database
├── docs/                       # Specifications & reference samples
│   ├── REQUIREMENTS.md         # Original project extraction requirements
│   └── samples/                # Reference API payload & specification samples
│       ├── kcs_142010_api_response.json
│       └── kcs_14_20_10.json
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── ai_recommender.py       # Google Gemini AI specification recommender
│   ├── document_generator.py   # BeautifulSoup HML document generator
│   ├── document_orchestrator.py # Document caching, throttling & generation orchestrator
│   ├── hml_bridge.py           # HML template parsing & section injection bridge
│   ├── hml_generator.py        # Core HML XML element builder
│   ├── hml_generator_recovered.py # Backup HML generator engine
│   ├── kcsc_api_client.py      # KCSC OpenAPI integration client
│   └── jinja2_generator/       # Jinja2 template rendering engine
│       ├── __init__.py
│       ├── jinja2_hml_generator.py
│       └── templates/
│           └── base_template.hml.j2
├── templates/                  # Document template definitions
│   ├── base_template.hml       # Primary HML document template
│   ├── base_template2.hml      # Secondary HML document template
│   └── table_snippet.xml.j2    # Jinja2 table snippet template
└── tests/                      # Test suite
    ├── conftest.py             # Pytest fixtures & configuration
    ├── test_ai_recommendation.py
    ├── test_api_endpoints.py   # Integration tests for FastAPI routes
    ├── test_database.py        # Database unit tests
    ├── test_document_generation.py
    ├── test_hml_bridge.py      # HML bridge logic tests
    ├── test_hml_generator.py   # HML generator unit tests
    ├── test_hml_table_image_deep_dive.py
    ├── test_jinja2_hml_generator.py
    ├── test_kcsc_api.py
    └── features/               # BDD scenario feature specifications
        ├── ai_recommendation.feature
        ├── document_generation.feature
        └── kcsc_api.feature
```

---

## 📦 Detailed Module Description

| Category | File / Subdirectory | Primary Function & Responsibility |
|---|---|---|
| **Entry Points** | `main.py` | FastAPI application defining REST API routes (`/api/kcs/documents`, `/api/kcs/merge`, `/api/kcs/download/{filename}`, `/api/kcs/presets`) and CORS middleware configuration. |
| | `generate_cli.py` | Headless CLI runner that fetches specification data from KCSC OpenAPI and generates HML/HWP documents directly from the command line. |
| | `run_services.bat` | Windows batch file launcher script for services. |
| **Database Layer** | `db/database.py` | SQLite helper providing database connections (`get_db_connection()`) and SQL execution utilities. |
| | `db/kcs.db` | Embedded SQLite storage containing KCS specification standards catalog and code metadata. |
| | `db/kcs_documents.db` | Embedded SQLite storage for document cache, metadata, and user presets. |
| | `db/kcsc.db` | Embedded SQLite storage holding KCSC API reference metadata. |
| **Services** | `services/document_orchestrator.py` | High-level orchestrator handling document caching, rate throttling, KCSC API fetching, and multi-code document merging. |
| | `services/hml_generator.py` | Core HML XML DOM element builder and placeholder injection engine. |
| | `services/hml_bridge.py` | Section injection and BeautifulSoup XML bridge for table/image formatting within HML templates. |
| | `services/kcsc_api_client.py` | Client library for communicating with official KCSC OpenAPI endpoints with key handling and retry capabilities. |
| | `services/ai_recommender.py` | Google Gemini AI integration for standard specification code recommendations and content analysis. |
| | `services/document_generator.py` | HTML/XML element parser converting web specifications into structured HML markup. |
| | `services/jinja2_generator/` | Modular Jinja2 rendering engine (`jinja2_hml_generator.py`) using `templates/base_template.hml.j2`. |
| **Templates** | `templates/base_template.hml` | Primary baseline XML template (v1) for HML document generation. |
| | `templates/base_template2.hml` | Secondary baseline XML template (v2) used by the CLI runner. |
| | `templates/table_snippet.xml.j2` | Jinja2 template snippet for rendering HML table structures. |
| **Documentation** | `docs/REQUIREMENTS.md` | Core extraction requirements specification for the project. |
| | `docs/samples/` | Sample API response JSONs (`kcs_142010_api_response.json`, `kcs_14_20_10.json`) used for offline testing and verification. |
| | `CONTEXT.md` | Comprehensive system design, architectural boundaries, and API specification documentation. |
| | `migration_guide.md` | Deployment guide covering virtual environment setup, service launch, and Synology NAS Docker deployment. |
| **Test Suite** | `tests/conftest.py` | Pytest fixtures and mock client configurations. |
| | `tests/test_*.py` | Comprehensive unit and integration test suite covering API endpoints, SQLite DB, HML builder, Jinja2 renderer, AI recommender, and KCSC API client. |
| | `tests/features/` | Pytest-BDD Gherkin feature files (`ai_recommendation.feature`, `document_generation.feature`, `kcsc_api.feature`). |

---

## 🚀 Setup & Usage Instructions

### 1. Virtual Environment Setup

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Windows CMD)
.\venv\Scripts\activate.bat
```

### 2. Dependency Installation

Install all required Python packages declared in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Dependencies include `fastapi`, `uvicorn`, `beautifulsoup4`, `lxml`, `google-generativeai`, `pytest`, `pytest-bdd`, and `Pillow`.

### 3. Running the FastAPI Web Server

Start the REST API server on `http://127.0.0.1:8000`:

```bash
uvicorn main:app --reload
```

Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### 4. Running the CLI Document Generator

Generate a specification document directly via the command line:

```bash
python generate_cli.py --code 411200
```

Additional CLI arguments:

```bash
python generate_cli.py --code 411200 --type KCS --output concrete_spec.hwp
```

### 5. Running Tests

Execute unit, integration, and BDD tests using `pytest`:

```bash
pytest
```

---

## 🔌 REST API Specification

| Method | Endpoint | Description | Request Payload / Params |
|---|---|---|---|
| `GET` | `/api/kcs/documents` | Retrieve list of cached KCS document metadata and status | None |
| `POST` | `/api/kcs/merge` | Merge specified KCS specification codes into an HML/HWP document | `{"codes": ["411200", "142010"], "title": "Combined Spec"}` |
| `GET` | `/api/kcs/download/{filename}` | Download a generated HML/HWP specification document file | Path param: `filename` (e.g. `merged_123.hwp`) |
| `GET` | `/api/kcs/presets` | List all saved user document presets | None |
| `POST` | `/api/kcs/presets` | Save a new document preset configuration | `{"name": "Preset 1", "codes": ["411200"]}` |
| `DELETE` | `/api/kcs/presets/{preset_id}` | Delete a saved user preset | Path param: `preset_id` |

---

## 📜 Repository Origin Note

> **Historical Note on Repository Default Content**
>
> The initial default content (`# -`) in the GitHub remote repository (`https://github.com/soltocsh-prog/-.git`) originated directly from GitHub's default repository initialization command:
> ```bash
> echo "# -" >> README.md
> ```
> executed during repository creation for repository `soltocsh-prog/-`. This default placeholder content has been superseded by this comprehensive project documentation.
