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
sys.path.append('../scripts')
from llm_report_generator import LLMReportGenerator
from load_diagnostic_items import load_diagnostic_items
from llm_prompt_generator import generate_batch_prompts
from llm_caller import LLMCaller

# GitHub Secrets 관련
import requests
from base64 import b64decode

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# Flask 앱 설정
app = Flask(__name__)
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

def get_github_secret(secret_name: str) -> str:
    """GitHub Secrets에서 시크릿 값을 가져옴"""
    try:
        # GitHub Actions 환경에서 실행 중인지 확인
        if os.getenv('GITHUB_TOKEN'):
            # GitHub API를 통해 시크릿 가져오기
            headers = {
                'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # GitHub API 엔드포인트 (예시)
            # 실제 구현에서는 GitHub API를 통해 시크릿을 가져와야 함
            # https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}
            
            # 임시로 환경변수에서 가져오기
            return os.getenv(secret_name)
        else:
            # 로컬 환경에서는 환경변수에서 가져오기
            return os.getenv(secret_name)
    except Exception as e:
        logger.error(f"GitHub Secret 가져오기 실패: {e}")
        return None

def setup_gemini_api():
    """Gemini API 설정 (GitHub Secrets에서 키 가져오기)"""
    try:
        # GitHub Secrets에서 API 키 가져오기
        api_key = get_github_secret('GEMINI_API_KEY')
        
        if not api_key:
            # 환경변수에서 직접 가져오기 시도
            api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            genai.configure(api_key=api_key)
            logger.info("Gemini API 설정 완료 (GitHub Secrets에서 가져옴)")
            return True
        else:
            logger.warning("GEMINI_API_KEY를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        logger.error(f"Gemini API 설정 실패: {e}")
        return False

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'json'}

def ensure_directories():
    """필요한 디렉토리 생성"""
    for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, OUTPUT_FOLDER]:
        os.makedirs(folder, exist_ok=True)

def validate_json_file(file_path):
    """JSON 파일 유효성 검증"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 필수 필드 확인
        if 'results' not in data:
            return False, "JSON 파일에 'results' 필드가 없습니다."
        
        if not isinstance(data['results'], list):
            return False, "JSON 파일의 'results' 필드가 배열이 아닙니다."
        
        # 최소 1개 이상의 결과가 있는지 확인
        if len(data['results']) == 0:
            return False, "JSON 파일에 진단 결과가 없습니다."
        
        return True, "JSON 파일이 유효합니다."
    
    except json.JSONDecodeError:
        return False, "JSON 파일 형식이 올바르지 않습니다."
    except Exception as e:
        return False, f"JSON 파일 검증 중 오류 발생: {str(e)}"

def generate_report_filename(original_filename):
    """리포트 파일명 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(original_filename)[0]
    return f"{base_name}_llm_report_{timestamp}.xlsx"

async def process_with_llm(file_path, system_type="Linux"):
    """LLM을 사용하여 진단 결과를 처리하고 상세 정보를 추가"""
    try:
        # Gemini API 설정 (GitHub Secrets에서 키 가져오기)
        if not setup_gemini_api():
            raise ValueError("GEMINI_API_KEY가 필요합니다.")
        
        # 1단계: JSON 진단 항목 로딩
        logger.info("🔄 1단계: JSON 진단 항목 로딩 시작...")
        items = load_diagnostic_items(file_path)
        if not items:
            raise ValueError("로드할 진단 항목이 없습니다.")
        
        # 전체 항목 처리 (36개)
        # items = items[:3]  # 제한 해제
        logger.info(f"✅ 1단계 완료: {len(items)}개 항목 로드 (전체 처리)")
        
        # 2단계: LLM 프롬프트 생성
        logger.info("🔄 2단계: LLM 프롬프트 생성 시작...")
        prompts = generate_batch_prompts(items, system_type)
        logger.info(f"✅ 2단계 완료: {len(prompts)}개 프롬프트 생성")
        
        # 3단계: LLM API 호출 (실제 Gemini API 사용)
        logger.info("🔄 3단계: Gemini API 호출 시작...")
        logger.info(f"📊 총 {len(prompts)}개 항목 처리 예정 (예상 시간: 약 {len(prompts) * 15 // 60}분)")
        caller = LLMCaller()
        results = await caller.process_prompts_batch(prompts)
        success_count = sum(1 for r in results if r['llm_response']['success'])
        failure_count = len(results) - success_count
        logger.info(f"✅ 3단계 완료: 성공 {success_count}, 실패 {failure_count}")
        
        # 4단계: LLM 결과를 원본 데이터와 결합
        enhanced_items = []
        for result in results:
            original_item = result['original_data']
            llm_response = result['llm_response']
            
            if llm_response['success']:
                enhanced_item = {
                    **original_item,
                    '시스템': system_type,
                    '상세해설': llm_response['data'].get('상세해설', ''),
                    '조치방법': llm_response['data'].get('조치방법', [])
                }
            else:
                enhanced_item = {
                    **original_item,
                    '시스템': system_type,
                    '상세해설': 'LLM 처리 실패',
                    '조치방법': ['LLM 처리 실패']
                }
            enhanced_items.append(enhanced_item)
        
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
            return redirect(request.url)
        
        file = request.files['file']
        
        # 파일명 확인
        if file.filename == '':
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(request.url)
        
        # 파일 확장자 확인
        if not allowed_file(file.filename):
            flash('JSON 파일만 업로드 가능합니다.', 'error')
            return redirect(request.url)
        
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
            os.remove(file_path)  # 잘못된 파일 삭제
            flash(f'파일 검증 실패: {message}', 'error')
            return redirect(request.url)
        
        flash('파일 업로드 성공! LLM 분석 및 리포트 생성 중...', 'success')
        
        # LLM 처리 및 리포트 생성
        try:
            # 시스템 타입 추정 (파일명에서)
            system_type = "Linux"  # 기본값
            if "windows" in filename.lower():
                system_type = "Windows"
            elif "mysql" in filename.lower() or "db" in filename.lower():
                system_type = "MySQL"
            elif "nginx" in filename.lower() or "web" in filename.lower():
                system_type = "Nginx"
            elif "docker" in filename.lower():
                system_type = "Docker"
            
            # LLM 처리 (비동기)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            enhanced_items = loop.run_until_complete(process_with_llm(file_path, system_type))
            loop.close()
            
            # LLM이 추가한 상세 정보를 포함한 Excel 리포트 생성
            generator = LLMReportGenerator()
            
            # Excel 리포트 생성
            output_file = generator.generate_excel_report(enhanced_items, system_type)
            
            # 생성된 파일의 실제 파일명 추출
            report_filename = os.path.basename(output_file)
            
            logger.info(f"LLM 기반 Excel 리포트 생성 완료: {output_file}")
            flash('LLM 기반 Excel 리포트 생성 완료!', 'success')
            
            # 다운로드 링크 제공
            download_url = url_for('download_file', filename=report_filename)
            return render_template('upload.html', 
                                download_url=download_url, 
                                report_filename=report_filename,
                                success=True)
        
        except Exception as e:
            logger.error(f"LLM 리포트 생성 실패: {e}")
            flash(f'LLM 리포트 생성 실패: {str(e)}', 'error')
            return redirect(request.url)
    
    except Exception as e:
        logger.error(f"업로드 처리 중 오류: {e}")
        flash(f'업로드 처리 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    """생성된 리포트 다운로드"""
    try:
        # output 폴더에서 파일 찾기
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            # reports 폴더에서도 찾기 시도
            file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
            
        if not os.path.exists(file_path):
            flash('다운로드 파일을 찾을 수 없습니다.', 'error')
            return redirect(url_for('index'))
        
        return send_file(file_path, 
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        logger.error(f"다운로드 실패: {e}")
        flash(f'다운로드 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/upload-stats')
def api_upload_stats():
    """업로드 통계"""
    try:
        upload_count = len([f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.json')])
        report_count = len([f for f in os.listdir(REPORTS_FOLDER) if f.endswith('.xlsx')])
        
        return jsonify({
            'uploaded_files': upload_count,
            'generated_reports': report_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """파일 크기 초과 처리"""
    flash('파일 크기가 너무 큽니다. (최대 16MB)', 'error')
    return redirect(url_for('index'))

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
    # 디렉토리 생성
    ensure_directories()
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5001) 