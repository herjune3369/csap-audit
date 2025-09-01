#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 호출 디버깅 테스트 스크립트
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from llm_caller import LLMCaller

# .env 파일 로드
load_dotenv()


async def test_single_llm_call():
    """단일 LLM 호출 테스트"""
    try:
        print("🔍 LLM 호출 테스트 시작...")

        # LLM 호출기 초기화
        caller = LLMCaller()

        # 간단한 테스트 프롬프트
        test_prompt = """
다음은 Linux 시스템 보안 점검 결과입니다.

● CCE ID: CCE-0001
● 점검 항목: root 계정 원격 접속 제한
● 결과: 취약
● 현황: PermitRootLogin is set to  (should be no)
● 개선방안: SSH 설정에서 PermitRootLogin을 no로 설정하십시오.

질문:
1. 이 취약점이 발생하면 어떤 보안 위협과 공격 시나리오가 있습니까?
2. 이 항목의 목적과 보안 중요성을 비전문가가 이해할 수 있도록 설명해 주세요.
3. 실제 Linux 시스템 기준으로 조치하는 방법을 알려주세요.

JSON 형식으로 응답해주세요:
{
  "상세해설": "상세한 설명",
  "공격시나리오": "공격 시나리오 설명",
  "비전문가설명": "쉬운 설명",
  "조치방법": ["1단계", "2단계", "3단계"]
}
"""

        print(f"📝 테스트 프롬프트 길이: {len(test_prompt)} 문자")
        print("🔄 LLM 호출 시작...")

        # LLM 호출
        result = await caller.call_llm(test_prompt)

        print("📊 결과:")
        print(f"성공: {result['success']}")

        if result["success"]:
            print("✅ LLM 호출 성공!")
            print("📝 응답 데이터:")
            print(json.dumps(result["data"], ensure_ascii=False, indent=2))
        else:
            print(f"❌ LLM 호출 실패: {result.get('error', 'Unknown error')}")
            print(f"📝 원본 응답: {result.get('raw_response', 'No response')}")

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")


async def test_multiple_calls():
    """여러 번의 LLM 호출 테스트 (5개 항목)"""
    try:
        print("\n🔍 다중 LLM 호출 테스트 시작...")

        caller = LLMCaller()

        test_prompts = [
            {"CCE_ID": "CCE-0001", "prompt": "Linux root 계정 원격 접속 제한에 대한 보안 분석을 해주세요."},
            {"CCE_ID": "CCE-0002", "prompt": "Linux 패스워드 복잡도 설정에 대한 보안 분석을 해주세요."},
            {"CCE_ID": "CCE-0003", "prompt": "Linux 파일 권한 설정에 대한 보안 분석을 해주세요."},
            {"CCE_ID": "CCE-0004", "prompt": "Linux 패스워드 최대 사용 기간 설정에 대한 보안 분석을 해주세요."},
            {"CCE_ID": "CCE-0005", "prompt": "Linux 패스워드 파일 보호에 대한 보안 분석을 해주세요."},
        ]

        print(f"📋 {len(test_prompts)}개 프롬프트 테스트")

        results = await caller.process_prompts_batch(test_prompts)

        print(f"📊 결과:")
        success_count = sum(1 for r in results if r["llm_response"]["success"])
        failure_count = len(results) - success_count

        print(f"✅ 성공: {success_count}")
        print(f"❌ 실패: {failure_count}")

        # 상세 결과 출력
        for i, result in enumerate(results, 1):
            cce_id = result["CCE_ID"]
            success = result["llm_response"]["success"]
            status = "✅ 성공" if success else "❌ 실패"
            print(f"  {i}. {cce_id}: {status}")

            if not success:
                error = result["llm_response"].get("error", "Unknown error")
                print(f"     오류: {error}")

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")


async def main():
    """메인 실행 함수"""
    print("🚀 LLM 호출 디버깅 테스트 시작")
    print("=" * 50)

    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    print(f"✅ API 키 확인됨 (길이: {len(api_key)} 문자)")

    # 단일 호출 테스트
    await test_single_llm_call()

    # 다중 호출 테스트
    await test_multiple_calls()

    print("\n🏁 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())
