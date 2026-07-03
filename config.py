import os
from pathlib import Path
from dotenv import load_file

# 尝试加载 .env 文件
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent.parent

CRAWLER_SCRIPT = str(PARENT_DIR / 'nba_daily_crawler.py')
STATUS_FILE = str(PARENT_DIR / 'crawl_status.json')

# 🔴 高：数据库凭证外部化
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5433)),
    'database': os.getenv('DB_NAME', 'nba'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# 🔴 高：安全白名单 - 严格限制可公开通过 API 浏览器访问的表
ALLOWED_TABLES = {
    'team_mapping', 
    'team_game_splits', 
    'player_per_game', 
    'player_totals', 
    'player_advanced', 
    'games'
}