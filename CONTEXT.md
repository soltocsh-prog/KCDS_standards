# 🏛️ KCS Automation System Context & Architecture Overview

> **Context Clarification**: `KCS_Automation` is a **standalone modularized Python backend microservice and CLI tool** extracted from the broader ArchHub / Soltovity workspace. It handles Korean Construction Specification (KCS - 한국건설기준 표준시방서) database querying, HML/HWP document generation, and Gemini AI specification recommendation.

---

## 0. Standalone KCS Automation Engine Context

### 0.1 Scope & System Boundary
* **Core Purpose**: Standalone generation, parsing, and manipulation of Korean Construction Specification (KCS) HML/HWP documents.
* **Architecture Style**: Modularized Python microservice (FastAPI REST API) + Headless CLI tool runner (`generate_cli.py`).
* **Storage Layer**: Embedded SQLite databases (`db/kcs.db`, `db/kcsc.db`, `db/kcs_documents.db`) containing specification text, mapping rules, and metadata.
* **Template & Generation Engine**: Jinja2 templates + BeautifulSoup HML XML manipulation (`services/hml_generator.py`, `services/hml_bridge.py`, `services/jinja2_generator/`).
* **AI Integration**: Google Gemini API client (`services/ai_recommender.py`) for automated spec section recommendation.

### 0.2 Integration Points & Deployment
* **REST API**: Listens on `http://0.0.0.0:8000` (Endpoints: `/api/specs`, `/api/generate-hml`, `/api/ai-recommend`, `/health`).
* **Headless CLI Execution**: Runs via `python generate_cli.py --kcs-code <code_number>` for batch or local pipeline automation.
* **Client Consumers**: Serves external web frontends (e.g., ArchHub / Soltovity React app) or desktop tools over standard HTTP REST API calls.

---

## 📜 Historical Workspace Context (ArchHub / Soltovity Parent Context)

본 문서는 ArchHub 프로젝트의 현재 개발 진행 상황, 핵심 기술 스택, 그리고 주요 아키텍처 결정 사항을 기록하여 개발 연속성을 유지하기 위해 작성되었습니다.

## 1. 프로젝트 개요
*   **프로젝트명**: ArchHub
*   **목표**: 건축 설계 실무자를 위한 사내 AI/SaaS 도구 통합 및 노하우 공유 워크스페이스(PWA).
*   **개발 철학**: Lean & Pragmatic. 불필요한 테스트 코드(BDD 등) 작성을 지양하고, 실제 UI와 사용자 경험(UX) 중심의 빠른 프로토타이핑 및 개발을 최우선으로 합니다.

## 2. 핵심 기술 스택
*   **프레임워크**: React + Vite (빠른 빌드와 HMR 지원)
*   **스타일링**: Tailwind CSS (유틸리티 클래스 기반의 빠른 UI 구성)
*   **라우팅**: React Router DOM (3단 레이아웃 내에서의 원활한 페이지 전환 및 상태 유지)
*   **상태 관리**: React Context API + LocalStorage (별도의 백엔드 없이 사용자별 워크플로우 커스텀 설정 유지)
*   **PWA**: `vite-plugin-pwa` (앱 설치 및 서비스 워커 기반 캐싱)

## 3. 주요 결정 사항 (Key Decisions)

### 3.1. 외부 SaaS Iframe 임베딩과 보안 한계
*   **이슈**: NotebookLM, Pinterest 등 최신 SaaS는 자체 보안 정책(X-Frame-Options, CSP)으로 인해 다른 웹사이트(ArchHub)의 `<iframe>` 내부에서 열리는 것을 차단합니다.
*   **현재 결정 (웹앱 단계)**: Iframe 차단 서비스의 경우, 메인 스테이지에 안내 문구를 띄우고 **[새 창에서 열기]** 버튼을 제공하는 우회 방식을 채택했습니다. (사이드바 탭 상태는 유지됨)
*   **향후 계획**: 이 문제는 브라우저 정책이므로 웹앱에서는 완벽한 해결이 불가능합니다. 추후 [Phase 4]에서 **Electron 또는 Tauri 기반의 데스크탑 앱**으로 전환 시, 자체 Webview를 통해 보안 정책을 우회하여 내부에 강제로 띄울 예정입니다.

### 3.2. 통합 계정 금고 (Vault) 및 자동 로그인
*   **이슈**: 사용자가 비밀번호를 입력해 두면 외부 사이트 로그인 창에 자동으로 주입(Auto-fill)하는 기능 구현 여부.
*   **현재 결정**: 브라우저 기반의 Same-Origin Policy로 인해 다른 도메인의 Iframe에 스크립트를 주입하는 것은 보안상 불가능합니다. 따라서 '비밀번호 자동 주입' 기능은 개발하지 않기로 결정했습니다.
*   **대안**: Vault를 '사내 공용 계정 게시판' 및 '내 워크플로우에 새 툴을 추가하는 도구 관리소' 역할로 정의했습니다. 툴 자체의 자동 로그인은 사용 중인 웹 브라우저(Chrome, Edge 등)의 기본 세션/쿠키 유지 기능을 그대로 활용합니다.

### 3.3. 동적 워크플로우 아키텍처 (Dynamic Workflows)
*   초기에는 고정된 JSON 데이터(`workflows.js`)를 사용했으나, 사용자가 직접 개인용 SaaS 도구를 원하는 워크플로우(예: 디자인 베이스)에 추가할 수 있도록 **React Context와 LocalStorage를 결합한 동적 상태 관리 구조**로 리팩토링했습니다.

---

## 4. 현재 개발 진행 상황 (Status)

**✅ Phase 1 & 2: 기초 뼈대 및 SaaS 대시보드 (완료)**
*   3단 패널 레이아웃 (사이드바, 메인 스테이지, 도움말 바)
*   React Router 기반의 다중 탭 관리 및 워크플로우별 대시보드 UI
*   Iframe 래퍼 컴포넌트 (`SaaSViewer`) 및 차단 사이트 예외 처리
*   PWA 설치 가능하도록 Manifest 및 플러그인 세팅

**🔄 Phase 3: 사내 데이터 통합 (+a) (진행 중)**
*   ✅ **공용 캘린더 연동**: 여러 구글 캘린더 ID를 중첩해서 렌더링하고 관리하는 기능 (`CalendarPage`, `CalendarWidget`)
*   ✅ **스크립트 & 리소스 뱅크 UI**: 아코디언 메뉴, 태그 필터링, 프리미엄 카드 UI 구축 (`ResourcesPage`)
*   ✅ **동적 워크플로우 & Vault UI**: 새로운 툴 추가 및 삭제 로직을 Context에 구현하고, 이를 관리하는 `VaultPage` 구축
*   ⏳ **동적 매뉴얼 (Help Bar)**: 우측 매뉴얼 바를 정적 텍스트가 아닌, 사용자가 직접 각 툴의 마크다운 가이드를 작성하고 저장할 수 있는 기능 **(다음 개발 목표)**

**⏳ Phase 4: 데스크탑 셸 및 운영 고도화 (대기)**
*   Electron 도입, Iframe 차단 무력화, 파일 시스템 다이렉트 연동 등.
