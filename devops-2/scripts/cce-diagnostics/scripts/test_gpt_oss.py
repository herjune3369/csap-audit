#!/usr/bin/env python3
"""
GPT-OSS-20B 시스템 테스트
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_oss_caller import GPTOSSCaller

class TestGPTOSSCaller:
    """GPTOSSCaller 클래스 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        caller = GPTOSSCaller()
        assert caller.model_name == "llama2:7b"
        assert caller.base_url == "http://localhost:11434"
    
    def test_init_custom_model(self):
        """사용자 정의 모델명으로 초기화 테스트"""
        caller = GPTOSSCaller("custom-model")
        assert caller.model_name == "custom-model"
    
    @patch('subprocess.run')
    def test_check_ollama_service_success(self, mock_run):
        """Ollama 서비스 상태 확인 성공 테스트"""
        mock_run.return_value.returncode = 0
        caller = GPTOSSCaller()
        result = caller.check_ollama_service()
        assert result is True
    
    @patch('subprocess.run')
    def test_check_ollama_service_failure(self, mock_run):
        """Ollama 서비스 상태 확인 실패 테스트"""
        mock_run.return_value.returncode = 1
        caller = GPTOSSCaller()
        result = caller.check_ollama_service()
        assert result is False
    
    @patch('subprocess.run')
    def test_load_model_already_loaded(self, mock_run):
        """이미 로드된 모델 테스트"""
        mock_run.return_value.stdout = "llama2:7b    78e26419b446    3.8 GB"
        mock_run.return_value.returncode = 0
        
        caller = GPTOSSCaller()
        result = caller.load_model()
        assert result is True
    
    @patch('subprocess.run')
    def test_generate_response_success(self, mock_run):
        """응답 생성 성공 테스트"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Hello! This is a test response."
        
        caller = GPTOSSCaller()
        response = caller.generate_response("Hello, test")
        
        assert response == "Hello! This is a test response."
    
    @patch('subprocess.run')
    def test_generate_response_failure(self, mock_run):
        """응답 생성 실패 테스트"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Model not found"
        
        caller = GPTOSSCaller()
        response = caller.generate_response("Hello, test")
        
        assert response is None
    
    def test_create_security_analysis_prompt(self):
        """보안 분석 프롬프트 생성 테스트"""
        caller = GPTOSSCaller()
        test_data = {"test": "data", "security": "check"}
        
        prompt = caller._create_security_analysis_prompt(test_data)
        
        assert "Linux 시스템 보안 진단 결과" in prompt
        assert "보안 취약점과 개선 방안" in prompt
        assert "test" in prompt
        assert "data" in prompt
    
    @patch('subprocess.run')
    def test_health_check_healthy(self, mock_run):
        """시스템 상태 확인 - 정상 테스트"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "llama2:7b    78e26419b446    3.8 GB"
        
        caller = GPTOSSCaller()
        health = caller.health_check()
        
        assert health["status"] == "healthy"
        assert health["ollama_service"] is True
        assert health["model_loaded"] is True
        assert "timestamp" in health
    
    @patch('subprocess.run')
    def test_health_check_unhealthy(self, mock_run):
        """시스템 상태 확인 - 비정상 테스트"""
        mock_run.return_value.returncode = 1
        
        caller = GPTOSSCaller()
        health = caller.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["ollama_service"] is False
        assert health["model_loaded"] is False

class TestGPTOSSCallerIntegration:
    """GPT-OSS-20B 시스템 통합 테스트"""
    
    def test_security_analysis_integration(self):
        """보안 진단 분석 통합 테스트"""
        caller = GPTOSSCaller()
        
        # 테스트 데이터
        test_diagnostic_data = {
            "system_info": {
                "hostname": "test-server",
                "os": "Ubuntu 22.04"
            },
            "security_checks": [
                {
                    "check_id": "ACC-001",
                    "description": "Root 계정 원격 접속 제한",
                    "status": "FAIL",
                    "details": "SSH 설정에서 root 로그인 허용됨"
                },
                {
                    "check_id": "ACC-002", 
                    "description": "패스워드 복잡도 설정",
                    "status": "PASS",
                    "details": "패스워드 정책 적절히 설정됨"
                }
            ]
        }
        
        # 분석 실행 (실제 모델이 없을 수 있으므로 예외 처리)
        try:
            result = caller.analyze_security_diagnostic(test_diagnostic_data)
            assert "status" in result
            assert "model" in result
            assert "timestamp" in result
        except Exception as e:
            # 실제 모델이 없을 때는 에러 상태 확인
            assert "error" in str(e) or "failed" in str(e)

def test_gpt_oss_caller_import():
    """GPT-OSS-20B 호출기 모듈 임포트 테스트"""
    try:
        from gpt_oss_caller import GPTOSSCaller
        assert GPTOSSCaller is not None
    except ImportError as e:
        pytest.fail(f"GPT-OSS-20B 호출기 모듈 임포트 실패: {e}")

if __name__ == "__main__":
    # 기본 테스트 실행
    pytest.main([__file__, "-v"]) 