#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 진단 항목 로딩기
CSAP Linux 취약점 진단 결과 파일을 읽고 LLM 프롬프트 생성에 필요한 필드만 정리
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_diagnostic_items(input_path: str) -> List[Dict[str, Any]]:
    """
    JSON 진단 결과 파일을 로드하여 정리된 항목 리스트 반환

    Args:
        input_path (str): JSON 파일 경로

    Returns:
        List[Dict[str, Any]]: 정리된 진단 항목 리스트
    """
    try:
        # 파일 존재 확인
        if not Path(input_path).exists():
            logger.error(f"파일을 찾을 수 없습니다: {input_path}")
            return []

        # JSON 파일 로드
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"JSON 파일 로드 완료: {input_path}")

        # 데이터 구조 확인 및 정리
        items = []

        # 기존 형식과 새로운 형식 모두 지원
        if isinstance(data, dict) and "results" in data:
            raw_items = data["results"]
        elif isinstance(data, list):
            raw_items = data
        else:
            logger.error(f"지원하지 않는 JSON 형식: {input_path}")
            return []

        # 필수 필드 검사 및 정리
        required_fields = ["CCE_ID", "항목", "결과", "detail", "remediation"]

        for i, item in enumerate(raw_items):
            if not isinstance(item, dict):
                logger.warning(f"항목 {i}가 딕셔너리가 아닙니다. 건너뜁니다.")
                continue

            # 필수 필드 확인
            missing_fields = []
            for field in required_fields:
                if field not in item or not item[field]:
                    missing_fields.append(field)

            if missing_fields:
                logger.warning(f"항목 {i}에서 필수 필드 누락: {missing_fields}")
                continue

            # 정리된 항목 생성 (필드명 매핑)
            clean_item = {
                "CCE_ID": str(item["CCE_ID"]),
                "점검항목": str(item["항목"]),
                "결과": str(item["결과"]),
                "현황": str(item["detail"]),
                "개선방안": str(item["remediation"]),
            }

            # 선택적 필드 추가
            if "시스템" in item:
                clean_item["시스템"] = str(item["시스템"])
            if "분류" in item:
                clean_item["분류"] = str(item["분류"])
            if "중요도" in item:
                clean_item["중요도"] = str(item["중요도"])
            if "detail" in item:
                clean_item["detail"] = str(item["detail"])
            if "remediation" in item:
                clean_item["remediation"] = str(item["remediation"])

            items.append(clean_item)

        logger.info(f"총 {len(items)}개 항목 로드 완료")
        return items

    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"파일 로드 중 오류: {e}")
        return []


def main():
    """메인 실행 함수"""
    # 테스트용 파일 경로들
    test_files = [
        "output/linux_result.json",
        "example_output.json",
        "report_generator/test/sample_linux_result.json",
    ]

    for file_path in test_files:
        print(f"\n📁 파일 처리: {file_path}")
        items = load_diagnostic_items(file_path)

        if items:
            print(f"✅ {len(items)}개 항목 로드 완료")
            print("📋 첫 번째 항목 예시:")
            if items:
                print(json.dumps(items[0], ensure_ascii=False, indent=2))
        else:
            print("❌ 로드된 항목이 없습니다.")


if __name__ == "__main__":
    main()
