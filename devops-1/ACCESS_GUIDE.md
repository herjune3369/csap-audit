# 🌐 devops-1-security-app 접속 및 사용 가이드

## ✅ 배포 완료 확인

GitHub Actions 실행이 성공했다면, 다음 단계로 접속 정보를 확인하세요.

---

## 📍 접속 정보 확인 방법

### 방법 1: GitHub Actions 로그에서 확인

1. **GitHub 저장소 → Actions 탭**
   ```
   https://github.com/herjune3369/csap-audit/actions
   ```

2. **최신 실행 클릭 → Deploy Infrastructure Job 클릭**

3. **"Save Terraform outputs" 단계에서 출력 확인**
   - `alb_dns_name`: ALB DNS 이름
   - `web1_public_ip`: 웹서버1 공인 IP
   - `web2_public_ip`: 웹서버2 공인 IP
   - `rds_endpoint`: RDS 엔드포인트

### 방법 2: Terraform Output 명령어로 확인

```bash
cd devops-1/terraform
terraform output
```

**출력 예시:**
```
alb_dns_name = "devops-1-app-lb-1234567890.ap-northeast-2.elb.amazonaws.com"
web1_public_ip = "13.125.15.62"
web2_public_ip = "54.180.129.222"
rds_endpoint = "devops-1-flask-db.xxxxx.ap-northeast-2.rds.amazonaws.com"
rds_database = "saju"
```

### 방법 3: AWS 콘솔에서 확인

1. **EC2 Dashboard → Load Balancers**
   - `devops-1-app-lb` 찾기
   - DNS name 확인

2. **EC2 Dashboard → Instances**
   - `webserver1`, `webserver2` 태그 확인
   - Public IPv4 주소 확인

---

## 🌐 애플리케이션 접속 방법

### **방법 1: ALB를 통한 접속 (권장)**

Load Balancer를 통해 접속하면 자동으로 트래픽이 분산됩니다.

```
http://<ALB_DNS_NAME>/
```

**예시:**
```
http://devops-1-app-lb-1234567890.ap-northeast-2.elb.amazonaws.com/
```

### **방법 2: EC2 인스턴스 직접 접속**

개별 EC2 인스턴스에 직접 접속할 수도 있습니다.

```
http://<WEB1_PUBLIC_IP>:5000/
http://<WEB2_PUBLIC_IP>:5000/
```

**예시:**
```
http://13.125.15.62:5000/
http://54.180.129.222:5000/
```

---

## 📱 애플리케이션 사용법

### **CSAP 기술진단 SaaS 플랫폼**

이 애플리케이션은 Google Gemini API를 사용하여 보안 진단 결과를 분석하고 Excel 리포트를 생성하는 Flask 웹 애플리케이션입니다.

#### **1. 보안 진단 리포트 생성하기**

1. **웹 브라우저에서 ALB 주소 접속**
   ```
   http://<ALB_DNS_NAME>/
   ```

2. **보안 진단 JSON 파일 업로드**
   - 파일 선택 버튼 클릭
   - Linux 보안 진단 결과 JSON 파일 선택
   - 파일 형식: `.json` (예: `real_linux_result.json`)

3. **"분석 시작" 또는 "업로드" 버튼 클릭**
   - Google Gemini API가 진단 결과를 분석합니다
   - 분석 완료까지 약 5-10분 소요 (항목 수에 따라 다름)

4. **Excel 리포트 다운로드**
   - 분석 완료 후 "다운로드" 버튼 클릭
   - Excel 파일이 자동으로 다운로드됩니다

#### **2. 리포트 내용**

생성된 Excel 리포트에는 다음 정보가 포함됩니다:

- **시스템 정보**: Linux, Windows, MySQL, Nginx, Docker 등
- **점검 항목**: 각 보안 진단 항목별 상세 정보
- **진단 결과**: 양호/취약/정보 등
- **현황**: 현재 시스템 상태
- **조치방법**: Gemini AI가 분석한 상세 해설과 조치 방법 (한국어)

---

## 🔧 관리 및 모니터링

### **EC2 인스턴스 SSH 접속**

```bash
# SSH 키 설정
chmod 400 ~/.ssh/id_rsa

# webserver1 접속
ssh -i ~/.ssh/id_rsa ubuntu@<WEB1_PUBLIC_IP>

# webserver2 접속
ssh -i ~/.ssh/id_rsa ubuntu@<WEB2_PUBLIC_IP>
```

### **애플리케이션 로그 확인**

```bash
# SSH 접속 후
cd /home/ubuntu/myapp
tail -f flask.log

# 또는
cat flask.log
```

### **Flask 애플리케이션 프로세스 확인**

```bash
# 프로세스 확인
ps aux | grep app.py

# 포트 확인
sudo netstat -tlnp | grep :5000
# 또는
sudo ss -tlnp | grep :5000
```

### **애플리케이션 재시작**

```bash
# 기존 프로세스 종료
pkill -f app.py

# 애플리케이션 재시작
cd /home/ubuntu/myapp
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &
```

### **애플리케이션 디렉토리 구조**

```bash
# 애플리케이션 위치
cd /home/ubuntu/myapp

# 디렉토리 구조 확인
ls -la
tree -L 2  # (tree가 설치되어 있다면)
```

**예상 구조:**
```
/home/ubuntu/myapp/
├── app.py              # Flask 애플리케이션 메인 파일
├── requirements.txt    # Python 패키지 목록
├── .env               # 환경 변수 (GEMINI_API_KEY 등)
├── flask.log          # 애플리케이션 로그
├── uploads/           # 업로드된 JSON 파일
├── reports/           # 생성된 Excel 리포트
├── output/            # 임시 출력 파일
├── scripts/           # 보안 진단 스크립트
│   ├── llm_caller.py
│   ├── llm_report_generator.py
│   ├── load_diagnostic_items.py
│   └── llm_prompt_generator.py
└── templates/         # HTML 템플릿
    └── upload.html
```

---

## 🔍 문제 해결

### **문제 1: ALB 접속 불가 (502 Bad Gateway)**

**확인 사항:**
1. Security Group이 HTTP(80) 포트를 허용하는지 확인
2. ALB Health Check 상태 확인
   - EC2 Dashboard → Target Groups → `devops-1-app-tg` 확인
   - Targets 탭에서 Health 상태 확인
3. Flask 애플리케이션이 실행 중인지 확인

**해결 방법:**
```bash
# SSH 접속 후 Flask 앱 확인
ssh ubuntu@<WEB1_PUBLIC_IP>
ps aux | grep app.py

# 로그 확인
cd /home/ubuntu/myapp
tail -50 flask.log

# 앱 재시작
pkill -f app.py
cd /home/ubuntu/myapp
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &
```

### **문제 2: 파일 업로드 실패**

**확인 사항:**
1. JSON 파일 형식이 올바른지 확인
   - `results` 필드가 있어야 함
   - `results`는 배열이어야 함
2. 파일 크기가 16MB 이하인지 확인

**JSON 파일 형식 예시:**
```json
{
  "results": [
    {
      "CCE_ID": "CCE-12345",
      "항목": "계정 관리",
      "결과": "양호",
      "현황": "설정됨",
      "개선방안": "정기 점검"
    }
  ]
}
```

### **문제 3: Gemini API 오류**

**확인 사항:**
1. `.env` 파일에 `GEMINI_API_KEY`가 설정되어 있는지 확인
2. API 키가 유효한지 확인
3. API 할당량 초과 여부 확인

**해결 방법:**
```bash
# .env 파일 확인
cd /home/ubuntu/myapp
cat .env

# GEMINI_API_KEY 확인
grep GEMINI_API_KEY .env
```

### **문제 4: Excel 리포트 생성 실패**

**확인 사항:**
1. 필요한 Python 패키지가 설치되어 있는지 확인
   - `pandas`, `openpyxl`, `xlsxwriter`
2. 디스크 공간이 충분한지 확인

**해결 방법:**
```bash
# 패키지 확인
cd /home/ubuntu/myapp
source venv/bin/activate
pip list | grep -E "pandas|openpyxl|xlsxwriter"

# 패키지 재설치
pip install -r requirements.txt
```

---

## 📊 모니터링 대시보드

### **AWS 콘솔에서 확인**

1. **EC2 Dashboard**
   - 인스턴스 상태, CPU, 네트워크 사용량

2. **Load Balancer Dashboard**
   - ALB 요청 수, 응답 시간, 오류율

3. **RDS Dashboard**
   - 데이터베이스 연결 수, CPU, 메모리 사용량

4. **CloudWatch**
   - 상세 메트릭 및 로그 확인

---

## 🔐 보안 참고사항

### **현재 설정**

- **HTTP**: 포트 80 (ALB)
- **HTTPS**: 미설정 (프로덕션 환경에서는 HTTPS 권장)
- **SSH**: 포트 22 (Security Group에서 0.0.0.0/0 허용)
- **데이터베이스**: 포트 3306 (Private Subnet, Security Group 제한)

### **보안 강화 권장사항**

1. **SSH 접근 제한**
   - Security Group에서 특정 IP만 허용

2. **HTTPS 적용**
   - ALB에 SSL/TLS 인증서 연결
   - ACM (AWS Certificate Manager) 사용

3. **RDS 보안**
   - Private Subnet 사용 (현재 적용됨)
   - Security Group을 더 엄격하게 설정

4. **API 키 보안**
   - GitHub Secrets에서 안전하게 관리
   - 환경 변수로 주입

---

## 🎯 빠른 참조

### **접속 URL 확인 명령어**

```bash
# ALB DNS 이름
cd devops-1/terraform
terraform output alb_dns_name

# 웹서버 IP
terraform output web1_public_ip
terraform output web2_public_ip

# RDS 엔드포인트
terraform output rds_endpoint
```

### **애플리케이션 기능**

- **메인 페이지**: `/` - 보안 진단 JSON 파일 업로드
- **파일 업로드**: `/upload` - POST 요청으로 파일 업로드 및 분석
- **리포트 다운로드**: `/download/<filename>` - 생성된 Excel 리포트 다운로드

### **지원되는 시스템 타입**

- Linux
- Windows
- MySQL
- Nginx
- Docker

---

## 📝 사용 예시

### **1. 로컬에서 테스트용 JSON 파일 준비**

```bash
# devops-1/scripts/cce-diagnostics/output/real_linux_result.json
# 또는
# devops-1/scripts/cce-diagnostics/example_output.json
```

### **2. 웹 브라우저에서 접속**

```
http://devops-1-app-lb-2094532548.ap-northeast-2.elb.amazonaws.com/
```

### **3. JSON 파일 업로드**

1. "파일 선택" 버튼 클릭
2. `real_linux_result.json` 선택
3. "업로드" 또는 "분석 시작" 버튼 클릭

### **4. 분석 완료 대기**

- 진행 상황이 로그에 표시됩니다
- 분석 시간은 항목 수에 따라 다릅니다 (약 5-10분)

### **5. Excel 리포트 다운로드**

- "다운로드" 버튼 클릭
- `csap_linux_report_YYYYMMDD_HHMMSS.xlsx` 파일 다운로드

---

## 📞 지원

문제가 발생하면:

1. **GitHub Actions 로그 확인**
   - Actions 탭에서 최신 실행 로그 확인

2. **EC2 인스턴스 로그 확인**
   ```bash
   ssh ubuntu@<WEB1_PUBLIC_IP>
   cd /home/ubuntu/myapp
   tail -100 flask.log
   ```

3. **AWS 콘솔에서 리소스 상태 확인**
   - EC2, ALB, RDS 상태 확인

4. **GitHub Issues에 문제 보고**
   - 상세한 오류 메시지와 함께 보고

---

**배포 완료! 이제 보안 진단 애플리케이션을 사용할 수 있습니다.** 🎉
