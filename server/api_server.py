#!/usr/bin/env python3
"""
NBACore Desktop — Backend API Server
=====================================
为 Electron 桌面应用提供全面的 REST API

用法:
  python api_server.py              # 默认端口 5577
  python api_server.py --port 8080
"""
from __future__ import annotations

import os
import sys
import json
import time
import queue
import threading
import subprocess
import logging
from datetime import date, datetime
from pathlib import Path
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS

# Clear proxy
for _key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
             'http_proxy', 'https_proxy', 'all_proxy']:
    os.environ.pop(_key, None)

# ── Config ──
BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent.parent  # nba_data/
CRAWLER_SCRIPT = str(PARENT_DIR / 'nba_daily_crawler.py')
STATUS_FILE = str(PARENT_DIR / 'crawl_status.json')

DB_CONFIG = {
    'host': 'localhost', 'port': 5433,
    'database': 'nba', 'user': 'postgres', 'password': 'postgres'
}

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary', '-q'])
    import psycopg2
    from psycopg2.extras import RealDictCursor

try:
    from flask_cors import CORS
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-cors', '-q'])
    from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('nbacore.api')

app = Flask(__name__)
CORS(app)

# ── Global state ──
_log_queue: queue.Queue = queue.Queue(maxsize=1000)
_crawl_running = False
_crawl_thread = None
_last_result = None
_crawl_process = None  # subprocess.Popen handle for stop


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


# ════════════════════════════════════════
# DB helpers
# ════════════════════════════════════════

def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def is_port_open(host='localhost', port=5433):
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        r = s.connect_ex((host, port))
        s.close()
        return r == 0
    except:
        return False


def ensure_db():
    if is_port_open():
        return True
    logger.info('PostgreSQL not running, starting...')
    for svc in ['postgresql-x64-17', 'postgresql-x64-16', 'postgresql-x64-15',
                'postgresql-17', 'postgresql-16', 'postgresql-15']:
        try:
            r = subprocess.run(['net', 'start', svc], capture_output=True, text=True, timeout=30)
            if r.returncode == 0 or '已经启动' in r.stdout or 'already started' in r.stdout.lower():
                logger.info(f'Started: {svc}')
                for _ in range(10):
                    time.sleep(1)
                    if is_port_open():
                        return True
        except:
            continue
    return False


def _get_current_season() -> int:
    d = date.today()
    return d.year + 1 if d.month >= 10 else d.year


def _serialize(row):
    """Convert a RealDictRow to a JSON-safe dict."""
    if row is None:
        return None
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, (datetime, date)):
            d[k] = v.isoformat()
    return d


# ════════════════════════════════════════
# Health & Status
# ════════════════════════════════════════

@app.route('/api/health')
def api_health():
    return jsonify({'status': 'ok', 'db': is_port_open(), 'timestamp': time.time()})


@app.route('/api/status')
def api_status():
    try:
        if not ensure_db():
            return jsonify({'error': 'Cannot connect to database'}), 500

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [r['table_name'] for r in cur.fetchall()]

        table_info = []
        total_records = 0
        for t in tables:
            try:
                cur.execute(f"SELECT count(*) AS cnt FROM {t}")
                cnt = cur.fetchone()['cnt']
                total_records += cnt
                table_info.append({'name': t, 'rows': cnt})
            except:
                table_info.append({'name': t, 'rows': 0})

        try:
            cur.execute("SELECT count(*) AS cnt FROM team_mapping WHERE is_active = true")
            active_teams = cur.fetchone()['cnt']
        except:
            active_teams = 0

        try:
            cur.execute("SELECT max(game_date) AS d FROM games")
            last_game = cur.fetchone()['d']
            last_game = str(last_game) if last_game else None
        except:
            last_game = None

        try:
            cur.execute("SELECT count(distinct team_abbr) AS t, count(distinct season) AS s, count(*) AS c FROM team_game_splits")
            ts = cur.fetchone()
            splits_teams, splits_seasons, splits_total = ts['t'], ts['s'], ts['c']
        except:
            splits_teams, splits_seasons, splits_total = 0, 0, 0

        top_scorers = []
        try:
            cur.execute("""
                SELECT team_abbr, pts, games, plus_minus
                FROM team_game_splits
                WHERE season = 2026 AND split_type = 'total'
                ORDER BY pts DESC LIMIT 10
            """)
            for r in cur.fetchall():
                top_scorers.append({
                    'team': r['team_abbr'], 'pts': float(r['pts']) if r['pts'] else 0,
                    'games': r['games'], 'plus_minus': float(r['plus_minus']) if r['plus_minus'] else 0
                })
        except:
            pass

        recent_games = []
        try:
            cur.execute("""
                SELECT game_date, away_team_abbr, home_team_abbr, away_pts, home_pts
                FROM games WHERE game_date IS NOT NULL
                ORDER BY game_date DESC LIMIT 10
            """)
            for r in cur.fetchall():
                recent_games.append({
                    'date': str(r['game_date']) if r['game_date'] else '',
                    'away': r['away_team_abbr'], 'home': r['home_team_abbr'],
                    'away_pts': r['away_pts'], 'home_pts': r['home_pts']
                })
        except:
            pass

        cur.close()
        conn.close()

        crawl_status = {}
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                crawl_status = json.load(f)

        return jsonify({
            'tables': table_info,
            'total_tables': len(tables),
            'total_records': total_records,
            'active_teams': active_teams,
            'last_game_date': last_game,
            'splits': {'teams': splits_teams, 'seasons': splits_seasons, 'total': splits_total},
            'top_scorers': top_scorers,
            'recent_games': recent_games,
            'crawl_running': _crawl_running,
            'crawl_status': crawl_status,
            'last_result': _last_result,
            'season': _get_current_season(),
        })
    except Exception as e:
        logger.error(f"Status API error: {e}")
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Table Browser
# ════════════════════════════════════════

@app.route('/api/tables')
def api_tables():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = []
        for r in cur.fetchall():
            tname = r['table_name']
            try:
                cur.execute(f"SELECT count(*) AS cnt FROM {tname}")
                cnt = cur.fetchone()['cnt']
            except:
                cnt = 0
            tables.append({'name': tname, 'rows': cnt})
        cur.close()
        conn.close()
        return jsonify({'tables': tables, 'total': len(tables)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables/<table_name>')
def api_table_data(table_name):
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 500)
    search = request.args.get('search', '')
    offset = (page - 1) * per_page

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        """, (table_name,))
        if not cur.fetchone():
            return jsonify({'error': 'Table not found'}), 404

        cur.execute("""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [{'name': r['column_name'], 'type': r['data_type']} for r in cur.fetchall()]
        col_names = [c['name'] for c in columns]

        where_clause = ''
        params = []
        if search:
            search_cols = [c for c in col_names if c not in ('id', 'created_at', 'scraped_at')]
            if search_cols:
                conditions = [f"CAST({c} AS TEXT) ILIKE %s" for c in search_cols[:8]]
                where_clause = "WHERE " + " OR ".join(conditions)
                params = [f"%{search}%"] * len(conditions[:8])

        cur.execute(f"SELECT count(*) AS cnt FROM {table_name} {where_clause}", params)
        total = cur.fetchone()['cnt']

        cur.execute(
            f"SELECT * FROM {table_name} {where_clause} ORDER BY 1 LIMIT %s OFFSET %s",
            params + [per_page, offset]
        )
        rows = [_serialize(r) for r in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            'columns': col_names,
            'rows': rows,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        logger.error(f"Table data API error: {e}")
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Teams
# ════════════════════════════════════════

@app.route('/api/teams')
def api_teams():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT team_code AS team_abbr, team_name, is_active
            FROM team_mapping
            ORDER BY is_active DESC, team_code
        """)
        teams = [_serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'teams': teams, 'total': len(teams)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/teams/<abbr>/splits')
def api_team_splits(abbr):
    season = request.args.get('season', '2026')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM team_game_splits
            WHERE team_abbr = %s AND season = %s
            ORDER BY split_type
        """, (abbr.upper(), int(season)))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'splits': rows, 'total': len(rows)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Players
# ════════════════════════════════════════

@app.route('/api/players')
def api_players():
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 200)
    search = request.args.get('search', '')
    season = request.args.get('season', '2026')
    offset = (page - 1) * per_page

    try:
        conn = get_db()
        cur = conn.cursor()

        where = "WHERE season = %s"
        params = [int(season)]
        if search:
            where += " AND player ILIKE %s"
            params.append(f"%{search}%")

        cur.execute(f"SELECT count(*) AS cnt FROM player_per_game {where}", params)
        total = cur.fetchone()['cnt']

        cur.execute(f"""
            SELECT player AS player_name, team, g, mp_per_game AS mp,
                   pts_per_game AS pts, trb_per_game AS reb, ast_per_game AS ast,
                   stl_per_game AS stl, blk_per_game AS blk, tov_per_game AS tov,
                   fg_percent AS fg_pct, x3p_percent AS fg3_pct, ft_percent AS ft_pct,
                   e_fg_percent AS e_fg_pct
            FROM player_per_game {where}
            ORDER BY pts_per_game DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        rows = [_serialize(r) for r in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            'players': rows, 'total': total,
            'page': page, 'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Leaderboards
# ════════════════════════════════════════

@app.route('/api/leaderboard/<stat_type>')
def api_leaderboard(stat_type):
    season = request.args.get('season', '2026')
    limit = min(int(request.args.get('limit', 20)), 100)

    valid_tables = {
        'per_game': 'player_per_game',
        'totals': 'player_totals',
        'advanced': 'player_advanced',
    }
    table = valid_tables.get(stat_type, 'player_per_game')

    sort_col = request.args.get('sort', 'pts')
    valid_cols = {'pts', 'reb', 'ast', 'stl', 'blk', 'tov', 'fg_pct', 'fg3_pct', 'ft_pct',
                  'per', 'ts_pct', 'usg_pct', 'bpm', 'vorp', 'ws', 'mp'}
    if sort_col not in valid_cols:
        sort_col = 'pts'

    # Map sort col to actual DB column names per table
    col_map = {
        'per_game': {'pts': 'pts_per_game', 'reb': 'trb_per_game', 'ast': 'ast_per_game',
                     'stl': 'stl_per_game', 'blk': 'blk_per_game', 'tov': 'tov_per_game',
                     'fg_pct': 'fg_percent', 'fg3_pct': 'x3p_percent', 'ft_pct': 'ft_percent',
                     'mp': 'mp_per_game', 'ts_pct': 'e_fg_percent'},
        'totals': {'pts': 'pts', 'reb': 'trb', 'ast': 'ast', 'stl': 'stl', 'blk': 'blk',
                   'tov': 'tov', 'fg_pct': 'fg_percent', 'fg3_pct': 'x3p_percent',
                   'ft_pct': 'ft_percent', 'mp': 'mp'},
        'advanced': {'per': 'per', 'ts_pct': 'ts_percent', 'usg_pct': 'usg_percent',
                     'bpm': 'bpm', 'vorp': 'vorp', 'ws': 'ws', 'mp': 'mp'},
    }
    actual_sort = col_map.get(stat_type, {}).get(sort_col, sort_col)

    select_cols = {
        'per_game': """player AS player_name, team, g, mp_per_game AS mp,
                   pts_per_game AS pts, trb_per_game AS reb, ast_per_game AS ast,
                   stl_per_game AS stl, blk_per_game AS blk, tov_per_game AS tov,
                   fg_percent AS fg_pct, x3p_percent AS fg3_pct, ft_percent AS ft_pct,
                   e_fg_percent AS e_fg_pct, NULL AS ts_pct""",
        'totals': """player AS player_name, team, g, mp,
                   pts, trb AS reb, ast, stl, blk, tov,
                   fg_percent AS fg_pct, x3p_percent AS fg3_pct, ft_percent AS ft_pct,
                   e_fg_percent AS e_fg_pct, NULL AS ts_pct""",
        'advanced': """player AS player_name, team, g, mp,
                   NULL AS pts, NULL AS reb, NULL AS ast, NULL AS stl, NULL AS blk, NULL AS tov,
                   NULL AS fg_pct, NULL AS fg3_pct, NULL AS ft_pct,
                   NULL AS e_fg_pct, ts_percent AS ts_pct""",
    }
    select_clause = select_cols.get(stat_type, select_cols['per_game'])

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {select_clause}
            FROM {table}
            WHERE season = %s AND g >= 10
            ORDER BY {actual_sort} DESC NULLS LAST
            LIMIT %s
        """, (int(season), limit))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'leaderboard': rows, 'stat_type': stat_type, 'sort': sort_col})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Games
# ════════════════════════════════════════

@app.route('/api/games')
def api_games():
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 200)
    season = request.args.get('season')
    offset = (page - 1) * per_page

    try:
        conn = get_db()
        cur = conn.cursor()

        where = "WHERE 1=1"
        params = []
        if season:
            where += " AND season = %s"
            params.append(int(season))

        cur.execute(f"SELECT count(*) AS cnt FROM games {where}", params)
        total = cur.fetchone()['cnt']

        cur.execute(f"""
            SELECT gameid, game_date, season, away_team_abbr, home_team_abbr,
                   away_pts, home_pts, game_type, status
            FROM games {where}
            ORDER BY game_date DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        rows = [_serialize(r) for r in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            'games': rows, 'total': total,
            'page': page, 'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Charts / Visualization data
# ════════════════════════════════════════

@app.route('/api/charts/scoring-trend')
def api_scoring_trend():
    """Team scoring trend across seasons."""
    team = request.args.get('team', 'BOS')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT season, pts, plus_minus, games, reb, ast, stl, blk
            FROM team_game_splits
            WHERE team_abbr = %s AND split_type = 'total'
            ORDER BY season
        """, (team.upper(),))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'data': rows, 'team': team.upper()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/team-comparison')
def api_team_comparison():
    """Compare two teams across multiple stats."""
    team1 = request.args.get('team1', 'BOS')
    team2 = request.args.get('team2', 'LAL')
    season = request.args.get('season', '2026')
    try:
        conn = get_db()
        cur = conn.cursor()
        result = {}
        for abbr in [team1.upper(), team2.upper()]:
            cur.execute("""
                SELECT split_type, pts, fg_pct, fg3_pct, ft_pct,
                       reb, ast, stl, blk, tov, plus_minus
                FROM team_game_splits
                WHERE team_abbr = %s AND season = %s AND split_type = 'total'
            """, (abbr, int(season)))
            r = cur.fetchone()
            result[abbr] = _serialize(r)
        cur.close()
        conn.close()
        return jsonify({'teams': result, 'season': int(season)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/team-radar')
def api_team_radar():
    """Radar chart data for a team."""
    team = request.args.get('team', 'BOS')
    season = request.args.get('season', '2026')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT pts, reb, ast, stl, blk, fg_pct, fg3_pct, ft_pct, plus_minus
            FROM team_game_splits
            WHERE team_abbr = %s AND season = %s AND split_type = 'total'
        """, (team.upper(), int(season)))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'data': _serialize(r), 'team': team.upper()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/league-scoring')
def api_league_scoring():
    """All teams scoring for bar chart."""
    season = request.args.get('season', '2026')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT team_abbr, pts, plus_minus, games, reb, ast
            FROM team_game_splits
            WHERE season = %s AND split_type = 'total'
            ORDER BY pts DESC
        """, (int(season),))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'data': rows, 'season': int(season)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════
# Crawler Control
# ════════════════════════════════════════

@app.route('/api/crawl', methods=['POST'])
def api_crawl():
    global _crawl_running, _crawl_thread, _last_result

    if _crawl_running:
        return jsonify({'error': 'A crawl is already running'}), 409

    req = request.json or {}
    mode = req.get('mode', 'check')
    params = req.get('params', {})

    _crawl_running = True
    _last_result = None

    _crawl_thread = threading.Thread(
        target=_run_crawl_task, args=(mode, params), daemon=True
    )
    _crawl_thread.start()

    return jsonify({'status': 'started', 'mode': mode})


@app.route('/api/crawl/status')
def api_crawl_status():
    return jsonify({'running': _crawl_running, 'last_result': _last_result})


@app.route('/api/crawl/stop', methods=['POST'])
def api_crawl_stop():
    """Stop the running crawl process."""
    global _crawl_running, _crawl_process, _last_result
    if not _crawl_running or _crawl_process is None:
        return jsonify({'error': 'No crawl is running'}), 400
    try:
        pid = _crawl_process.pid
        logger.info(f"Stopping crawl process (PID={pid})...")
        # Kill the process tree on Windows
        subprocess.run(['taskkill', '/pid', str(pid), '/f', '/t'],
                       capture_output=True, timeout=10)
        _crawl_process = None
        _crawl_running = False
        _last_result = {'status': 'stopped', 'duration': 0}
        logger.info("Crawl stopped by user.")
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Failed to stop crawl: {e}")
        return jsonify({'error': str(e)}), 500


def _run_crawl_task(mode: str, params: dict):
    global _crawl_running, _last_result, _crawl_process
    start_time = time.time()
    logger.info(f"=== Crawl started: mode={mode}, params={params} ===")

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
            cmd = [python_exe, CRAWLER_SCRIPT, '--full-season', str(params.get('season', _get_current_season()))]
        elif mode == 'list_tables':
            cmd = [python_exe, CRAWLER_SCRIPT, '--list-tables']
        else:
            _last_result = {'status': 'error', 'error': f'Unknown mode: {mode}'}
            _crawl_running = False
            return

        logger.info(f"Command: {' '.join(cmd)}")

        # Build environment with crawl settings
        crawl_env = {**os.environ, 'HTTP_PROXY': '', 'HTTPS_PROXY': ''}
        if params.get('interval'):
            crawl_env['CRAWL_INTERVAL'] = str(params['interval'])
            logger.info(f"Crawl interval set to {params['interval']}s")
        if params.get('duration'):
            crawl_env['CRAWL_DURATION'] = str(params['duration'])
            logger.info(f"Crawl duration limit set to {params['duration']}s")

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=crawl_env,
        )
        _crawl_process = proc

        # If duration is set, start a timer to kill the process
        duration_limit = params.get('duration')
        timer = None
        if duration_limit:
            def _kill_after_duration():
                if _crawl_process is not None:
                    logger.info(f"Duration limit ({duration_limit}s) reached, stopping crawl...")
                    try:
                        subprocess.run(['taskkill', '/pid', str(_crawl_process.pid), '/f', '/t'],
                                       capture_output=True, timeout=10)
                    except:
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


# ════════════════════════════════════════
# SSE Log Stream
# ════════════════════════════════════════

@app.route('/api/logs/stream')
def api_logs_stream():
    def generate():
        while True:
            try:
                msg = _log_queue.get(timeout=1)
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                yield f": keepalive\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


# ════════════════════════════════════════
# Main
# ════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description='NBACore Desktop API Server')
    parser.add_argument('--port', type=int, default=5577, help='Port (default: 5577)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host')
    args = parser.parse_args()

    if not ensure_db():
        logger.warning("Cannot start PostgreSQL! API will start but DB features won't work.")

    print(f"\n{'='*55}")
    print(f"  NBACore Desktop API — http://{args.host}:{args.port}")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*55}\n")

    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
