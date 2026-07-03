import pytest
from unittest.mock import patch, MagicMock
from app import app
from db import init_pool, get_db_conn, release_db_conn

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1. 测试连接池借出与归还行为
@patch('db._pool')
def test_db_pool_connection(mock_pool):
    mock_conn = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    
    # 初始化及借出
    init_pool()
    conn = get_db_conn()
    assert conn == mock_conn
    mock_pool.getconn.assert_called_once()
    
    # 归还
    release_db_conn(conn)
    mock_pool.putconn.assert_called_with(mock_conn)

# 2. 测试表名越权拦截（不在白名单内）
def test_table_data_security_whitelist(client):
    # 尝试访问系统敏感表
    response = client.get('/api/v1/tables/pg_shadow')
    assert response.status_code == 403
    assert b'Access Denied' in response.data

# 3. 测试分页参数非负、非空等合法性校验
def test_table_data_invalid_params(client):
    # 传入非法的负数分页
    response = client.get('/api/v1/tables/games?page=-5&per_page=abc')
    assert response.status_code == 400
    assert b'Invalid page' in response.data or b'must be integers' in response.data