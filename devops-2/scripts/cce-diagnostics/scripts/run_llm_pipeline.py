#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 파이프라인 통합 실행 스크립트
1단계: JSON 진단 항목 로딩
2단계: LLM 프롬프트 생성
3단계: LLM API 호출
4단계: 결과 통합 및 Excel 보고서 생성
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_step1_load_items(input_file: str) -> List[Dict[str, Any]]:
    """1단계: JSON 진단 항목 로딩"""
    print("🔄 1단계: JSON 진단 항목 로딩 시작...")
    
    from load_diagnostic_items import load_diagnostic_items
    items = load_diagnostic_items(input_file)
    
    if not items:
        raise ValueError("로드할 진단 항목이 없습니다.")
    
    print(f"✅ 1단계 완료: {len(items)}개 항목 로드")
    return items

def run_step2_generate_prompts(items: List[Dict[str, Any]], system_type: str = "Linux") -> List[Dict[str, Any]]:
    """2단계: LLM 프롬프트 생성"""
    print("🔄 2단계: LLM 프롬프트 생성 시작...")
    
    from llm_prompt_generator import generate_batch_prompts, save_prompts_to_file
    
    prompts = generate_batch_prompts(items, system_type)
    
    # 프롬프트 저장
    output_file = "output/llm_prompts.json"
    save_prompts_to_file(prompts, output_file)
    
    print(f"✅ 2단계 완료: {len(prompts)}개 프롬프트 생성")
    return prompts

async def run_step3_call_llm(prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """3단계: LLM API 호출"""
    print("🔄 3단계: LLM API 호출 시작...")
    
    from llm_caller import LLMCaller
    
    caller = LLMCaller()
    results = await caller.process_prompts_batch(prompts)
    
    # 결과 저장
    output_file = "output/llm_responses.json"
    caller.save_results(results, output_file)
    
    # 성공/실패 통계
    success_count = sum(1 for r in results if r['llm_response']['success'])
    failure_count = len(results) - success_count
    
    print(f"✅ 3단계 완료: 성공 {success_count}, 실패 {failure_count}")
    return results

def run_step4_generate_excel(results: List[Dict[str, Any]], system_type: str = "Linux"):
    """4단계: Excel 보고서 생성"""
    print("🔄 4단계: Excel 보고서 생성 시작...")
    
    # LLM 응답을 원본 데이터와 통합
    enhanced_items = []
    
    for result in results:
        original_item = result['original_item']
        llm_response = result['llm_response']
        
        if llm_response['success']:
            # LLM 응답 데이터 추가
            enhanced_item = {
                **original_item,
                '시스템': system_type,
                '상세해설': llm_response['data'].get('상세해설', ''),
                '조치방법': llm_response['data'].get('조치방법', [])
            }
        else:
            # LLM 실패 시 기본값
            enhanced_item = {
                **original_item,
                '시스템': system_type,
                '상세해설': 'LLM 처리 실패',
                '조치방법': ['LLM 처리 실패']
            }
        
        enhanced_items.append(enhanced_item)
    
    # Excel 보고서 생성
    from report_generator.generate_csap_excel import CSAPExcelReportGenerator
    
    generator = CSAPExcelReportGenerator()
    timestamp = generator.generate_csap_excel_from_items(enhanced_items, system_type)
    
    print(f"✅ 4단계 완료: Excel 보고서 생성 - {timestamp}")

async def main():
    """메인 실행 함수"""
    try:
        print("🚀 LLM 파이프라인 시작")
        print("=" * 50)
        
        # 입력 파일 설정
        input_file = "output/linux_result.json"
        system_type = "Linux"
        
        # 1단계: JSON 진단 항목 로딩
        items = run_step1_load_items(input_file)
        
        # 2단계: LLM 프롬프트 생성
        prompts = run_step2_generate_prompts(items, system_type)
        
        # 3단계: LLM API 호출
        results = await run_step3_call_llm(prompts)
        
        # 4단계: Excel 보고서 생성
        run_step4_generate_excel(results, system_type)
        
        print("=" * 50)
        print("🎉 LLM 파이프라인 완료!")
        print("\n📁 생성된 파일들:")
        print("- output/llm_prompts.json")
        print("- output/llm_responses.json")
        print("- output/csap_linux_report_*.xlsx")
        
    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 