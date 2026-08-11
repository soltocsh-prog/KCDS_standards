## 2026-08-11T16:03:38Z
Your working directory is: c:\Users\solto\OneDrive\문서\Soltovity\.agents\teamwork_preview_worker_m1_1

MANDATORY FIRST STEP:
Read c:\Users\solto\OneDrive\문서\Soltovity\.agents\ORIGINAL_REQUEST.md and c:\Users\solto\OneDrive\문서\Soltovity\PROJECT.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

YOUR TASK (Milestone 1: Core Backend Extraction):
Extract core backend files from `c:\Users\solto\OneDrive\문서\Soltovity` to `c:\Users\solto\OneDrive\문서\KCS_Automation`.

1. Create target directory `c:\Users\solto\OneDrive\문서\KCS_Automation` if it does not exist.
2. Copy the following core files/directories from `c:\Users\solto\OneDrive\문서\Soltovity` into `c:\Users\solto\OneDrive\문서\KCS_Automation`:
   - `backend/main.py` -> `KCS_Automation/main.py`
   - `backend/generate_cli.py` -> `KCS_Automation/generate_cli.py`
   - `backend/requirements.txt` -> `KCS_Automation/requirements.txt`
   - `run_services.bat` -> `KCS_Automation/run_services.bat`
   - `backend/db/database.py`, `kcs_documents.db`, `kcs.db`, `kcsc.db` -> `KCS_Automation/db/`
   - `backend/services/` (`document_orchestrator.py`, `hml_bridge.py`, `hml_generator.py`, `hml_generator_recovered.py`, `kcsc_api_client.py`, `ai_recommender.py`, `document_generator.py`, `jinja2_generator/`) -> `KCS_Automation/services/`
   - `backend/templates/` (`base_template.hml`, `base_template2.hml`, `table_snippet.xml.j2`, `#old/`) -> `KCS_Automation/templates/`
   - `backend/tests/` (`conftest.py`, `test_*.py`, `features/`) -> `KCS_Automation/tests/`

3. STRICT EXCLUSIONS (Do NOT copy any of these to `KCS_Automation`):
   - Do NOT copy root `scratch_*.py`, `recovered_*.py`, `scratch/`, `debug/`.
   - Do NOT copy `backend/scratch/`, `backend/sample/`, `backend/output/`, `backend/venv/`, `backend/__pycache__/`, `.pytest_cache/`.
   - Do NOT copy individual debug scripts in `backend/` (`analyze_*.py`, `check_*.py`, `debug_*.py`, `find_*.py`, `inspect_*.py`, `preview_run.py`, `scratch_*.py`, `verify_style.py`, etc.).
   - Do NOT delete or modify any files in `c:\Users\solto\OneDrive\문서\Soltovity`!

4. Verify that all core files are present in `KCS_Automation` and zero temp/debug files exist in `KCS_Automation`.
5. Document your changes in `changes.md` and write a clear handoff report in `handoff.md`.
