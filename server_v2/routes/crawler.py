"""
Crawler Blueprint — Start, stop, status, SSE logs
"""
import os
import sys
import json
import time
import queue
import threading
import subprocess
import logging
from flask import Blueprint, jsonify, request, Response

from config import CRAWLER_SCRIPT, get_current_season
from common import get_crawler_status

logger = logging.getLogger('nbacore.routes.crawler')
crawler_bp = Blueprint('crawler', __name__)

# ── Global state ──
_log_queue: queue.Queue = queue.Queue(maxsize=1000)
_crawl_running = False
_crawl_thread = None
_crawl_process = None
_last_result = None


class QueueLogHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            _log_queue.put_nowait({'time': record.created, 'level': record.levelname, 'msg': msg})
        except queue.Full:
            pass


_qh = QueueLogHandler()
_qh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
logging.getLogger().addHandler(_qh)


@crawler_bp.route('/crawl', methods=['POST'])
def start_crawl():
    """Start a crawl job in background thread."""
    global _crawl_running, _crawl_thread, _last_result

    if _crawl_running:
        return jsonify({'error': 'A crawl is already running'}), 409

    req = request.json or {}
    mode = req.get('mode', 'check')
    params = req.get('params', {})

    _crawl_running = True
    _last_result = None
    _crawl_thread = threading.Thread(target=_run_crawl_task, args=(mode, params), daemon=True)
    _crawl_thread.start()
    return jsonify({'status': 'started', 'mode': mode})


@crawler_bp.route('/crawl/status')
def crawl_status():
    return jsonify({'running': _crawl_running, 'last_result': _last_result})


@crawler_bp.route('/crawl/stop', methods=['POST'])
def stop_crawl():
    """Stop the running crawl process."""
    global _crawl_running, _crawl_process, _last_result
    if not _crawl_running or _crawl_process is None:
        return jsonify({'error': 'No crawl is running'}), 400
    try:
        pid = _crawl_process.pid
        logger.info(f"Stopping crawl process (PID={pid})...")
        subprocess.run(['taskkill', '/pid', str(pid), '/f', '/t'], capture_output=True, timeout=10)
        _crawl_process = None
        _crawl_running = False
        _last_result = {'status': 'stopped', 'duration': 0}
        logger.info("Crawl stopped by user.")
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Failed to stop crawl: {e}")
        return jsonify({'error': str(e)}), 500


@crawler_bp.route('/logs/stream')
def logs_stream():
    """SSE stream for real-time logs."""
    def generate():
        while True:
            try:
                msg = _log_queue.get(timeout=1)
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                yield f": keepalive\n\n"
    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


def _run_crawl_task(mode: str, params: dict):
    global _crawl_running, _last_result, _crawl_process
    start_time = time.time()
    logger.info(f"=== Crawl started: mode={mode}, params={params} ===")

    timer = None
    try:
        python_exe = sys.executable
        if mode == 'check':
            cmd = [python_exe, CRAWLER_SCRIPT, '--check']
        elif mode == 'daily':
            cmd = [python_exe, CRAWLER_SCRIPT]
            if params.get('date'):
                cmd += ['--date', params['date']]
        elif mode == 'backfill':
            cmd = [python_exe, CRAWLER_SCRIPT, '--backfill', str(params.get('days', 7))]
        elif mode == 'single':
            table = params.get('table', 'team_game_splits')
            cmd = [python_exe, CRAWLER_SCRIPT, '--table', table]
            if params.get('season'):
                cmd += ['--season', str(params['season'])]
            if params.get('teams'):
                cmd += ['--teams', params['teams']]
        elif mode == 'full_season':
            cmd = [python_exe, CRAWLER_SCRIPT, '--full-season', str(params.get('season', get_current_season()))]
        elif mode == 'list_tables':
            cmd = [python_exe, CRAWLER_SCRIPT, '--list-tables']
        else:
            _last_result = {'status': 'error', 'error': f'Unknown mode: {mode}'}
            _crawl_running = False
            return

        logger.info(f"Command: {' '.join(cmd)}")

        crawl_env = {**os.environ, 'HTTP_PROXY': '', 'HTTPS_PROXY': ''}
        if params.get('interval'):
            crawl_env['CRAWL_INTERVAL'] = str(params['interval'])
        if params.get('duration'):
            crawl_env['CRAWL_DURATION'] = str(params['duration'])

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=crawl_env)
        _crawl_process = proc

        duration_limit = params.get('duration')
        if duration_limit:
            def _kill_after_duration():
                if _crawl_process is not None:
                    logger.info(f"Duration limit ({duration_limit}s) reached, stopping...")
                    try:
                        subprocess.run(['taskkill', '/pid', str(_crawl_process.pid), '/f', '/t'],
                                       capture_output=True, timeout=10)
                    except Exception:
                        pass
            timer = threading.Timer(float(duration_limit), _kill_after_duration)
            timer.start()

        for line in proc.stdout:
            line = line.rstrip()
            if line:
                level = 'INFO'
                if '[ERROR]' in line or 'Error' in line:
                    level = 'ERROR'
                elif '[WARNING]' in line or 'Warning' in line:
                    level = 'WARNING'
                logger.info(line)
                try:
                    _log_queue.put_nowait({'time': time.time(), 'level': level, 'msg': line})
                except queue.Full:
                    pass

        proc.wait()
        rc = proc.returncode
        duration = time.time() - start_time

        if rc == 0:
            _last_result = {'status': 'success', 'duration': round(duration, 1)}
            logger.info(f"=== Crawl completed in {duration:.1f}s ===")
        else:
            _last_result = {'status': 'error', 'error': f'Exit code {rc}', 'duration': round(duration, 1)}
            logger.error(f"=== Crawl failed (exit {rc}) in {duration:.1f}s ===")
    except Exception as e:
        duration = time.time() - start_time
        _last_result = {'status': 'error', 'error': str(e)[:200], 'duration': round(duration, 1)}
        logger.error(f"=== Crawl failed: {e} ===")
    finally:
        if timer:
            timer.cancel()
        _crawl_process = None
        _crawl_running = False
