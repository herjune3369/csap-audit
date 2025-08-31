#!/bin/bash

# 서비스 관리 진단 스크립트
# CCE-0020 ~ CCE-0029

# 절대 경로로 수정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../utils/json_writer.sh"

# CCE-0020: Finger 서비스 비활성화
check_finger_service() {
    local finger_service=$(systemctl is-active finger 2>/dev/null || echo "inactive")
    
    if [[ "$finger_service" == "inactive" ]]; then
        add_check_result "CCE-0020" "Finger 서비스 비활성화" "양호" "Finger service is disabled or inactive"
    else
        add_check_result "CCE-0020" "Finger 서비스 비활성화" "취약" "Finger service is enabled and active"
    fi
}

# CCE-0021: Anonymous FTP 서비스 비활성화
check_anonymous_ftp() {
    local vsftpd_conf="/etc/vsftpd.conf"
    local anonymous_enabled=$(grep "^anonymous_enable" "$vsftpd_conf" 2>/dev/null | awk -F= '{print $2}' | tr -d ' ')
    
    if [[ "$anonymous_enabled" != "YES" ]]; then
        add_check_result "CCE-0021" "Anonymous FTP 서비스 비활성화" "양호" "Anonymous FTP is disabled or not configured"
    else
        add_check_result "CCE-0021" "Anonymous FTP 서비스 비활성화" "취약" "Anonymous FTP is enabled"
    fi
}

# CCE-0022: r계열 서비스 비활성화
check_r_services() {
    local r_services=("rsh" "rlogin" "rexec")
    local all_disabled=true
    
    for service in "${r_services[@]}"; do
        local status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        if [[ "$status" == "active" ]]; then
            all_disabled=false
            break
        fi
    done
    
    if [[ "$all_disabled" == "true" ]]; then
        add_check_result "CCE-0022" "r계열 서비스 비활성화" "양호" "All r-series services are disabled"
    else
        add_check_result "CCE-0022" "r계열 서비스 비활성화" "취약" "Some r-series services are enabled"
    fi
}

# CCE-0023: DoS 공격에 취약한 서비스 비활성화
check_dos_vulnerable_services() {
    local dos_services=("chargen" "daytime" "echo" "discard" "time")
    local all_disabled=true
    
    for service in "${dos_services[@]}"; do
        local status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        if [[ "$status" == "active" ]]; then
            all_disabled=false
            break
        fi
    done
    
    if [[ "$all_disabled" == "true" ]]; then
        add_check_result "CCE-0023" "DoS 공격에 취약한 서비스 비활성화" "양호" "All DoS vulnerable services are disabled"
    else
        add_check_result "CCE-0023" "DoS 공격에 취약한 서비스 비활성화" "취약" "Some DoS vulnerable services are enabled"
    fi
}

# CCE-0024: NFS 서비스 비활성화
check_nfs_service() {
    local nfs_service=$(systemctl is-active nfs-server 2>/dev/null || echo "inactive")
    
    if [[ "$nfs_service" == "inactive" ]]; then
        add_check_result "CCE-0024" "NFS 서비스 비활성화" "양호" "NFS service is disabled or inactive"
    else
        add_check_result "CCE-0024" "NFS 서비스 비활성화" "취약" "NFS service is enabled and active"
    fi
}

# CCE-0025: NFS 접근통제
check_nfs_access_control() {
    local exports_file="/etc/exports"
    
    if [[ ! -f "$exports_file" ]] || [[ ! -s "$exports_file" ]]; then
        add_check_result "CCE-0025" "NFS 접근통제" "양호" "NFS exports file is empty or not found"
    else
        local has_restrictions=$(grep -v "^#" "$exports_file" | grep -E "(ro|no_root_squash)" 2>/dev/null)
        if [[ -n "$has_restrictions" ]]; then
            add_check_result "CCE-0025" "NFS 접근통제" "양호" "NFS access controls are configured"
        else
            add_check_result "CCE-0025" "NFS 접근통제" "취약" "NFS access controls are not properly configured"
        fi
    fi
}

# CCE-0026: automountd 제거
check_automount_service() {
    local automount_service=$(systemctl is-active autofs 2>/dev/null || echo "inactive")
    
    if [[ "$automount_service" == "inactive" ]]; then
        add_check_result "CCE-0026" "automountd 제거" "양호" "Automount service is disabled or inactive"
    else
        add_check_result "CCE-0026" "automountd 제거" "취약" "Automount service is enabled and active"
    fi
}

# CCE-0027: RPC 서비스 확인
check_rpc_service() {
    local rpc_service=$(systemctl is-active rpcbind 2>/dev/null || echo "inactive")
    
    if [[ "$rpc_service" == "inactive" ]]; then
        add_check_result "CCE-0027" "RPC 서비스 확인" "양호" "RPC service is disabled or inactive"
    else
        add_check_result "CCE-0027" "RPC 서비스 확인" "취약" "RPC service is enabled and active"
    fi
}

# CCE-0028: NIS, NIS+ 점검
check_nis_services() {
    local nis_services=("ypbind" "ypserv" "yppasswdd" "ypxfrd")
    local all_disabled=true
    
    for service in "${nis_services[@]}"; do
        local status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        if [[ "$status" == "active" ]]; then
            all_disabled=false
            break
        fi
    done
    
    if [[ "$all_disabled" == "true" ]]; then
        add_check_result "CCE-0028" "NIS, NIS+ 점검" "양호" "All NIS/NIS+ services are disabled"
    else
        add_check_result "CCE-0028" "NIS, NIS+ 점검" "취약" "Some NIS/NIS+ services are enabled"
    fi
}

# CCE-0029: tftp, talk 서비스 비활성화
check_tftp_talk_services() {
    local tftp_talk_services=("tftp" "talk" "ntalk")
    local all_disabled=true
    
    for service in "${tftp_talk_services[@]}"; do
        local status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        if [[ "$status" == "active" ]]; then
            all_disabled=false
            break
        fi
    done
    
    if [[ "$all_disabled" == "true" ]]; then
        add_check_result "CCE-0029" "tftp, talk 서비스 비활성화" "양호" "All tftp/talk services are disabled"
    else
        add_check_result "CCE-0029" "tftp, talk 서비스 비활성화" "취약" "Some tftp/talk services are enabled"
    fi
}

# CCE-0030: Sendmail 버전 점검
check_sendmail_version() {
    local sendmail_version=$(sendmail -d0.1 -bv root 2>/dev/null | grep "Version" | awk '{print $2}')
    
    if [[ -n "$sendmail_version" ]]; then
        add_check_result "CCE-0030" "Sendmail 버전 점검" "정보" "Sendmail version: $sendmail_version"
    else
        add_check_result "CCE-0030" "Sendmail 버전 점검" "양호" "Sendmail is not installed or not running"
    fi
}

# CCE-0031: 스팸 메일 릴레이 제한
check_sendmail_relay() {
    local sendmail_conf="/etc/mail/sendmail.cf"
    
    if [[ ! -f "$sendmail_conf" ]]; then
        add_check_result "CCE-0031" "스팸 메일 릴레이 제한" "양호" "Sendmail is not configured"
    else
        local relay_restrictions=$(grep -i "relay" "$sendmail_conf" 2>/dev/null)
        if [[ -n "$relay_restrictions" ]]; then
            add_check_result "CCE-0031" "스팸 메일 릴레이 제한" "양호" "Sendmail relay restrictions are configured"
        else
            add_check_result "CCE-0031" "스팸 메일 릴레이 제한" "취약" "Sendmail relay restrictions are not configured"
        fi
    fi
}

# CCE-0032: 일반 사용자의 Sendmail 실행 방지
check_sendmail_permissions() {
    local sendmail_bin="/usr/sbin/sendmail"
    
    if [[ -f "$sendmail_bin" ]]; then
        local perms=$(stat -c "%a" "$sendmail_bin" 2>/dev/null)
        if [[ "$perms" == "755" ]]; then
            add_check_result "CCE-0032" "일반 사용자의 Sendmail 실행 방지" "양호" "Sendmail binary permissions are properly set"
        else
            add_check_result "CCE-0032" "일반 사용자의 Sendmail 실행 방지" "취약" "Sendmail binary permissions are not properly set: $perms"
        fi
    else
        add_check_result "CCE-0032" "일반 사용자의 Sendmail 실행 방지" "양호" "Sendmail is not installed"
    fi
}

# CCE-0033: DNS 보안 버전 패치
check_dns_security() {
    local dns_services=("bind9" "named")
    local dns_running=false
    
    for service in "${dns_services[@]}"; do
        local status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        if [[ "$status" == "active" ]]; then
            dns_running=true
            break
        fi
    done
    
    if [[ "$dns_running" == "true" ]]; then
        add_check_result "CCE-0033" "DNS 보안 버전 패치" "정보" "DNS service is running, check for latest security patches"
    else
        add_check_result "CCE-0033" "DNS 보안 버전 패치" "양호" "DNS service is not running"
    fi
}

# CCE-0034: DNS Zone Transfer 설정
check_dns_zone_transfer() {
    local named_conf="/etc/bind/named.conf"
    
    if [[ -f "$named_conf" ]]; then
        local allow_transfer=$(grep -i "allow-transfer" "$named_conf" 2>/dev/null)
        if [[ -n "$allow_transfer" ]]; then
            add_check_result "CCE-0034" "DNS Zone Transfer 설정" "양호" "DNS zone transfer restrictions are configured"
        else
            add_check_result "CCE-0034" "DNS Zone Transfer 설정" "취약" "DNS zone transfer restrictions are not configured"
        fi
    else
        add_check_result "CCE-0034" "DNS Zone Transfer 설정" "양호" "DNS is not configured"
    fi
}

# 모든 서비스 관리 체크 실행
run_service_management_checks() {
    echo "🔍 서비스 관리 진단 시작..."
    
    check_finger_service
    check_anonymous_ftp
    check_r_services
    check_dos_vulnerable_services
    check_nfs_service
    check_nfs_access_control
    check_automount_service
    check_rpc_service
    check_nis_services
    check_tftp_talk_services
    check_sendmail_version
    check_sendmail_relay
    check_sendmail_permissions
    check_dns_security
    check_dns_zone_transfer
    
    echo "✅ 서비스 관리 진단 완료"
} 