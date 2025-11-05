# ⏱️ GitHub Actions 배포 시간 안내

## 📊 예상 실행 시간

### 전체 배포 시간: **약 20-30분**

---

## 🔍 단계별 소요 시간

### 1. **Validate** (약 2-3분)
- Terraform 코드 검증
- Terraform Plan 생성
- **빠른 단계** ✅

### 2. **Deploy Infrastructure** (약 15-20분) ⚠️ **가장 오래 걸림**
- VPC 생성: 1-2분
- EC2 인스턴스 2개: 각 2-3분 (총 4-6분)
- **RDS 인스턴스: 5-10분** ⚠️ **가장 느림**
- ALB (Load Balancer): 2-3분
- Security Groups, Subnets, Route Tables: 1-2분
- NAT Gateway: 1-2분

### 3. **Deploy Application** (약 5-10분)
- EC2 인스턴스 부팅 대기: 2-3분
- SSH 연결 확인: 1분
- Ansible 배포:
  - Python/Flask 설치: 2-3분
  - 패키지 설치: 1-2분
  - 애플리케이션 설정: 1-2분

### 4. **Notify** (약 10초)
- 배포 결과 알림

---

## ⚠️ 시간이 오래 걸리는 주요 이유

### 1. **RDS 인스턴스 생성 (5-10분)**
- 데이터베이스 인스턴스는 AWS에서 가장 오래 걸리는 리소스
- 초기화 및 설정 시간 필요
- 이것이 전체 배포 시간의 대부분을 차지함

### 2. **EC2 인스턴스 부팅 (2-3분/개)**
- EC2 인스턴스가 완전히 부팅되고 SSH 접속 가능해질 때까지 대기
- 2개의 인스턴스가 있으므로 순차적으로 진행

### 3. **ALB (Application Load Balancer) 생성 (2-3분)**
- 로드 밸런서 생성 및 설정 시간

### 4. **Ansible 배포 (3-5분)**
- 시스템 패키지 업데이트
- Python, Flask, 의존성 설치
- 애플리케이션 설정 및 배포

---

## 📈 실행 시간 단축 방법

### 1. **RDS 인스턴스 제거 (테스트 환경)**
- 개발/테스트 환경에서는 RDS 없이 실행 가능
- **시간 단축: 약 5-10분**

### 2. **EC2 인스턴스 수 감소**
- 웹서버 1개만 사용 (webserver2 제거)
- **시간 단축: 약 2-3분**

### 3. **빠른 인스턴스 타입 사용**
- `t3.micro` → `t3.small` (더 빠른 부팅)
- **시간 단축: 약 1-2분**

### 4. **Ansible 최적화**
- 불필요한 패키지 설치 제거
- 캐시 활용
- **시간 단축: 약 1-2분**

---

## 🔍 현재 실행 상태 확인 방법

### GitHub 웹에서 확인

1. **GitHub 저장소 → Actions 탭**
   ```
   https://github.com/herjune3369/csap-audit/actions
   ```

2. **실행 중인 워크플로우 클릭**

3. **각 Job 클릭하여 상세 로그 확인**
   - Validate: 빠름 (2-3분)
   - Deploy Infrastructure: 오래 걸림 (15-20분)
   - Deploy Application: 중간 (5-10분)

### 로그에서 확인할 수 있는 정보

- **Terraform Apply 진행 상황**
  ```
  aws_db_instance.flask_db: Still creating... [5m30s elapsed]
  ```

- **EC2 인스턴스 상태**
  ```
  Instance is running
  Waiting for SSH...
  ```

- **Ansible 배포 진행**
  ```
  TASK [flask : Install Python packages]
  ```

---

## ⏰ 예상 시간표

| 단계 | 시간 | 상태 |
|------|------|------|
| Validate | 2-3분 | ✅ 빠름 |
| Deploy Infrastructure | 15-20분 | ⚠️ 오래 걸림 |
|   - VPC 생성 | 1-2분 | |
|   - EC2 인스턴스 | 4-6분 | |
|   - **RDS 인스턴스** | **5-10분** | ⚠️ **가장 느림** |
|   - ALB 생성 | 2-3분 | |
| Deploy Application | 5-10분 | 중간 |
|   - EC2 부팅 대기 | 2-3분 | |
|   - Ansible 배포 | 3-5분 | |
| **전체** | **20-30분** | |

---

## 🎯 정리

- **정상적인 배포 시간입니다** (20-30분)
- RDS 인스턴스 생성이 가장 오래 걸립니다 (5-10분)
- GitHub Actions에서 실시간 로그를 확인할 수 있습니다
- 각 단계가 순차적으로 진행되므로 전체 시간이 합쳐집니다

**현재 실행 중인 워크플로우를 확인하려면:**
- GitHub → Actions 탭 → 최신 실행 클릭

---

**참고:** 프로덕션 환경에서는 안정성을 위해 시간이 오래 걸리는 것이 정상입니다.

