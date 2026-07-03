"""
Stats Blueprint — Chart/visualization data endpoints
"""
import logging
from flask import Blueprint, jsonify, request

from common import serialize, run_query

logger = logging.getLogger('nbacore.routes.stats')
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/charts/league-scoring')
def league_scoring():
    """All teams scoring for bar chart."""
    season = request.args.get('season', '2026')
    try:
        rows = run_query("""
            SELECT team_abbr, pts, plus_minus, games, reb, ast
            FROM team_game_splits
            WHERE season = %s AND split_type = 'total'
            ORDER BY pts DESC
        """, [int(season)], fetch='all')
        data = [serialize(r) for r in rows]
        return jsonify({'data': data, 'season': int(season)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/charts/scoring-trend')
def scoring_trend():
    """Team scoring trend across seasons."""
    team = request.args.get('team', 'BOS')
    try:
        rows = run_query("""
            SELECT season, pts, plus_minus, games, reb, ast, stl, blk
            FROM team_game_splits
            WHERE team_abbr = %s AND split_type = 'total'
            ORDER BY season
        """, [team.upper()], fetch='all')
        data = [serialize(r) for r in rows]
        return jsonify({'data': data, 'team': team.upper()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/charts/team-radar')
def team_radar():
    """Radar chart data for a team."""
    team = request.args.get('team', 'BOS')
    season = request.args.get('season', '2026')
    try:
        row = run_query("""
            SELECT pts, reb, ast, stl, blk, fg_pct, fg3_pct, ft_pct, plus_minus
            FROM team_game_splits
            WHERE team_abbr = %s AND season = %s AND split_type = 'total'
        """, [team.upper(), int(season)], fetch='one')
        return jsonify({'data': serialize(row), 'team': team.upper()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/charts/team-comparison')
def team_comparison():
    """Compare two teams across multiple stats."""
    team1 = request.args.get('team1', 'BOS')
    team2 = request.args.get('team2', 'LAL')
    season = request.args.get('season', '2026')
    try:
        result = {}
        for abbr in [team1.upper(), team2.upper()]:
            row = run_query("""
                SELECT split_type, pts, fg_pct, fg3_pct, ft_pct,
                       reb, ast, stl, blk, tov, plus_minus
                FROM team_game_splits
                WHERE team_abbr = %s AND season = %s AND split_type = 'total'
            """, [abbr, int(season)], fetch='one')
            result[abbr] = serialize(row)
        return jsonify({'teams': result, 'season': int(season)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
