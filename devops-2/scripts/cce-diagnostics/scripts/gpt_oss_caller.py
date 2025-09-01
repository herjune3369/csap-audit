#!/usr/bin/env python3
"""
GPT-OSS-20B 기반 LLM 호출기
Ollama를 사용하여 로컬에서 GPT-OSS-20B 모델 실행
"""
import subprocess
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPTOSSCaller:
    """GPT-OSS-20B 모델을 사용한 LLM 호출기"""

    def __init__(self, model_name: str = "llama2:7b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"

    def check_ollama_service(self) -> bool:
        """Ollama 서비스 상태 확인"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("Ollama 서비스를 찾을 수 없습니다.")
            return False

    def load_model(self) -> bool:
        """모델 로드/다운로드"""
        try:
            logger.info(f"모델 {self.model_name} 로드 중...")
            result = subprocess.run(
                ["ollama", "pull", self.model_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
            )
            if result.returncode == 0:
                logger.info(f"모델 {self.model_name} 로드 완료")
                return True
            else:
                logger.error(f"모델 로드 실패: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("모델 로드 시간 초과")
            return False

    def generate_response(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """프롬프트에 대한 응답 생성"""
        try:
            logger.info(f"프롬프트 처리 중: {prompt[:50]}...")
            result = subprocess.run(
                [
                    "ollama",
                    "run",
                    self.model_name,
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"응답 생성 완료: {len(response)} 문자")
                return response
            else:
                logger.error(f"응답 생성 실패: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            logger.error("응답 생성 시간 초과")
            return None

    def analyze_security_diagnostic(self, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """보안 진단 결과 분석"""
        try:
            prompt = self._create_security_analysis_prompt(diagnostic_data)
            response = self.generate_response(prompt)
            
            if response:
                return {
                    "status": "success",
                    "model": self.model_name,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "analysis": response,
                    "recommendations": self._extract_recommendations(response),
                }
            else:
                return {
                    "status": "error",
                    "model": self.model_name,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "error": "응답 생성 실패",
                }
        except Exception as e:
            logger.error(f"보안 진단 분석 실패: {e}")
            return {
                "status": "error",
                "model": self.model_name,
                "timestamp": "2024-01-01T00:00:00Z",
                "error": str(e),
            }

    def _create_security_analysis_prompt(self, diagnostic_data: Dict[str, Any]) -> str:
        """보안 분석 프롬프트 생성"""
        prompt = f"""
다음 Linux 시스템 보안 진단 결과를 분석하고 개선 권장사항을 제시해주세요:

시스템 정보:
- 호스트명: {diagnostic_data.get('system_info', {}).get('hostname', 'Unknown')}
- OS: {diagnostic_data.get('system_info', {}).get('os', 'Unknown')}

진단 결과:
"""
        
        for check in diagnostic_data.get("security_checks", []):
            prompt += f"""
- {check.get('check_id', 'Unknown')}: {check.get('description', 'No description')}
  상태: {check.get('status', 'Unknown')}
  상세: {check.get('details', 'No details')}
"""
        
        prompt += """

분석 요청사항:
1. 전체 보안 상태 평가
2. 주요 취약점 식별
3. 우선순위별 개선 권장사항
4. 즉시 조치가 필요한 항목
5. 장기적 보안 강화 방안

JSON 형식으로 응답해주세요:
{
  "security_score": "점수/100",
  "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
  "critical_issues": ["즉시 조치 필요 항목들"],
  "recommendations": ["개선 권장사항들"],
  "next_steps": ["다음 단계 액션들"]
}
"""
        return prompt

    def _extract_recommendations(self, response: str) -> list:
        """응답에서 권장사항 추출"""
        try:
            # JSON 응답 파싱 시도
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get("recommendations", [])
        except (json.JSONDecodeError, KeyError):
            pass
        
        # JSON 파싱 실패 시 텍스트에서 추출
        recommendations = []
        lines = response.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["권장", "개선", "조치", "설정"]):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # 최대 5개 반환

    def health_check(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            ollama_ok = self.check_ollama_service()
            model_ok = False
            
            if ollama_ok:
                # 모델 존재 여부 확인
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and self.model_name in result.stdout:
                    model_ok = True
            
            return {
                "status": "healthy" if ollama_ok and model_ok else "unhealthy",
                "ollama_service": "running" if ollama_ok else "stopped",
                "model_loaded": model_ok,
                "model_name": self.model_name,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "ollama_service": "unknown",
                "model_loaded": False,
                "model_name": self.model_name,
            }


if __name__ == "__main__":
    caller = GPTOSSCaller()
    health = caller.health_check()
    print(f"시스템 상태: {health}")
    if health["status"] == "healthy":
        response = caller.generate_response("Hello, how are you?")
        print(f"테스트 응답: {response}")
