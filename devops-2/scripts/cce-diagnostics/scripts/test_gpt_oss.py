#!/usr/bin/env python3
"""
GPT-OSS-20B 시스템 테스트
"""
import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_oss_caller import GPTOSSCaller


class TestGPTOSSCaller:
    """GPT-OSS-20B 호출기 단위 테스트"""

    def test_init(self):
        """초기화 테스트"""
        caller = GPTOSSCaller()
        assert caller.model_name == "llama2:7b"
        assert caller.base_url == "http://localhost:11434"

    def test_init_custom_model(self):
        """사용자 정의 모델로 초기화 테스트"""
        caller = GPTOSSCaller("custom-model")
        assert caller.model_name == "custom-model"

    @patch("subprocess.run")
    def test_check_ollama_service_success(self, mock_run):
        """Ollama 서비스 확인 성공 테스트"""
        mock_run.return_value.returncode = 0
        caller = GPTOSSCaller()
        result = caller.check_ollama_service()
        assert result is True

    @patch("subprocess.run")
    def test_check_ollama_service_failure(self, mock_run):
        """Ollama 서비스 확인 실패 테스트"""
        mock_run.return_value.returncode = 1
        caller = GPTOSSCaller()
        result = caller.check_ollama_service()
        assert result is False

    @patch("subprocess.run")
    def test_load_model_success(self, mock_run):
        """모델 로드 성공 테스트"""
        mock_run.return_value.returncode = 0
        caller = GPTOSSCaller()
        result = caller.load_model()
        assert result is True

    @patch("subprocess.run")
    def test_load_model_failure(self, mock_run):
        """모델 로드 실패 테스트"""
        mock_run.return_value.returncode = 1
        caller = GPTOSSCaller()
        result = caller.load_model()
        assert result is False

    @patch("subprocess.run")
    def test_generate_response_success(self, mock_run):
        """응답 생성 성공 테스트"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Test response"
        caller = GPTOSSCaller()
        result = caller.generate_response("Test prompt")
        assert result == "Test response"

    @patch("subprocess.run")
    def test_generate_response_failure(self, mock_run):
        """응답 생성 실패 테스트"""
        mock_run.return_value.returncode = 1
        caller = GPTOSSCaller()
        result = caller.generate_response("Test prompt")
        assert result is None

    def test_create_security_analysis_prompt(self):
        """보안 분석 프롬프트 생성 테스트"""
        caller = GPTOSSCaller()
        test_data = {
            "system_info": {"hostname": "test-server", "os": "Ubuntu 22.04"},
            "security_checks": [
                {
                    "check_id": "ACC-001",
                    "description": "Root 계정 원격 접속 제한",
                    "status": "FAIL",
                    "details": "SSH 설정에서 root 로그인 허용됨",
                }
            ],
        }
        prompt = caller._create_security_analysis_prompt(test_data)
        assert "test-server" in prompt
        assert "ACC-001" in prompt
        assert "Root 계정 원격 접속 제한" in prompt

    @patch("subprocess.run")
    def test_health_check_success(self, mock_run):
        """헬스 체크 성공 테스트"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "llama2:7b"
        caller = GPTOSSCaller()
        result = caller.health_check()
        assert result["status"] == "healthy"
        assert result["ollama_service"] == "running"
        assert result["model_loaded"] is True


class TestGPTOSSCallerIntegration:
    """GPT-OSS-20B 시스템 통합 테스트"""

    def test_security_analysis_integration(self):
        """보안 진단 분석 통합 테스트"""
        caller = GPTOSSCaller()
        test_diagnostic_data = {
            "system_info": {
                "hostname": "test-server",
                "os": "Ubuntu 22.04",
            },
            "security_checks": [
                {
                    "check_id": "ACC-001",
                    "description": "Root 계정 원격 접속 제한",
                    "status": "FAIL",
                    "details": "SSH 설정에서 root 로그인 허용됨",
                },
                {
                    "check_id": "ACC-002",
                    "description": "패스워드 복잡도 설정",
                    "status": "PASS",
                    "details": "패스워드 정책 적절히 설정됨",
                },
            ],
        }
        try:
            result = caller.analyze_security_diagnostic(test_diagnostic_data)
            assert "status" in result
            assert "model" in result
            assert "timestamp" in result
        except Exception as e:
            assert "error" in str(e) or "failed" in str(e)


def test_gpt_oss_caller_import():
    """GPT-OSS-20B 호출기 모듈 임포트 테스트"""
    try:
        from gpt_oss_caller import GPTOSSCaller
        assert GPTOSSCaller is not None
    except ImportError as e:
        pytest.fail(f"GPT-OSS-20B 호출기 모듈 임포트 실패: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
