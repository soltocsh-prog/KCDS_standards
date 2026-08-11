## 2026-08-11T16:15:19Z

Task: Create README.md for KCS_Automation project.

File Requirements:
1. Title & Overview: KCS 표준시방서 자동화 프로젝트 (KCS Automation) — Standalone FastAPI backend service and CLI runner for Korean Construction Specification (KCS) HML/HWP document generation.
2. Complete Directory Tree Architecture in ASCII code block matching all files and folders in KCS_Automation (main.py, generate_cli.py, requirements.txt, run_services.bat, README.md, CONTEXT.md, migration_guide.md, db/, docs/, services/, templates/, tests/).
3. Detailed Module Description table covering entry points, database layer, services, templates, docs, and test suite.
4. Setup & Usage instructions: Virtual environment creation (python -m venv venv), dependency installation (pip install -r requirements.txt), running server (uvicorn main:app --reload), running CLI (generate_cli.py --code 411200), running tests (pytest).
5. REST API Specification table for main endpoints (GET /api/kcs/documents, POST /api/kcs/merge, GET /api/kcs/download/{filename}, presets endpoints).
6. Explicit Repository Origin Note: Document that the initial GitHub repository default content ('# -') originated from GitHub's default initialization command (echo "# -" >> README.md) for repository soltocsh-prog/-.
7. Path Sanitation: Ensure zero occurrences of obsolete legacy paths (Soltovity, backend/, scratch_*.py).
