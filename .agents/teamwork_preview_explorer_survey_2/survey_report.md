# Documentation & Project Specifications Survey Report

## Executive Summary
This report presents the findings from an exhaustive survey of documentation, specifications, and project metadata files in the source workspace `c:\Users\solto\OneDrive\문서\Soltovity`. The survey was conducted to prepare for extracting the backend KCS (Korean Construction Specification) Automation system into a standalone repository `KCS_Automation`.

---

## 1. Documentation & Specification Inventory

The source workspace contains the following core documentation and specification files:

### 1.1 `CONTEXT.md`
- **Location**: `c:\Users\solto\OneDrive\문서\Soltovity\CONTEXT.md` (4,480 bytes, 50 lines)
- **Summary**: Documents the architecture context, technical stack decisions (React, Vite, Tailwind, FastAPI), development philosophy (Lean & Pragmatic), key architectural decisions (SaaS iframe embedding limits, account vault scope, dynamic workflow management), and implementation phase status.
- **Copy Recommendation**: **Copy to `KCS_Automation/CONTEXT.md`**. It provides essential background context regarding the overall system design and technical rationale.

### 1.2 `migration_guide.md`
- **Location**: `c:\Users\solto\OneDrive\문서\Soltovity\migration_guide.md` (5,857 bytes, 137 lines)
- **Summary**: Complete migration, installation, and deployment guide specifically written for the "KCS 시방서 자동화 대시보드" (KCS Specification Automation Dashboard). Provides step-by-step instructions for:
  1. File packaging (excluding `node_modules` and `backend/venv`).
  2. Local PC execution (Python 3.9+, Node.js, `pip install -r requirements.txt`, `uvicorn main:app`, `npm run dev`).
  3. Docker Compose deployment on Synology NAS (`Container Manager` configuration with `python:3.11-slim` and `node:20-alpine`).
  4. API endpoint configuration troubleshooting (`API_BASE_URL` in `KcsAutomationPage.jsx`).
- **Copy Recommendation**: **Copy to `KCS_Automation/migration_guide.md`**. This is a primary operational document for the backend service.

### 1.3 `README.md`
- **Location**: `c:\Users\solto\OneDrive\문서\Soltovity\README.md` (4,640 bytes, 67 lines)
- **Summary**: Workspace root README describing the "ArchHub: 건축 전용 워크스페이스 플랫폼" project, including 3-panel layout, tech stack, and 4-phase implementation roadmap.
- **Action**: Create a new, dedicated `README.md` for `KCS_Automation` tailored specifically to the backend automation service, while referencing the origin of the initial repository README.

### 1.4 `.agents/ORIGINAL_REQUEST.md`
- **Location**: `c:\Users\solto\OneDrive\문서\Soltovity\.agents\ORIGINAL_REQUEST.md` (2,800 bytes, 44 lines)
- **Summary**: Captures the initial project specification (R1: core file extraction, R2: doc inclusion, R3: tree architecture & README, R4: logging & GitHub push).
- **Copy Recommendation**: Recommended to be archived under `KCS_Automation/docs/REQUIREMENTS.md` for project lineage and auditability.

### 1.5 Supplementary Specifications & Data Documents
- **`kcs_142010_api_response.json`** (437,872 bytes): Sample API response schema and payload for KCS standard section 14 20 10.
- **`kcs_14_20_10.json`** (350,999 bytes): Standard specification JSON structure for KCS 14 20 10.
- **`backend/requirements.txt`** (94 bytes, 10 lines): Specifies backend python package requirements (`fastapi`, `uvicorn`, `beautifulsoup4`, `lxml`, `Pillow`, `google-generativeai`, `pytest`, `pytest-bdd`, `pytest-watch`).
- **`run_services.bat`** (770 bytes): Batch launcher script for starting FastAPI (port 8000) and Vite (port 5173).

---

## 2. README.md Origin Analysis (`echo "# -" >> README.md`)

- **Observed Origin**:
  - The local workspace is linked to remote repository `https://github.com/soltocsh-prog/-.git`.
  - When creating a repository named `-` on GitHub, GitHub automatically generates quickstart instructions containing:
    ```bash
    echo "# -" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/soltocsh-prog/-.git
    git push -u origin main
    ```
  - The `# -` string originated directly from GitHub's default repository creation wizard where `# -` is the H1 title based on the repository name `-`.
  - **Inclusion in New README**: The new `KCS_Automation/README.md` will explicitly note this origin in a "Repository Origin & History" section to explain the repository's initial state.

---

## 3. Recommended Tree Architecture for `KCS_Automation/README.md`

The extracted `KCS_Automation` project should be documented in `README.md` using the following clean tree architecture:

```
KCS_Automation/
├── main.py                     # FastAPI application entry point & REST API routes
├── generate_cli.py             # CLI-based specification document generator
├── requirements.txt            # Python dependencies specification
├── run_services.bat            # Windows double-click launcher script
├── README.md                   # Project overview, tree architecture & repository history
├── CONTEXT.md                  # System architecture context & design decisions
├── migration_guide.md          # Migration and deployment guide (PC & Synology NAS Docker)
├── docs/                       # Project documentation & reference samples
│   ├── REQUIREMENTS.md         # Original extraction requirements specification
│   ├── kcs_142010_api_response.json
│   └── kcs_14_20_10.json
├── db/                         # Database layer & SQLite storage
│   ├── database.py             # SQLite connection & query wrapper module
│   ├── kcs.db                  # KCS standards primary database
│   ├── kcs_documents.db        # KCS document metadata database
│   └── kcsc.db                 # KCSC standards database
├── services/                   # Business logic services
│   ├── kcs_service.py          # Specification search & data handling
│   ├── hml_generator.py        # HML document generation service (lxml engine)
│   ├── hml_parser.py           # HML document parsing & table extraction service
│   ├── image_service.py        # Specification image processing service
│   ├── kcsc_api_client.py      # KCSC external API integration client
│   └── jinja2_generator/       # Jinja2 template rendering engine
│       ├── jinja2_hml_generator.py
│       └── templates/
│           └── table_snippet.xml.j2
├── templates/                  # Document template definitions
│   ├── base_template.hml       # Primary HML document template
│   └── base_template2.hml      # Secondary HML document template
└── tests/                      # Test suite
    ├── conftest.py             # Pytest fixtures & setup
    ├── test_api_endpoints.py   # FastAPI endpoint integration tests
    ├── test_database.py        # SQLite database unit tests
    ├── test_hml_bridge.py      # HML bridge logic tests
    ├── test_hml_generator.py   # HML generator unit tests
    └── test_kcsc_api.py        # KCSC API client unit tests
```

---

## 4. Proposed Content Structure for the New `README.md`

1. **Title & Badges**: `# KCS Automation Service (KCS 표준시방서 자동화 시스템)`
2. **Project Overview**: Description of the FastAPI-based automated generation engine for Korean Construction Specifications in HML/HWP formats.
3. **Repository Lineage**: Clear note referencing the original GitHub repository initialization (`echo "# -" >> README.md` for repo `soltocsh-prog/-`).
4. **Project Architecture**: The tree diagram shown above.
5. **Key Modules & Capabilities**:
   - RESTful API endpoints for spec searching and generation.
   - HML XML parsing and templating via lxml and Jinja2.
   - Multi-database SQLite storage (`kcs.db`, `kcs_documents.db`, `kcsc.db`).
6. **Quick Start**: Instructions for setting up python virtual environment, installing dependencies, and running Uvicorn.
7. **Deployment & Operations**: Link to `migration_guide.md`.
8. **Testing**: Running `pytest` suite.
