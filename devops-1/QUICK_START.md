# 🚀 devops-1 빠른 실행 가이드

## 📋 실행 방법

### **방법 1: GitHub Actions 자동 배포 (AWS) - 프로덕션** ⭐⭐⭐
- GitHub Actions를 통해 AWS에 자동 배포
- 코드 푸시 시 자동 실행
- 또는 수동 실행 (workflow_dispatch)

### **방법 2: 로컬 실행 (개발/테스트)** ⭐⭐
- 로컬에서 Flask 앱 실행
- localhost:5001 접속

---

## 🚀 방법 1: GitHub Actions 자동 배포

### **자동 실행 (코드 푸시)**
```bash
git add devops-1/
git commit -m "Update devops-1"
git push origin main  # 또는 develop
```

### **수동 실행**
1. GitHub 저장소 > **Actions** 탭
2. **DevOps Infrastructure Automation** 선택
3. **Run workflow** 클릭
4. 환경 선택 (dev/staging/prod)
5. **Run workflow** 클릭

### **필요한 GitHub Secrets**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SSH_PRIVATE_KEY`
- `GEMINI_API_KEY` (선택)

### **배포된 애플리케이션 접근**
```
http://<alb-dns-name>.ap-northeast-2.elb.amazonaws.com
```

---

## 💻 방법 2: 로컬 실행

### ✅ 사전 준비

1. **Google Gemini API 키 발급**
   - https://makersuite.google.com/app/apikey 접속
   - API 키 복사

2. **Python 가상환경 준비**
   - Python 3.7 이상 필요

---

## 🎯 방법 1: 웹 인터페이스 실행 (3단계)

### **터미널에서 실행**

```bash
# 1. 디렉토리 이동
cd /Users/junheo/devsecops-lab/csap-audit/devops-1/scripts/cce-diagnostics/flask_app

# 2. 가상환경 활성화 (없으면 생성)
python3 -m venv venv  # 처음 한 번만
source venv/bin/activate

# 3. 의존성 설치 및 Flask 앱 실행
pip install -r requirements.txt google-generativeai python-dotenv
export GEMINI_API_KEY="your-api-key-here"  # API 키 설정
python3 app.py
```

**출력 예시:**
```
INFO:__main__:CSAP 기술진단 SaaS 플랫폼 시작...
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

---

### **브라우저에서 접속**

```
http://localhost:5001
```

---

### **JSON 파일 업로드**

1. **테스트용 JSON 파일 위치:**
   ```
   ../output/real_linux_result.json
   ```

2. **웹 페이지에서:**
   - "파일 선택" 버튼 클릭
   - `real_linux_result.json` 선택
   - "업로드" 버튼 클릭
   - Gemini AI 분석 대기 (약 1-2분)
   - "다운로드" 버튼으로 Excel 리포트 다운로드

---

## 🎯 방법 2: 명령줄 (CLI) 실행 (2단계)

### **터미널에서 실행**

```bash
# 1. 디렉토리 이동
cd /Users/junheo/devsecops-lab/csap-audit/devops-1/scripts/cce-diagnostics/scripts

# 2. 가상환경 활성화 (필요시)
source ../flask_app/venv/bin/activate

# 3. API 키 설정 및 리포트 생성
export GEMINI_API_KEY="your-api-key-here"
python3 run_llm_pipeline.py
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

## 📁 생성된 파일 위치

### **웹 인터페이스 사용 시:**
```
devops-1/scripts/cce-diagnostics/flask_app/reports/
  └── csap_linux_report_YYYYMMDD_HHMMSS.xlsx
```

### **CLI 사용 시:**
```
devops-1/scripts/cce-diagnostics/scripts/output/
  └── csap_linux_report_YYYYMMDD_HHMMSS.xlsx
```

---

## 🔧 문제 해결

### **포트 5001이 이미 사용 중**
```bash
# 포트 사용 확인
lsof -i :5001

# 프로세스 종료
kill -9 <PID>
```

### **Gemini API 키 확인**
```bash
# 환경 변수 확인
echo $GEMINI_API_KEY

# .env 파일 확인
cat devops-1/scripts/cce-diagnostics/flask_app/.env

# API 키 재설정
export GEMINI_API_KEY="your-api-key-here"
```

### **모듈 오류**
```bash
# 가상환경 재활성화
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt google-generativeai python-dotenv
```

---

## 📝 주요 명령어 요약

```bash
# 웹 인터페이스
cd devops-1/scripts/cce-diagnostics/flask_app
source venv/bin/activate
export GEMINI_API_KEY="your-api-key-here"
python3 app.py
# → http://localhost:5001 접속

# CLI
cd devops-1/scripts/cce-diagnostics/scripts
source ../flask_app/venv/bin/activate
export GEMINI_API_KEY="your-api-key-here"
python3 run_llm_pipeline.py
```

---

**🎉 준비 완료! 바로 실행하세요!**

