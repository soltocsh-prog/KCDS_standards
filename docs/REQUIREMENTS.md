# Original User Request

## 2026-08-11T07:01:02Z

<USER_REQUEST>
# Teamwork Project Prompt — Draft

> Status: Ready for launch — awaiting user approval.
> Goal: Craft prompt → get user approval → delegate to teamwork_preview

KCS 표준시방서 자동화 프로젝트의 핵심 파일을 추출하여 모듈화된 별도 폴더에 정리하고, README 작성 및 GitHub에 업로드합니다.

Working directory: c:\Users\solto\OneDrive\문서\KCS_Automation
Integrity mode: development

## Requirements

### R1. 핵심 파일 추출 및 폴더 구성
Soltovity 워크스페이스 내에서 KCS 표준시방서 자동화와 관련된 핵심 백엔드 파이썬 파일(main.py, services, templates, db, tests 등)만 선별하여 `c:\Users\solto\OneDrive\문서\KCS_Automation` 폴더로 복사합니다. 임시/디버깅 스크립트(`scratch_*.py`, `check_*.py` 등)는 제외합니다. 기존 워크스페이스(`Soltovity`)의 파일은 절대 삭제하거나 훼손하지 않습니다.

### R2. 관련 문서 및 이슈 포함
기존에 작성된 관련된 기획 문서, 컨텍스트 문서(CONTEXT.md 등)나 마이그레이션 이슈 가이드(migration_guide.md) 등을 새 프로젝트에 포함하여 문서적으로 완성된 구조를 만듭니다.

### R3. 아키텍처 정리 및 README 작성
새로 구성된 폴더의 아키텍처(파일 및 디렉토리 구조)를 트리 형태로 명확히 정리한 `README.md`를 작성합니다. 또한, 현재 GitHub에 작성되어 있는 기존 README(내용이 `# -`로만 되어 있는 것)의 출처가 GitHub의 초기 리포지토리 생성 안내 명령어(`echo "# -" >> README.md`)에서 온 것임을 README 문서나 로그에 명시합니다.

### R4. 로깅 및 GitHub 업로드
복사된 파일들의 전체 목록(로그)을 작성하여 사용자에게 보고합니다. 이후 새 폴더(`KCS_Automation`)를 Git으로 초기화하고, 사용자 지정 리포지토리에 푸시(Push)하여 업로드합니다.

## Acceptance Criteria

### 구조 및 파일 검증
- [ ] 핵심 실행 및 서비스 코드(`main.py`, `services/`, `templates/`, `db/`)가 KCS_Automation 폴더에 복사되어야 합니다.
- [ ] 임시 스크립트 파일이 KCS_Automation 폴더 내에 존재하지 않아야 합니다.

### 문서화
- [ ] `README.md` 파일에 전체 폴더 아키텍처가 트리 형태로 문서화되어 있어야 합니다.
- [ ] 관련 참고 문서(`migration_guide.md`, `CONTEXT.md` 등)가 새 폴더에 복사되어야 합니다.

### 로깅 및 업로드
- [ ] 작업 완료 후 콘솔 또는 파일 형태의 명시적인 복사 파일 목록 로그가 제공되어야 합니다.
- [ ] KCS_Automation 폴더가 git push를 통해 성공적으로 GitHub에 업로드되어야 합니다.
</USER_REQUEST>
