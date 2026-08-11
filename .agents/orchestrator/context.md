# Context — KCS 표준시방서 자동화 프로젝트

## Source Workspace
- Path: `c:\Users\solto\OneDrive\문서\Soltovity`

## Target Destination
- Path: `c:\Users\solto\OneDrive\문서\KCS_Automation`

## Key Requirements & Acceptance Criteria
- R1: Core backend python files (`main.py`, `services/`, `templates/`, `db/`, `tests/`) copied to `KCS_Automation`. Temporary/debug scripts (`scratch_*.py`, `check_*.py`) excluded. Soltovity files untouched.
- R2: Documentation files (`CONTEXT.md`, `migration_guide.md`, etc.) copied to `KCS_Automation`.
- R3: `README.md` created with tree architecture of new folder and note explaining `# -` origin (`echo "# -" >> README.md`).
- R4: Log of copied files generated and reported. Git repo initialized in `KCS_Automation` and pushed to designated remote repository.
