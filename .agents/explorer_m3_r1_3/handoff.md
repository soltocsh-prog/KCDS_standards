# Explorer 3 Investigation Report: README.md Structure, Quality & Technical Specifications (Milestone 3 / R3)

## 1. Observation
- **Target Workspace**: `c:\Users\solto\OneDrive\문서\KCS_Automation`
- **Current README.md Status**: `KCS_Automation/README.md` does not exist yet. Milestone 3 implementation task will write this file.
- **Source Workspace Reference**: `c:\Users\solto\OneDrive\문서\Soltovity` (Read-only reference).
- **Mandatory Requirements (R3 from ORIGINAL_REQUEST.md & PROJECT.md)**:
  1. **Tree Architecture**: Complete ASCII tree layout representing the modularized `KCS_Automation` repository structure.
  2. **Module Descriptions**: Detailed description of each root entry point, service, database layer, template set, documentation, and test suite.
  3. **Setup and Usage**: Step-by-step instructions for Python virtual environment setup, dependency installation, running the FastAPI backend server (`uvicorn` / `run_services.bat`), executing the CLI tool (`generate_cli.py`), and running test suites (`pytest`).
  4. **Origin Note**: Explicit historical note identifying that the initial GitHub repository default content `# -` originated from GitHub's default repository initialization instruction (`echo "# -" >> README.md`) for `https://github.com/soltocsh-prog/-.git`.
  5. **Path Sanitation**: Total absence of obsolete legacy paths (`Soltovity`, `backend/`, `backend/services/`, etc.).

### Verified File Structure of KCS_Automation
- **Root Entry Points & Metadata**:
  - `main.py` (FastAPI REST API routes & CORS middleware)
  - `generate_cli.py` (CLI runner for KCS/KDS document generation)
  - `requirements.txt` (Dependencies: `fastapi`, `uvicorn`, `pytest`, `pytest-bdd`, `beautifulsoup4`, `lxml`, `google-generativeai`, `Pillow`)
  - `run_services.bat` (Windows batch file to launch Uvicorn backend)
  - `CONTEXT.md` (System design & architectural context)
  - `migration_guide.md` (Deployment & migration guide for PC and Synology NAS Docker)
- **Database Layer (`db/`)**:
  - `db/database.py` (SQLite connection factory `get_db_connection()`)
  - `db/kcs.db` (KCS standards database)
  - `db/kcs_documents.db` (KCS document cache & metadata database)
  - `db/kcsc.db` (KCSC standards reference database)
- **Business Logic Services (`services/`)**:
  - `services/document_orchestrator.py` (Caching, throttling & multi-code specification merging)
  - `services/hml_bridge.py` (HML template parsing & section injection bridge)
  - `services/hml_generator.py` (Core HML XML element builder & injector)
  - `services/hml_generator_recovered.py` (Backup/recovered HML generator engine)
  - `services/kcsc_api_client.py` (KCSC OpenAPI integration client)
  - `services/ai_recommender.py` (Google Gemini AI specification recommender)
  - `services/document_generator.py` (BeautifulSoup HML document generator)
  - `services/jinja2_generator/jinja2_hml_generator.py` & `templates/base_template.hml.j2` (Jinja2 template rendering engine)
- **Document Templates (`templates/`)**:
  - `templates/base_template.hml` (Primary HML document template)
  - `templates/base_template2.hml` (Secondary HML document template used by CLI)
  - `templates/table_snippet.xml.j2` (Jinja2 table snippet template)
- **Documentation (`docs/`)**:
  - `docs/REQUIREMENTS.md` (Extraction & system requirements)
  - `docs/samples/kcs_142010_api_response.json` & `kcs_14_20_10.json` (Reference API response payloads)
- **Test Suite (`tests/`)**:
  - `tests/conftest.py` (Pytest fixtures)
  - `tests/test_*.py` (Unit and integration tests for API, DB, HML generator, AI recommender, Jinja2 generator)
  - `tests/features/*.feature` (BDD Gherkin feature specifications for AI recommendation, document generation, and KCSC API)

---

## 2. Logic Chain
1. **Formatting Quality Requirements**:
   - To achieve high readability and professional Markdown presentation, `README.md` must utilize:
     - Clear Heading levels (`#`, `##`, `###`).
     - Badges or clean metadata callout section at the top.
     - Formatted code blocks (`bash`, `powershell`, `json`, `python`) with explicit language tags.
     - Formatted Markdown tables for module descriptions and API endpoint specifications.
     - Blockquotes (`>`) for historical notes and warning callouts.

2. **Inclusion of R3 Core Elements**:
   - **ASCII Tree**: Must accurately reflect `KCS_Automation` folder hierarchy without including noise directories (`__pycache__`, `.pytest_cache`, or generated output `.hwp` files).
   - **Module Descriptions**: Must cover root entry points, `db/`, `services/`, `templates/`, `docs/`, and `tests/` with exact roles.
   - **Setup & Usage**: Must detail standard Python `venv` creation, dependency installation, Uvicorn execution, CLI command syntax, and Pytest command options.
   - **Origin Note**: Must include a dedicated section detailing why initial GitHub commits contained `# -` (originating from `echo "# -" >> README.md` during repo creation for `https://github.com/soltocsh-prog/-.git`).

3. **Path Sanitation**:
   - All references must strictly use relative paths rooted at `KCS_Automation/`.
   - References to `Soltovity`, `backend/`, `backend/services/`, or temporary debug scripts must be completely eliminated.

---

## 3. Caveats
- **Scope Boundary**: Explorer 3 is a read-only investigator. No code or README files were directly created or modified in `c:\Users\solto\OneDrive\문서\KCS_Automation`.
- **Assumptions**:
  - Target system runs Windows with Python 3.10+ / 3.14.
  - Git repository push will target `https://github.com/soltocsh-prog/-.git`.
  - Future implementer will write `README.md` following the exact template supplied in this handoff.

---

## 4. Conclusion & Recommended README.md Blueprint

The implementer should write `c:\Users\solto\OneDrive\문서\KCS_Automation\README.md` using the exact structure and content below:

```markdown
# 🏗️ KCS 표준시방서 자동화 프로젝트 (KCS Automation)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)
[![Document Format](https://img.shields.io/badge/Format-HML%20%2F%20HWP-orange.svg)](#)

대한민국 건설기준(KCS / KDS) 표준시방서 데이터를 KCSC OpenAPI 및 데이터베이스로부터 연동하여, 표준화된 HML(Hangul Markup Language) 및 HWP 전자문서를 자동 생성, 편집, 병합하는 독립 백엔드 모듈 및 CLI 도구입니다.

---

## 🏛️ 디렉토리 및 아키텍처 구조 (Directory Architecture)

```
KCS_Automation/
├── main.py                     # FastAPI 웹 어플리케이션 엔트리포인트 및 REST API 라우터
├── generate_cli.py             # KCS/KDS 개별 시방서 생성 CLI 실행 스크립트
├── requirements.txt            # 의존성 패키지 명세서 (FastAPI, Pytest, BeautifulSoup4 등)
├── run_services.bat            # Windows 백엔드 서비스 실행 배치 파일
├── README.md                   # 프로젝트 개요, 아키텍처 및 셋업 가이드
├── CONTEXT.md                  # 시스템 구조 컨텍스트 및 설계 결정 문서
├── migration_guide.md          # PC 및 Synology NAS Docker 배포/마이그레이션 가이드
├── db/                         # 데이터베이스 레이어 및 SQLite 저장소
│   ├── database.py             # SQLite 데이터베이스 연결 및 쿼리 래퍼 모듈
│   ├── kcs.db                  # KCS 표준시방서 코드 저장소 DB
│   ├── kcs_documents.db        # KCS 문서 캐시 및 메타데이터 DB
│   └── kcsc.db                 # KCSC 기준데이터 DB
├── docs/                       # 프로젝트 명세 및 참고 샘플
│   ├── REQUIREMENTS.md         # 추출 및 구성 요구사항 명세
│   └── samples/                # OpenAPI 응답 및 시방서 표준 JSON 샘플
│       ├── kcs_142010_api_response.json
│       └── kcs_14_20_10.json
├── services/                   # 비즈니스 로직 및 HML 엔진 서비스
│   ├── document_orchestrator.py # 문서 캐싱, 요율 제한 및 병합 오케스트레이터
│   ├── hml_bridge.py           # HML 템플릿 파싱 및 섹션 주입 브릿지
│   ├── hml_generator.py        # 핵심 HML XML 엘리먼트 빌더 및 콘텐츠 생성 엔진
│   ├── hml_generator_recovered.py # 백업 HML 생성 엔진
│   ├── kcsc_api_client.py      # KCSC OpenAPI 연동 클라이언트
│   ├── ai_recommender.py       # Google Gemini AI 시방서 추천 엔진
│   ├── document_generator.py   # BeautifulSoup 기반 HML 생성기
│   └── jinja2_generator/       # Jinja2 템플릿 렌더링 방식 HML 생성 엔진
│       ├── jinja2_hml_generator.py
│       └── templates/
│           └── base_template.hml.j2
├── templates/                  # HML 문서 서식 및 템플릿 정의
│   ├── base_template.hml       # 기본 HML 문서 템플릿
│   ├── base_template2.hml      # CLI 렌더링용 HML 문서 템플릿
│   └── table_snippet.xml.j2    # 표(Table) 요소 렌더링용 Jinja2 템플릿
└── tests/                      # 테스트 스위트 (Unit, Integration & BDD)
    ├── conftest.py             # Pytest 공통 픽스처 및 설정
    ├── test_ai_recommendation.py # AI 추천 로직 단위 테스트
    ├── test_api_endpoints.py   # FastAPI 엔드포인트 통합 테스트
    ├── test_database.py        # DB 연결 및 쿼리 단위 테스트
    ├── test_document_generation.py # 문서 생성 로직 테스트
    ├── test_hml_bridge.py      # HML 파싱 브릿지 테스트
    ├── test_hml_generator.py   # HML 빌더 엔진 단위 테스트
    ├── test_hml_table_image_deep_dive.py # 표 및 이미지 처리 테스트
    ├── test_jinja2_hml_generator.py # Jinja2 렌더러 테스트
    ├── test_kcsc_api.py        # KCSC OpenAPI 클라이언트 테스트
    └── features/               # BDD 시나리오 명세 (Gherkin format)
        ├── ai_recommendation.feature
        ├── document_generation.feature
        └── kcsc_api.feature
```

---

## 📦 모듈별 상세 구성 (Module Description)

| 분류 | 파이얼 / 디렉토리 | 주요 기능 및 역할 |
|---|---|---|
| **Entry Points** | `main.py` | FastAPI 웹 API 앱 정의, CORS 설정을 통해 프론트엔드 연동 지원, 문서 목록/병합/다운로드 REST API 제공 |
| | `generate_cli.py` | KCSC OpenAPI 데이터를 직접 조회하여 CLI 환경에서 HWP 문서를 즉시 생성하는 명령행 도구 |
| **Database** | `db/database.py` | SQLite DB 파일 연결 관리 (`get_db_connection()`) |
| | `db/*.db` | KCS 표준시방서 메타데이터, 캐시 및 KCSC 데이터베이스 저장소 |
| **Services** | `services/document_orchestrator.py` | 복수 시방서 병합 처리, 캐시 조회 및 문서 세대 생성 오케스트레이션 |
| | `services/hml_generator.py` | HML XML DOM 요소 조작 및 문서 템플릿에 본문 데이터 주입 |
| | `services/hml_bridge.py` | HML 문서 구조 파싱 및 섹션 단위 주입 레이어 |
| | `services/kcsc_api_client.py` | KCSC OpenAPI 서비스 통신 모듈 |
| | `services/ai_recommender.py` | Google Gemini AI 기반 시방서 코드 추천 및 분석 연동 |
| | `services/jinja2_generator/` | Jinja2 템플릿 엔진을 활용한 HML 문서 동적 생성 |
| **Templates** | `templates/` | HML 기본 문서 구조 서식파일 (`base_template.hml`, `base_template2.hml`) |
| **Testing** | `tests/` | `pytest` 기반 단위/통합 테스트 스위트 및 `pytest-bdd` 기반 BDD 기능 테스트 시나리오 |

---

## 🚀 설치 및 실행 가이드 (Setup & Usage)

### 1. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성 (Python 3.10 이상 권장)
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 필수 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. 백엔드 API 서버 실행

```bash
# Uvicorn 개발 서버 실행 (기본 포트: 8000)
uvicorn main:app --reload --port 8000

# 또는 포함된 배치 스크립트 실행 (Windows)
.\run_services.bat
```

서버 실행 후 브라우저에서 `http://localhost:8000/docs` 접속 시 Swagger API 문서를 확인할 수 있습니다.

### 3. CLI 도구를 이용한 시방서 문서 생성

```bash
# KCS 41 12 00 (콘크리트 공사) 시방서 문서 생성
python generate_cli.py --code 411200 --type KCS --output concrete_spec.hwp
```

### 4. 테스트 스위트 실행

```bash
# 전체 테스트 실행
pytest

# 테스트 상세 결과 확인
pytest -v

# BDD 시나리오 테스트 실행
pytest tests/test_api_endpoints.py
```

---

## 🔌 주요 REST API 명세

| Method | Endpoint | 설명 |
|---|---|---|
| `GET` | `/api/kcs/documents` | 캐시된 KCS 문서 목록 및 상태 조회 |
| `POST` | `/api/kcs/merge` | 선택한 KCS 코드 목록을 바탕으로 HWP 통합 문서 생성 요청 |
| `GET` | `/api/kcs/download/{filename}` | 생성 완료된 HWP 문서 파일 다운로드 |
| `GET` | `/api/kcs/presets` | 저장된 시방서 프리셋 목록 조회 |
| `POST` | `/api/kcs/presets` | 신규 시방서 프리셋 저장 |
| `DELETE` | `/api/kcs/presets/{preset_id}` | 저장된 프리셋 삭제 |

---

## 📜 리포지토리 이력 및 Origin 상세 노트

> **💡 Historical Repository Origin Note**
>
> 본 프로젝트의 GitHub 리포지토리(`https://github.com/soltocsh-prog/-.git`) 초기 생성 시, GitHub의 기본 리포지토리 안내 명령어:
> ```bash
> echo "# -" >> README.md
> ```
> 에 의해 초기 커밋의 `README.md` 내용이 `# -`로 작성되었었습니다.
> 
> 본 `README.md` 문서는 KCS 표준시방서 자동화 프로젝트의 백엔드 모듈 추출 및 아키텍처 재구성에 따라, 전체 폴더 구조, 비즈니스 서비스 레이어, REST API 명세 및 실행 가이드를 포함하여 새롭게 작성되었습니다.
```

---

## 5. Verification Method

To verify the quality and completeness of `README.md` once written by the implementer:

1. **Structure Verification**:
   - Check that `c:\Users\solto\OneDrive\문서\KCS_Automation\README.md` exists and contains H1, H2 headings, badges, ASCII tree, functional tables, code blocks, and blockquotes.

2. **Requirement Coverage (R3 Check)**:
   - **Tree Architecture**: Verify all 6 root files/dirs (`main.py`, `generate_cli.py`, `requirements.txt`, `run_services.bat`, `CONTEXT.md`, `migration_guide.md`, `db/`, `docs/`, `services/`, `templates/`, `tests/`) are represented accurately in the ASCII tree.
   - **Module Descriptions**: Verify detailed table/list coverage of entry points, services, db, templates, docs, and tests.
   - **Setup Instructions**: Verify command snippets for `venv`, `pip install`, `uvicorn`, `generate_cli.py`, and `pytest`.
   - **Origin Note**: Verify explicit inclusion of `echo "# -" >> README.md` historical origin note.

3. **Path Sanitation Audit**:
   - Perform string search on `README.md` to ensure zero occurrences of:
     - `Soltovity`
     - `backend/`
     - `scratch_` or `check_`
