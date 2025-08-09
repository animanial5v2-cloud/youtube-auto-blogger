from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, Response
import os
import json
import zipfile
import tempfile
from youtube_auto_blogger import YouTubeAutoBlogger
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import threading
import time
import queue
import subprocess
import shutil
import sys
import os as _os
import requests as _req
import subprocess
import shutil
import sys
import os as _os

app = Flask(__name__)
app.secret_key = 'premium_auto_blogger_secret_key_2024'

# Allow HTTP redirect URIs for local development (OAuthlib requires HTTPS by default)
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

# Pexels API 키 (기본값). 런타임에 /api/save-api-keys로 변경 가능
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', 'S7a7shjluIEyZweFJ3WHV7T2I2hrUv1lX4fwdtCZ4YhwsHqmZ0V9RghC')

# YouTubeAutoBlogger 인스턴스 생성
auto_blogger = YouTubeAutoBlogger(pexels_api_key=PEXELS_API_KEY)

# Ensure docs/screenshots exists for documentation uploads
try:
    os.makedirs(os.path.join('docs', 'screenshots'), exist_ok=True)
except Exception:
    pass

# --- Simple in-process log streaming (SSE) ---
_log_clients: list[queue.Queue] = []

def push_log(message: str) -> None:
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {message}"
    print(line)
    for q in list(_log_clients):
        try:
            q.put_nowait(line)
        except Exception:
            pass

@app.route('/api/log-stream')
def log_stream():
    def event_stream(q: queue.Queue):
        try:
            while True:
                msg = q.get()
                yield f"data: {msg}\n\n"
        except GeneratorExit:
            pass
    q: queue.Queue = queue.Queue()
    _log_clients.append(q)
    # detach on client close by returning generator; Flask will garbage collect
    return Response(event_stream(q), mimetype='text/event-stream')

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('premium_auto_blogger.html')

@app.route('/api/health')
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'healthy', 'message': 'Premium Auto Blogger is running'})

@app.route('/api/convert', methods=['POST'])
def convert_youtube_to_blog():
    """YouTube URL을 블로그 포스트로 변환"""
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url', '')
        target_audience = data.get('target_audience', '일반인')
        blog_id = data.get('blog_id', '')

        if not youtube_url:
            return jsonify({'success': False, 'error': 'YouTube URL이 필요합니다.'}), 400

        # Google 인증 확인 (token.pickle 또는 credentials.json)
        if not os.path.exists('token.pickle') and not os.path.exists('credentials.json'):
            print("⚠️ Google 인증 파일이 없습니다. 콘텐츠 생성만 진행합니다.")
            blog_id = None
        else:
            # 가능하면 기존 토큰으로 서비스 초기화
            try:
                auto_blogger.initialize_blogger_from_token()
            except Exception:
                pass

        # 전체 자동화 패키지 생성
        push_log('단일 변환 시작')
        auto_blogger.log_callback = push_log
        # 길이 범위는 기본 3000~4000자로 고정. 필요 시 프론트에서 옵션화 가능
        package = auto_blogger.generate_full_auto_package(
            youtube_url=youtube_url,
            target_audience=target_audience,
            blog_id=blog_id,
            min_len=int(os.environ.get('CONTENT_MIN_LEN', '3000')),
            max_len=int(os.environ.get('CONTENT_MAX_LEN', '4000')),
            publish_at_iso=(data.get('publish_at_iso') if data else None)
        )

        if package and package.get('success'):
            push_log('단일 변환 완료')
            # 포스팅 성공 시 크롬으로 새 창 열기
            try:
                post_url = package.get('post_url') if isinstance(package, dict) else None
                open_target = post_url or (f"https://www.blogger.com/blog/posts/{blog_id}" if blog_id else None)
                if open_target:
                    _open_in_chrome(open_target)
            except Exception:
                pass
            return jsonify({
                'success': True,
                'package': package
            })
        else:
            push_log('단일 변환 실패')
            return jsonify({
                'success': False,
                'error': package.get('error') if isinstance(package, dict) and package.get('error') else '콘텐츠 생성에 실패했습니다.'
            }), 500

    except Exception as e:
        push_log(f"❌ 변환 중 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/save-api-keys', methods=['POST'])
def save_api_keys():
    """OpenAI/PEXELS API 키 및 모델 저장(런타임 적용)."""
    try:
        data = request.get_json() or {}
        openai_key = data.get('openai_api_key', '').strip()
        openai_model = data.get('openai_model', '').strip()
        pexels_key = data.get('pexels_api_key', '').strip()

        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
            # 런타임 인스턴스에도 즉시 반영
            try:
                auto_blogger.openai_api_key = openai_key
            except Exception:
                pass
        if openai_model:
            os.environ['OPENAI_MODEL'] = openai_model
            try:
                auto_blogger.openai_model = openai_model
            except Exception:
                pass
        if pexels_key:
            os.environ['PEXELS_API_KEY'] = pexels_key
            auto_blogger.pexels_api_key = pexels_key

        return jsonify({'success': True, 'message': 'API 키가 저장되었고 즉시 적용되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'API 키 저장 중 오류: {str(e)}'}), 500

@app.route('/api/list-models', methods=['GET'])
def list_models():
    """저장된 OpenAI 키로 사용 가능한 모델 목록을 반환. 실패 시 권장 목록을 제공."""
    try:
        key = os.environ.get('OPENAI_API_KEY', '') or getattr(auto_blogger, 'openai_api_key', '')
        models: list[str] = []
        if key:
            try:
                headers = {"Authorization": f"Bearer {key}"}
                resp = _req.get('https://api.openai.com/v1/models', headers=headers, timeout=20)
                if resp.status_code == 200:
                    data = resp.json().get('data', [])
                    names = [m.get('id') for m in data if isinstance(m, dict)]
                    # 채팅/멀티모달 대표 모델 필터
                    for n in names:
                        if not isinstance(n, str):
                            continue
                        if any(t in n for t in ['gpt-4o', 'gpt-4.1', 'o4', 'gpt-3.5']):
                            models.append(n)
                    models = sorted(set(models))
            except Exception:
                pass
        # 권장 기본 목록 (키가 없거나 실패 시)
        if not models:
            models = [
                'gpt-4o-mini',
                'gpt-4o',
                'gpt-4.1-mini',
                'gpt-4.1'
            ]
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'error': f'모델 조회 오류: {str(e)}', 'models': []}), 500

@app.route('/api/test-openai-key', methods=['POST'])
def test_openai_key():
    """전달된 OpenAI 키의 유효성 및(옵션) 쿼터 확인. 키는 저장하지 않음.
    mode: 'quick' → 모델 목록만 확인(빠름), 'full' → + 소량 채팅 호출(쿼터 체크)
    """
    try:
        data = request.get_json() or {}
        key = (data.get('openai_api_key') or '').strip()
        model = (data.get('openai_model') or 'gpt-4o-mini').strip()
        mode = (data.get('mode') or 'quick').strip().lower()
        if not key:
            return jsonify({'success': False, 'error': 'API 키가 비어 있습니다.'}), 400

        session = _req.Session()
        session.trust_env = False
        headers = {"Authorization": f"Bearer {key}"}

        # 1) 모델 목록으로 키 유효성 확인
        try:
            r = session.get('https://api.openai.com/v1/models', headers=headers, timeout=5)
        except Exception as e:
            return jsonify({'success': False, 'error': f'네트워크 오류: {str(e)}'}), 502

        if r.status_code == 401:
            return jsonify({'success': True, 'valid': False, 'quota': 'unknown', 'status': 401, 'message': '키가 유효하지 않습니다.'})
        if r.status_code >= 400:
            return jsonify({'success': True, 'valid': None, 'quota': 'unknown', 'status': r.status_code, 'message': r.text[:400]})

        # quick 모드면 여기서 종료
        if mode == 'quick':
            return jsonify({'success': True, 'valid': True, 'quota': 'unknown', 'status': r.status_code})

        # 2) full 모드: 소량 Chat 호출로 쿼터 확인
        try:
            chat_headers = {**headers, 'Content-Type': 'application/json'}
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': 'ok'}],
                'max_tokens': 5,
                'temperature': 0
            }
            cr = session.post('https://api.openai.com/v1/chat/completions', headers=chat_headers, json=payload, timeout=8)
            if cr.status_code == 200:
                return jsonify({'success': True, 'valid': True, 'quota': 'ok', 'status': 200})
            if cr.status_code == 429:
                return jsonify({'success': True, 'valid': True, 'quota': 'insufficient', 'status': 429, 'message': cr.text[:400]})
            if cr.status_code == 401:
                return jsonify({'success': True, 'valid': False, 'quota': 'unknown', 'status': 401, 'message': '키가 유효하지 않습니다.'})
            return jsonify({'success': True, 'valid': True, 'quota': 'unknown', 'status': cr.status_code, 'message': cr.text[:400]})
        except Exception as e:
            return jsonify({'success': False, 'error': f'네트워크 오류: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'success': False, 'error': f'키 테스트 중 오류: {str(e)}'}), 500

@app.route('/api/preview', methods=['POST'])
def preview_content():
    """콘텐츠 미리보기"""
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url', '')
        target_audience = data.get('target_audience', '일반인')

        if not youtube_url:
            return jsonify({'success': False, 'error': 'YouTube URL이 필요합니다.'}), 400

        # 스크립트 추출
        push_log('미리보기: 스크립트 추출 시작')
        script = auto_blogger.extract_youtube_script(youtube_url)
        
        if script:
            push_log('미리보기 완료')
            return jsonify({
                'success': True,
                'preview': {
                    'script_length': len(script),
                    'script_preview': script[:200] + '...' if len(script) > 200 else script
                }
            })
        else:
            push_log('미리보기 스크립트 추출 실패')
            return jsonify({
                'success': False,
                'error': '스크립트 추출에 실패했습니다.'
            }), 500

    except Exception as e:
        push_log(f"❌ 미리보기 중 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'미리보기 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/download', methods=['POST'])
def download_package():
    """패키지 다운로드"""
    try:
        data = request.get_json()
        package = data.get('package', {})

        if not package:
            return jsonify({'success': False, 'error': '다운로드할 패키지가 없습니다.'}), 400

        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # HTML 파일 생성
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{package.get('analysis', {}).get('title', '블로그 포스트')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        h1 {{ color: #2d3748; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #4a5568; margin-top: 30px; }}
        h3 {{ color: #718096; }}
        p {{ color: #2d3748; }}
        .keywords {{ background: #f7fafc; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .keywords h4 {{ color: #667eea; margin-top: 0; }}
        .keywords ul {{ margin: 0; padding-left: 20px; }}
        .keywords li {{ color: #4a5568; margin: 5px 0; }}
        .meta {{ background: #e6fffa; padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #38b2ac; }}
        .meta h4 {{ color: #2c7a7b; margin-top: 0; }}
        .meta p {{ color: #2d3748; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{package.get('analysis', {}).get('title', '제목 없음')}</h1>
        
        <div class="meta">
            <h4>📊 메타 정보</h4>
            <p><strong>타겟:</strong> {package.get('target_audience', 'N/A')}</p>
            <p><strong>스크립트 길이:</strong> {len(package.get('script', ''))}자</p>
            <p><strong>키워드 수:</strong> {len(package.get('english_keywords', []))}개</p>
        </div>

        <div class="meta">
            <h4>🔍 메타 설명</h4>
            <p>{package.get('analysis', {}).get('meta_description', '메타 설명 없음')}</p>
        </div>

        <div class="keywords">
            <h4>🎯 키워드</h4>
            <ul>
                {''.join([f'<li>{keyword}</li>' for keyword in package.get('english_keywords', [])])}
            </ul>
        </div>

        <div>
            <h2>📝 블로그 콘텐츠</h2>
            {package.get('blog_content', '콘텐츠 없음')}
        </div>

        {f'<div class="meta"><h4>🖼️ 이미지</h4><p><strong>URL:</strong> {package.get("image_url", "N/A")}</p></div>' if package.get('image_url') else ''}
    </div>
</body>
</html>
            """

            # 파일들 생성
            files = {
                'blog_post.html': html_content,
                'analysis.json': json.dumps(package, ensure_ascii=False, indent=2),
                'script.txt': package.get('script', ''),
                'keywords.txt': '\n'.join(package.get('english_keywords', [])),
                'content.md': f"""# {package.get('analysis', {}).get('title', '제목 없음')}

## 메타 정보
- 타겟: {package.get('target_audience', 'N/A')}
- 스크립트 길이: {len(package.get('script', ''))}자
- 키워드 수: {len(package.get('english_keywords', []))}개

## 메타 설명
{package.get('analysis', {}).get('meta_description', '메타 설명 없음')}

## 키워드
{chr(10).join([f'- {keyword}' for keyword in package.get('english_keywords', [])])}

## 블로그 콘텐츠

{package.get('blog_content', '콘텐츠 없음')}

{f'## 이미지\n{package.get("image_url", "N/A")}' if package.get('image_url') else ''}
"""
            }

            # ZIP 파일 생성
            zip_path = os.path.join(temp_dir, 'auto_blogger_package.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, content in files.items():
                    zipf.writestr(filename, content)

            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f'auto_blogger_package_{package.get("analysis", {}).get("title", "unknown").replace(" ", "_")}.zip',
                mimetype='application/zip'
            )

    except Exception as e:
        print(f"❌ 다운로드 중 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'다운로드 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/api/upload-doc-screenshot', methods=['POST'])
def upload_doc_screenshot():
    """문서용 스크린샷 업로드: README_GOOGLE_BLOGGER.md에서 참조하는 이미지 파일 저장.

    form fields:
      - name: 저장 파일명 (예: 01-project-select.png)
      - file: 이미지 파일 (png/jpg)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400
        name = (request.form.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'error': '파일명을 지정해주세요.'}), 400
        # sanitize filename (영문/숫자/하이픈/언더스코어/점만 허용)
        import re as _re
        safe = ''.join(_re.findall(r"[A-Za-z0-9_.-]", name))
        if not safe:
            return jsonify({'success': False, 'error': '유효한 파일명이 아닙니다.'}), 400
        # enforce .png default if 확장자 없음
        if '.' not in safe:
            safe += '.png'
        f = request.files['file']
        base = os.path.join('docs', 'screenshots')
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, safe)
        f.save(path)
        return jsonify({'success': True, 'path': path.replace('\\', '/')})
    except Exception as e:
        return jsonify({'success': False, 'error': f'업로드 실패: {str(e)}'}), 500

def _run_batch(urls, interval_minutes, blog_id, target_audience, auto_shutdown, schedule_isos=None):
    try:
        total = len(urls)
        push_log(f"🚀 일괄 포스팅 시작: {total}건, 간격 {interval_minutes}분, 타겟 {target_audience}")
        for idx, url in enumerate(urls):
            push_log(f"[{idx+1}/{total}] 처리: {url}")
            try:
                auto_blogger.log_callback = push_log
                pkg = auto_blogger.generate_full_auto_package(
                    youtube_url=url,
                    target_audience=target_audience,
                    blog_id=blog_id or None,
                    publish_at_iso=(schedule_isos[idx] if schedule_isos and idx < len(schedule_isos) else None)
                )
                try:
                    if isinstance(pkg, dict):
                        purl = pkg.get('post_url')
                        target = purl or (f"https://www.blogger.com/blog/posts/{blog_id}" if blog_id else None)
                        if target:
                            _open_in_chrome(target)
                except Exception:
                    pass
            except Exception as e:
                push_log(f"❌ 항목 처리 실패: {e}")
            if idx < total - 1:
                time.sleep(max(1, int(interval_minutes)) * 60)
        push_log("✅ 모든 일괄 작업 완료")
    finally:
        if auto_shutdown:
            push_log("🛑 자동 종료 옵션이 활성화되어 프로그램을 종료합니다.")
            # dev 서버이므로 안전 종료 대신 즉시 종료 사용
            os._exit(0)

def _open_in_chrome(url: str) -> None:
    """크롬으로 URL 열기 (Windows 우선). 실패 시 기본 브라우저로 폴백.

    사용자 지정(환경변수):
      - CHROME_INCOGNITO=1           → 시크릿 모드
      - CHROME_NEW_WINDOW=0/1        → 새 창 (기본 1)
      - CHROME_PROFILE_DIR=Profile 2 → 특정 프로필 디렉터리 이름
      - CHROME_USER_DATA_DIR=C:\\...  → 사용자 데이터 디렉터리 전체 경로
      - CHROME_EXTRA_ARGS=--flag ...  → 임의의 추가 인자(공백 구분)
    """
    if not url:
        return
    try:
        chrome = shutil.which('chrome') or shutil.which('chrome.exe')
        if not chrome:
            # 일반적인 설치 경로
            candidates = [
                _os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                _os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                _os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
            for p in candidates:
                if _os.path.exists(p):
                    chrome = p
                    break
        args = []
        if _os.environ.get('CHROME_NEW_WINDOW', '1') != '0':
            args.append('--new-window')
        if _os.environ.get('CHROME_INCOGNITO') == '1':
            args.append('--incognito')
        if _os.environ.get('CHROME_USER_DATA_DIR'):
            args.append(f"--user-data-dir={_os.environ['CHROME_USER_DATA_DIR']}")
        if _os.environ.get('CHROME_PROFILE_DIR'):
            args.append(f"--profile-directory={_os.environ['CHROME_PROFILE_DIR']}")
        if _os.environ.get('CHROME_EXTRA_ARGS'):
            args.extend(_os.environ['CHROME_EXTRA_ARGS'].split())

        if chrome:
            subprocess.Popen([chrome, *args, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        # 기본 브라우저로 폴백
        if sys.platform.startswith('win'):
            subprocess.Popen(["cmd", "/c", "start", "", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    except Exception:
        pass

@app.route('/api/logout', methods=['POST'])
def logout_google():
    """Google 로그아웃: 토큰 제거 및 서비스 초기화"""
    try:
        # 토큰 파일 삭제 시도
        try:
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
        except Exception:
            pass
        # 세션/인스턴스 정리
        session.pop('oauth_state', None)
        try:
            auto_blogger.creds = None
            auto_blogger.blogger_service = None
        except Exception:
            pass
        try:
            push_log('🔒 Google 로그아웃 완료')
        except Exception:
            pass
        return jsonify({'success': True, 'message': '로그아웃되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'로그아웃 중 오류: {str(e)}'}), 500

@app.route('/api/batch-convert', methods=['POST'])
def batch_convert():
    try:
        data = request.get_json() or {}
        urls = data.get('urls', [])
        target_audience = data.get('target_audience', '일반인')
        blog_id = data.get('blog_id', '')
        interval_minutes = int(data.get('interval_minutes', 1))
        auto_shutdown = bool(data.get('auto_shutdown', False))
        schedule_base_iso = (data.get('schedule_base_iso') or '').strip()
        repeat_days = int(data.get('repeat_days', 1))
        time_of_day = (data.get('time_of_day') or '').strip()  # "HH:MM"
        interval_days = int(data.get('interval_days', 1))
        weekdays_only = bool(data.get('weekdays_only', False))
        weekends_only = bool(data.get('weekends_only', False))

        if not isinstance(urls, list) or not urls:
            return jsonify({'success': False, 'error': 'YouTube URL 목록이 비어 있습니다.'}), 400

        # 전처리: 공백 제거/중복 제거/최대 10개 제한
        cleaned = []
        seen = set()
        for u in urls:
            if not isinstance(u, str):
                continue
            s = u.strip()
            if not s or s in seen:
                continue
            if not (s.startswith('http://') or s.startswith('https://')):
                continue
            cleaned.append(s)
            seen.add(s)
            if len(cleaned) >= 10:
                break

        if not cleaned:
            return jsonify({'success': False, 'error': '유효한 YouTube URL이 없습니다.'}), 400

        interval_minutes = max(1, min(10, interval_minutes))

        # 예약 반복 스케줄 확장(간격/요일 필터/특정 시간 적용)
        schedule_isos = None
        expanded_urls = cleaned
        if schedule_base_iso:
            try:
                from datetime import datetime, timedelta
                # parse ISO (including Z)
                base = datetime.fromisoformat(schedule_base_iso.replace('Z', '+00:00'))
                repeat_days = max(1, min(30, repeat_days))
                interval_days = max(1, min(30, interval_days))
                # time_of_day 적용: HH:MM 형식이면 base의 시:분으로 치환
                if time_of_day and len(time_of_day.split(':')) == 2:
                    try:
                        hh, mm = [int(x) for x in time_of_day.split(':')]
                        base = base.replace(hour=hh, minute=mm, second=0, microsecond=0)
                    except Exception:
                        pass
                schedule_isos = []
                expanded = []
                day_count = 0
                cur = base
                while day_count < repeat_days:
                    # 요일 필터
                    if weekdays_only and cur.weekday() >= 5:  # 토(5), 일(6)
                        cur = cur + timedelta(days=1)
                        continue
                    if weekends_only and cur.weekday() < 5:
                        cur = cur + timedelta(days=1)
                        continue
                    for u in cleaned:
                        expanded.append(u)
                        schedule_isos.append(cur.isoformat())
                    day_count += 1
                    cur = cur + timedelta(days=interval_days)
                expanded_urls = expanded
            except Exception:
                schedule_isos = None
                expanded_urls = cleaned

        # 배치 작업은 백그라운드 스레드로 처리
        t = threading.Thread(target=_run_batch, args=(expanded_urls, interval_minutes, blog_id, target_audience, auto_shutdown, schedule_isos), daemon=True)
        t.start()

        return jsonify({'success': True, 'message': f'{len(expanded_urls)}건 일괄 포스팅을 시작했습니다.', 'queued': len(expanded_urls)})
    except Exception as e:
        print(f"❌ 배치 시작 오류: {e}")
        return jsonify({'success': False, 'error': f'배치 시작 중 오류: {str(e)}'}), 500

@app.route('/api/setup-google-auth', methods=['POST'])
def setup_google_auth():
    """Google 인증 시작: 인증 URL을 반환하여 프론트에서 새 창으로 열도록 함"""
    try:
        data = request.get_json()
        client_id = data.get('client_id', '')
        client_secret = data.get('client_secret', '')

        if not client_id or not client_secret:
            return jsonify({'error': '클라이언트 ID와 Secret을 모두 입력해주세요.'}), 400

        # credentials.json 생성 (이미 존재해도 갱신)
        try:
            auto_blogger._create_credentials_file(client_id, client_secret)
        except Exception:
            # private 메서드 호출이 실패하면 직접 생성
            credentials_data = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                }
            }
            with open('credentials.json', 'w', encoding='utf-8') as f:
                json.dump(credentials_data, f, indent=2)

        # OAuth Flow 생성 (웹 리다이렉션 방식)
        redirect_uri = url_for('oauth2callback', _external=True)
        flow = Flow.from_client_secrets_file(
            'credentials.json', scopes=auto_blogger.SCOPES, redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true', prompt='consent'
        )

        session['oauth_state'] = state

        return jsonify({'success': True, 'auth_url': authorization_url})

    except Exception as e:
        return jsonify({'error': f'Google 인증 설정 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/oauth2callback')
def oauth2callback():
    """Google OAuth 콜백: 토큰 저장 및 서비스 초기화"""
    try:
        state = session.get('oauth_state')
        redirect_uri = url_for('oauth2callback', _external=True)
        flow = Flow.from_client_secrets_file(
            'credentials.json', scopes=auto_blogger.SCOPES, state=state, redirect_uri=redirect_uri
        )
        flow.fetch_token(authorization_response=request.url)

        creds = flow.credentials
        # token.pickle 저장 및 서비스 초기화
        import pickle
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

        auto_blogger.creds = creds
        auto_blogger.blogger_service = build('blogger', 'v3', credentials=creds)

        # 작은 완료 페이지: opener에 postMessage 후 창 닫기
        success_html = """
        <html><body>
        <script>
            try {
                if (window.opener) {
                    window.opener.postMessage({ type: 'GOOGLE_AUTH_SUCCESS' }, '*');
                }
            } catch (e) {}
            window.close();
        </script>
        인증이 완료되었습니다. 이 창은 자동으로 닫힙니다.
        </body></html>
        """
        return success_html
    except Exception as e:
        return f"인증 처리 중 오류: {str(e)}", 500

# 자동 설정(개발용) 엔드포인트 제거되었습니다.

@app.route('/api/upload-credentials', methods=['POST'])
def upload_credentials():
    """credentials.json 파일 업로드"""
    try:
        if 'credentials' not in request.files:
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        file = request.files['credentials']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        if file and file.filename.endswith('.json'):
            file.save('credentials.json')
            return jsonify({
                'success': True,
                'message': 'credentials.json 파일이 업로드되었습니다.'
            })
        else:
            return jsonify({'error': 'JSON 파일만 업로드 가능합니다.'}), 400
        
    except Exception as e:
        return jsonify({'error': f'파일 업로드 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎥 Premium YouTube AI Auto Blogger Pro")
    print("=" * 50)
    print("✅ 모든 준비가 완료되었습니다!")
    print("🚀 웹 애플리케이션을 시작합니다...")
    print("📱 웹 브라우저에서 http://localhost:5000 접속하세요")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

