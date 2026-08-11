# 🚚 KCS 시방서 자동화 엔진 마이그레이션 & 설치 가이드

이 문서는 개발 PC에서 작동하던 **KCS 시방서 자동화 백엔드 엔진(KCS_Automation)**을 **다른 일반 PC** 또는 **Synology NAS**로 안전하게 이전(Migration)하고 실행하는 방법을 안내합니다.

---

## 📦 1단계: 프로젝트 복사하기

원래 컴퓨터의 프로젝트 폴더를 복사해서 새 컴퓨터로 옮깁니다.

* **프로젝트 폴더 위치:** `C:\Users\solto\OneDrive\문서\KCS_Automation`

### ⚠️ 중요: 파이썬 가상환경 폴더 제외
용량이 크거나 환경에 맞게 재생성해야 하는 가상환경 폴더(`.venv` 또는 `venv`, `__pycache__`)는 복사에서 제외하거나 지운 후 복사합니다.

---

## 💻 2단계 (방법 A): 새로운 "일반 PC"에 설치하고 실행하기

새로운 컴퓨터(Windows 또는 macOS)에서 직접 구동하고 싶을 때 사용하는 방법입니다.

### 1. 필수 프로그램 설치
* **Python (3.9 이상 버전):** 백엔드 API 서버 및 CLI 실행 필수 도구

### 2. 프로젝트 폴더 이동
터미널(Terminal) 또는 명령 프롬프트(cmd)를 열고 `KCS_Automation` 폴더로 이동합니다:
```bash
cd C:\Users\solto\OneDrive\문서\KCS_Automation
```

### 3. 의존성 패키지 설치
`KCS_Automation` 루트 디렉토리에서 필요한 파이썬 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

### 4. 프로그램 실행

#### ① FastAPI REST API 서버 실행
루트 폴더에서 아래 명령어를 실행하여 백엔드 API 서버를 켭니다:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
* 접속 확인: 브라우저에서 `http://localhost:8000/docs` 접속 (Swagger API 문서 확인)

#### ② CLI 커맨드라인 자동화 실행 (선택)
독립 실행형 CLI 스크립트로 HML 문서를 바로 생성할 때 실행합니다:
```bash
python generate_cli.py --kcs-code 142010
```

---

## 🐳 3단계 (방법 B): "Synology NAS"에 도커(Docker)로 실행하기

NAS에 24시간 백엔드 서비스를 켜두고 외부/사내 서비스와 연동할 때 사용하는 방법입니다.

### 1. NAS에 Container Manager 설치
1. Synology NAS 패키지 센터 접속
2. **`Container Manager`** (구버전: **`Docker`**) 설치

### 2. 파일 업로드
NAS File Station에서 `docker/kcs-automation` 폴더를 생성하고 `KCS_Automation` 프로젝트 파일 전체를 업로드합니다.

### 3. Docker Compose로 백엔드 서비스 실행
1. **Container Manager** 실행 -> **프로젝트 (Project)** -> **생성 (Create)**
2. 프로젝트 설정:
   * **프로젝트 이름:** `kcs-automation`
   * **경로:** `docker/kcs-automation`
   * **소스:** `docker-compose.yml 생성`
3. 아래 `docker-compose.yml` 내용을 붙여넣습니다:

```yaml
version: '3.8'
services:
  kcs-backend:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    command: sh -c "pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000"
    restart: always
```

4. 완료 버튼을 누르면 NAS가 자동으로 파이썬 컨테이너를 빌드하고 `http://[NAS_IP]:8000`에서 백엔드 서비스를 시작합니다.

---

## 🛠️ 문제 해결 (Troubleshooting)

### Q. 외부 프론트엔드 웹 앱에서 API 연동 시 CORS 오류 또는 연결 불가 발생
* **원인:** 프론트엔드 앱이 이전 백엔드 주소(`http://127.0.0.1:8000`)를 바라보고 있거나 API 엔드포인트 설정이 변경된 경우입니다.
* **해결법:**
  1. 외부 프론트엔드(예: ArchHub / Soltovity 웹 대시보드)의 API 설정 파일에서 Base URL을 수정합니다:
     ```javascript
     const API_BASE_URL = 'http://[새로운 PC 또는 NAS IP]:8000/api';
     ```
  2. `KCS_Automation/main.py`에 CORS 미들웨어가 등록되어 있는지 확인합니다. (`http://localhost:5173` 및 사용자 IP 허용)
