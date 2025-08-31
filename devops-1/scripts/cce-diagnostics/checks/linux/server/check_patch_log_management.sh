#!/bin/bash

# 패치 및 로그 관리 진단 스크립트
# CCE-0030 ~ CCE-0036

# 절대 경로로 수정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../utils/json_writer.sh"

# CCE-0035: 최신 보안 패치 및 벤더 권고 사항 적용
check_security_patches() {
    local os_type=""
    local update_available=false
    
    # OS 타입 확인
    if [[ -f /etc/os-release ]]; then
        os_type=$(grep "^ID=" /etc/os-release | cut -d= -f2 | tr -d '"')
    elif [[ -f /etc/redhat-release ]]; then
        os_type="rhel"
    elif [[ -f /etc/debian_version ]]; then
        os_type="debian"
    else
        os_type="unknown"
    fi
    
    # OS별 패키지 업데이트 확인
    case "$os_type" in
        "ubuntu"|"debian")
        apt list --upgradable 2>/dev/null | grep -q "security"
        if [[ $? -eq 0 ]]; then
            update_available=true
        fi
            ;;
        "rhel"|"centos"|"fedora")
        yum check-update --security 2>/dev/null | grep -q "security"
        if [[ $? -eq 0 ]]; then
            update_available=true
        fi
            ;;
        *)
            # 알 수 없는 OS의 경우 수동 확인 필요
            update_available=true
            ;;
    esac
    
    if [[ "$update_available" == "true" ]]; then
        add_check_result "CCE-0035" "최신 보안 패치 및 벤더 권고 사항 적용" "취약" "Security updates are available for $os_type"
    else
        add_check_result "CCE-0035" "최신 보안 패치 및 벤더 권고 사항 적용" "양호" "System appears to be up to date with security patches"
    fi
}

# CCE-0036: 로그의 정기적 검토 및 백업
check_log_management() {
    local log_rotation_configured=false
    local log_backup_configured=false
    local status="양호"
    local detail=""
    
    # logrotate 설정 확인
    if [[ -f /etc/logrotate.conf ]]; then
        log_rotation_configured=true
    fi
    
    # 로그 백업 설정 확인 (cron 작업에서 로그 백업 확인)
    local log_backup_cron=$(crontab -l 2>/dev/null | grep -i "log.*backup\|backup.*log")
    if [[ -n "$log_backup_cron" ]]; then
        log_backup_configured=true
    fi
    
    # rsyslog 설정 확인
    local rsyslog_conf="/etc/rsyslog.conf"
    if [[ -f "$rsyslog_conf" ]]; then
        local has_remote_logging=$(grep -E "^\*\.\*.*@" "$rsyslog_conf" 2>/dev/null)
        if [[ -n "$has_remote_logging" ]]; then
            log_backup_configured=true
            fi
        fi
    
    # 결과 판정
    if [[ "$log_rotation_configured" == "true" ]] && [[ "$log_backup_configured" == "true" ]]; then
        status="양호"
        detail="Log rotation and backup are properly configured"
    elif [[ "$log_rotation_configured" == "true" ]]; then
        status="정보"
        detail="Log rotation is configured but backup needs verification"
        else
        status="취약"
        detail="Log management is not properly configured"
        fi
        
    add_check_result "CCE-0036" "로그의 정기적 검토 및 백업" "$status" "$detail"
}

# 모든 패치 및 로그 관리 체크 실행
run_patch_log_management_checks() {
    echo "🔍 패치 및 로그 관리 진단 시작..."
    
    check_security_patches
    check_log_management
    
    echo "✅ 패치 및 로그 관리 진단 완료"
} 