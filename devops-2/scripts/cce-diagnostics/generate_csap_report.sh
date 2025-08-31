#!/bin/bash

# CSAP 기술진단 통합 리포트 생성 스크립트
# Linux 진단 → JSON → Excel 리포트 자동 생성

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$SCRIPT_DIR/report_generator"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                CSAP 기술진단 리포트 생성기                    ║"
echo "║                    Linux → Excel 자동 변환                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1단계: Linux 진단 실행
echo -e "${BLUE}🔍 1단계: Linux 보안 진단 실행 중...${NC}"
cd "$SCRIPT_DIR"

# 루트 권한 확인
if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  루트 권한이 없습니다. 일부 진단이 제한될 수 있습니다.${NC}"
    echo "   sudo $0"
fi

# Linux 진단 실행
if [[ -f "cce_check_linux.sh" ]]; then
    echo "   📋 Linux 진단 스크립트 실행..."
    ./cce_check_linux.sh -o /tmp/linux_result.json
    echo -e "${GREEN}✅ Linux 진단 완료${NC}"
else
    echo -e "${RED}❌ Linux 진단 스크립트를 찾을 수 없습니다.${NC}"
    exit 1
fi

# 2단계: JSON 파일 확인
echo -e "${BLUE}📄 2단계: JSON 결과 파일 확인...${NC}"
if [[ -f "/tmp/linux_result.json" ]]; then
    echo "   ✅ JSON 파일 생성됨: /tmp/linux_result.json"
    file_size=$(stat -f%z /tmp/linux_result.json 2>/dev/null || echo "unknown")
    echo "   📊 파일 크기: $file_size bytes"
else
    echo -e "${RED}❌ JSON 파일이 생성되지 않았습니다.${NC}"
    exit 1
fi

# 3단계: Excel 리포트 생성
echo -e "${BLUE}📊 3단계: Excel 리포트 생성 중...${NC}"
cd "$REPORT_DIR"

if [[ -f "generate_linux_excel.py" ]]; then
    echo "   🐍 Python 스크립트 실행..."
    python generate_linux_excel.py
    echo -e "${GREEN}✅ Excel 리포트 생성 완료${NC}"
else
    echo -e "${RED}❌ Excel 생성 스크립트를 찾을 수 없습니다.${NC}"
    exit 1
fi

# 4단계: 결과 요약
echo -e "${BLUE}📋 4단계: 결과 요약${NC}"
echo ""
echo -e "${GREEN}🎉 CSAP 기술진단 리포트 생성 완료!${NC}"
echo ""

# 생성된 파일들 확인
echo "📁 생성된 파일들:"
if [[ -f "/tmp/linux_result.json" ]]; then
    echo "   ✅ /tmp/linux_result.json"
fi
if [[ -f "/output/linux_result.json" ]]; then
    echo "   ✅ /output/linux_result.json"
fi

# Excel 파일 확인
latest_excel=$(ls -t output/linux_report_*.xlsx 2>/dev/null | head -1)
if [[ -n "$latest_excel" ]]; then
    echo "   ✅ $latest_excel"
    file_size=$(stat -f%z "$latest_excel" 2>/dev/null || echo "unknown")
    echo "   📊 Excel 파일 크기: $file_size bytes"
fi

echo ""
echo "💡 다음 단계:"
echo "   1. Excel 파일을 열어서 결과 확인"
echo "   2. SaaS 플랫폼에 업로드"
echo "   3. 챗봇 연동을 통한 QA 인터페이스 활용"
echo "   4. 취약점 항목에 대한 보안 강화 조치"
echo ""

# Excel 파일 열기 (macOS)
if [[ "$OSTYPE" == "darwin"* ]] && [[ -n "$latest_excel" ]]; then
    echo -e "${YELLOW}📂 Excel 파일을 자동으로 열까요? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        open "$latest_excel"
        echo "   🚀 Excel 파일이 열렸습니다."
    fi
fi

echo -e "${GREEN}✅ 모든 작업이 완료되었습니다!${NC}" 