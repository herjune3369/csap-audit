#!/bin/bash

# JSON 결과 작성 유틸리티 (SaaS 시스템 최적화)
# 사용법: add_check_result "CCE-0001" "root 계정 원격 접속 제한" "양호" "PermitRootLogin is set to no" "패스워드 정책을 강화하십시오"

# 기본 결과 파일 경로
RESULT_FILE="/tmp/linux_result.json"
OUTPUT_DIR="./output"

# 출력 디렉토리 생성
create_output_dir() {
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
    fi
}

# JSON 파일 초기화
init_json() {
    create_output_dir
    
    # 메타데이터와 함께 배열 형태로 초기화
    echo "{" > "$RESULT_FILE"
    echo "  \"metadata\": {" >> "$RESULT_FILE"
    echo "    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$RESULT_FILE"
    echo "    \"hostname\": \"$(hostname)\"," >> "$RESULT_FILE"
    echo "    \"os_info\": \"$(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"' 2>/dev/null || echo 'Unknown')\"," >> "$RESULT_FILE"
    echo "    \"os_type\": \"linux\"," >> "$RESULT_FILE"
    echo "    \"total_checks\": 36," >> "$RESULT_FILE"
    echo "    \"version\": \"1.0\"" >> "$RESULT_FILE"
    echo "  }," >> "$RESULT_FILE"
    echo "  \"results\": [" >> "$RESULT_FILE"
}

# 체크 결과 추가 (SaaS 시스템 최적화)
add_check_result() {
    local cce_id="$1"
    local item="$2"
    local status="$3"
    local detail="$4"
    local remediation="$5"
    
    # JSON 이스케이프 처리
    item=$(echo "$item" | sed 's/"/\\"/g')
    detail=$(echo "$detail" | sed 's/"/\\"/g')
    remediation=$(echo "$remediation" | sed 's/"/\\"/g')
    
    # remediation이 제공되지 않은 경우 기본값 설정
    if [[ -z "$remediation" ]]; then
        case "$status" in
            "양호")
                remediation="현재 설정이 적절합니다."
                ;;
            "취약")
                remediation="보안 강화 조치가 필요합니다."
                ;;
            "정보")
                remediation="추가 정보 확인이 필요합니다."
                ;;
            *)
                remediation="수동 확인이 필요합니다."
                ;;
        esac
    fi
    
    echo "    {" >> "$RESULT_FILE"
    echo "      \"CCE_ID\": \"$cce_id\"," >> "$RESULT_FILE"
    echo "      \"항목\": \"$item\"," >> "$RESULT_FILE"
    echo "      \"결과\": \"$status\"," >> "$RESULT_FILE"
    echo "      \"detail\": \"$detail\"," >> "$RESULT_FILE"
    echo "      \"remediation\": \"$remediation\"" >> "$RESULT_FILE"
    echo "    }," >> "$RESULT_FILE"
}

# JSON 파일 완성
finish_json() {
    # 마지막 쉼표 제거
    sed -i '$ s/,$//' "$RESULT_FILE"
    echo "  ]" >> "$RESULT_FILE"
    echo "}" >> "$RESULT_FILE"
    
    # 결과 통계 계산
    local total_checks=$(jq '.results | length' "$RESULT_FILE" 2>/dev/null || echo "0")
    local good_count=$(jq '.results | map(select(.결과 == "양호")) | length' "$RESULT_FILE" 2>/dev/null || echo "0")
    local vulnerable_count=$(jq '.results | map(select(.결과 == "취약")) | length' "$RESULT_FILE" 2>/dev/null || echo "0")
    local info_count=$(jq '.results | map(select(.결과 == "정보")) | length' "$RESULT_FILE" 2>/dev/null || echo "0")
    
    # 메타데이터에 통계 추가
    local temp_file=$(mktemp)
    jq --arg total "$total_checks" \
       --arg good "$good_count" \
       --arg vulnerable "$vulnerable_count" \
       --arg info "$info_count" \
       '.metadata += {"statistics": {"total": $total, "good": $good, "vulnerable": $vulnerable, "info": $info}}' \
       "$RESULT_FILE" > "$temp_file" && mv "$temp_file" "$RESULT_FILE"
    
    # 출력 디렉토리에도 복사
    cp "$RESULT_FILE" "$OUTPUT_DIR/linux_result.json"
    
    echo "✅ 진단 결과가 저장되었습니다:"
    echo "   📄 $RESULT_FILE"
    echo "   📄 $OUTPUT_DIR/linux_result.json"
    echo ""
    echo "📊 진단 통계:"
    echo "   📈 총 항목: $total_checks"
    echo "   ✅ 양호: $good_count"
    echo "   ❌ 취약: $vulnerable_count"
    echo "   ℹ️  정보: $info_count"
}

# 결과 파일 경로 반환
get_result_file() {
    echo "$RESULT_FILE"
}

# 결과 파일 유효성 검증
validate_json() {
    local file="$1"
    if [[ -f "$file" ]]; then
        if jq empty "$file" 2>/dev/null; then
            echo "✅ JSON 파일이 유효합니다: $file"
            return 0
        else
            echo "❌ JSON 파일이 유효하지 않습니다: $file"
            return 1
        fi
    else
        echo "❌ 결과 파일이 존재하지 않습니다: $file"
        return 1
    fi
}

# 결과 파일 정렬 (CCE_ID 기준)
sort_results() {
    local file="$1"
    local temp_file=$(mktemp)
    
    jq '.results |= sort_by(.CCE_ID)' "$file" > "$temp_file" && mv "$temp_file" "$file"
    
    echo "✅ 결과가 CCE_ID 기준으로 정렬되었습니다."
}

# 예외 처리 함수
handle_error() {
    local error_msg="$1"
    echo "❌ 오류 발생: $error_msg" >&2
    
    # 부분 결과라도 저장
    if [[ -f "$RESULT_FILE" ]]; then
        finish_json
        echo "⚠️  부분 결과가 저장되었습니다."
    fi
    
    exit 1
} 