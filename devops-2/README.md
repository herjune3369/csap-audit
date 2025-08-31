# DevOps Infrastructure Automation

이 프로젝트는 Ansible과 Terraform을 사용하여 클라우드 인프라를 자동화하고 Flask 애플리케이션을 배포하는 DevOps 도구입니다.

## 🚀 기능

- Terraform을 통한 AWS 인프라 자동화
- Ansible을 통한 애플리케이션 배포 자동화
- Flask 웹 애플리케이션 배포
- 멀티 환경 지원 (개발/스테이징/프로덕션)
- 데이터베이스 초기화 및 설정
- GitHub Actions를 통한 CI/CD 자동화

## 📋 사전 요구사항

- Python 3.7+
- Ansible 2.9+
- Terraform 1.0+
- AWS CLI
- AWS 계정 및 자격 증명

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
# Ansible 설치
pip install ansible

# AWS CLI 설치 (macOS)
brew install awscli

# AWS CLI 설치 (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2. AWS 자격 증명 설정

```bash
# AWS 자격 증명 설정
aws configure

# 또는 환경 변수 설정
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### 3. GitHub Secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿을 설정하세요:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키

## 🚀 자동화된 배포

### GitHub Actions를 통한 자동 배포

이 프로젝트는 GitHub Actions를 통해 자동화된 CI/CD 파이프라인을 제공합니다:

1. **코드 푸시 시 자동 실행**: `main` 또는 `develop` 브랜치에 푸시하면 자동으로 실행됩니다
2. **수동 실행**: GitHub Actions 탭에서 수동으로 워크플로우를 실행할 수 있습니다
3. **환경 선택**: 개발, 스테이징, 프로덕션 환경 중 선택하여 배포할 수 있습니다

### 워크플로우 단계

1. **Validate**: Terraform 코드 검증 및 포맷 확인
2. **Security Scan**: Trivy를 통한 보안 취약점 스캔
3. **Deploy Infrastructure**: Terraform을 통한 AWS 인프라 배포
4. **Deploy Application**: Ansible을 통한 애플리케이션 배포
5. **Notify**: 배포 결과 알림

## 📁 프로젝트 구조

```
devops/
├── README.md                   # 프로젝트 문서
├── ansible/                   # Ansible 플레이북
│   ├── playbook.yml          # 메인 플레이북
│   ├── inventories/          # 인벤토리 파일
│   │   ├── aws_ec2.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── roles/                # Ansible 역할
│       └── flask/
│           ├── files/        # 애플리케이션 파일
│           │   ├── app.py
│           │   ├── requirements.txt
│           │   └── init_db.sql
│           ├── tasks/        # 작업 정의
│           │   └── main.yml
│           └── templates/    # 템플릿 파일
└── terraform/                # Terraform 설정
    ├── main.tf              # 메인 설정
    ├── variables.tf         # 변수 정의
    ├── outputs.tf          # 출력 정의
    ├── backend.tf          # 백엔드 설정
    ├── terraform.tfvars    # 변수 값
    └── save_outputs.sh     # 출력 저장 스크립트
```

## 🔧 수동 실행 (로컬)

### Terraform 초기화

```bash
cd terraform
terraform init
```

### 인프라 배포

```bash
# Terraform 계획 확인
terraform plan

# 인프라 생성
terraform apply

# 출력값 저장
./save_outputs.sh
```

### 애플리케이션 배포

```bash
cd ../ansible

# 인벤토리 파일 확인
cat inventories/aws_ec2.yml

# Ansible 플레이북 실행
ansible-playbook -i inventories/aws_ec2.yml playbook.yml
```

## 🌐 배포된 애플리케이션

배포가 완료되면 다음 URL에서 Flask 애플리케이션에 접근할 수 있습니다:

- **개발 환경**: `http://dev-your-domain.com`
- **스테이징 환경**: `http://staging-your-domain.com`
- **프로덕션 환경**: `http://your-domain.com`

## 📊 모니터링

### GitHub Actions에서 확인

1. GitHub 저장소의 Actions 탭에서 워크플로우 실행 상태를 확인할 수 있습니다
2. 각 단계별 상세 로그를 확인할 수 있습니다
3. 보안 스캔 결과는 Security 탭에서 확인할 수 있습니다

### 로그 확인

```bash
# EC2 인스턴스에 SSH 접속
ssh -i ~/.ssh/your-key.pem ubuntu@your-instance-ip

# 애플리케이션 로그 확인
sudo journalctl -u flask-app -f

# 시스템 로그 확인
sudo tail -f /var/log/syslog
```

### 상태 확인

```bash
# 서비스 상태 확인
sudo systemctl status flask-app

# 포트 확인
sudo netstat -tlnp | grep :5000
```

## 🔒 보안

- SSH 키 기반 인증
- 보안 그룹을 통한 네트워크 접근 제어
- IAM 역할을 통한 최소 권한 원칙 적용
- HTTPS 강제 적용 (프로덕션)
- Trivy를 통한 정기적인 보안 스캔

## 🧹 정리

### 인프라 삭제

```bash
cd terraform
terraform destroy
```

### 로컬 파일 정리

```bash
# Terraform 상태 파일 삭제
rm -rf .terraform
rm -f .terraform.lock.hcl

# Ansible 캐시 삭제
rm -rf ~/.ansible
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요. # test
# Trigger workflow
