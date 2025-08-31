#!/bin/bash

# 계정 관리 진단 스크립트
# CCE-0001 ~ CCE-0005

# 절대 경로로 수정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../utils/json_writer.sh"

# CCE-0001: root 계정 원격 접속 제한
check_root_remote_login() {
    local sshd_config="/etc/ssh/sshd_config"
    local permit_root_login=$(grep -i "PermitRootLogin" "$sshd_config" | grep -v "^#" | awk '{print $2}')
    
    if [[ "$permit_root_login" == "no" ]]; then
        add_check_result "CCE-0001" "root 계정 원격 접속 제한" "양호" "PermitRootLogin is set to no" "현재 설정이 적절합니다."
    else
        add_check_result "CCE-0001" "root 계정 원격 접속 제한" "취약" "PermitRootLogin is set to $permit_root_login (should be no)" "SSH 설정에서 PermitRootLogin을 no로 설정하십시오. (/etc/ssh/sshd_config)"
    fi
}

# CCE-0002: 패스워드 복잡도 설정
check_password_complexity() {
    local login_defs="/etc/login.defs"
    local pam_config="/etc/pam.d/common-password"
    
    local minlen=$(grep "^PASS_MIN_LEN" "$login_defs" | awk '{print $2}')
    local has_pam_pwquality=$(grep "pam_pwquality" "$pam_config" 2>/dev/null)
    
    if [[ "$minlen" -ge 8 ]] && [[ -n "$has_pam_pwquality" ]]; then
        add_check_result "CCE-0002" "패스워드 복잡도 설정" "양호" "Password complexity is properly configured (minlen: $minlen)" "현재 설정이 적절합니다."
    else
        add_check_result "CCE-0002" "패스워드 복잡도 설정" "취약" "Password complexity is not properly configured (minlen: $minlen)" "패스워드 최소 길이를 8자 이상으로 설정하고 pam_pwquality 모듈을 활성화하십시오. (/etc/login.defs, /etc/pam.d/common-password)"
    fi
}

# CCE-0003: 계정 잠금 임계값 설정
check_account_lockout() {
    local pam_config="/etc/pam.d/common-auth"
    local faillock_config="/etc/security/faillock.conf"
    
    local has_faillock=$(grep "pam_faillock" "$pam_config" 2>/dev/null)
    local deny=$(grep "^deny" "$faillock_config" 2>/dev/null | awk '{print $2}')
    
    if [[ -n "$has_faillock" ]] && [[ "$deny" -le 5 ]]; then
        add_check_result "CCE-0003" "계정 잠금 임계값 설정" "양호" "Account lockout is configured (deny: $deny)" "현재 설정이 적절합니다."
    else
        add_check_result "CCE-0003" "계정 잠금 임계값 설정" "취약" "Account lockout is not properly configured" "계정 잠금 임계값을 5회 이하로 설정하십시오. (/etc/security/faillock.conf)"
    fi
}

# CCE-0004: 패스워드 최대 사용 기간 설정
check_password_max_age() {
    local login_defs="/etc/login.defs"
    local max_age=$(grep "^PASS_MAX_DAYS" "$login_defs" | awk '{print $2}')
    
    if [[ "$max_age" -le 90 ]] && [[ "$max_age" -gt 0 ]]; then
        add_check_result "CCE-0004" "패스워드 최대 사용 기간 설정" "양호" "Password max age is set to $max_age days" "현재 설정이 적절합니다."
    else
        add_check_result "CCE-0004" "패스워드 최대 사용 기간 설정" "취약" "Password max age is set to $max_age days (should be <= 90)" "패스워드 최대 사용 기간을 90일 이하로 설정하십시오. (/etc/login.defs)"
    fi
}

# CCE-0005: 패스워드 파일 보호
check_password_file_protection() {
    local passwd_perms=$(stat -c "%a" /etc/passwd 2>/dev/null)
    local shadow_perms=$(stat -c "%a" /etc/shadow 2>/dev/null)
    local passwd_owner=$(stat -c "%U" /etc/passwd 2>/dev/null)
    local shadow_owner=$(stat -c "%U" /etc/shadow 2>/dev/null)
    
    if [[ "$passwd_perms" == "644" ]] && [[ "$shadow_perms" == "640" ]] && \
       [[ "$passwd_owner" == "root" ]] && [[ "$shadow_owner" == "root" ]]; then
        add_check_result "CCE-0005" "패스워드 파일 보호" "양호" "Password files are properly protected" "현재 설정이 적절합니다."
    else
        add_check_result "CCE-0005" "패스워드 파일 보호" "취약" "Password files are not properly protected (passwd: $passwd_perms, shadow: $shadow_perms)" "패스워드 파일 권한을 적절히 설정하십시오. (/etc/passwd: 644, /etc/shadow: 640)"
    fi
}

# 모든 계정 관리 체크 실행
run_account_checks() {
    echo "🔍 계정 관리 진단 시작..."
    
    check_root_remote_login
    check_password_complexity
    check_account_lockout
    check_password_max_age
    check_password_file_protection
    
    echo "✅ 계정 관리 진단 완료"
} 