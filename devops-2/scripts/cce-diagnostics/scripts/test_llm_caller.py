#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 호출 테스트 스크립트
몇 개 항목만 테스트하여 LLM API가 정상 작동하는지 확인
"""

import json
import asyncio
import logging
from pathlib import Path
from llm_caller import LLMCaller

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_llm_caller():
    """LLM 호출 테스트"""
    try:
        # LLM 호출기 초기화
        caller = LLMCaller()
        
        # 프롬프트 파일 로드
        prompts_file = "output/llm_prompts.json"
        
        if not Path(prompts_file).exists():
            logger.error(f"프롬프트 파일을 찾을 수 없습니다: {prompts_file}")
            return
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        print(f"📋 {len(prompts)}개 프롬프트 로드 완료")
        
        # 처음 3개 항목만 테스트
        test_prompts = prompts[:3]
        print(f"🧪 처음 3개 항목으로 LLM 테스트 시작...")
        
        # LLM 배치 처리
        results = await caller.process_prompts_batch(test_prompts)
        
        print(f"✅ {len(results)}개 LLM 응답 처리 완료")
        
        # 성공/실패 통계
        success_count = sum(1 for r in results if r['llm_response']['success'])
        failure_count = len(results) - success_count
        
        print(f"📊 성공: {success_count}, 실패: {failure_count}")
        
        # 첫 번째 성공 응답 예시 출력
        for result in results:
            if result['llm_response']['success']:
                print("\n📝 첫 번째 성공 응답 예시:")
                print("=" * 50)
                print(json.dumps(result['llm_response']['data'], ensure_ascii=False, indent=2))
                print("=" * 50)
                break
        
        # 결과 저장
        output_file = "output/test_llm_responses.json"
        caller.save_results(results, output_file)
        
        print(f"\n💾 테스트 결과 저장 완료: {output_file}")
        
    except Exception as e:
        logger.error(f"LLM 테스트 중 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_caller()) 