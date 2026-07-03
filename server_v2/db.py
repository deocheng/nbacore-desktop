"""
NBACore Desktop — Database Connection Module v2
================================================
修复: 使用 ThreadedConnectionPool 替代每次 connect
"""
import time
import socket
import subprocess
import logging
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG

logger = logging.getLogger('nbacore.db')

_pool: ThreadedConnectionPool | None = None


def init_pool():
    """Initialize the thread-safe connection pool (1-20 connections)."""
    global _pool
    if _pool is None:
        try:
            _pool = ThreadedConnectionPool(
                1, 20, **DB_CONFIG, cursor_factory=RealDictCursor
            )
            logger.info(f"DB pool initialized -> {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        except Exception as e:
            logger.error(f"Failed to initialize DB pool: {e}")
            raise


def get_db_conn():
    """Borrow a connection from the pool."""
    if _pool is None:
        init_pool()
    return _pool.getconn()


def release_db_conn(conn):
    """Return a connection to the pool."""
    if _pool and conn:
        try:
            _pool.putconn(conn)
        except Exception:
            pass


def close_all():
    """Close all connections (called on shutdown)."""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
        logger.info("DB pool closed.")


def is_port_open(host: str = None, port: int = None) -> bool:
    """Check if the PostgreSQL port is accepting connections."""
    h = host or DB_CONFIG['host']
    p = port or DB_CONFIG['port']
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        r = s.connect_ex((h, p))
        s.close()
        return r == 0
    except Exception:
        return False


def ensure_db() -> bool:
    """Ensure PostgreSQL is running; attempt to start it if not."""
    if is_port_open():
        return True
    logger.info('PostgreSQL port closed, attempting to wake up service...')
    for svc in ['postgresql-x64-17', 'postgresql-x64-16', 'postgresql-x64-15',
                'postgresql-17', 'postgresql-16', 'postgresql-15']:
        try:
            r = subprocess.run(['net', 'start', svc], capture_output=True, text=True, timeout=15)
            if r.returncode == 0 or '已经启动' in r.stdout or 'already started' in r.stdout.lower():
                logger.info(f'Started: {svc}')
                for _ in range(10):
                    time.sleep(1)
                    if is_port_open():
                        return True
        except Exception:
            continue
    return False
