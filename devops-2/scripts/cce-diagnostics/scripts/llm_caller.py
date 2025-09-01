#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 호출기
생성된 프롬프트를 사용하여 LLM API를 호출하고 응답을 처리
"""

import json
import os
import asyncio
import logging
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# LLM 관련
import google.generativeai as genai

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()


class LLMCaller:
    """LLM API 호출 및 응답 처리 클래스 (API 호출 제한 관리)"""

    def __init__(self):
        # Gemini API 설정
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
            raise ValueError("GEMINI_API_KEY가 필요합니다.")

        genai.configure(api_key=api_key)

        # Gemini 1.5 Pro 모델 사용 (Flash가 과부하 상태이므로)
        try:
            self.model = genai.GenerativeModel("gemini-1.5-pro")
            logger.info("Gemini 1.5 Pro 모델 초기화 완료")
        except Exception as e:
            logger.error(f"Gemini 1.5 Pro 모델 초기화 실패: {e}")
            raise

        # API 호출 제한 관리
        self.call_count = 0
        self.last_call_time = 0
        self.rate_limit_window = 60  # 60초 윈도우
        self.max_calls_per_window = 10  # 60초당 최대 10회 호출

        logger.info("LLM 모델 초기화 완료")

    def _check_rate_limit(self):
        """API 호출 제한 확인"""
        import time

        current_time = time.time()

        # 윈도우가 지났으면 카운터 리셋
        if current_time - self.last_call_time > self.rate_limit_window:
            self.call_count = 0
            self.last_call_time = current_time

        # 호출 제한 확인
        if self.call_count >= self.max_calls_per_window:
            wait_time = self.rate_limit_window - (current_time - self.last_call_time)
            if wait_time > 0:
                logger.warning(f"API 호출 제한 도달. {wait_time:.1f}초 대기 필요")
                return wait_time

        return 0

    async def call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        LLM API 호출 (지수 백오프 + 호출 제한 적용)

        Args:
            prompt (str): LLM 프롬프트

        Returns:
            Dict[str, Any]: LLM 응답 (파싱된 JSON 또는 오류 정보)
        """
        max_retries = 3  # 재시도 횟수
        timeout = 300  # 5분 타임아웃으로 증가
        base_delay = 2  # 기본 대기 시간 (초)

        for attempt in range(max_retries):
            try:
                import asyncio
                import time

                # API 호출 제한 확인
                wait_time = self._check_rate_limit()
                if wait_time > 0:
                    logger.info(f"API 호출 제한으로 인해 {wait_time:.1f}초 대기...")
                    await asyncio.sleep(wait_time)

                logger.info(
                    f"LLM API 호출 시도 {attempt + 1}/{max_retries} (타임아웃: {timeout}초)"
                )

                # 호출 카운터 증가
                self.call_count += 1

                # 프롬프트 길이 로깅
                logger.info(f"프롬프트 길이: {len(prompt)} 문자")

                # Gemini 1.5 Pro API 호출 방식
                response = await asyncio.wait_for(
                    self.model.generate_content_async(prompt), timeout=timeout
                )
                response_text = response.text

                # 응답 길이 및 내용 로깅
                logger.info(f"LLM 응답 수신: {len(response_text)} 문자")
                logger.info(f"응답 미리보기: {response_text[:200]}...")

                logger.info(f"LLM API 호출 성공 (응답 길이: {len(response_text)} 문자)")

                # JSON 응답 파싱 시도 (강화된 파싱 로직)
                try:
                    import re

                    # 마크다운 코드 블록 제거 (정규식 사용)
                    cleaned_response = response_text.strip()

                    # ```json ... ``` 패턴 제거
                    json_pattern = r"```json\s*(.*?)\s*```"
                    match = re.search(json_pattern, cleaned_response, re.DOTALL)

                    if match:
                        cleaned_response = match.group(1).strip()
                    else:
                        # 일반 ``` ... ``` 패턴 제거
                        code_pattern = r"```\s*(.*?)\s*```"
                        match = re.search(code_pattern, cleaned_response, re.DOTALL)
                        if match:
                            cleaned_response = match.group(1).strip()

                    # 추가 정리: 불필요한 공백과 줄바꿈 제거
                    cleaned_response = re.sub(r"\n\s*\n", "\n", cleaned_response)
                    cleaned_response = cleaned_response.strip()

                    # JSON 파싱 시도
                    llm_data = json.loads(cleaned_response)
                    logger.info("JSON 파싱 성공")
                    return {
                        "success": True,
                        "data": llm_data,
                        "raw_response": response_text,
                    }
                except json.JSONDecodeError as e:
                    # JSON 파싱 실패 시 강화된 대안 파싱 시도
                    logger.warning(f"JSON 파싱 실패: {e}")
                    logger.warning(f"파싱 시도한 텍스트: {cleaned_response[:200]}...")

                    # 강화된 JSON 추출 및 수정 시도
                    try:
                        # 1단계: 기본 JSON 추출
                        json_start = cleaned_response.find("{")
                        json_end = cleaned_response.rfind("}") + 1

                        if json_start != -1 and json_end > json_start:
                            json_part = cleaned_response[json_start:json_end]

                            # 2단계: 일반적인 JSON 오류 수정
                            # 불완전한 문자열 수정
                            json_part = json_part.replace("...", "")
                            json_part = json_part.replace('"상세해설": "', '"상세해설": "')

                            # 3단계: 중괄호 균형 확인 및 수정
                            open_braces = json_part.count("{")
                            close_braces = json_part.count("}")

                            if open_braces > close_braces:
                                # 부족한 닫는 중괄호 추가
                                json_part += "}" * (open_braces - close_braces)
                            elif close_braces > open_braces:
                                # 부족한 여는 중괄호 추가
                                json_part = (
                                    "{" * (close_braces - open_braces) + json_part
                                )

                            # 4단계: 불완전한 문자열 수정
                            lines = json_part.split("\n")
                            fixed_lines = []
                            for line in lines:
                                if '"상세해설":' in line and not line.strip().endswith('"'):
                                    # 불완전한 문자열 라인 수정
                                    line = line.strip()
                                    if not line.endswith('"'):
                                        line += '"'
                                    if not line.endswith(","):
                                        line += ","
                                fixed_lines.append(line)

                            json_part = "\n".join(fixed_lines)

                            # 5단계: 최종 JSON 파싱 시도
                            llm_data = json.loads(json_part)
                            logger.info("강화된 JSON 파싱 성공")
                            return {
                                "success": True,
                                "data": llm_data,
                                "raw_response": response_text,
                            }
                    except Exception as alt_e:
                        logger.warning(f"강화된 JSON 파싱도 실패: {alt_e}")

                        # 6단계: 최후의 수단 - 기본 구조 생성
                        try:
                            # 응답에서 상세해설 부분만 추출
                            detail_start = cleaned_response.find('"상세해설": "')
                            if detail_start != -1:
                                detail_start += len('"상세해설": "')
                                detail_end = cleaned_response.find('"', detail_start)
                                if detail_end == -1:
                                    detail_end = len(cleaned_response)

                                detail_text = cleaned_response[detail_start:detail_end]
                                if len(detail_text) > 50:  # 의미있는 텍스트가 있는 경우
                                    llm_data = {
                                        "상세해설": detail_text,
                                        "조치방법": ["LLM 응답에서 추출된 상세해설을 참고하세요."],
                                    }
                                    logger.info("기본 구조 생성 성공")
                                    return {
                                        "success": True,
                                        "data": llm_data,
                                        "raw_response": response_text,
                                    }
                        except Exception as final_e:
                            logger.warning(f"기본 구조 생성도 실패: {final_e}")

                    return {
                        "success": False,
                        "error": "JSON 파싱 실패",
                        "raw_response": response_text,
                    }

            except asyncio.TimeoutError:
                logger.warning(
                    f"LLM 호출 타임아웃 (시도 {attempt + 1}/{max_retries}, {timeout}초 초과)"
                )
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": f"타임아웃 ({timeout}초 초과)",
                        "raw_response": "",
                    }
                # 지수 백오프: 2초, 4초, 8초
                delay = base_delay * (2**attempt)
                logger.info(f"재시도 전 {delay}초 대기...")
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"LLM 호출 중 오류 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": str(e), "raw_response": ""}
                # 지수 백오프: 2초, 4초, 8초
                delay = base_delay * (2**attempt)
                logger.info(f"재시도 전 {delay}초 대기...")
                await asyncio.sleep(delay)

    async def process_prompts_batch(
        self, prompts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        프롬프트 배치를 순차적으로 처리 (API 호출 빈도 제한)
        전체 36개 항목 처리

        Args:
            prompts (List[Dict[str, Any]]): 처리할 프롬프트 리스트

        Returns:
            List[Dict[str, Any]]: 처리된 결과 리스트
        """
        # 전체 항목 처리 (36개)
        # prompts = prompts[:5]  # 제한 해제

        results = []
        total_prompts = len(prompts)
        batch_size = 5  # 배치 크기를 5개로 설정 (36개 처리 최적화)

        logger.info(f"배치 처리 시작: {total_prompts}개 프롬프트 (배치 크기: {batch_size}) - 전체 처리 모드")

        for i, prompt_data in enumerate(prompts, 1):
            cce_id = prompt_data.get("original_item", {}).get("CCE_ID", f"Unknown-{i}")
            prompt_text = prompt_data.get("prompt", "")

            # 진행률 계산
            progress = (i / total_prompts) * 100
            estimated_remaining = (total_prompts - i) * 15  # 예상 남은 시간 (초)

            logger.info(f"🔄 LLM 처리 중: {i}/{total_prompts} ({progress:.1f}%) - {cce_id}")
            logger.info(
                f"⏱️  예상 남은 시간: {estimated_remaining // 60}분 {estimated_remaining % 60}초"
            )

            # LLM 호출
            llm_response = await self.call_llm(prompt_text)

            # 결과 조합
            result = {
                "CCE_ID": cce_id,
                "original_data": prompt_data.get("original_item", {}),
                "llm_response": llm_response,
            }

            results.append(result)

            # 배치 단위로 대기 (5개마다 20초 대기)
            if i % batch_size == 0 and i < total_prompts:
                logger.info(f"배치 완료 ({i}/{total_prompts}). 20초 대기 후 다음 배치 시작...")
                await asyncio.sleep(20)
            else:
                # 개별 요청 간 8초 대기 (36개 처리 최적화)
                if i < total_prompts:
                    await asyncio.sleep(8)

        logger.info(f"배치 처리 완료: {len(results)}개 결과 (전체 처리 모드)")
        return results

    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """
        LLM 응답 결과를 파일로 저장

        Args:
            results (List[Dict[str, Any]]): LLM 응답 결과
            output_file (str): 출력 파일 경로
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"LLM 응답 결과 저장 완료: {output_file}")

        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")


async def main():
    """메인 실행 함수"""
    try:
        # LLM 호출기 초기화
        caller = LLMCaller()

        # 프롬프트 파일 로드
        prompts_file = "output/llm_prompts.json"

        if not Path(prompts_file).exists():
            logger.error(f"프롬프트 파일을 찾을 수 없습니다: {prompts_file}")
            return

        with open(prompts_file, "r", encoding="utf-8") as f:
            prompts = json.load(f)

        print(f"📋 {len(prompts)}개 프롬프트 로드 완료")

        # LLM 배치 처리
        results = await caller.process_prompts_batch(prompts)

        print(f"✅ {len(results)}개 LLM 응답 처리 완료")

        # 성공/실패 통계
        success_count = sum(1 for r in results if r["llm_response"]["success"])
        failure_count = len(results) - success_count

        print(f"📊 성공: {success_count}, 실패: {failure_count}")

        # 첫 번째 성공 응답 예시 출력
        for result in results:
            if result["llm_response"]["success"]:
                print("\n📝 첫 번째 성공 응답 예시:")
                print("=" * 50)
                print(
                    json.dumps(
                        result["llm_response"]["data"], ensure_ascii=False, indent=2
                    )
                )
                print("=" * 50)
                break

        # 결과 저장
        output_file = "output/llm_responses.json"
        caller.save_results(results, output_file)

        print(f"\n💾 LLM 응답 결과 저장 완료: {output_file}")

    except Exception as e:
        logger.error(f"LLM 처리 중 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
