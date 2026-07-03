import time
from flask import Flask, request, g
from routes.common import common_bp
import logging

logger = logging.getLogger('nbacore.request')

app = Flask(__name__)

# 🟢 低：全自动化请求监控日志
@app.before_request
def start_timer():
    g.start_time = time.time()
    # 记录基础请求元数据
    logger.info(f"==> [{request.method}] {request.path} | Args: {dict(request.args)} | JSON: {request.get_json(silent=True)}")

@app.after_request
def log_request(response):
    if hasattr(g, 'start_time'):
        elapsed_time = (time.time() - g.start_time) * 1000  # 毫秒单位
        logger.info(f"<== [{request.method}] {request.path} | Status: {response.status_code} | Cost: {elapsed_time:.2f}ms")
    return response

app.register_blueprint(common_bp, url_prefix='/api/v1')

if __name__ == '__main__':
    app.run(port=5577)