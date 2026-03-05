import os
import json
import base64
import time
from datetime import datetime, timezone

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), 'dist')

# ─── API 路由 ────────────────────────────────────────────────────────────────

@app.get('/api/health')
def health():
    return jsonify(status='ok', timestamp=int(time.time()))


@app.post('/api/json/format')
def json_format():
    body = request.get_json(silent=True) or {}
    raw = body.get('text', '')
    indent = body.get('indent', 2)
    try:
        obj = json.loads(raw)
        formatted = json.dumps(obj, indent=indent, ensure_ascii=False)
        return jsonify(success=True, result=formatted)
    except json.JSONDecodeError as e:
        return jsonify(success=False, error=str(e)), 400


@app.post('/api/json/minify')
def json_minify():
    body = request.get_json(silent=True) or {}
    raw = body.get('text', '')
    try:
        obj = json.loads(raw)
        minified = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
        return jsonify(success=True, result=minified)
    except json.JSONDecodeError as e:
        return jsonify(success=False, error=str(e)), 400


@app.post('/api/base64/encode')
def base64_encode():
    body = request.get_json(silent=True) or {}
    text = body.get('text', '')
    try:
        encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
        return jsonify(success=True, result=encoded)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400


@app.post('/api/base64/decode')
def base64_decode():
    body = request.get_json(silent=True) or {}
    text = body.get('text', '')
    try:
        decoded = base64.b64decode(text).decode('utf-8')
        return jsonify(success=True, result=decoded)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400


@app.post('/api/timestamp/convert')
def timestamp_convert():
    """双向转换：传 timestamp 返回日期字符串，传 datetime 返回时间戳"""
    body = request.get_json(silent=True) or {}

    if 'timestamp' in body:
        try:
            ts = float(body['timestamp'])
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return jsonify(
                success=True,
                utc=dt.strftime('%Y-%m-%d %H:%M:%S'),
                iso=dt.isoformat(),
            )
        except (ValueError, OSError) as e:
            return jsonify(success=False, error=str(e)), 400

    if 'datetime' in body:
        try:
            dt = datetime.fromisoformat(body['datetime'])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return jsonify(success=True, timestamp=int(dt.timestamp()))
        except ValueError as e:
            return jsonify(success=False, error=str(e)), 400

    return jsonify(success=False, error='请提供 timestamp 或 datetime 参数'), 400


@app.get('/api/timestamp/now')
def timestamp_now():
    now = datetime.now(tz=timezone.utc)
    return jsonify(
        timestamp=int(now.timestamp()),
        utc=now.strftime('%Y-%m-%d %H:%M:%S'),
        iso=now.isoformat(),
    )


# ─── 生产环境：提供前端静态文件 ──────────────────────────────────────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if not os.path.isdir(FRONTEND_DIST):
        return jsonify(error='前端未构建，请先执行 npm run build'), 404

    file_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')


# ─── 启动 ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
