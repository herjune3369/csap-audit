# 🔐 Git 계정 변경 문제 해결 가이드

## ❌ 오류 메시지
```
remote: Permission to herjune3369/csap-audit.git denied to JuneHer.
fatal: unable to access 'https://github.com/herjune3369/csap-audit.git/': The requested URL returned error: 403
```

## 🔍 문제 원인
- **계정 불일치**: 로컬 Git 설정 계정과 GitHub 저장소 소유자 계정이 다름
- 현재 로컬: `JuneHer` 또는 `herjune`
- 저장소 소유자: `herjune3369`

---

## ✅ 해결 방법 (계정 변경 상황)

### **방법 1: 새 계정(herjune3369)의 인증 정보 사용** ⭐ (추천)

#### **A. SSH 키 사용 (가장 안전)**

**1단계: SSH 키 확인/생성**
```bash
# 기존 SSH 키 확인
ls -la ~/.ssh/id_*.pub

# 없으면 생성
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter 키 3번 (기본값 사용)
```

**2단계: 공개 키 복사**
```bash
cat ~/.ssh/id_ed25519.pub
# 또는 macOS에서 클립보드로 복사
pbcopy < ~/.ssh/id_ed25519.pub
```

**3단계: herjune3369 계정에 SSH 키 등록**
1. **herjune3369 계정으로** GitHub 로그인: https://github.com
2. 우측 상단 프로필 아이콘 클릭 → **Settings** 클릭
   - 또는 직접 접속: https://github.com/settings/profile
3. 좌측 메뉴에서 **SSH and GPG keys** 클릭
   - 또는 직접 접속: https://github.com/settings/keys
4. **New SSH key** 버튼 클릭 (우측 상단)
5. **Title** 입력 (예: "MacBook Pro" 또는 "My Mac")
6. **Key** 필드에 공개 키 붙여넣기
7. **Add SSH key** 버튼 클릭

**4단계: Git 원격 URL을 SSH로 변경**
```bash
cd /Users/junheo/devsecops-lab/csap-audit
git remote set-url origin git@github.com:herjune3369/csap-audit.git
```

**5단계: 연결 테스트**
```bash
ssh -T git@github.com
# 출력: Hi herjune3369! You've successfully authenticated...
```

**6단계: Push 테스트**
```bash
git push origin main
```

---

#### **B. Personal Access Token 사용**

**1단계: herjune3369 계정으로 토큰 발급**
1. **herjune3369 계정으로** GitHub 로그인
2. Settings > Developer settings > Personal access tokens > Tokens (classic)
3. Generate new token (classic)
4. 권한 선택: `repo`, `workflow`
5. Generate token 클릭
6. 토큰 복사 (예: `ghp_xxxxxxxxxxxxxxxxxxxx`)

**2단계: Git 원격 URL에 토큰 포함**
```bash
cd /Users/junheo/devsecops-lab/csap-audit
git remote set-url origin https://<YOUR_TOKEN>@github.com/herjune3369/csap-audit.git

# 예시:
# git remote set-url origin https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/herjune3369/csap-audit.git
```

**3단계: Push 테스트**
```bash
git push origin main
```

---

### **방법 2: Git 사용자 정보 업데이트 (선택사항)**

로컬 Git 설정을 새 계정으로 변경 (저장소 접근과는 무관하지만, 커밋 작성자 정보 변경):

```bash
# 전역 설정
git config --global user.name "herjune3369"
git config --global user.email "your_email@example.com"

# 또는 이 저장소만 (로컬 설정)
cd /Users/junheo/devsecops-lab/csap-audit
git config user.name "herjune3369"
git config user.email "your_email@example.com"
```

⚠️ **주의**: 이 설정은 커밋 작성자 정보만 변경하며, 인증과는 무관합니다.

---

## 🎯 핵심 요약

### **문제**
- 로컬 Git 설정 계정 ≠ GitHub 저장소 소유자 계정
- `JuneHer` 계정으로 `herjune3369` 저장소에 접근 시도 → 권한 거부

### **해결**
1. **herjune3369 계정의 인증 정보 사용**
   - SSH 키를 herjune3369 계정에 등록
   - 또는 Personal Access Token을 herjune3369 계정으로 발급

2. **Git 원격 URL 확인**
   - 올바른 저장소 주소: `git@github.com:herjune3369/csap-audit.git`
   - 또는 `https://github.com/herjune3369/csap-audit.git`

---

## 📝 빠른 해결 체크리스트

- [ ] herjune3369 계정으로 GitHub 로그인 확인
- [ ] SSH 키 생성 또는 확인
- [ ] SSH 키를 herjune3369 계정에 등록
- [ ] Git 원격 URL을 SSH로 변경: `git remote set-url origin git@github.com:herjune3369/csap-audit.git`
- [ ] SSH 연결 테스트: `ssh -T git@github.com`
- [ ] Push 테스트: `git push origin main`

---

## 🔍 확인 명령어

### **현재 원격 저장소 확인**
```bash
git remote -v
# 올바른 출력: origin  git@github.com:herjune3369/csap-audit.git (fetch)
#            origin  git@github.com:herjune3369/csap-audit.git (push)
```

### **SSH 연결 테스트**
```bash
ssh -T git@github.com
# 올바른 출력: Hi herjune3369! You've successfully authenticated...
```

### **Git 사용자 정보 확인**
```bash
git config user.name
git config user.email
```

---

## ✅ 해결 완료 후

인증이 완료되면 정상적으로 push가 가능합니다:

```bash
git add devops-1/
git commit -m "Fix Internet Gateway issue"
git push origin main
```

---

**계정 변경 문제 해결 완료!**

