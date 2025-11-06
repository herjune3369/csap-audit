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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    cce_id = item.get('CCE_ID', '')
    check_item = item.get('점검항목', '')
    result = item.get('결과', '')
    status = item.get('현황', '')
    improvement = item.get('개선방안', '')
    
    prompt = f"""
다음은 {system_type} 시스템 보안 점검 결과입니다.

● CCE ID: {cce_id}
● 점검 항목: {check_item}
● 결과: {result}
● 현황: {status}
● 개선방안: {improvement}

다음 내용을 한국어로 자세히 작성해주세요:

1. 상세해설:
   - 이 보안 항목의 목적과 중요성 설명
   - 취약점이 존재할 경우 발생할 수 있는 구체적인 해킹 유형과 공격 시나리오
   - 실제 사례가 있다면 언급
   - 해킹 시 발생할 수 있는 피해 내용

2. 조치방법:
   - 실제 {system_type} 시스템에서 따라할 수 있는 구체적인 단계별 조치 방법
   - 각 단계마다 실행할 명령어나 설정 방법을 포함
   - 예시: "sudo vi /etc/passwd" 같은 구체적인 명령어
   - 조치 후 확인 방법도 포함

다음 JSON 형식으로 답변해주세요:
{{
    "상세해설": "이 보안 항목의 목적과 중요성을 설명하고, 취약 시 발생할 수 있는 구체적인 해킹 유형(예: SQL Injection, XSS, 권한 상승, 정보 유출 등)과 공격 시나리오를 포함한 상세한 기술적 설명",
    "조치방법": [
        "1단계: [구체적인 명령어나 설정 방법] - 예: sudo vi /etc/passwd",
        "2단계: [구체적인 명령어나 설정 방법] - 예: 특정 라인 추가 또는 수정",
        "3단계: [조치 후 확인 방법] - 예: sudo cat /etc/passwd | grep root"
    ]
}}

중요: 
- 상세해설에는 반드시 취약 시 발생할 수 있는 해킹 유형과 공격 시나리오를 포함해주세요.
- 조치방법은 실제로 따라할 수 있도록 구체적인 명령어와 설정 값을 포함해주세요.
"""
    return prompt

def generate_batch_prompts(items: List[Dict[str, Any]], system_type: str = "Linux") -> List[Dict[str, Any]]:
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
            'index': i,
            'original_item': item,
            'prompt': prompt,
            'system_type': system_type
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
        with open(output_file, 'w', encoding='utf-8') as f:
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
        print(first_prompt['prompt'])
        print("=" * 50)
    
    # 프롬프트 파일로 저장
    output_file = "output/llm_prompts.json"
    save_prompts_to_file(prompts, output_file)
    
    print(f"\n💾 프롬프트 저장 완료: {output_file}")

if __name__ == "__main__":
    main() 