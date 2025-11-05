# 🔐 Git 인증 문제 해결 가이드

## ❌ 오류 메시지
```
remote: Permission to herjune3369/csap-audit.git denied to JuneHer.
fatal: unable to access 'https://github.com/herjune3369/csap-audit.git/': The requested URL returned error: 403
```

## 🔍 원인
- **계정 변경**: 로컬 Git 설정 계정(`JuneHer`)과 GitHub 저장소 소유자(`herjune3369`)가 다름
- GitHub Personal Access Token (PAT) 필요
- 또는 SSH 키 인증 필요

## 📋 현재 상황
- **GitHub 저장소 소유자**: `herjune3369`
- **로컬 Git 설정**: `herjune` (또는 `JuneHer`)
- **문제**: 다른 계정으로 인증 시도하여 권한 거부

---

## 🛠️ 해결 방법 (3가지)

### **방법 1: Personal Access Token (PAT) 사용** ⭐ (추천)

#### **1단계: GitHub에서 Personal Access Token 발급 (herjune3369 계정으로)**
1. **herjune3369 계정으로** GitHub 접속: https://github.com
2. 우측 상단 프로필 아이콘 클릭 → **Settings** 클릭
   - 또는 직접 접속: https://github.com/settings/profile
3. 좌측 하단 **Developer settings** 클릭
   - 또는 직접 접속: https://github.com/settings/apps
4. **Personal access tokens** → **Tokens (classic)** 클릭
   - 또는 직접 접속: https://github.com/settings/tokens
5. **Generate new token** → **Generate new token (classic)** 클릭
6. **Note** 입력 (예: "MacBook Pro Token")
7. **Expiration** 선택 (예: 90 days 또는 No expiration)
8. 권한 선택 (스크롤하여 체크):
   - ✅ `repo` (전체 저장소 접근)
   - ✅ `workflow` (GitHub Actions 사용 시)
9. 맨 아래 **Generate token** 버튼 클릭
10. 토큰 복사 (한 번만 표시됨! `ghp_`로 시작)
   - ⚠️ **주의**: `herjune3369` 계정으로 로그인한 상태에서 토큰 발급

#### **2단계: Git 원격 URL에 토큰 포함**
```bash
cd /Users/junheo/devsecops-lab/csap-audit

# 기존 원격 URL 확인
git remote -v

# Personal Access Token을 포함한 URL로 변경
git remote set-url origin https://<YOUR_TOKEN>@github.com/herjune3369/csap-audit.git

# 예시:
# git remote set-url origin https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/herjune3369/csap-audit.git
```

#### **3단계: Push 테스트**
```bash
git push origin main
```

---

### **방법 2: SSH 키 사용** ⭐⭐ (더 안전)

#### **1단계: SSH 키 생성 (없는 경우)**
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"

# 또는 기존 키 사용
ls -la ~/.ssh/id_*.pub
```

#### **2단계: GitHub에 SSH 키 등록 (herjune3369 계정으로)**
1. 공개 키 복사
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 또는
   cat ~/.ssh/id_rsa.pub
   ```

2. **herjune3369 계정으로** GitHub에 등록
   - ⚠️ **주의**: `herjune3369` 계정으로 로그인한 상태에서 진행
   
   **경로 (단계별):**
   1. GitHub 접속: https://github.com
   2. 우측 상단 프로필 아이콘 클릭 (원형 아이콘)
   3. 드롭다운 메뉴에서 **Settings** 클릭
   4. 좌측 메뉴에서 **SSH and GPG keys** 클릭
   5. 우측 상단 **New SSH key** 버튼 클릭
   6. **Title** 입력 (예: "MacBook Pro")
   7. **Key** 필드에 공개 키 붙여넣기
   8. **Add SSH key** 버튼 클릭
   
   **직접 링크:**
   - https://github.com/settings/keys

#### **3단계: Git 원격 URL을 SSH로 변경**
```bash
cd /Users/junheo/devsecops-lab/csap-audit

# HTTPS → SSH로 변경
git remote set-url origin git@github.com:herjune3369/csap-audit.git

# 확인
git remote -v
# 출력: origin  git@github.com:herjune3369/csap-audit.git
```

#### **4단계: SSH 연결 테스트**
```bash
ssh -T git@github.com
# 출력: Hi herjune3369! You've successfully authenticated...
```

#### **5단계: Push 테스트**
```bash
git push origin main
```

---

### **방법 3: GitHub CLI 사용** ⭐⭐⭐ (가장 간단)

#### **1단계: GitHub CLI 설치**
```bash
# macOS
brew install gh

# 또는 GitHub Desktop 사용
```

#### **2단계: GitHub CLI 로그인**
```bash
gh auth login

# 브라우저에서 인증
# 또는 토큰으로 인증
```

#### **3단계: 자동 인증 설정**
```bash
# Git credential helper 설정
gh auth setup-git
```

#### **4단계: Push 테스트**
```bash
git push origin main
```

---

## 🔍 현재 상태 확인

### **원격 저장소 확인**
```bash
git remote -v
```

### **인증 상태 확인**
```bash
# HTTPS인 경우
git ls-remote origin

# SSH인 경우
ssh -T git@github.com
```

---

## 📝 빠른 해결 (권장)

### **SSH 키 사용 (가장 안전하고 편리)**

```bash
# 1. SSH 키 확인
ls -la ~/.ssh/id_*.pub

# 2. SSH 키가 없으면 생성
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter 키 3번 (기본값 사용)

# 3. 공개 키 복사
cat ~/.ssh/id_ed25519.pub
# 또는
pbcopy < ~/.ssh/id_ed25519.pub  # macOS에서 클립보드로 복사

# 4. GitHub에 SSH 키 등록
# GitHub > Settings > SSH and GPG keys > New SSH key

# 5. Git 원격 URL을 SSH로 변경
cd /Users/junheo/devsecops-lab/csap-audit
git remote set-url origin git@github.com:herjune3369/csap-audit.git

# 6. 연결 테스트
ssh -T git@github.com

# 7. Push
git push origin main
```

---

## 🎯 GitHub 저장소 주소

**현재 저장소:**
```
https://github.com/herjune3369/csap-audit.git
```

**SSH 형식:**
```
git@github.com:herjune3369/csap-audit.git
```

---

## ✅ 인증 완료 후

인증이 완료되면 정상적으로 push가 가능합니다:

```bash
git add devops-1/
git commit -m "Fix Internet Gateway issue"
git push origin main
```

---

## 🔧 추가 문제 해결

### **문제: SSH 키가 여러 개 있을 때**
```bash
# SSH config 파일 생성/수정
vim ~/.ssh/config

# 내용 추가:
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

### **문제: credential helper 캐시 문제**
```bash
# macOS에서 credential helper 제거
git credential-osxkeychain erase
host=github.com
protocol=https
# (Enter 키 2번)

# 또는 credential helper 재설정
git config --global credential.helper osxkeychain
```

---

**이제 Git 인증 문제가 해결되었습니다!**

