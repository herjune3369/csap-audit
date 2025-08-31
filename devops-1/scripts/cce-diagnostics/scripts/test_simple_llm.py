#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 LLM 테스트 스크립트
몇 개 항목만 테스트하여 과부하 방지
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

async def test_simple_llm():
    """간단한 LLM 테스트 (3개 항목만)"""
    
    # API 키 설정
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyB-lFb9w-Uy-sJtw31xlVx8ohnQpzNje4g')
    genai.configure(api_key=api_key)
    
    # 모델 초기화
    model = genai.GenerativeModel('gemini-1.5-pro')
    print("✅ Gemini 1.5 Pro 모델 초기화 완료")
    
    # 테스트용 간단한 프롬프트들
    test_prompts = [
        {
            "CCE_ID": "CCE-0001",
            "prompt": "다음은 Linux 시스템 보안 점검 결과입니다.\n● CCE ID: CCE-0001\n● 점검 항목: root 계정 원격 접속 제한\n● 결과: 양호\n● 현황: PermitRootLogin no로 설정됨\n● 개선방안: 현재 설정 유지\n\n질문:\n1. 이 보안 설정의 목적과 중요성을 설명해주세요.\n2. 이 설정이 없으면 어떤 공격이 가능한가요?\n3. 비전문가도 이해할 수 있도록 설명해주세요.\n4. 실제 Linux 시스템에서 확인하는 방법을 알려주세요.\n\nJSON 형식으로 응답해주세요."
        },
        {
            "CCE_ID": "CCE-0002", 
            "prompt": "다음은 Linux 시스템 보안 점검 결과입니다.\n● CCE ID: CCE-0002\n● 점검 항목: 패스워드 최소 길이 설정\n● 결과: 취약\n● 현황: minlen=6으로 설정됨\n● 개선방안: minlen=9 이상으로 설정 권장\n\n질문:\n1. 이 취약점의 위험성을 설명해주세요.\n2. 공격자가 이 취약점을 이용하는 방법은?\n3. 비전문가도 이해할 수 있도록 설명해주세요.\n4. 실제 조치 방법을 단계별로 알려주세요.\n\nJSON 형식으로 응답해주세요."
        },
        {
            "CCE_ID": "CCE-0003",
            "prompt": "다음은 Linux 시스템 보안 점검 결과입니다.\n● CCE ID: CCE-0003\n● 점검 항목: 불필요한 서비스 비활성화\n● 결과: 양호\n● 현황: telnet, rsh 서비스 비활성화됨\n● 개선방안: 현재 설정 유지\n\n질문:\n1. 이 보안 설정의 중요성을 설명해주세요.\n2. 불필요한 서비스가 활성화되면 어떤 위험이 있나요?\n3. 비전문가도 이해할 수 있도록 설명해주세요.\n4. 서비스 상태를 확인하는 명령어를 알려주세요.\n\nJSON 형식으로 응답해주세요."
        }
    ]
    
    results = []
    
    for i, prompt_data in enumerate(test_prompts, 1):
        cce_id = prompt_data['CCE_ID']
        prompt_text = prompt_data['prompt']
        
        print(f"\n🔄 처리 중: {i}/3 - {cce_id}")
        
        try:
            # LLM 호출
            response = await asyncio.wait_for(
                model.generate_content_async(prompt_text),
                timeout=60
            )
            
            print(f"✅ {cce_id} 처리 완료 (응답 길이: {len(response.text)} 문자)")
            
            # JSON 파싱 시도
            try:
                llm_data = json.loads(response.text)
                print(f"✅ JSON 파싱 성공")
            except json.JSONDecodeError:
                print(f"⚠️ JSON 파싱 실패, 텍스트 응답 사용")
                llm_data = {"raw_response": response.text}
            
            results.append({
                'CCE_ID': cce_id,
                'success': True,
                'data': llm_data
            })
            
        except Exception as e:
            print(f"❌ {cce_id} 처리 실패: {e}")
            results.append({
                'CCE_ID': cce_id,
                'success': False,
                'error': str(e)
            })
        
        # 요청 간 5초 대기
        if i < len(test_prompts):
            print("⏳ 5초 대기 중...")
            await asyncio.sleep(5)
    
    print(f"\n🎉 테스트 완료: {len(results)}개 결과")
    
    # 결과 저장
    with open('test_llm_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("💾 결과가 test_llm_results.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(test_simple_llm()) 