# Handoff Report: Backend Source Code Survey

## 1. Observation

- **Workspace Path**: `c:\Users\solto\OneDrive\문서\Soltovity`
- **Command & Tool Executions**:
  - `list_dir` on root: Found top-level directories (`backend`, `src`, `public`, `scratch`, `debug`, `.agents`, etc.) and files (`CONTEXT.md`, `migration_guide.md`, `README.md`, `scratch_*.py`, `recovered_*.py`, etc.).
  - `find_by_name` on `backend`: Located FastAPI app entry (`backend/main.py`), database directory (`backend/db/`), service modules (`backend/services/`), XML templates (`backend/templates/`), unit/BDD tests (`backend/tests/`), dependencies (`backend/requirements.txt`), and numerous temporary scripts.
  - `view_file` on `backend/main.py`: Confirmed FastAPI app defining `/api/kcs/documents`, `/api/kcs/merge`, `/api/kcs/download/{filename}`, and `/api/kcs/presets`.
  - `view_file` on `backend/requirements.txt`: Identified core dependencies (`fastapi`, `pytest`, `pytest-bdd`, `pytest-watch`, `beautifulsoup4`, `lxml`, `google-generativeai`, `uvicorn`, `Pillow`).
  - `view_file` on `backend/db/database.py`: Identified SQLite schema definitions (`kcs_documents`, `kcs_presets`) and connection logic.
  - `view_file` on `backend/services/document_orchestrator.py`: Identified orchestrator service connecting DB, OpenAPI, and HML bridge.
  - `view_file` on `backend/generate_cli.py`: Identified CLI generation tool for KCS/KDS documents.
  - `view_file` on `preview_run.py`, `recovered_from_all.py`, `recovered_hml.py`: Identified hardcoded local paths and text recovery dumps.

## 2. Logic Chain

1. **Premise**: The goal is to separate production-ready backend components for KCS automation from frontend code and temporary debug scripts.
2. **Step 1 (Core Application Entry)**: `backend/main.py` imports `db.database.get_db_connection` and `services.document_orchestrator.DocumentOrchestrator`, which forms the primary API entry point for document rendering and management. Therefore, `main.py` is a CORE file.
3. **Step 2 (Business Logic & Data Access)**:
   - `backend/services/` contains `document_orchestrator.py`, `hml_bridge.py`, `hml_generator.py`, `kcsc_api_client.py`, `ai_recommender.py`, `document_generator.py`, and `jinja2_generator/`. These implement document processing, API fetching, and HML generation. Therefore, all service files are CORE.
   - `backend/db/` contains `database.py` and SQLite databases (`kcs_documents.db`, `kcs.db`, `kcsc.db`). These define the persistent database schema and hold cached catalog data. Therefore, `backend/db/` is CORE.
4. **Step 3 (Templates & Tests)**:
   - `backend/templates/` contains base HML templates (`base_template2.hml`, `base_template.hml`) required by `hml_bridge.py` and `generate_cli.py`. Therefore, `backend/templates/` is CORE.
   - `backend/tests/` contains `conftest.py`, unit test files (`test_*.py`), and BDD features (`features/*.feature`). These validate core functionalities. Therefore, `backend/tests/` is CORE.
5. **Step 4 (Exclusion of Debug & Temporary Scripts)**:
   - Root level `scratch_*.py`, `recovered_*.py`, `scratch/`, `debug/`, `backend/scratch/`, and 37 individual `backend/*.py` files (e.g. `check_*.py`, `analyze_*.py`, `inspect_*.py`, `preview_run.py`) are standalone test scripts, log dumps, or one-off experiment scripts. None are imported by `main.py` or the test suite. Therefore, these are classified as TEMP/DEBUG and excluded from migration.
6. **Step 5 (Documentation & Configuration)**:
   - `backend/requirements.txt` defines package dependencies.
   - `CONTEXT.md` and `migration_guide.md` provide architectural context and deployment instructions (fulfilling Requirement R2).

## 3. Caveats

- SQLite database files (`kcs_documents.db`, `kcs.db`, `kcsc.db`) contain pre-cached KCS document catalog data. Migrating them ensures offline capability; if clean database initialization is preferred, running `database.py` on startup will recreate and re-seed `kcs_documents.db`.
- `backend/services/hml_generator_recovered.py` is a recovered backup file. It can be kept alongside `hml_generator.py` or archived.

## 4. Conclusion

All backend source components, test suites, configuration files, and documentation needed for `KCS_Automation` have been identified and categorized in `survey_report.md`. 
The core backend consists of `main.py`, `generate_cli.py`, `requirements.txt`, `db/`, `services/`, `templates/`, `tests/`, `CONTEXT.md`, and `migration_guide.md`. All debug/scratch scripts have been flagged for exclusion.

## 5. Verification Method

- **Inspect Report**: Read `c:\Users\solto\OneDrive\문서\Soltovity\.agents\teamwork_preview_explorer_survey_1\survey_report.md` to review the complete file matrix.
- **Run Pytest Suite**: Execute `pytest backend/tests` in `c:\Users\solto\OneDrive\문서\Soltovity` to verify that all unit test modules in CORE pass without dependency on TEMP/DEBUG scripts.
