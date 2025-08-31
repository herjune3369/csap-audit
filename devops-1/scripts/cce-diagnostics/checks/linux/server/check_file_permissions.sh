#!/bin/bash

# 파일 권한 진단 스크립트
# CCE-0006 ~ CCE-0015

# 절대 경로로 수정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../utils/json_writer.sh"

# CCE-0006: root 홈 디렉터리 소유자 설정
check_root_home_owner() {
    local root_home_owner=$(stat -c "%U" /root 2>/dev/null)
    local root_home_perms=$(stat -c "%a" /root 2>/dev/null)
    
    if [[ "$root_home_owner" == "root" ]] && [[ "$root_home_perms" == "700" ]]; then
        add_check_result "CCE-0006" "root 홈 디렉터리 소유자 설정" "양호" "Root home directory is properly owned by root with 700 permissions"
    else
        add_check_result "CCE-0006" "root 홈 디렉터리 소유자 설정" "취약" "Root home directory owner: $root_home_owner, perms: $root_home_perms"
    fi
}

# CCE-0007: 파일 및 디렉터리 소유자 설정
check_file_directory_owners() {
    local critical_files=("/etc/passwd" "/etc/shadow" "/etc/hosts" "/etc/services" "/etc/ssh/sshd_config")
    local all_secure=true
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            local owner=$(stat -c "%U" "$file" 2>/dev/null)
            if [[ "$owner" != "root" ]]; then
                all_secure=false
                break
            fi
        fi
    done
    
    if [[ "$all_secure" == "true" ]]; then
        add_check_result "CCE-0007" "파일 및 디렉터리 소유자 설정" "양호" "All critical files are properly owned by root"
    else
        add_check_result "CCE-0007" "파일 및 디렉터리 소유자 설정" "취약" "Some critical files are not owned by root"
    fi
}

# CCE-0008: /etc/passwd 파일 소유자 및 권한 설정
check_passwd_file() {
    local passwd_owner=$(stat -c "%U" /etc/passwd 2>/dev/null)
    local passwd_perms=$(stat -c "%a" /etc/passwd 2>/dev/null)
    
    if [[ "$passwd_owner" == "root" ]] && [[ "$passwd_perms" == "644" ]]; then
        add_check_result "CCE-0008" "/etc/passwd 파일 소유자 및 권한 설정" "양호" "/etc/passwd is properly configured"
    else
        add_check_result "CCE-0008" "/etc/passwd 파일 소유자 및 권한 설정" "취약" "/etc/passwd owner: $passwd_owner, perms: $passwd_perms"
    fi
}

# CCE-0009: /etc/shadow 파일 소유자 및 권한 설정
check_shadow_file() {
    local shadow_owner=$(stat -c "%U" /etc/shadow 2>/dev/null)
    local shadow_perms=$(stat -c "%a" /etc/shadow 2>/dev/null)
    
    if [[ "$shadow_owner" == "root" ]] && [[ "$shadow_perms" == "640" ]]; then
        add_check_result "CCE-0009" "/etc/shadow 파일 소유자 및 권한 설정" "양호" "/etc/shadow is properly configured"
    else
        add_check_result "CCE-0009" "/etc/shadow 파일 소유자 및 권한 설정" "취약" "/etc/shadow owner: $shadow_owner, perms: $shadow_perms"
    fi
}

# CCE-0010: /etc/hosts 파일 소유자 및 권한 설정
check_hosts_file() {
    local hosts_owner=$(stat -c "%U" /etc/hosts 2>/dev/null)
    local hosts_perms=$(stat -c "%a" /etc/hosts 2>/dev/null)
    
    if [[ "$hosts_owner" == "root" ]] && [[ "$hosts_perms" == "644" ]]; then
        add_check_result "CCE-0010" "/etc/hosts 파일 소유자 및 권한 설정" "양호" "/etc/hosts is properly configured"
    else
        add_check_result "CCE-0010" "/etc/hosts 파일 소유자 및 권한 설정" "취약" "/etc/hosts owner: $hosts_owner, perms: $hosts_perms"
    fi
}

# CCE-0011: /etc/(x)inetd.conf 파일 소유자 및 권한 설정
check_inetd_conf_file() {
    local inetd_conf="/etc/inetd.conf"
    local xinetd_conf="/etc/xinetd.conf"
    local all_secure=true
    
    if [[ -f "$inetd_conf" ]]; then
        local owner=$(stat -c "%U" "$inetd_conf" 2>/dev/null)
        local perms=$(stat -c "%a" "$inetd_conf" 2>/dev/null)
        if [[ "$owner" != "root" ]] || [[ "$perms" != "600" ]]; then
            all_secure=false
        fi
    fi
    
    if [[ -f "$xinetd_conf" ]]; then
        local owner=$(stat -c "%U" "$xinetd_conf" 2>/dev/null)
        local perms=$(stat -c "%a" "$xinetd_conf" 2>/dev/null)
        if [[ "$owner" != "root" ]] || [[ "$perms" != "600" ]]; then
            all_secure=false
        fi
    fi
    
    if [[ "$all_secure" == "true" ]]; then
        add_check_result "CCE-0011" "/etc/(x)inetd.conf 파일 소유자 및 권한 설정" "양호" "inetd/xinetd config files are properly secured"
    else
        add_check_result "CCE-0011" "/etc/(x)inetd.conf 파일 소유자 및 권한 설정" "취약" "inetd/xinetd config files are not properly secured"
    fi
}

# CCE-0012: /etc/syslog.conf 파일 소유자 및 권한 설정
check_syslog_conf_file() {
    local syslog_conf="/etc/syslog.conf"
    local rsyslog_conf="/etc/rsyslog.conf"
    local all_secure=true
    
    if [[ -f "$syslog_conf" ]]; then
        local owner=$(stat -c "%U" "$syslog_conf" 2>/dev/null)
        local perms=$(stat -c "%a" "$syslog_conf" 2>/dev/null)
        if [[ "$owner" != "root" ]] || [[ "$perms" != "644" ]]; then
            all_secure=false
        fi
    fi
    
    if [[ -f "$rsyslog_conf" ]]; then
        local owner=$(stat -c "%U" "$rsyslog_conf" 2>/dev/null)
        local perms=$(stat -c "%a" "$rsyslog_conf" 2>/dev/null)
        if [[ "$owner" != "root" ]] || [[ "$perms" != "644" ]]; then
            all_secure=false
        fi
    fi
    
    if [[ "$all_secure" == "true" ]]; then
        add_check_result "CCE-0012" "/etc/syslog.conf 파일 소유자 및 권한 설정" "양호" "syslog config files are properly secured"
    else
        add_check_result "CCE-0012" "/etc/syslog.conf 파일 소유자 및 권한 설정" "취약" "syslog config files are not properly secured"
    fi
}

# CCE-0013: /etc/services 파일 소유자 및 권한 설정
check_services_file() {
    local services_owner=$(stat -c "%U" /etc/services 2>/dev/null)
    local services_perms=$(stat -c "%a" /etc/services 2>/dev/null)
    
    if [[ "$services_owner" == "root" ]] && [[ "$services_perms" == "644" ]]; then
        add_check_result "CCE-0013" "/etc/services 파일 소유자 및 권한 설정" "양호" "/etc/services is properly configured"
    else
        add_check_result "CCE-0013" "/etc/services 파일 소유자 및 권한 설정" "취약" "/etc/services owner: $services_owner, perms: $services_perms"
    fi
}

# CCE-0014: SUID, SGID, Sticky bit 설정 파일 점검
check_suid_sgid_files() {
    local suid_files=$(find / -type f -perm -4000 2>/dev/null | wc -l)
    local sgid_files=$(find / -type f -perm -2000 2>/dev/null | wc -l)
    local sticky_dirs=$(find / -type d -perm -1000 2>/dev/null | wc -l)
    
    if [[ "$suid_files" -le 50 ]] && [[ "$sgid_files" -le 20 ]]; then
        add_check_result "CCE-0014" "SUID, SGID, Sticky bit 설정 파일 점검" "양호" "SUID files: $suid_files, SGID files: $sgid_files, Sticky dirs: $sticky_dirs"
    else
        add_check_result "CCE-0014" "SUID, SGID, Sticky bit 설정 파일 점검" "취약" "Too many SUID/SGID files found (SUID: $suid_files, SGID: $sgid_files)"
    fi
}

# CCE-0015: 사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정
check_startup_files() {
    local startup_files=("/etc/profile" "/etc/bash.bashrc" "/etc/environment" "/etc/profile.d")
    local all_secure=true
    
    for file in "${startup_files[@]}"; do
        if [[ -f "$file" ]] || [[ -d "$file" ]]; then
            local owner=$(stat -c "%U" "$file" 2>/dev/null)
            local perms=$(stat -c "%a" "$file" 2>/dev/null)
            
            if [[ "$owner" != "root" ]] || [[ "$perms" != "644" ]]; then
                all_secure=false
                break
            fi
        fi
    done
    
    if [[ "$all_secure" == "true" ]]; then
        add_check_result "CCE-0015" "사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정" "양호" "All startup files are properly secured"
    else
        add_check_result "CCE-0015" "사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정" "취약" "Some startup files are not properly secured"
    fi
}

# CCE-0016: world writable 파일 점검
check_world_writable_files() {
    local world_writable=$(find / -type f -perm -002 2>/dev/null | wc -l)
    
    if [[ "$world_writable" -le 10 ]]; then
        add_check_result "CCE-0016" "world writable 파일 점검" "양호" "World writable files: $world_writable"
    else
        add_check_result "CCE-0016" "world writable 파일 점검" "취약" "Too many world writable files found: $world_writable"
    fi
}

# CCE-0017: $HOME/.rhosts, hosts.equiv 사용 금지
check_rhosts_files() {
    local rhosts_files=$(find /home -name ".rhosts" 2>/dev/null | wc -l)
    local hosts_equiv=$(test -f /etc/hosts.equiv && echo "exists" || echo "not found")
    
    if [[ "$rhosts_files" -eq 0 ]] && [[ "$hosts_equiv" == "not found" ]]; then
        add_check_result "CCE-0017" "$HOME/.rhosts, hosts.equiv 사용 금지" "양호" "No .rhosts files found, /etc/hosts.equiv not found"
    else
        add_check_result "CCE-0017" "$HOME/.rhosts, hosts.equiv 사용 금지" "취약" "Found $rhosts_files .rhosts files, hosts.equiv: $hosts_equiv"
    fi
}

# CCE-0018: 접속 IP 및 포트 제한
check_ssh_access_restrictions() {
    local sshd_config="/etc/ssh/sshd_config"
    local allow_users=$(grep "^AllowUsers" "$sshd_config" 2>/dev/null)
    local deny_users=$(grep "^DenyUsers" "$sshd_config" 2>/dev/null)
    
    if [[ -n "$allow_users" ]] || [[ -n "$deny_users" ]]; then
        add_check_result "CCE-0018" "접속 IP 및 포트 제한" "양호" "SSH access restrictions are configured"
    else
        add_check_result "CCE-0018" "접속 IP 및 포트 제한" "취약" "No SSH access restrictions configured"
    fi
}

# CCE-0019: cron파일 소유자 및 권한 설정
check_cron_files() {
    local cron_dirs=("/etc/cron.d" "/etc/cron.daily" "/etc/cron.hourly" "/etc/cron.monthly" "/etc/cron.weekly")
    local all_secure=true
    
    for dir in "${cron_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            local owner=$(stat -c "%U" "$dir" 2>/dev/null)
            local perms=$(stat -c "%a" "$dir" 2>/dev/null)
            
            if [[ "$owner" != "root" ]] || [[ "$perms" != "700" ]]; then
                all_secure=false
                break
            fi
        fi
    done
    
    if [[ "$all_secure" == "true" ]]; then
        add_check_result "CCE-0019" "cron파일 소유자 및 권한 설정" "양호" "All cron directories are properly secured"
    else
        add_check_result "CCE-0019" "cron파일 소유자 및 권한 설정" "취약" "Some cron directories are not properly secured"
    fi
}

# 모든 파일 권한 체크 실행
run_file_permission_checks() {
    echo "🔍 파일 및 디렉터리 관리 진단 시작..."
    
    check_root_home_owner
    check_file_directory_owners
    check_passwd_file
    check_shadow_file
    check_hosts_file
    check_inetd_conf_file
    check_syslog_conf_file
    check_services_file
    check_suid_sgid_files
    check_startup_files
    check_world_writable_files
    check_rhosts_files
    check_ssh_access_restrictions
    check_cron_files
    
    echo "✅ 파일 및 디렉터리 관리 진단 완료"
} 