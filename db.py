import time
import socket
import subprocess
import logging
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

logger = logging.getLogger('nbacore.db')

# 🟡 中：引入线程安全连接池（最小1个，最大20个连接）
_pool = None

def init_pool():
    global _pool
    if _pool is None:
        try:
            _pool = ThreadedConnectionPool(1, 20, **DB_CONFIG, cursor_factory=RealDictCursor)
            logger.info("Database connection pool initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")

def get_db_conn():
    if _pool is None:
        init_pool()
    return _pool.getconn()

def release_db_conn(conn):
    if _pool and conn:
        _pool.putconn(conn)

def is_port_open():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        r = s.connect_ex((DB_CONFIG['host'], DB_CONFIG['port']))
        s.close()
        return r == 0
    except:
        return False

def ensure_db():
    if is_port_open():
        return True
    logger.info('PostgreSQL port closed, attempting to wake up service...')
    for svc in ['postgresql-x64-17', 'postgresql-x64-16', 'postgresql-17', 'postgresql-16']:
        try:
            r = subprocess.run(['net', 'start', svc], capture_output=True, text=True, timeout=15)
            if r.returncode == 0 or '已经启动' in r.stdout or 'already started' in r.stdout.lower():
                for _ in range(5):
                    time.sleep(1)
                    if is_port_open():
                        return True
        except:
            continue
    return False