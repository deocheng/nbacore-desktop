"""
System Blueprint — Health, Tables, Table Data
"""
import logging
from flask import Blueprint, jsonify, request

from config import ALLOWED_TABLES, get_current_season
from db import ensure_db, is_port_open
from common import get_disk_usage, get_crawler_status, check_crawler_script, serialize, get_table_info, run_query

logger = logging.getLogger('nbacore.routes.system')
system_bp = Blueprint('system', __name__)


@system_bp.route('/health')
def health():
    """Comprehensive health check."""
    db_ok = is_port_open()
    return jsonify({
        'status': 'ok' if db_ok else 'degraded',
        'db': db_ok,
        'crawler_script': check_crawler_script(),
        'disk': get_disk_usage(),
        'server_time': get_current_season(),
    })


@system_bp.route('/status')
def status():
    """Full dashboard status — tables, records, teams, splits, recent games."""
    if not ensure_db():
        return jsonify({'error': 'Cannot connect to database'}), 500

    try:
        tables = run_query("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, fetch='all')

        table_info = []
        total_records = 0
        for t in tables:
            tname = t['table_name']
            try:
                row = run_query(f"SELECT count(*) AS cnt FROM {tname}", fetch='one')
                cnt = row['cnt']
                total_records += cnt
            except Exception:
                cnt = 0
            table_info.append({'name': tname, 'rows': cnt})

        active_teams = 0
        try:
            r = run_query("SELECT count(*) AS cnt FROM team_mapping WHERE is_active = true", fetch='one')
            active_teams = r['cnt']
        except Exception:
            pass

        last_game = None
        try:
            r = run_query("SELECT max(game_date) AS d FROM games", fetch='one')
            last_game = str(r['d']) if r and r['d'] else None
        except Exception:
            pass

        splits = {'teams': 0, 'seasons': 0, 'total': 0}
        try:
            r = run_query(
                "SELECT count(distinct team_abbr) AS t, count(distinct season) AS s, count(*) AS c FROM team_game_splits",
                fetch='one'
            )
            if r:
                splits = {'teams': r['t'], 'seasons': r['s'], 'total': r['c']}
        except Exception:
            pass

        top_scorers = []
        try:
            rows = run_query("""
                SELECT team_abbr, pts, games, plus_minus
                FROM team_game_splits
                WHERE season = 2026 AND split_type = 'total'
                ORDER BY pts DESC LIMIT 10
            """, fetch='all')
            top_scorers = [{
                'team': r['team_abbr'],
                'pts': float(r['pts']) if r['pts'] else 0,
                'games': r['games'],
                'plus_minus': float(r['plus_minus']) if r['plus_minus'] else 0,
            } for r in rows]
        except Exception:
            pass

        recent_games = []
        try:
            rows = run_query("""
                SELECT game_date, away_team_abbr, home_team_abbr, away_pts, home_pts
                FROM games WHERE game_date IS NOT NULL
                ORDER BY game_date DESC LIMIT 10
            """, fetch='all')
            recent_games = [{
                'date': str(r['game_date']) if r['game_date'] else '',
                'away': r['away_team_abbr'], 'home': r['home_team_abbr'],
                'away_pts': r['away_pts'], 'home_pts': r['home_pts'],
            } for r in rows]
        except Exception:
            pass

        return jsonify({
            'tables': table_info,
            'total_tables': len(table_info),
            'total_records': total_records,
            'active_teams': active_teams,
            'last_game_date': last_game,
            'splits': splits,
            'top_scorers': top_scorers,
            'recent_games': recent_games,
            'season': get_current_season(),
        })
    except Exception as e:
        logger.error(f"Status API error: {e}")
        return jsonify({'error': str(e)}), 500


@system_bp.route('/tables')
def list_tables():
    """List all public tables with row counts."""
    try:
        rows = run_query("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, fetch='all')
        tables = []
        for r in rows:
            tname = r['table_name']
            try:
                cnt_row = run_query(f"SELECT count(*) AS cnt FROM {tname}", fetch='one')
                cnt = cnt_row['cnt']
            except Exception:
                cnt = 0
            tables.append({'name': tname, 'rows': cnt})
        return jsonify({'tables': tables, 'total': len(tables)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@system_bp.route('/tables/<table_name>')
def table_data(table_name):
    """Browse a table with pagination and search."""
    if table_name not in ALLOWED_TABLES:
        return jsonify({'error': f"Table '{table_name}' not allowed. Allowed: {sorted(ALLOWED_TABLES)}"}), 403

    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 500)
    search = request.args.get('search', '')

    try:
        columns, rows, total, total_pages = get_table_info(table_name, page, per_page, search)
        return jsonify({
            'columns': columns,
            'rows': rows,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Table data error: {e}")
        return jsonify({'error': str(e)}), 500
