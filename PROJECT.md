# Project: KCS 표준시방서 자동화 프로젝트 (KCS Automation)

## Architecture
Standalone modularized FastAPI backend service and CLI tool for Korean Construction Specification (KCS) HML/HWP document generation.

Target Directory: `c:\Users\solto\OneDrive\문서\KCS_Automation`

```
KCS_Automation/
├── main.py                     # FastAPI application entry point & REST API routes
├── generate_cli.py             # CLI specification generator runner
├── requirements.txt            # Python dependencies specification
├── run_services.bat            # Windows service launcher script
├── README.md                   # Project overview, tree architecture & repository history
├── CONTEXT.md                  # System architecture context & design decisions
├── migration_guide.md          # Migration and deployment guide (PC & Synology NAS Docker)
├── docs/                       # Specifications & reference samples
│   ├── REQUIREMENTS.md         # Original project extraction requirements
│   └── samples/                # Reference API payload & specification samples
│       ├── kcs_142010_api_response.json
│       └── kcs_14_20_10.json
├── db/                         # Database layer & SQLite storage
│   ├── database.py             # SQLite connection & query wrapper module
│   ├── kcs.db                  # KCS standards database
│   ├── kcs_documents.db        # KCS document metadata database
│   └── kcsc.db                 # KCSC standards database
├── services/                   # Business logic services
│   ├── document_orchestrator.py # Document caching, throttling & generation orchestrator
│   ├── hml_bridge.py           # HML template parsing & section injection bridge
│   ├── hml_generator.py        # Core HML XML element builder
│   ├── hml_generator_recovered.py # Backup HML generator engine
│   ├── kcsc_api_client.py      # KCSC OpenAPI integration client
│   ├── ai_recommender.py       # Google Gemini AI specification recommender
│   ├── document_generator.py   # BeautifulSoup HML document generator
│   └── jinja2_generator/       # Jinja2 template rendering engine
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

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Core Backend Extraction | Extract main.py, generate_cli.py, services/, templates/, db/, tests/, requirements.txt into KCS_Automation while excluding scratch/debug scripts. Leave Soltovity untouched. | M1 | R1 |
| 2 | Documentation Migration | Copy CONTEXT.md, migration_guide.md, requirements, and sample JSON specs into KCS_Automation. | M2 | R2 |
| 3 | README & Tree Arch | Write comprehensive README.md in KCS_Automation containing tree architecture and explicit note on `# -` GitHub origin (`echo "# -" >> README.md`). | M3 | R3 |
| 4 | Migration Logging & Push | Generate migration file list log, initialize git repo in KCS_Automation, commit, and push to GitHub remote (`https://github.com/soltocsh-prog/-.git`). | M4 | R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Core Backend Extraction | Extract core backend code (`main.py`, `generate_cli.py`, `services/`, `templates/`, `db/`, `tests/`, `requirements.txt`, `run_services.bat`) to `c:\Users\solto\OneDrive\문서\KCS_Automation` | none | DONE |
| 2 | Documentation Migration | Copy `CONTEXT.md`, `migration_guide.md`, `docs/REQUIREMENTS.md`, and sample JSON files to `KCS_Automation` | M1 | DONE |
| 3 | README & Architecture Doc | Write new `KCS_Automation/README.md` with full tree architecture, module descriptions, setup instructions, and `# -` GitHub default origin note | M2 | DONE |
| 4 | Migration Logging & Git Push | Generate file list log (`migration_log.txt`), init git repository in `KCS_Automation`, stage, commit, and force-push to `https://github.com/soltocsh-prog/-.git` | M3 | DONE |

## Code Layout & Boundaries
- Target Workspace: `c:\Users\solto\OneDrive\문서\KCS_Automation`
- Source Workspace: `c:\Users\solto\OneDrive\문서\Soltovity` (READ-ONLY, untouched)
- Exclusions: All `scratch_*.py`, `check_*.py`, `debug/`, `scratch/`, `backend/scratch/`, `backend/sample/`, `backend/output/`, `backend/venv/`, `__pycache__`, `.pytest_cache`.
