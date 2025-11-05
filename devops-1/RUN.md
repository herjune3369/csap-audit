# 🚀 devops-1 실행 가이드

## 📋 devops-1란?
- **Google Gemini API** 기반 보안 진단 시스템
- **devops-2**와 달리 외부 API를 사용하여 빠른 분석 제공
- **JSON 파일 업로드** → **Gemini AI 분석** → **Excel 리포트 생성**
- **GitHub Actions**를 통한 자동화된 AWS 배포 지원

---

## 🎯 실행 방법 (3가지)

### 방법 1: GitHub Actions 자동 배포 (AWS) - 프로덕션 ⭐⭐⭐
### 방법 2: 웹 인터페이스 (로컬 Flask 앱) - 개발/테스트 ⭐⭐
### 방법 3: 명령줄 (CLI) - 빠른 테스트 ⭐

---

## 🚀 방법 1: GitHub Actions 자동 배포 (AWS)

### **devops-1의 주요 실행 방식**
devops-1은 **GitHub Actions**를 통해 AWS에 자동 배포됩니다.

### **워크플로우 파일 위치**
```
.github/workflows/devops-1-workflow.yml
```

### **자동 트리거 조건**
1. **코드 푸시 시 자동 실행**
   - `main` 또는 `develop` 브랜치에 푸시
   - `devops-1/**` 경로의 파일이 변경됨

2. **Pull Request 시 검증**
   - `main` 브랜치로 PR 생성 시
   - Terraform 코드 검증만 수행

3. **수동 실행 (workflow_dispatch)**
   - GitHub Actions 탭에서 수동 실행 가능
   - 환경 선택: dev, staging, prod

---

### **워크플로우 단계**

#### **1단계: Validate (코드 검증)**
- Terraform 코드 포맷 확인
- Terraform 초기화 및 검증
- Terraform Plan 실행

#### **2단계: Deploy Infrastructure (인프라 배포)**
- AWS 인프라 자동 생성 (Terraform)
- VPC, EC2, RDS, ALB 등 생성
- Terraform outputs 저장

#### **3단계: Deploy Application (애플리케이션 배포)**
- Ansible을 통한 Flask 앱 배포
- EC2 인스턴스에 애플리케이션 설치
- 서비스 시작 및 설정

#### **4단계: Notify (배포 알림)**
- 배포 결과 알림

---

### **GitHub Actions 실행 방법**

#### **방법 A: 코드 푸시로 자동 실행**
```bash
# devops-1 브랜치 또는 main 브랜치에 푸시
git add devops-1/
git commit -m "Update devops-1"
git push origin main  # 또는 develop
```

**자동 실행 조건:**
- `devops-1/**` 경로의 파일이 변경됨
- `main` 또는 `develop` 브랜치에 푸시

---

#### **방법 B: 수동 실행 (workflow_dispatch)**
1. GitHub 저장소 접속
2. **Actions** 탭 클릭
3. **DevOps Infrastructure Automation** 워크플로우 선택
4. **Run workflow** 버튼 클릭
5. 환경 선택:
   - `dev` (개발 환경)
   - `staging` (스테이징 환경)
   - `prod` (프로덕션 환경)
6. **Run workflow** 클릭

---

### **GitHub Secrets 설정**

GitHub 저장소의 **Settings > Secrets and variables > Actions**에서 설정:

1. **AWS_ACCESS_KEY_ID**
   - AWS 액세스 키 ID

2. **AWS_SECRET_ACCESS_KEY**
   - AWS 시크릿 액세스 키

3. **SSH_PRIVATE_KEY**
   - EC2 인스턴스 접속용 SSH 개인 키
   - Ansible 배포 시 사용

4. **GEMINI_API_KEY** (선택사항)
   - Gemini API 키 (애플리케이션에서 사용)

---

### **배포된 애플리케이션 접근**

배포 완료 후 Terraform outputs에서 URL 확인:

1. **GitHub Actions 로그 확인**
   - Actions 탭 > 최근 실행 > Terraform outputs 확인

2. **Terraform outputs 확인**
   ```bash
   cd devops-1/terraform
   terraform output
   ```

3. **ALB DNS 이름으로 접근**
   ```
   http://<alb-dns-name>.ap-northeast-2.elb.amazonaws.com
   ```

---

### **배포 상태 확인**

1. **GitHub Actions 탭**
   - 각 단계별 실행 상태 확인
   - 로그 확인 및 디버깅

2. **AWS 콘솔**
   - EC2 인스턴스 상태 확인
   - ALB Health Check 확인
   - CloudWatch 로그 확인

---

### **워크플로우 파일 구조**

```yaml
name: DevOps Infrastructure Automation

on:
  push:
    branches: [ main, develop ]
    paths: [ 'devops-1/**' ]
  workflow_dispatch:
    inputs:
      environment:
        options: [ dev, staging, prod ]

jobs:
  validate:
    - Terraform 코드 검증
    
  deploy-infrastructure:
    - AWS 인프라 배포 (Terraform)
    
  deploy-application:
    - Flask 앱 배포 (Ansible)
    
  notify:
    - 배포 결과 알림
```

---

## 💻 방법 2: 웹 인터페이스 실행 (로컬)

### **1단계: Google Gemini API 키 준비**

#### Google AI Studio에서 API 키 발급:
1. https://makersuite.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. API 키 복사

#### 환경 변수 설정:
```bash
# .env 파일 생성 (flask_app 디렉토리)
cd devops-1/scripts/cce-diagnostics/flask_app
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

또는 시스템 환경 변수로 설정:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

---

### **2단계: 프로젝트 디렉토리로 이동**
```bash
cd /Users/junheo/devsecops-lab/csap-audit/devops-1/scripts/cce-diagnostics/flask_app
```

---

### **3단계: Python 가상환경 설정**

#### 가상환경 생성 (처음 한 번만):
```bash
python3 -m venv venv
```

#### 가상환경 활성화:
```bash
# macOS/Linux
source venv/bin/activate
```

---

### **4단계: 의존성 설치**

```bash
# Flask 앱 디렉토리에서
pip install -r requirements.txt

# Google Gemini API 추가 설치
pip install google-generativeai python-dotenv
```

필요한 패키지:
- `flask>=2.3.0`
- `google-generativeai` (Gemini API)
- `pandas>=1.5.0`
- `openpyxl>=3.0.0`
- `python-dotenv>=1.0.0`

---

### **5단계: Flask 앱 실행**

```bash
python3 app.py
```

**출력 예시:**
```
INFO:__main__:CSAP 기술진단 SaaS 플랫폼 시작...
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

---

### **6단계: 웹 브라우저 접속**

브라우저에서 다음 주소로 접속:
```
http://localhost:5001
```

---

### **7단계: JSON 파일 업로드 및 리포트 생성**

1. **JSON 파일 준비**
   - `../output/real_linux_result.json` 파일 사용 가능
   - 또는 자체 보안 진단 JSON 파일 (필수 필드: `results` 배열)

2. **웹 페이지에서 업로드**
   - "파일 선택" 버튼 클릭
   - JSON 파일 선택
   - "업로드" 버튼 클릭

3. **Gemini AI 분석 대기**
   - Google Gemini API로 분석 (약 1-2분 소요)
   - 진행 상황이 콘솔에 표시됨

4. **Excel 리포트 다운로드**
   - 분석 완료 후 "다운로드" 버튼 클릭
   - 파일명: `csap_linux_report_YYYYMMDD_HHMMSS.xlsx`

---

## 💻 방법 3: 명령줄 (CLI) 실행 (로컬)

### **1단계: Google Gemini API 키 설정**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

---

### **2단계: 프로젝트 디렉토리로 이동**
```bash
cd /Users/junheo/devsecops-lab/csap-audit/devops-1/scripts/cce-diagnostics/scripts
```

---

### **3단계: Python 가상환경 설정**
```bash
# 가상환경 생성 (처음 한 번만)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

---

### **4단계: 의존성 설치**
```bash
pip install -r requirements.txt
pip install google-generativeai python-dotenv
```

---

### **5단계: 리포트 생성 스크립트 실행**
```bash
python3 run_llm_pipeline.py
```

또는

```bash
python3 llm_report_generator.py
```

**출력 예시:**
```
INFO:__main__:JSON 파일 로드 완료: ../output/real_linux_result.json
INFO:__main__:총 36개 항목 로드 완료
INFO:__main__:Gemini API 분석 시작...
...
INFO:__main__:Excel 리포트 생성 완료: output/csap_linux_report_YYYYMMDD_HHMMSS.xlsx
```

---

### **6단계: 생성된 Excel 파일 확인**
```bash
# 파일 목록 확인
ls -la output/*.xlsx

# Excel 파일 열기 (macOS)
open output/csap_linux_report_*.xlsx
```

---

## 🔧 문제 해결

### **문제 1: GEMINI_API_KEY를 찾을 수 없습니다**

```bash
# .env 파일 확인
cat devops-1/scripts/cce-diagnostics/flask_app/.env

# 환경 변수 확인
echo $GEMINI_API_KEY

# .env 파일 생성 또는 수정
echo "GEMINI_API_KEY=your-api-key-here" > devops-1/scripts/cce-diagnostics/flask_app/.env
```

---

### **문제 2: 모듈을 찾을 수 없습니다 (ModuleNotFoundError)**

```bash
# 가상환경 활성화 확인
which python3  # venv/bin/python3 이어야 함

# 가상환경 재활성화
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
pip install google-generativeai python-dotenv
```

---

### **문제 3: 포트 5001이 이미 사용 중입니다**

```bash
# 포트 사용 확인
lsof -i :5001

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
# app.py 파일에서 port=5001을 다른 포트로 변경
```

---

### **문제 4: Gemini API 호출 실패**

```bash
# API 키 확인
echo $GEMINI_API_KEY

# API 키 재설정
export GEMINI_API_KEY="your-api-key-here"

# .env 파일 확인
cat .env
```

**API 키 발급 위치:**
- https://makersuite.google.com/app/apikey

---

## 📂 파일 구조

```
devops-1/
├── scripts/
│   └── cce-diagnostics/
│       ├── flask_app/              # 웹 인터페이스
│       │   ├── app.py              # Flask 앱 (메인)
│       │   ├── requirements.txt    # Flask 앱 의존성
│       │   ├── .env                # 환경 변수 (GEMINI_API_KEY)
│       │   ├── uploads/            # 업로드된 JSON 파일
│       │   ├── reports/            # 생성된 Excel 리포트
│       │   └── templates/         # HTML 템플릿
│       │       └── upload.html
│       │
│       └── scripts/                # CLI 스크립트
│           ├── llm_report_generator.py  # 메인 리포트 생성기
│           ├── llm_caller.py            # Gemini API 호출기
│           ├── requirements.txt         # 스크립트 의존성
│           └── output/                  # 생성된 Excel 파일
│
└── output/                          # JSON 진단 결과
    └── real_linux_result.json      # 테스트용 JSON 파일
```

---

## 🎯 주요 명령어 요약

```bash
# 1. API 키 설정
export GEMINI_API_KEY="your-api-key-here"
# 또는
echo "GEMINI_API_KEY=your-api-key-here" > .env

# 2. 웹 인터페이스 실행
cd devops-1/scripts/cce-diagnostics/flask_app
source venv/bin/activate
pip install -r requirements.txt google-generativeai python-dotenv
python3 app.py
# → http://localhost:5001 접속

# 3. CLI 실행
cd devops-1/scripts/cce-diagnostics/scripts
source venv/bin/activate
pip install -r requirements.txt google-generativeai python-dotenv
python3 run_llm_pipeline.py
```

---

## ✅ 체크리스트

실행 전 확인사항:
- [ ] Google Gemini API 키 발급 완료
- [ ] GEMINI_API_KEY 환경 변수 설정 완료
- [ ] Python 가상환경 생성 및 활성화
- [ ] 의존성 설치 완료 (`pip install -r requirements.txt google-generativeai python-dotenv`)
- [ ] JSON 파일 준비 (`real_linux_result.json` 또는 자체 파일)
- [ ] 인터넷 연결 확인 (Gemini API 호출 필요)

---

## 🔄 실행 방법 비교

### **GitHub Actions (AWS 배포) vs 로컬 실행**

| 항목 | GitHub Actions (AWS) | 로컬 실행 |
|------|---------------------|----------|
| **대상** | 프로덕션 환경 | 개발/테스트 |
| **인프라** | AWS 자동 생성 | 로컬 환경 |
| **접근** | ALB DNS | localhost:5001 |
| **비용** | AWS 사용료 | 무료 |
| **설정** | GitHub Secrets | .env 파일 |
| **자동화** | 완전 자동화 | 수동 실행 |

---

## 🔄 devops-1 vs devops-2 비교

| 항목 | devops-1 | devops-2 |
|------|----------|----------|
| **LLM** | Google Gemini API | 로컬 LLM (Ollama) |
| **인터넷** | 필수 | 불필요 |
| **비용** | API 사용료 | 무료 |
| **속도** | 빠름 (1-2분) | 느림 (5-10분) |
| **데이터 보안** | 외부 전송 | 로컬 처리 |
| **포트** | 5001 | 6001 |
| **API 키** | GEMINI_API_KEY 필요 | 불필요 |

---

## 📞 추가 도움말

- **Google Gemini API 문서**: https://ai.google.dev/docs
- **Flask 문서**: https://flask.palletsprojects.com/
- **프로젝트 구조**: `devops-1/README.md` 참고

---

**🎉 준비 완료! 이제 devops-1을 실행할 수 있습니다!**

