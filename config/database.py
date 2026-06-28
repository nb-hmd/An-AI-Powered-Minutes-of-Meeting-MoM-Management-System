"""
Database connection module.
Provides connection pool and helper functions for PostgreSQL.
"""

import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
from config.settings import DB_CONFIG


# ============================================
# Connection Pool
# ============================================
_connection_pool = None


def init_connection_pool(min_conn=1, max_conn=10):
    """Initialize the database connection pool."""
    global _connection_pool
    try:
        _connection_pool = pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        return True
    except psycopg2.Error as e:
        print(f"❌ Error initializing connection pool: {e}")
        return False


def get_connection_pool():
    """Get the connection pool, initializing it if necessary."""
    global _connection_pool
    if _connection_pool is None:
        init_connection_pool()
    return _connection_pool


@contextmanager
def get_connection():
    """
    Context manager that provides a database connection from the pool.
    Automatically returns the connection to the pool when done.
    
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
    """
    conn_pool = get_connection_pool()
    conn = conn_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn_pool.putconn(conn)


@contextmanager
def get_cursor(dict_cursor=True):
    """
    Context manager that provides a database cursor.
    Uses RealDictCursor by default for dict-like row access.
    
    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
    """
    with get_connection() as conn:
        cursor_factory = extras.RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


def test_connection():
    """Test the database connection."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 AS connected")
            result = cur.fetchone()
            if result and result["connected"] == 1:
                print("✅ Database connection successful!")
                return True
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
    return False


def close_all_connections():
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        print("✅ All database connections closed.")
