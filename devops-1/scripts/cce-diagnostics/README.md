# CCE 기반 보안 진단 스크립트 (5종 확정) + Excel 리포트 생성 + Flask SaaS 플랫폼

CSAP(Common Criteria Security Assurance Program) 인증을 준비하는 중소기업을 위한 **5종 플랫폼 보안 진단 자동화 스크립트**, **Excel 리포트 자동 생성 시스템**, 그리고 **Flask 기반 SaaS 웹 플랫폼**입니다.

## 🎯 지원 플랫폼 (5종 확정)

### ✅ 현재 지원
- **🐧 Server(Linux)**: Ubuntu, CentOS, RHEL, SUSE 등 (36개 진단 항목)

### 📋 향후 지원 예정
- **🪟 Server(Windows)**: Windows Server 보안 진단
- **🗄️ MySQL**: 데이터베이스 보안 진단
- **🌐 Nginx**: 웹서버 보안 진단
- **🐳 Docker**: 컨테이너 보안 진단

## 📋 Linux Server 진단 항목 (현재 구현 - 36개)

### 가. 계정 관리 (5개 항목)
- CCE-0001: root 계정 원격 접속 제한
- CCE-0002: 패스워드 복잡도 설정
- CCE-0003: 계정 잠금 임계값 설정
- CCE-0004: 패스워드 최대 사용 기간 설정
- CCE-0005: 패스워드 파일 보호

### 나. 파일 및 디렉터리 관리 (14개 항목)
- CCE-0006: root 홈 디렉터리 소유자 설정
- CCE-0007: 파일 및 디렉터리 소유자 설정
- CCE-0008: /etc/passwd 파일 소유자 및 권한 설정
- CCE-0009: /etc/shadow 파일 소유자 및 권한 설정
- CCE-0010: /etc/hosts 파일 소유자 및 권한 설정
- CCE-0011: /etc/(x)inetd.conf 파일 소유자 및 권한 설정
- CCE-0012: /etc/syslog.conf 파일 소유자 및 권한 설정
- CCE-0013: /etc/services 파일 소유자 및 권한 설정
- CCE-0014: SUID, SGID, Sticky bit 설정 파일 점검
- CCE-0015: 사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정
- CCE-0016: world writable 파일 점검
- CCE-0017: $HOME/.rhosts, hosts.equiv 사용 금지
- CCE-0018: 접속 IP 및 포트 제한
- CCE-0019: cron파일 소유자 및 권한 설정

### 다. 서비스 관리 (15개 항목)
- CCE-0020: Finger 서비스 비활성화
- CCE-0021: Anonymous FTP 서비스 비활성화
- CCE-0022: r계열 서비스 비활성화
- CCE-0023: DoS 공격에 취약한 서비스 비활성화
- CCE-0024: NFS 서비스 비활성화
- CCE-0025: NFS 접근통제
- CCE-0026: automountd 제거
- CCE-0027: RPC 서비스 확인
- CCE-0028: NIS, NIS+ 점검
- CCE-0029: tftp, talk 서비스 비활성화
- CCE-0030: Sendmail 버전 점검
- CCE-0031: 스팸 메일 릴레이 제한
- CCE-0032: 일반 사용자의 Sendmail 실행 방지
- CCE-0033: DNS 보안 버전 패치
- CCE-0034: DNS Zone Transfer 설정

### 라. 패치 및 로그 관리 (2개 항목)
- CCE-0035: 최신 보안 패치 및 벤더 권고 사항 적용
- CCE-0036: 로그의 정기적 검토 및 백업

## 🚀 사용법

### 1. 통합 SaaS 시스템 실행 (권장)
```bash
# 전체 시스템 테스트 (Linux 진단 → Flask 앱 → 웹 브라우저)
./test_saas_system.sh
```

### 2. 단계별 실행
```bash
# 1단계: Linux 진단
sudo ./cce_check_linux.sh

# 2단계: Flask SaaS 앱 시작
cd flask_app
python app.py

# 3단계: 웹 브라우저에서 http://localhost:5000 접속
```

### 3. 개별 기능 사용
```bash
# Linux 진단만 실행
sudo ./cce_check_linux.sh -v

# Excel 리포트만 생성
cd report_generator
python generate_linux_excel.py

# Flask 앱만 시작
cd flask_app
python app.py
```

## 📊 출력 결과

### JSON 형식 (SaaS 시스템 최적화)
```json
{
  "metadata": {
    "timestamp": "2024-07-30T05:30:00Z",
    "hostname": "linux-server-01",
    "os_info": "Ubuntu 20.04.3 LTS",
    "os_type": "linux",
    "total_checks": 36,
    "version": "1.0",
    "statistics": {
      "total": 36,
      "good": 28,
      "vulnerable": 6,
      "info": 2
    }
  },
  "results": [
    {
      "CCE_ID": "CCE-0001",
      "항목": "root 계정 원격 접속 제한",
      "결과": "양호",
      "detail": "PermitRootLogin is set to no",
      "remediation": "현재 설정이 적절합니다."
    }
  ]
}
```

### Excel 형식 (CSAP 공식 양식)
- **시트 1: 요약** - 분류별 통계 및 보안수준
- **시트 2: 상세결과** - 개별 진단 항목별 상세 결과

| No | 분류 | CCE ID | 점검 항목 | 중요도 | 결과 | 현황 | 개선방안 |
|----|------|--------|-----------|--------|------|------|----------|
| 1 | U1 계정관리 | CCE-0001 | root 원격 접속 제한 | H | 양호 | PermitRootLogin no | - |

## 📁 5종 디렉토리 구조

```
cce-diagnostics/
├── cce_check_linux.sh                # ✅ Linux 전용 메인 스크립트
├── generate_csap_report.sh           # ✅ 통합 실행 스크립트
├── test_saas_system.sh              # ✅ SaaS 시스템 테스트 스크립트
├── checks/
│   ├── linux/                        # Linux 기반 진단
│   │   └── server/                   # ✅ Server(Linux) 진단 완료
│   │       ├── check_account_management.sh
│   │       ├── check_file_permissions.sh
│   │       ├── check_service_management.sh
│   │       └── check_patch_log_management.sh
│   ├── windows/                      # 📋 계획
│   ├── database/                     # 📋 계획
│   ├── webserver/                    # 📋 계획
│   └── container/                    # 📋 계획
├── report_generator/                 # ✅ Excel 리포트 생성기
│   ├── generate_linux_excel.py       # ✅ CSAP Excel 생성기
│   ├── requirements.txt              # ✅ Python 패키지 목록
│   ├── test/                         # ✅ 테스트 파일
│   └── output/                       # ✅ 생성된 Excel 파일
├── flask_app/                        # ✅ Flask SaaS 웹 플랫폼
│   ├── app.py                        # ✅ Flask 메인 앱
│   ├── templates/                    # ✅ HTML 템플릿
│   │   └── upload.html              # ✅ 업로드 UI
│   ├── uploads/                      # ✅ 업로드 파일 저장소
│   ├── reports/                      # ✅ 생성된 리포트 저장소
│   └── requirements.txt              # ✅ Flask 패키지 목록
├── utils/
│   └── json_writer.sh                # ✅ JSON 결과 작성 유틸리티
└── README.md                          # 이 파일
```

## 🔧 요구사항

### Linux 진단
- **OS**: Ubuntu, CentOS, RHEL, SUSE 등
- **권한**: 루트 권한 필요 (sudo)
- **도구**: bash, jq (결과 요약용)

### Excel 리포트 생성
- **Python**: 3.7+
- **패키지**: pandas, openpyxl, xlsxwriter
- **설치**: `pip install -r report_generator/requirements.txt`

### Flask SaaS 플랫폼
- **Python**: 3.7+
- **패키지**: Flask, Werkzeug, pandas, openpyxl
- **설치**: `pip install -r flask_app/requirements.txt`

### 향후 지원 예정
- **Windows**: PowerShell, Windows Management Framework
- **Database**: MySQL CLI 도구
- **Webserver**: Nginx 설정 파일 접근
- **Container**: Docker CLI 도구

## 📈 결과 해석

- **양호**: 보안 설정이 적절히 구성됨 (초록색)
- **취약**: 보안 강화가 필요한 항목 (빨간색)
- **정보**: 참고용 정보 (노란색)

## 🔄 5종 개발 로드맵

### Phase 1: 서버 환경 완성 ✅
- [x] **Server(Linux)**: 36개 진단 항목 완료
- [x] **JSON → Excel 자동 변환**: CSAP 양식 완료
- [x] **Flask SaaS 웹 플랫폼**: 업로드 → 리포트 생성 → 다운로드 완료
- [ ] **Server(Windows)**: Windows 서버 보안 점검 자동화

### Phase 2: 데이터베이스 보안 📋
- [ ] **MySQL**: 인증, 권한, 로깅, 암호화 설정 점검

### Phase 3: 웹서버 보안 📋
- [ ] **Nginx**: 설정 파일, 보안 헤더, SSL/TLS 설정 점검

### Phase 4: 컨테이너 보안 📋
- [ ] **Docker**: 컨테이너 보안, 이미지 스캔, 런타임 보안

## 🛡️ 보안 고려사항

- 이 스크립트는 시스템 정보를 수집합니다
- 결과 파일에는 민감한 정보가 포함될 수 있습니다
- 결과 파일은 안전한 방법으로 전송하고 저장하세요
- 각 플랫폼별 보안 가이드라인을 준수합니다

## 💡 SaaS 시스템 연동

### 웹 기반 업로드 → 자동 변환
1. **웹 브라우저 접속**: http://localhost:5000
2. **JSON 파일 업로드**: 드래그 앤 드롭 또는 파일 선택
3. **자동 Excel 생성**: CSAP 양식 기반 리포트 생성
4. **즉시 다운로드**: 생성된 Excel 파일 다운로드

### API 엔드포인트
- `GET /`: 메인 업로드 페이지
- `POST /upload`: JSON 파일 업로드 및 리포트 생성
- `GET /download/<filename>`: 생성된 리포트 다운로드
- `GET /api/status`: API 상태 확인
- `GET /api/upload-stats`: 업로드 통계

### 챗봇 연동 준비
- JSON 구조가 챗봇 QA 인터페이스에 최적화됨
- CCE_ID 기반 질의응답 가능
- remediation 필드로 실무 가이드 제공

## 🌐 웹 인터페이스 기능

### 업로드 페이지
- **드래그 앤 드롭**: JSON 파일을 쉽게 업로드
- **진행률 표시**: 리포트 생성 진행 상황 실시간 표시
- **자동 다운로드**: 생성 완료 시 즉시 다운로드 링크 제공
- **반응형 디자인**: 모바일/데스크톱 모든 기기 지원

### 보안 기능
- **파일 형식 검증**: JSON 파일만 허용
- **파일 크기 제한**: 최대 16MB
- **안전한 파일명**: UUID 기반 고유 파일명 생성
- **에러 처리**: 상세한 오류 메시지 제공

## 📞 지원

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해 주세요.

---

**CSAP 인증 준비를 위한 5종 플랫폼 보안 진단 자동화 도구 + Excel 리포트 생성기 + Flask SaaS 웹 플랫폼** 