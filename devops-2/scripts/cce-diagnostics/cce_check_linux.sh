#!/bin/bash

# CCE 기반 Linux 보안 진단 스크립트
# 현재: Linux 지원 (36개 진단 항목)
# 향후: Windows, macOS, Android, iOS 등 5종 지원 예정

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# OS 타입 감지 및 설정
detect_os_type() {
    if [[ -f /etc/os-release ]]; then
        # Linux 계열
        local os_name=$(grep "^ID=" /etc/os-release | cut -d'=' -f2 | tr -d '"')
        case "$os_name" in
            "ubuntu"|"debian")
                echo "linux-debian"
                ;;
            "centos"|"rhel"|"fedora"|"rocky"|"alma")
                echo "linux-redhat"
                ;;
            "sles"|"opensuse")
                echo "linux-suse"
                ;;
            *)
                echo "linux-generic"
                ;;
        esac
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# OS별 진단 스크립트 로드
load_os_specific_checks() {
    local os_type="$1"
    local checks_dir="$SCRIPT_DIR/checks"
    
    case "$os_type" in
        "linux-debian"|"linux-redhat"|"linux-suse"|"linux-generic")
            # Linux 계열 공통 체크
            source "$checks_dir/linux/server/check_account_management.sh"
            source "$checks_dir/linux/server/check_file_permissions.sh"
            source "$checks_dir/linux/server/check_service_management.sh"
            source "$checks_dir/linux/server/check_patch_log_management.sh"
            ;;
        "macos")
            # macOS에서도 Linux 진단 실행 (호환성 모드)
            echo "🍎 macOS에서 Linux 진단을 호환성 모드로 실행합니다..."
            source "$checks_dir/linux/server/check_account_management.sh"
            source "$checks_dir/linux/server/check_file_permissions.sh"
            source "$checks_dir/linux/server/check_service_management.sh"
            source "$checks_dir/linux/server/check_patch_log_management.sh"
            ;;
        "windows")
            # Windows 전용 체크 (향후 구현)
            echo "⚠️  Windows 지원은 향후 구현 예정입니다."
            ;;
        *)
            echo "❌ 지원하지 않는 OS 타입: $os_type"
            exit 1
            ;;
    esac
}

# OS별 진단 실행 함수
run_os_specific_checks() {
    local os_type="$1"
    
    case "$os_type" in
        "linux-debian"|"linux-redhat"|"linux-suse"|"linux-generic")
            echo "🐧 Linux 진단 실행 중..."
            run_account_checks
            run_file_permission_checks
            run_service_management_checks
            run_patch_log_management_checks
            ;;
        "macos")
            echo "🍎 macOS에서 Linux 진단 실행 중... (호환성 모드)"
            run_account_checks
            run_file_permission_checks
            run_service_management_checks
            run_patch_log_management_checks
            ;;
        "windows")
            echo "🪟 Windows 진단 실행 중... (향후 구현)"
            ;;
    esac
}

# 유틸리티 및 체크 스크립트 소스
source "$SCRIPT_DIR/utils/json_writer.sh"

# 사용법 출력
show_usage() {
    echo -e "${BLUE}CCE 기반 Linux 보안 진단 스크립트${NC}"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -h, --help     이 도움말을 표시합니다"
    echo "  -v, --verbose  상세한 출력을 표시합니다"
    echo "  -o, --output   결과 파일 경로를 지정합니다 (기본: /tmp/cce_check_result.json)"
    echo "  --os-type      OS 타입을 수동으로 지정합니다 (자동 감지 기본)"
    echo ""
    echo "지원 OS (현재/향후):"
    echo "  🐧 Linux: Ubuntu, CentOS, RHEL, SUSE 등 (36개 진단 항목)"
    echo "  🍎 macOS: (향후 지원 예정)"
    echo "  🪟 Windows: (향후 지원 예정)"
    echo "  📱 Mobile: Android, iOS (향후 지원 예정)"
    echo ""
    echo "예시:"
    echo "  $0                    # 기본 실행 (자동 OS 감지)"
    echo "  $0 -v                 # 상세 출력과 함께 실행"
    echo "  $0 -o ./result.json   # 결과를 지정된 파일에 저장"
    echo "  $0 --os-type linux-redhat  # OS 타입 수동 지정"
    echo ""
}

# 진단 시작 메시지
show_banner() {
    local os_type="$1"
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                CCE 기반 Linux 보안 진단                      ║"
    echo "║                    CSAP 인증 준비용                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "🔍 진단 시작: $(date)"
    echo "🖥️  호스트명: $(hostname)"
    echo "💻 OS 타입: $os_type"
    
    # OS별 정보 표시
    case "$os_type" in
        "linux-debian"|"linux-redhat"|"linux-suse"|"linux-generic")
            echo "🐧 OS 정보: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')"
            ;;
        "macos")
            echo "🍎 OS 정보: $(sw_vers -productName) $(sw_vers -productVersion)"
            ;;
        "windows")
            echo "🪟 OS 정보: Windows"
            ;;
    esac
    echo ""
}

# 진단 완료 메시지
show_summary() {
    local result_file="$1"
    local os_type="$2"
    echo ""
    echo -e "${GREEN}✅ Linux 진단 완료!${NC}"
    echo "📄 결과 파일: $result_file"
    echo "📄 출력 파일: /output/linux_result.json"
    echo "💻 진단 대상: $os_type"
    echo ""
    echo "📊 결과 요약:"
    
    # JSON 결과에서 통계 계산
    local total_checks=$(jq '.metadata.statistics.total' "$result_file" 2>/dev/null || echo "0")
    local good_count=$(jq '.metadata.statistics.good' "$result_file" 2>/dev/null || echo "0")
    local vulnerable_count=$(jq '.metadata.statistics.vulnerable' "$result_file" 2>/dev/null || echo "0")
    local info_count=$(jq '.metadata.statistics.info' "$result_file" 2>/dev/null || echo "0")
    
    echo "   📈 총 진단 항목: $total_checks"
    echo "   ✅ 양호: $good_count"
    echo "   ❌ 취약: $vulnerable_count"
    echo "   ℹ️  정보: $info_count"
    echo ""
    echo "💡 SaaS 시스템 연동:"
    echo "   1. JSON 파일을 SaaS 플랫폼에 업로드"
    echo "   2. 자동 생성된 보고서 확인"
    echo "   3. 챗봇 연동을 통한 QA 인터페이스 활용"
    echo "   4. 취약점 항목에 대한 보안 강화 조치"
    echo ""
    echo "🔄 향후 확장 계획:"
    echo "   - 🪟 Windows Server 지원"
    echo "   - 🗄️ MySQL 보안 진단"
    echo "   - 🌐 Nginx 보안 진단"
    echo "   - 🐳 Docker 보안 진단"
    echo ""
    
    # JSON 파일 유효성 검증
    if validate_json "$result_file"; then
        echo "✅ JSON 파일이 SaaS 시스템에 적합합니다."
    else
        echo "❌ JSON 파일에 문제가 있습니다."
    fi
}

# 메인 실행 함수
main() {
    local verbose=false
    local output_file="/tmp/cce_check_result.json"
    local os_type=""
    
    # 명령행 인수 처리
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            --os-type)
                os_type="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}❌ 알 수 없는 옵션: $1${NC}"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # OS 타입 감지 (수동 지정이 없으면 자동 감지)
    if [[ -z "$os_type" ]]; then
        os_type=$(detect_os_type)
    fi
    
    # Linux 계열이 아닌 경우 권한 확인 생략
    if [[ "$os_type" =~ ^linux ]]; then
        # 루트 권한 확인
        if [[ $EUID -ne 0 ]]; then
            echo -e "${RED}❌ Linux 진단은 루트 권한으로 실행해야 합니다.${NC}"
            echo "   sudo $0"
            exit 1
        fi
    fi
    
    # 배너 표시
    show_banner "$os_type"
    
    # OS별 진단 스크립트 로드
    load_os_specific_checks "$os_type"
    
    # JSON 파일 초기화
    init_json
    
    # 진단 실행
    echo -e "${BLUE}🔍 Linux 진단 항목 실행 중...${NC}"
    echo ""
    
    if [[ "$verbose" == "true" ]]; then
        set -x
    fi
    
    # OS별 진단 실행
    run_os_specific_checks "$os_type"
    
    # JSON 파일 완성
    finish_json
    
    # 결과 요약 표시
    show_summary "$output_file" "$os_type"
}

# 스크립트 실행
main "$@" 