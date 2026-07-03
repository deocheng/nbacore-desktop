"""
NBACore Desktop — Configuration Module v2
==========================================
修复: dotenv 导入错误 -> 手动解析 .env
修复: 所有配置外部化
"""
import os
from pathlib import Path

# ── Path Resolution ──
BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent.parent  # nba_data/

CRAWLER_SCRIPT = str(PARENT_DIR / 'nba_daily_crawler.py')
STATUS_FILE = str(PARENT_DIR / 'crawl_status.json')

# ── .env File Loading (manual, no external dependency) ──
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

# ── Database Config ──
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5433')),
    'database': os.getenv('DB_NAME', 'nba'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}

# ── Security Whitelist ──
# Tables accessible via the /tables/<name> browser endpoint
ALLOWED_TABLES = {
    'team_mapping',
    'team_game_splits',
    'player_per_game',
    'player_totals',
    'player_advanced',
    'player_play_by_play',
    'games',
    'awards',
    'award_types',
    'team_awards',
}

# ── Server Config ──
SERVER_PORT = int(os.getenv('SERVER_PORT', '5577'))
SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')

# ── Current NBA Season ──
def get_current_season() -> int:
    from datetime import date
    d = date.today()
    return d.year + 1 if d.month >= 10 else d.year
