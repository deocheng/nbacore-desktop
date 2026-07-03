"""
NBACore Desktop — Common Utilities v2
======================================
修复: Windows 磁盘路径 (使用 os.path.splitdrive)
修复: 日期序列化 (datetime/date -> isoformat)
修复: 搜索功能补全
"""
import os
import shutil
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

from flask import jsonify
from psycopg2.extras import RealDictRow

from config import CRAWLER_SCRIPT, STATUS_FILE
from db import get_db_conn, release_db_conn, ensure_db, is_port_open

logger = logging.getLogger('nbacore.common')


# ── Serialization ──

def serialize(obj: Any) -> Any:
    """Convert a RealDictRow or dict to a JSON-safe structure.
    Handles datetime/date objects that psycopg2 returns natively.
    """
    if obj is None:
        return None
    if isinstance(obj, RealDictRow):
        obj = dict(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (datetime, date)):
                obj[k] = v.isoformat()
            elif isinstance(v, RealDictRow):
                obj[k] = serialize(v)
        return obj
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


# ── Query Helper ──

def run_query(query: str, params: list = None, fetch: str = 'all'):
    """Execute a query using a pooled connection.
    fetch: 'all' | 'one' | 'none'
    """
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(query, params or [])
        result = None
        if fetch == 'all':
            result = cur.fetchall()
        elif fetch == 'one':
            result = cur.fetchone()
        conn.commit()
        cur.close()
        return result
    except Exception as e:
        logger.error(f"Query error: {e}")
        if conn:
            try: conn.rollback()
            except Exception: pass
        raise
    finally:
        if conn:
            release_db_conn(conn)


# ── Table Browser with Search ──

def get_table_info(table_name: str, page: int = 1, per_page: int = 50, search: str = ''):
    """Fetch paginated table data with optional search.
    Returns (columns, rows, total, total_pages).
    """
    from config import ALLOWED_TABLES
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table_name}' is not in the allowed whitelist.")

    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()

        # Get column metadata
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        col_data = cur.fetchall()
        columns = [{'name': r['column_name'], 'type': r['data_type']} for r in col_data]
        col_names = [c['name'] for c in columns]

        # Build WHERE clause for search
        where_clause = ""
        params = []
        if search:
            searchable = [c for c in col_names if c not in ('id', 'created_at', 'scraped_at')]
            if searchable:
                conditions = [f"CAST({c} AS TEXT) ILIKE %s" for c in searchable[:8]]
                where_clause = " WHERE " + " OR ".join(conditions)
                params = [f"%{search}%"] * min(len(searchable), 8)

        # Total count
        cur.execute(f"SELECT count(*) AS cnt FROM {table_name}{where_clause}", params)
        total = cur.fetchone()['cnt']

        # Paginated data
        offset = (page - 1) * per_page
        cur.execute(
            f"SELECT * FROM {table_name}{where_clause} ORDER BY 1 LIMIT %s OFFSET %s",
            params + [per_page, offset]
        )
        rows = [serialize(r) for r in cur.fetchall()]

        cur.close()
        total_pages = (total + per_page - 1) // per_page
        return col_names, rows, total, total_pages
    finally:
        if conn:
            release_db_conn(conn)


# ── System Info (Windows-safe) ──

def get_disk_usage():
    """Get disk usage for the drive containing the project directory.
    Fix: Use the actual drive letter instead of '/' which fails on Windows.
    """
    try:
        # On Windows, resolve the system drive from the parent directory
        drive = os.path.splitdrive(str(Path(__file__).resolve().parent))[0]
        if not drive:
            drive = 'C:\\'
        total, used, free = shutil.disk_usage(drive)
        return {
            'drive': drive,
            'total_gb': round(total / (1024**3), 1),
            'used_gb': round(used / (1024**3), 1),
            'free_gb': round(free / (1024**3), 1),
            'free_pct': round(free / total * 100, 1) if total else 0,
        }
    except Exception as e:
        logger.warning(f"Could not get disk usage: {e}")
        return {'error': str(e)}


def get_crawler_status() -> dict:
    """Load crawl_status.json if it exists."""
    import json
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read crawl status: {e}")
    return {}


def check_crawler_script() -> bool:
    """Check if the crawler script exists on disk."""
    return os.path.exists(CRAWLER_SCRIPT)
