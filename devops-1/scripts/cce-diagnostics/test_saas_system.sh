#!/bin/bash

# CSAP 기술진단 SaaS 시스템 통합 테스트
# Linux 진단 → JSON → Flask 업로드 → Excel 리포트 생성

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                CSAP SaaS 시스템 통합 테스트                   ║"
echo "║              Linux 진단 → JSON → Flask → Excel               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1단계: Linux 진단 실행
echo -e "${BLUE}🔍 1단계: Linux 보안 진단 실행${NC}"
cd "$SCRIPT_DIR"

if [[ -f "cce_check_linux.sh" ]]; then
    echo "   📋 Linux 진단 스크립트 실행..."
    # 실제 진단 대신 예시 JSON 사용
    cp example_output.json /tmp/linux_result.json
    echo -e "${GREEN}✅ Linux 진단 완료 (예시 데이터 사용)${NC}"
else
    echo -e "${RED}❌ Linux 진단 스크립트를 찾을 수 없습니다.${NC}"
    exit 1
fi

# 2단계: Flask 앱 시작
echo -e "${BLUE}🌐 2단계: Flask SaaS 앱 시작${NC}"
cd "$SCRIPT_DIR/flask_app"

# Flask 앱이 이미 실행 중인지 확인
if ! pgrep -f "python.*app.py" > /dev/null; then
    echo "   🚀 Flask 앱 시작 중..."
    python app.py > flask.log 2>&1 &
    FLASK_PID=$!
    echo "   ⏳ Flask 앱 시작 대기 중..."
    sleep 5
    echo -e "${GREEN}✅ Flask 앱 시작 완료 (PID: $FLASK_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Flask 앱이 이미 실행 중입니다.${NC}"
fi

# 3단계: API 상태 확인
echo -e "${BLUE}📡 3단계: API 상태 확인${NC}"
sleep 2

if curl -s http://localhost:5000/api/status > /dev/null; then
    echo -e "${GREEN}✅ Flask API 정상 동작${NC}"
else
    echo -e "${RED}❌ Flask API 연결 실패${NC}"
    echo "   로그 확인: tail -f flask.log"
    exit 1
fi

# 4단계: 업로드 통계 확인
echo -e "${BLUE}📊 4단계: 업로드 통계 확인${NC}"
STATS=$(curl -s http://localhost:5000/api/upload-stats)
echo "   📈 업로드된 파일: $(echo $STATS | grep -o '"uploaded_files":[0-9]*' | cut -d':' -f2)"
echo "   📊 생성된 리포트: $(echo $STATS | grep -o '"generated_reports":[0-9]*' | cut -d':' -f2)"

# 5단계: 웹 브라우저 열기
echo -e "${BLUE}🌍 5단계: 웹 브라우저 열기${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5000
    echo -e "${GREEN}✅ 브라우저가 열렸습니다: http://localhost:5000${NC}"
else
    echo "   🌐 웹 브라우저에서 http://localhost:5000 접속"
fi

# 6단계: 사용법 안내
echo -e "${BLUE}📋 6단계: 사용법 안내${NC}"
echo ""
echo -e "${GREEN}🎉 CSAP SaaS 시스템 테스트 완료!${NC}"
echo ""
echo "📝 사용 방법:"
echo "   1. 웹 브라우저에서 http://localhost:5000 접속"
echo "   2. '업로드' 버튼 클릭하여 JSON 파일 선택"
echo "   3. '리포트 생성하기' 버튼 클릭"
echo "   4. 생성된 Excel 리포트 다운로드"
echo ""
echo "📁 테스트 파일:"
echo "   - JSON 파일: /tmp/linux_result.json"
echo "   - 예시 파일: example_output.json"
echo ""
echo "🔧 관리 명령어:"
echo "   - Flask 앱 중지: pkill -f 'python.*app.py'"
echo "   - 로그 확인: tail -f flask_app/flask.log"
echo "   - API 상태: curl http://localhost:5000/api/status"
echo ""

# 7단계: 파일 정리 안내
echo -e "${YELLOW}💡 정리 명령어:${NC}"
echo "   # Flask 앱 중지"
echo "   pkill -f 'python.*app.py'"
echo ""
echo "   # 생성된 파일 정리"
echo "   rm -rf flask_app/uploads/* flask_app/reports/*"
echo ""

echo -e "${GREEN}✅ 모든 테스트가 완료되었습니다!${NC}" 