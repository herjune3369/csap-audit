#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
36개 항목 처리 시간 측정 테스트
"""

import asyncio
import time
import sys
import os

# scripts 디렉토리 추가
sys.path.append(os.path.dirname(__file__))

from llm_caller import LLMCaller
from llm_prompt_generator import generate_batch_prompts
from load_diagnostic_items import load_diagnostic_items


async def test_single_item_time():
    """단일 항목 처리 시간 측정"""
    print("🔍 단일 항목 처리 시간 측정...")

    # 테스트용 간단한 항목
    test_item = {
        "CCE_ID": "CCE-0001",
        "점검항목": "root 계정 원격 접속 제한",
        "결과": "취약",
        "현황": "PermitRootLogin 설정 문제",
        "개선방안": "no로 설정",
    }

    # 프롬프트 생성
    prompts = generate_batch_prompts([test_item], "Linux")

    # LLM 호출 시간 측정
    caller = LLMCaller()

    start_time = time.time()
    results = await caller.process_prompts_batch(prompts)
    end_time = time.time()

    processing_time = end_time - start_time
    success = results[0]["llm_response"]["success"]

    print(f"⏱️  단일 항목 처리 시간: {processing_time:.1f}초")
    print(f"✅ 성공 여부: {success}")

    return processing_time


async def test_batch_time():
    """배치 처리 시간 측정 (5개 항목)"""
    print("\n🔍 배치 처리 시간 측정 (5개 항목)...")

    # 5개 테스트 항목
    test_items = [
        {
            "CCE_ID": f"CCE-{i:04d}",
            "점검항목": f"테스트 항목 {i}",
            "결과": "취약",
            "현황": "테스트",
            "개선방안": "테스트",
        }
        for i in range(1, 6)
    ]

    # 프롬프트 생성
    prompts = generate_batch_prompts(test_items, "Linux")

    # LLM 호출 시간 측정
    caller = LLMCaller()

    start_time = time.time()
    results = await caller.process_prompts_batch(prompts)
    end_time = time.time()

    processing_time = end_time - start_time
    success_count = sum(1 for r in results if r["llm_response"]["success"])

    print(f"⏱️  배치 처리 시간: {processing_time:.1f}초")
    print(f"✅ 성공: {success_count}, ❌ 실패: {len(results) - success_count}")
    print(f"📊 평균 처리 시간: {processing_time/len(results):.1f}초/항목")

    return processing_time


def calculate_total_time():
    """36개 항목 전체 처리 시간 계산"""
    print("\n📊 36개 항목 전체 처리 시간 계산...")

    # 실제 진단 결과 로드
    items = load_diagnostic_items("../output/real_linux_result.json")
    print(f"📋 {len(items)}개 항목 로드 완료")

    # 프롬프트 생성 시간 (즉시)
    prompts = generate_batch_prompts(items, "Linux")
    print(f"📝 {len(prompts)}개 프롬프트 생성 완료")

    # 처리 시간 계산
    batch_size = 5
    total_batches = (len(items) + batch_size - 1) // batch_size  # 올림 나눗셈

    # 예상 시간 계산
    avg_time_per_item = 15  # 초 (실제 측정 기반)
    batch_wait_time = 20  # 초
    individual_wait_time = 8  # 초

    total_processing_time = len(items) * avg_time_per_item
    total_wait_time = (total_batches - 1) * batch_wait_time + (
        len(items) - 1
    ) * individual_wait_time

    total_time = total_processing_time + total_wait_time
    total_minutes = total_time / 60

    print(f"⏱️  예상 총 처리 시간: {total_time:.1f}초 ({total_minutes:.1f}분)")
    print(f"📊 배치 수: {total_batches}개")
    print(f"⏳ 처리 시간: {total_processing_time:.1f}초")
    print(f"⏸️  대기 시간: {total_wait_time:.1f}초")


async def main():
    """메인 실행 함수"""
    print("🚀 36개 항목 처리 시간 측정 시작")
    print("=" * 50)

    try:
        # 단일 항목 처리 시간 측정
        single_time = await test_single_item_time()

        # 배치 처리 시간 측정
        batch_time = await test_batch_time()

        # 전체 처리 시간 계산
        calculate_total_time()

        print("\n✅ 시간 측정 완료!")

    except KeyboardInterrupt:
        print("\n⏹️  사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
