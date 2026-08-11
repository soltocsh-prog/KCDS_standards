# KCS Automation Backend Source Workspace Survey Report

- **Survey Target Directory**: `c:\Users\solto\OneDrive\문서\Soltovity`
- **Survey Date**: 2026-08-11
- **Surveyor**: explorer_survey_1 agent

---

## 1. Summary of Workspace Structure

The `Soltovity` repository is a full-stack project consisting of:
- **Frontend**: React + Vite application located in `src/`, `public/`, `package.json`, `vite.config.js`.
- **Backend**: FastAPI & Python services located in `backend/`.
- **Root Documentation**: `CONTEXT.md`, `migration_guide.md`, `README.md`.
- **Root Scratch/Debug**: `scratch/`, `debug/`, and root level `scratch_*.py` files.

---

## 2. Classification of Backend Python Files and Directories

### 2.1. CORE Backend Files (Targeted for Migration to `KCS_Automation`)

| Category | File Path / Directory | Description / Role | Status |
| :--- | :--- | :--- | :--- |
| **API Entry Point** | `backend/main.py` | FastAPI application exposing routes for document queries (`/api/kcs/documents`), document merging (`/api/kcs/merge`), file downloads (`/api/kcs/download/{filename}`), and preset management (`/api/kcs/presets`). | **CORE** |
| **CLI Runner** | `backend/generate_cli.py` | CLI execution utility to fetch KCS/KDS documents via API and generate HWP/HML output locally. | **CORE** |
| **Database Module** | `backend/db/database.py` | SQLite DB connection helper (`get_db_connection`), schema creation (`init_db`), and catalog seeding logic (`seed_kcs_catalog`). | **CORE** |
| **Database Files** | `backend/db/kcs_documents.db` | Primary SQLite database containing KCS catalog metadata and cached document content JSON. | **CORE** |
| | `backend/db/kcs.db` | Secondary SQLite database file. | **CORE** |
| | `backend/db/kcsc.db` | Secondary SQLite database file. | **CORE** |
| **Services** | `backend/services/__init__.py` | Package marker file. | **CORE** |
| | `backend/services/document_orchestrator.py` | Document orchestrator managing DB cache hits/misses, OpenAPI fetching, concurrency throttling, circuit breaker, and calling HML bridge. | **CORE** |
| | `backend/services/hml_bridge.py` | Bridge parsing template HML files and injecting formatted content sections into HML DOM using lxml. | **CORE** |
| | `backend/services/hml_generator.py` | Core low-level HML builder handling XML tags, paragraph shapes, character shapes, tables, borders, and image elements. | **CORE** |
| | `backend/services/hml_generator_recovered.py` | Backup/recovered variant of HML generator service. | **CORE** |
| | `backend/services/kcsc_api_client.py` | Async and sync client for KCSC OpenAPI (`CodeList`, `SearchDoc`, `CodeViewer`). | **CORE** |
| | `backend/services/ai_recommender.py` | AI service using Google Gemini (`google-generativeai`) to match user prompt descriptions with KCS codes. | **CORE** |
| | `backend/services/document_generator.py` | Alternative/legacy document generator using BeautifulSoup XML parsing. | **CORE** |
| | `backend/services/jinja2_generator/__init__.py` | Package marker file. | **CORE** |
| | `backend/services/jinja2_generator/jinja2_hml_generator.py` | Jinja2 template-based HML renderer. | **CORE** |
| | `backend/services/jinja2_generator/templates/base_template.hml.j2` | Base Jinja2 HML template. | **CORE** |
| **Templates** | `backend/templates/base_template.hml` | Base HML template document. | **CORE** |
| | `backend/templates/base_template2.hml` | Primary base HML template document used by Orchestrator and CLI. | **CORE** |
| | `backend/templates/table_snippet.xml.j2` | Jinja2 snippet template for table structures. | **CORE** |
| | `backend/templates/#old/base_template.hml` | Historical base template. | **CORE** |
| | `backend/templates/#old/table_snippet.xml.j2` | Historical table snippet template. | **CORE** |
| **Test Suite** | `backend/tests/conftest.py` | pytest fixtures and configuration. | **CORE** |
| | `backend/tests/test_ai_recommendation.py` | Unit tests for `ai_recommender.py`. | **CORE** |
| | `backend/tests/test_api_endpoints.py` | Unit tests for FastAPI endpoints in `main.py`. | **CORE** |
| | `backend/tests/test_database.py` | Unit tests for `database.py`. | **CORE** |
| | `backend/tests/test_document_generation.py` | Unit tests for `document_generator.py`. | **CORE** |
| | `backend/tests/test_hml_bridge.py` | Unit tests for `hml_bridge.py`. | **CORE** |
| | `backend/tests/test_hml_generator.py` | Unit tests for `hml_generator.py`. | **CORE** |
| | `backend/tests/test_hml_table_image_deep_dive.py` | Unit tests for HML table & image deep dive parsing. | **CORE** |
| | `backend/tests/test_jinja2_hml_generator.py` | Unit tests for `jinja2_hml_generator.py`. | **CORE** |
| | `backend/tests/test_kcsc_api.py` | Unit tests for `kcsc_api_client.py`. | **CORE** |
| | `backend/tests/features/ai_recommendation.feature` | BDD scenario definition for AI recommendations. | **CORE** |
| | `backend/tests/features/document_generation.feature` | BDD scenario definition for document generation. | **CORE** |
| | `backend/tests/features/kcsc_api.feature` | BDD scenario definition for KCSC API integration. | **CORE** |
| **Package Config** | `backend/requirements.txt` | Python package dependency definitions. | **CORE** |
| **Documentation** | `migration_guide.md` | Migration and deployment guide for PC/NAS environments. | **CORE (R2)** |
| | `CONTEXT.md` | Project architecture decision record and status context. | **CORE (R2)** |

---

### 2.2. TEMP / DEBUG Files (To Be Excluded from Migration)

| Category | Location | List of Files / Directories | Rationale for Exclusion |
| :--- | :--- | :--- | :--- |
| **Top-Level Backend Debug Scripts** | `backend/*.py` | `analyze_410000.py`, `analyze_411000.py`, `check_borderfill.py`, `check_contents.py`, `check_hml.py`, `check_hml_utf8.py`, `check_images.py`, `check_kds_images.py`, `check_large_images.py`, `check_output_validity.py`, `compare_5_7_6_and_5_8.py`, `debug_xml.py`, `extract_snippet.py`, `find_code.py`, `find_kcs_code.py`, `find_kds_figures.py`, `inspect_large_images_context.py`, `inspect_paragraphs.py`, `inspect_specific_indices.py`, `preview_run.py`, `scratch_check_all_lxml.py`, `scratch_count_tr.py`, `scratch_generate_and_inspect_each.py`, `scratch_inspect_tables_data.py`, `scratch_modify_template.py`, `scratch_run.py`, `scratch_run_jinja.py`, `scratch_test_parsers.py`, `scratch_test_table_children.py`, `test_api_411200.py`, `verify_style.py` | One-off analysis, inspection, and temporary debugging scripts. |
| **Backend Scratch Directory** | `backend/scratch/` | Entire `backend/scratch/` directory including `backup_hml_generator.py`, `check_dim.py`, `extract_images.py`, `find_img.py`, `find_kcs_mapping.py`, `find_page_break.py`, `inspect_merged_output.py`, `inspect_pagebreaks.py`, `inspect_section2.py`, `inspect_sections.py`, `inspect_template.py`, `parse_styles.py`, `query_kcs_codes.py`, `run_merge_kcs.py`, `search_kcsc.py`, `search_page_break.py`, `test_code_list.py`, `test_code_list_filter.py`, `test_different_codes.py`, `test_kcsc_real_api.py`, `test_move_secdef.py`, `test_note_newline.py`, `test_section_merge.py`, `extracted_images/`, HTML/JSON/TXT dumps. | Scratch experimentation folder. |
| **Backend Samples & Output** | `backend/sample/`, `backend/output/` | Sample HML files and generated HWP output files (`merged_*.hwp`, `output_*.hwp`). | Output artifacts and sample files. |
| **Root Scratch Scripts** | `Soltovity/*.py` | `recovered_from_all.py`, `recovered_hml.py`, `scratch_db.py`, `scratch_find_sup.py`, `scratch_generate_142010.py`, `scratch_parse_hml.py`, `scratch_query_kcs.py`, `scratch_sup_test.py` | Temporary scripts and recovery dumps at root directory. |
| **Root Scratch & Debug Directories** | `scratch/`, `debug/` | `check_shape_111.py`, `check_shapes.py`, `find_table_note_content.py`, `generate_exact_table.py`, `inspect_charshapes_local.py`, `list_kcs_codes.py`, `search_exact_table.py`, `search_kcs_full.py`, `test_exact_kcs.py`, `write_bat.py`, `inspect_generated_tables.py`, `inspect_image_size.py`, `inspect_sample_pictures.py`, `isolated_generator.py`, `test_solution.py`, etc. | Exploratory research and debugging folders. |
| **Virtual Environment & Cache** | `backend/venv/`, `backend/__pycache__/`, `.pytest_cache/` | Virtual environment binaries, compiled Python bytecode, pytest cache. | Auto-generated or environment-specific directories. |

---

## 3. System Dependencies and Database Schemas

### 3.1. Package Requirements (`backend/requirements.txt`)
```
fastapi
pytest
pytest-bdd
pytest-watch
beautifulsoup4
lxml
google-generativeai
uvicorn
Pillow
```

### 3.2. Database Schemas (`backend/db/database.py`)

#### Table: `kcs_documents`
```sql
CREATE TABLE kcs_documents (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    content_json TEXT,
    has_content BOOLEAN DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `kcs_presets`
```sql
CREATE TABLE IF NOT EXISTS kcs_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    codes_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Verification and Next Steps for Migration Agent

To ensure clean migration to `c:\Users\solto\OneDrive\문서\KCS_Automation`:
1. Copy all identified **CORE** files maintaining their original directory hierarchy (`main.py`, `db/`, `services/`, `templates/`, `tests/`, `requirements.txt`).
2. Copy related documentation (`CONTEXT.md`, `migration_guide.md`, `README.md`).
3. Ensure no TEMP/DEBUG files or scratch directories are copied.
