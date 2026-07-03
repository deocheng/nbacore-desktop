"""
Players Blueprint — Player search, leaderboard, games
"""
import logging
from flask import Blueprint, jsonify, request

from common import serialize, run_query

logger = logging.getLogger('nbacore.routes.players')
players_bp = Blueprint('players', __name__)


@players_bp.route('/players')
def list_players():
    """Search players by name within a season."""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 200)
    search = request.args.get('search', '')
    season = request.args.get('season', '2026')
    offset = (page - 1) * per_page

    try:
        where = "WHERE season = %s"
        params = [int(season)]
        if search:
            where += " AND player ILIKE %s"
            params.append(f"%{search}%")

        total_row = run_query(f"SELECT count(*) AS cnt FROM player_per_game {where}", params, fetch='one')
        total = total_row['cnt']

        rows = run_query(f"""
            SELECT player AS player_name, team, g, mp_per_game AS mp,
                   pts_per_game AS pts, trb_per_game AS reb, ast_per_game AS ast,
                   stl_per_game AS stl, blk_per_game AS blk, tov_per_game AS tov,
                   fg_percent AS fg_pct, x3p_percent AS fg3_pct, ft_percent AS ft_pct,
                   e_fg_percent AS e_fg_pct
            FROM player_per_game {where}
            ORDER BY pts_per_game DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, params + [per_page, offset], fetch='all')

        players = [serialize(r) for r in rows]
        return jsonify({
            'players': players, 'total': total,
            'page': page, 'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@players_bp.route('/leaderboard/<stat_type>')
def leaderboard(stat_type: str):
    """Player leaderboard sorted by a stat column."""
    season = request.args.get('season', '2026')
    limit = min(int(request.args.get('limit', 20)), 100)

    valid_tables = {'per_game': 'player_per_game', 'totals': 'player_totals', 'advanced': 'player_advanced'}
    table = valid_tables.get(stat_type, 'player_per_game')

    sort_col = request.args.get('sort', 'pts')
    valid_cols = {'pts', 'reb', 'ast', 'stl', 'blk', 'tov', 'fg_pct', 'fg3_pct', 'ft_pct',
                  'per', 'ts_pct', 'usg_pct', 'bpm', 'vorp', 'ws', 'mp'}
    if sort_col not in valid_cols:
        sort_col = 'pts'

    # Map sort column to actual DB column names per table
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
        rows = run_query(f"""
            SELECT {select_clause}
            FROM {table}
            WHERE season = %s AND g >= 10
            ORDER BY {actual_sort} DESC NULLS LAST
            LIMIT %s
        """, [int(season), limit], fetch='all')
        result = [serialize(r) for r in rows]
        return jsonify({'leaderboard': result, 'stat_type': stat_type, 'sort': sort_col})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@players_bp.route('/games')
def list_games():
    """Paginated list of games."""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 200)
    season = request.args.get('season')
    offset = (page - 1) * per_page

    try:
        where = "WHERE 1=1"
        params = []
        if season:
            where += " AND season = %s"
            params.append(int(season))

        total_row = run_query(f"SELECT count(*) AS cnt FROM games {where}", params, fetch='one')
        total = total_row['cnt']

        rows = run_query(f"""
            SELECT gameid, game_date, season, away_team_abbr, home_team_abbr,
                   away_pts, home_pts, game_type, status
            FROM games {where}
            ORDER BY game_date DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, params + [per_page, offset], fetch='all')

        games = [serialize(r) for r in rows]
        return jsonify({
            'games': games, 'total': total,
            'page': page, 'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
