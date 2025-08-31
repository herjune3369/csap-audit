#!/usr/bin/env python3
"""
GPT-OSS-20B 기반 LLM 호출기
Ollama를 사용하여 로컬에서 GPT-OSS-20B 모델 실행
"""

import subprocess
import json
import time
import logging
from typing import Dict, Any, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTOSSCaller:
    """GPT-OSS-20B 모델을 사용한 LLM 호출기"""
    
    def __init__(self, model_name: str = "llama2:7b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"  # Ollama 기본 포트
        
    def check_ollama_service(self) -> bool:
        """Ollama 서비스 상태 확인"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Ollama 서비스 확인 실패: {e}")
            return False
    
    def load_model(self) -> bool:
        """모델 로드 확인 및 필요시 다운로드"""
        try:
            # 모델 목록 확인
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if self.model_name in result.stdout:
                logger.info(f"모델 {self.model_name} 이미 로드됨")
                return True
            
            # 모델 다운로드
            logger.info(f"모델 {self.model_name} 다운로드 시작...")
            download_result = subprocess.run(
                ["ollama", "pull", self.model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if download_result.returncode == 0:
                logger.info(f"모델 {self.model_name} 다운로드 완료")
                return True
            else:
                logger.error(f"모델 다운로드 실패: {download_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """프롬프트에 대한 응답 생성"""
        try:
            # Ollama API 호출
            cmd = [
                "ollama", "run", self.model_name,
                prompt
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1분 타임아웃
            )
            end_time = time.time()
            
            if result.returncode == 0:
                response_time = end_time - start_time
                logger.info(f"응답 생성 완료 (소요시간: {response_time:.2f}초)")
                return result.stdout.strip()
            else:
                logger.error(f"응답 생성 실패: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("응답 생성 타임아웃")
            return None
        except Exception as e:
            logger.error(f"응답 생성 중 오류: {e}")
            return None
    
    def analyze_security_diagnostic(self, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """보안 진단 결과 분석"""
        try:
            # 진단 데이터를 프롬프트로 변환
            prompt = self._create_security_analysis_prompt(diagnostic_data)
            
            # GPT-OSS-20B로 분석
            analysis = self.generate_response(prompt)
            
            if analysis:
                return {
                    "status": "success",
                    "analysis": analysis,
                    "model": self.model_name,
                    "timestamp": time.time()
                }
            else:
                return {
                    "status": "error",
                    "message": "GPT-OSS-20B 분석 실패",
                    "model": self.model_name,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.error(f"보안 진단 분석 실패: {e}")
            return {
                "status": "error",
                "message": str(e),
                "model": self.model_name,
                "timestamp": time.time()
            }
    
    def _create_security_analysis_prompt(self, diagnostic_data: Dict[str, Any]) -> str:
        """보안 진단 분석을 위한 프롬프트 생성"""
        prompt = f"""
다음은 Linux 시스템 보안 진단 결과입니다. 이 결과를 분석하여 보안 취약점과 개선 방안을 제시해주세요.

진단 결과:
{json.dumps(diagnostic_data, indent=2, ensure_ascii=False)}

다음 형식으로 분석 결과를 제공해주세요:

## 보안 분석 결과

### 1. 주요 취약점
- [발견된 취약점들을 나열]

### 2. 위험도 평가
- [높음/중간/낮음으로 분류]

### 3. 개선 방안
- [구체적인 개선 방법들]

### 4. 우선순위
- [즉시/단기/장기로 분류]

분석을 시작해주세요.
"""
        return prompt.strip()
    
    def health_check(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            ollama_status = self.check_ollama_service()
            model_loaded = self.load_model() if ollama_status else False
            
            return {
                "status": "healthy" if ollama_status and model_loaded else "unhealthy",
                "ollama_service": ollama_status,
                "model_loaded": model_loaded,
                "model_name": self.model_name,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }

# 사용 예시
if __name__ == "__main__":
    caller = GPTOSSCaller()
    
    # 시스템 상태 확인
    health = caller.health_check()
    print(f"시스템 상태: {health}")
    
    # 간단한 테스트
    if health["status"] == "healthy":
        response = caller.generate_response("Hello, how are you?")
        print(f"테스트 응답: {response}") 