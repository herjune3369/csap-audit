# 🚀 GitHub Actions 실행 가이드 (devops-1)

## 📋 개요

`devops-1` 폴더의 변경사항을 GitHub Actions로 자동 배포하는 방법입니다.

---

## ✅ GitHub Actions 워크플로우 트리거 방법

### **방법 1: 자동 트리거 (Push)**

`devops-1` 브랜치에 `devops-1/` 폴더의 변경사항을 push하면 자동으로 실행됩니다.

```bash
# 1. 변경사항 확인
git status

# 2. 변경사항 추가
git add devops-1/

# 3. 커밋
git commit -m "수정 내용 설명"

# 4. Push (자동으로 GitHub Actions 실행)
git push origin devops-1
```

**트리거 조건:**
- 브랜치: `main`, `develop`, `devops-1`
- 경로: `devops-1/**` 또는 `.github/workflows/devops-1-workflow.yml`

---

### **방법 2: 수동 실행 (workflow_dispatch)**

GitHub 웹 인터페이스에서 수동으로 실행할 수 있습니다.

#### **단계:**

1. **GitHub 저장소로 이동**
   ```
   https://github.com/herjune3369/csap-audit
   ```

2. **Actions 탭 클릭**
   - 저장소 상단 메뉴에서 "Actions" 클릭

3. **워크플로우 선택**
   - 왼쪽 사이드바에서 "DevOps Infrastructure Automation" 선택

4. **수동 실행**
   - 오른쪽 상단의 "Run workflow" 버튼 클릭
   - 브랜치 선택: `devops-1`
   - Environment 선택: `dev`, `staging`, `prod` 중 선택
   - "Run workflow" 버튼 클릭

---

### **방법 3: 빈 커밋으로 트리거**

변경사항이 없어도 워크플로우를 실행하려면 빈 커밋을 사용할 수 있습니다.

```bash
# 빈 커밋 생성
git commit --allow-empty -m "Trigger GitHub Actions"

# Push
git push origin devops-1
```

---

## 🔍 워크플로우 실행 확인

### **GitHub 웹에서 확인**

1. 저장소 → **Actions** 탭
2. 왼쪽에서 **"DevOps Infrastructure Automation"** 선택
3. 실행 중인 워크플로우 확인

### **실행 단계**

워크플로우는 다음 단계로 실행됩니다:

1. **✅ Validate** - Terraform 코드 검증
   - Terraform Format Check
   - Terraform Init & Validate
   - Terraform Plan

2. **🚀 Deploy Infrastructure** - 인프라 배포
   - Terraform Apply
   - AWS 리소스 생성 (VPC, EC2, RDS, ALB 등)

3. **📦 Deploy Application** - 애플리케이션 배포
   - Ansible을 통한 애플리케이션 배포
   - Flask 앱 설치 및 설정

4. **📢 Notify** - 배포 상태 알림

---

## 🔧 필요한 GitHub Secrets

워크플로우가 정상 실행되려면 다음 Secrets가 설정되어 있어야 합니다:

### **필수 Secrets:**

1. **AWS_ACCESS_KEY_ID**
   - AWS 액세스 키 ID

2. **AWS_SECRET_ACCESS_KEY**
   - AWS 시크릿 액세스 키

3. **SSH_PRIVATE_KEY**
   - EC2 인스턴스 접속용 SSH 개인 키

### **Secrets 설정 방법:**

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Name과 Value 입력 후 **Add secret** 클릭

---

## 📝 예시: 변경사항 커밋 및 Push

```bash
# 1. 현재 브랜치 확인
git branch --show-current

# 2. devops-1 브랜치로 전환 (필요시)
git checkout devops-1

# 3. 변경사항 확인
git status

# 4. 변경사항 추가
git add devops-1/terraform/main.tf
git add devops-1/ansible/playbook.yml
# 또는 전체 추가
git add devops-1/

# 5. 커밋
git commit -m "Update Terraform configuration for Internet Gateway"

# 6. Push (GitHub Actions 자동 실행)
git push origin devops-1
```

---

## 🐛 문제 해결

### **문제 1: 워크플로우가 트리거되지 않음**

**원인:**
- `devops-1/` 폴더 외부의 파일만 변경됨
- 잘못된 브랜치에 push

**해결:**
```bash
# 변경사항이 devops-1/ 폴더에 있는지 확인
git status devops-1/

# 올바른 브랜치에 있는지 확인
git branch --show-current
```

### **문제 2: AWS 인증 오류**

**원인:**
- GitHub Secrets에 AWS 자격증명이 없음
- 잘못된 자격증명

**해결:**
1. GitHub Secrets 확인
2. AWS 자격증명 재설정

### **문제 3: Terraform 오류**

**원인:**
- Terraform 코드 문법 오류
- AWS 리소스 충돌

**해결:**
```bash
# 로컬에서 Terraform 검증
cd devops-1/terraform
terraform init
terraform validate
terraform plan
```

---

## 📊 워크플로우 실행 상태 확인

### **실행 중인 워크플로우 확인**

```bash
# GitHub CLI 사용 (설치 필요)
gh workflow list
gh run list --workflow="DevOps Infrastructure Automation"
```

### **로그 확인**

1. GitHub → Actions 탭
2. 실행 중인 워크플로우 클릭
3. 각 Job 클릭하여 로그 확인

---

## 🎯 빠른 실행 체크리스트

- [ ] `devops-1` 브랜치에 있음
- [ ] 변경사항이 `devops-1/` 폴더에 있음
- [ ] 변경사항 커밋 완료
- [ ] GitHub Secrets 설정 완료 (AWS, SSH)
- [ ] `git push origin devops-1` 실행
- [ ] GitHub Actions 탭에서 실행 상태 확인

---

## 📚 관련 문서

- [RUN.md](./RUN.md) - devops-1 실행 가이드
- [QUICK_START.md](./QUICK_START.md) - 빠른 시작 가이드

---

**GitHub Actions 실행 완료!** 🎉

