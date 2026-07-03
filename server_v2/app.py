"""
NBACore Desktop — Application Entry Point v2
=============================================
Modular architecture: config / db / common / routes

Usage:
  python app.py              # default port 5577
  python app.py --port 8080
"""
from __future__ import annotations

import os
import sys
import logging
import argparse

# Clear proxy before any imports
for _key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
    os.environ.pop(_key, None)

# Ensure server_v2 is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from config import SERVER_HOST, SERVER_PORT
from db import ensure_db, init_pool, close_all
from routes.system import system_bp
from routes.teams import teams_bp
from routes.players import players_bp
from routes.stats import stats_bp
from routes.crawler import crawler_bp

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('nbacore')


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    CORS(app)

    # Register all blueprints under /api/v1 (versioned)
    api_prefix = '/api/v1'
    app.register_blueprint(system_bp, url_prefix=api_prefix)
    app.register_blueprint(teams_bp, url_prefix=api_prefix)
    app.register_blueprint(players_bp, url_prefix=api_prefix)
    app.register_blueprint(stats_bp, url_prefix=api_prefix)
    app.register_blueprint(crawler_bp, url_prefix=api_prefix)

    # Legacy compatibility: mount under /api with unique names
    app.register_blueprint(system_bp, name='system_legacy', url_prefix='/api')
    app.register_blueprint(teams_bp, name='teams_legacy', url_prefix='/api')
    app.register_blueprint(players_bp, name='players_legacy', url_prefix='/api')
    app.register_blueprint(stats_bp, name='stats_legacy', url_prefix='/api')
    app.register_blueprint(crawler_bp, name='crawler_legacy', url_prefix='/api')

    logger.info(f"Registered 5 blueprints: system, teams, players, stats, crawler")
    return app


def main():
    parser = argparse.ArgumentParser(description='NBACore Desktop API Server v2')
    parser.add_argument('--port', type=int, default=SERVER_PORT, help=f'Port (default: {SERVER_PORT})')
    parser.add_argument('--host', type=str, default=SERVER_HOST, help=f'Host (default: {SERVER_HOST})')
    args = parser.parse_args()

    # Ensure DB is running
    if not ensure_db():
        logger.warning("Cannot start PostgreSQL! API will start but DB features won't work.")

    # Initialize connection pool
    try:
        init_pool()
    except Exception as e:
        logger.error(f"DB pool init failed: {e}")

    app = create_app()

    print(f"\n{'='*55}")
    print(f"  NBACore Desktop API v2 — http://{args.host}:{args.port}")
    print(f"  Endpoints: /api/v1/* and /api/* (legacy)")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*55}\n")

    # Use waitress (production WSGI) if available
    try:
        from waitress import serve
        logger.info("Using waitress production WSGI server")
        serve(app, host=args.host, port=args.port, threads=8)
    except ImportError:
        logger.warning("waitress not installed, falling back to Flask dev server")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == '__main__':
    try:
        main()
    finally:
        close_all()
