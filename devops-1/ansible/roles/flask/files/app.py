#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSAP 기술진단 SaaS 플랫폼
JSON 업로드 → LLM 분석 → Excel 리포트 자동 생성 → 다운로드 제공
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Flask 관련
from flask import Flask, request, render_template, flash, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# LLM 관련
import google.generativeai as genai
from dotenv import load_dotenv

# Excel 리포트 생성
import sys
sys.path.append('scripts')
from llm_report_generator import LLMReportGenerator
from load_diagnostic_items import load_diagnostic_items
from llm_prompt_generator import generate_batch_prompts
from llm_caller import LLMCaller

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# Flask 앱 설정
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# 업로드 및 출력 디렉토리 설정
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
OUTPUT_FOLDER = 'output'

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

def setup_gemini_api():
    """Gemini API 설정"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            logger.info("Gemini API 설정 완료")
            return True
        else:
            logger.warning("GEMINI_API_KEY를 찾을 수 없습니다.")
            return False
    except Exception as e:
        logger.error(f"Gemini API 설정 실패: {e}")
        return False

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'json'

def validate_json_file(file_path):
    """JSON 파일 유효성 검증"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'results' not in data:
            return False, "JSON 파일에 'results' 필드가 없습니다."
        
        if not isinstance(data['results'], list):
            return False, "JSON 파일의 'results' 필드가 배열이 아닙니다."
        
        if len(data['results']) == 0:
            return False, "JSON 파일에 진단 결과가 없습니다."
        
        return True, "JSON 파일이 유효합니다."
    
    except json.JSONDecodeError:
        return False, "JSON 파일 형식이 올바르지 않습니다."
    except Exception as e:
        return False, f"JSON 파일 검증 중 오류 발생: {str(e)}"

async def process_with_llm(file_path, system_type="Linux"):
    """LLM을 사용하여 진단 결과를 처리하고 상세 정보를 추가"""
    try:
        # Gemini API 설정
        if not setup_gemini_api():
            raise ValueError("Gemini API 설정 실패")
        
        # 1단계: JSON 진단 항목 로딩
        logger.info("🔄 1단계: JSON 진단 항목 로딩 시작...")
        items = load_diagnostic_items(file_path)
        
        if not items:
            raise ValueError("로드할 진단 항목이 없습니다.")
        
        logger.info(f"✅ {len(items)}개 항목 로드 완료")
        
        # 2단계: LLM 호출기 초기화
        logger.info("🔄 2단계: LLM 호출기 초기화...")
        llm_caller = LLMCaller()
        
        # 3단계: 프롬프트 생성
        logger.info("🔄 3단계: 프롬프트 생성 중...")
        prompts = generate_batch_prompts(items, system_type)
        logger.info(f"✅ {len(prompts)}개 프롬프트 생성 완료")
        
        # 4단계: LLM 배치 호출
        logger.info("🔄 4단계: LLM 배치 호출 중...")
        llm_responses = await llm_caller.process_prompts_batch(prompts)
        logger.info(f"✅ {len(llm_responses)}개 LLM 응답 수신 완료")
        
        # 5단계: 리포트 생성기 초기화 및 강화된 항목 생성
        logger.info("🔄 5단계: 리포트 생성 중...")
        report_generator = LLMReportGenerator()
        enhanced_items = report_generator.enhance_items_with_llm_responses(items, llm_responses, system_type)
        logger.info(f"✅ {len(enhanced_items)}개 항목 강화 완료")
        
        return enhanced_items
        
    except Exception as e:
        logger.error(f"LLM 처리 중 오류: {e}")
        raise e

@app.route('/')
def index():
    """메인 페이지 - 업로드 폼"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 및 LLM 기반 리포트 생성"""
    try:
        # 파일 업로드 확인
        if 'file' not in request.files:
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect('/')
        
        file = request.files['file']
        
        # 파일명 확인
        if file.filename == '':
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect('/')
        
        # 파일 확장자 확인
        if not allowed_file(file.filename):
            flash('JSON 파일만 업로드 가능합니다.', 'error')
            return redirect('/')
        
        # 안전한 파일명 생성
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 파일 저장
        file.save(file_path)
        logger.info(f"파일 업로드 완료: {file_path}")
        
        # JSON 파일 유효성 검증
        is_valid, message = validate_json_file(file_path)
        if not is_valid:
            os.remove(file_path)
            flash(f'파일 검증 실패: {message}', 'error')
            return redirect('/')
        
        flash('파일 업로드 성공! LLM 분석 및 리포트 생성 중...', 'success')
        
        # 시스템 타입 결정
        system_type = "Linux"
        if "windows" in filename.lower():
            system_type = "Windows"
        elif "mysql" in filename.lower() or "db" in filename.lower():
            system_type = "MySQL"
        elif "nginx" in filename.lower() or "web" in filename.lower():
            system_type = "Nginx"
        elif "docker" in filename.lower():
            system_type = "Docker"
        
        # LLM 처리 (비동기)
        logger.info(f"🤖 LLM 분석 시작 (시스템: {system_type})...")
        enhanced_items = asyncio.run(process_with_llm(file_path, system_type))
        
        # Excel 리포트 생성
        report_generator = LLMReportGenerator()
        report_generator.output_dir = app.config['REPORTS_FOLDER']
        report_filename = report_generator.generate_excel_report(enhanced_items, system_type)
        
        logger.info(f"✅ Excel 리포트 생성 완료: {report_filename}")
        flash('LLM 분석 및 Excel 리포트 생성 완료!', 'success')
        
        return render_template('upload.html', 
                             download_url=url_for('download_file', filename=os.path.basename(report_filename)),
                             report_filename=os.path.basename(report_filename))
        
    except Exception as e:
        logger.error(f"업로드 처리 중 오류: {e}")
        flash(f'오류가 발생했습니다: {str(e)}', 'error')
        return redirect('/')

@app.route('/download/<filename>')
def download_file(filename):
    """생성된 리포트 다운로드"""
    try:
        file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            flash('다운로드 파일을 찾을 수 없습니다.', 'error')
            return redirect('/')
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        logger.error(f"다운로드 실패: {e}")
        flash(f'다운로드 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect('/')

@app.errorhandler(413)
def too_large(e):
    """파일 크기 초과 처리"""
    flash('파일 크기가 너무 큽니다. (최대 16MB)', 'error')
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    """404 에러 처리"""
    return render_template('upload.html', error='페이지를 찾을 수 없습니다.'), 404

@app.errorhandler(500)
def internal_error(e):
    """500 에러 처리"""
    logger.error(f"내부 서버 오류: {e}")
    return render_template('upload.html', error='내부 서버 오류가 발생했습니다.'), 500

if __name__ == '__main__':
    logger.info("CSAP 기술진단 SaaS 플랫폼 시작...")
    app.run(debug=True, host='0.0.0.0', port=5000)
