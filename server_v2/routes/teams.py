"""
Teams Blueprint — Team list, team splits
"""
import logging
from flask import Blueprint, jsonify, request

from common import serialize, run_query

logger = logging.getLogger('nbacore.routes.teams')
teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/teams')
def list_teams():
    """List all teams."""
    try:
        rows = run_query("""
            SELECT team_code AS team_abbr, team_name, is_active
            FROM team_mapping
            ORDER BY is_active DESC, team_code
        """, fetch='all')
        teams = [serialize(r) for r in rows]
        return jsonify({'teams': teams, 'total': len(teams)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teams_bp.route('/teams/<abbr>/splits')
def team_splits(abbr: str):
    """Get team_game_splits for a specific team and season."""
    season = request.args.get('season', '2026')
    try:
        rows = run_query("""
            SELECT * FROM team_game_splits
            WHERE team_abbr = %s AND season = %s
            ORDER BY split_type
        """, [abbr.upper(), int(season)], fetch='all')
        splits = [serialize(r) for r in rows]
        return jsonify({'splits': splits, 'total': len(splits)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
