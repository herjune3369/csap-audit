#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 프롬프트 생성기
로딩된 진단 항목을 기반으로 LLM에 전달할 프롬프트를 생성
"""

import json
import logging
from typing import List, Dict, Any
from load_diagnostic_items import load_diagnostic_items

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_llm_prompt(item: Dict[str, Any], system_type: str = "Linux") -> str:
    """
    개별 진단 항목에 대한 LLM 프롬프트 생성

    Args:
        item (Dict[str, Any]): 진단 항목
        system_type (str): 시스템 타입 (Linux, Windows, DB 등)

    Returns:
        str: LLM 프롬프트
    """
    cce_id = item.get("CCE_ID", "")
    check_item = item.get("점검항목", "")
    result = item.get("결과", "")
    status = item.get("현황", "")
    improvement = item.get("개선방안", "")

    prompt = f"""
다음은 {system_type} 시스템 보안 점검 결과입니다.

● CCE ID: {cce_id}
● 점검 항목: {check_item}
● 결과: {result}
● 현황: {status}
● 개선방안: {improvement}

질문:
이 항목의 목적과 보안 중요성을 설명하고, 실제 {system_type} 시스템 기준으로 조치하는 방법을 알려주세요.

다음 JSON 형식으로 답변해주세요:
{{
    "상세해설": "취약점에 대한 상세한 기술적 설명",
    "조치방법": ["1단계: ...", "2단계: ...", "3단계: ..."]
}}
"""
    return prompt


def generate_batch_prompts(
    items: List[Dict[str, Any]], system_type: str = "Linux"
) -> List[Dict[str, Any]]:
    """
    여러 진단 항목에 대한 LLM 프롬프트 배치 생성

    Args:
        items (List[Dict[str, Any]]): 진단 항목 리스트
        system_type (str): 시스템 타입

    Returns:
        List[Dict[str, Any]]: 프롬프트와 원본 데이터가 포함된 리스트
    """
    prompts = []

    for i, item in enumerate(items):
        prompt = generate_llm_prompt(item, system_type)

        prompt_data = {
            "index": i,
            "original_item": item,
            "prompt": prompt,
            "system_type": system_type,
        }

        prompts.append(prompt_data)
        logger.info(f"프롬프트 생성 완료: {item.get('CCE_ID', 'Unknown')}")

    return prompts


def save_prompts_to_file(prompts: List[Dict[str, Any]], output_file: str):
    """
    생성된 프롬프트를 파일로 저장

    Args:
        prompts (List[Dict[str, Any]]): 프롬프트 리스트
        output_file (str): 출력 파일 경로
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

        logger.info(f"프롬프트 저장 완료: {output_file}")

    except Exception as e:
        logger.error(f"프롬프트 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    # 진단 항목 로드
    input_file = "output/linux_result.json"
    items = load_diagnostic_items(input_file)

    if not items:
        logger.error("로드할 진단 항목이 없습니다.")
        return

    print(f"📋 {len(items)}개 진단 항목 로드 완료")

    # LLM 프롬프트 생성
    system_type = "Linux"
    prompts = generate_batch_prompts(items, system_type)

    print(f"✅ {len(prompts)}개 LLM 프롬프트 생성 완료")

    # 첫 번째 프롬프트 예시 출력
    if prompts:
        first_prompt = prompts[0]
        print("\n📝 첫 번째 프롬프트 예시:")
        print("=" * 50)
        print(first_prompt["prompt"])
        print("=" * 50)

    # 프롬프트 파일로 저장
    output_file = "output/llm_prompts.json"
    save_prompts_to_file(prompts, output_file)

    print(f"\n💾 프롬프트 저장 완료: {output_file}")


if __name__ == "__main__":
    main()
