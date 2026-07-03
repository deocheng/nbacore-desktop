import os
import sys
import time
import logging
from datetime import date, datetime
from flask import Blueprint, jsonify, request, g
from config import ALLOWED_TABLES, CRAWLER_SCRIPT
from db import get_db_conn, release_db_conn, is_port_open

common_bp = Blueprint('common', __name__)
logger = logging.getLogger('nbacore.common')

# 🔴 高：递归转换 datetime/date 为字符串，完美解决 json 序列化报错
def deep_serialize(obj):
    if isinstance(obj, dict):
        return {k: deep_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [deep_serialize(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

@common_bp.route('/health')
def api_health():
    """
    🟢 低：跨平台磁盘检查优化
    在 Windows 下，获取当前脚本所在盘符（如 C: 或 D:），确保统计准确
    """
    try:
        drive, _ = os.path.splitdrive(os.path.abspath(__file__))
        drive_path = drive if drive else "/"
        import shutil
        total, used, free = shutil.disk_usage(drive_path)
        free_gb = free / (2**30)
    except Exception as e:
        logger.error(f"Disk check error: {e}")
        free_gb = 0.0

    crawler_exists = os.path.exists(CRAWLER_SCRIPT)
    status = 'ok' if (is_port_open() and crawler_exists and free_gb > 1.0) else 'warning'
    
    return jsonify({
        'status': status,
        'database_connected': is_port_open(),
        'crawler_script_exists': crawler_exists,
        'disk_free_gb': round(free_gb, 2),
        'drive_checked': drive_path,
        'timestamp': time.time()
    })

@common_bp.route('/tables/<table_name>')
def api_table_data(table_name):
    if table_name not in ALLOWED_TABLES:
        return jsonify({'error': 'Access Denied: Table not in security whitelist'}), 403

    # 🟡 中：参数校验（防止负数、零或恶意超大分页导致 OOM）
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        if page <= 0 or per_page <= 0:
            return jsonify({'error': 'Invalid page or per_page. Must be greater than 0.'}), 400
        per_page = min(per_page, 500)  # 硬限最大 500 条
    except ValueError:
        return jsonify({'error': 'Page and per_page must be integers.'}), 400

    # 🟡 中：获取前端传递的搜索与排序参数
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', '').strip()        # 列名
    sort_order = request.args.get('sort_order', 'ASC').upper() # ASC 或 DESC
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'ASC'

    offset = (page - 1) * per_page
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()

        # 1. 动态获取目标表的字段，用于安全校验和搜索
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
        """, (table_name,))
        columns_info = cur.fetchall()
        if not columns_info:
            return jsonify({'error': f'Table {table_name} metadata not found'}), 404
            
        all_cols = [r['column_name'] for r in columns_info]

        # 2. 构造安全搜索条件 (仅对文本/数字类型列进行 ILIKE 模糊查询)
        where_clause = ""
        query_params = []
        if search:
            search_conditions = []
            for col in all_cols:
                # 排除可能引起索引失效或格式冲突的非必搜大字段/时间字段
                if col not in ('id', 'created_at', 'scraped_at', 'updated_at'):
                    search_conditions.append(f"CAST({col} AS TEXT) ILIKE %s")
                    query_params.append(f"%{search}%")
            if search_conditions:
                where_clause = " WHERE " + " OR ".join(search_conditions)

        # 3. 构造安全排序条件 (严格校验排序字段是否在表字段白名单内，防 SQL 注入)
        order_clause = ""
        if sort_by and sort_by in all_cols:
            order_clause = f" ORDER BY {sort_by} {sort_order}"
        else:
            order_clause = f" ORDER BY 1 {sort_order}" # 默认用第一列排序

        # 4. 获取总数
        count_sql = f"SELECT count(*) AS cnt FROM {table_name} {where_clause}"
        cur.execute(count_sql, query_params)
        total = cur.fetchone()['cnt']

        # 5. 分页查询数据
        data_sql = f"SELECT * FROM {table_name} {where_clause} {order_clause} LIMIT %s OFFSET %s"
        cur.execute(data_sql, query_params + [per_page, offset])
        raw_rows = cur.fetchall()

        # 🔴 高：调用递归序列化，深度转换所有行数据
        serialized_rows = deep_serialize(raw_rows)

        return jsonify({
            'columns': all_cols,
            'rows': serialized_rows,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f"Database error in api_table_data: {e}")
        return jsonify({'error': 'Internal server database error'}), 500
    finally:
        release_db_conn(conn)