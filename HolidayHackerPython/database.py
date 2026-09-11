import os
import sys
import sqlite3
import re
from datetime import date, datetime

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

class SQLiteCursorWrapper:
    """Wraps an SQLite cursor to emulate MySQL connector dictionary cursor & parameter handling."""
    def __init__(self, sqlite_cursor, connection):
        self._cursor = sqlite_cursor
        self._conn = connection

    def execute(self, query, params=None):
        # Convert MySQL %s parameter syntax to SQLite ? parameter syntax
        converted_query = re.sub(r'(?<!%)(%s)', '?', query)
        converted_query = converted_query.replace('%%', '%')
        
        # MySQL JSON functions or syntax adjustments if any
        if params is not None:
            # Format date/datetime params to strings for SQLite
            formatted_params = []
            for p in params:
                if isinstance(p, (date, datetime)):
                    formatted_params.append(p.isoformat())
                else:
                    formatted_params.append(p)
            return self._cursor.execute(converted_query, formatted_params)
        return self._cursor.execute(converted_query)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def _row_to_dict(self, row):
        res = {}
        for idx, col in enumerate(self._cursor.description):
            val = row[idx]
            col_name = col[0]
            # Convert ISO date strings to date objects for compatibility with models
            if col_name in ('holiday_date', 'leave_date', 'start_date', 'end_date') and isinstance(val, str):
                try:
                    val = date.fromisoformat(val[:10])
                except Exception:
                    pass
            elif col_name == 'created_at' and isinstance(val, str):
                try:
                    val = datetime.fromisoformat(val)
                except Exception:
                    pass
            res[col_name] = val
        return res

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()


class SQLiteConnectionWrapper:
    """Wraps an SQLite connection to provide MySQL connector compatible interface."""
    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self):
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                available_leaves INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS public_holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holiday_name TEXT NOT NULL,
                holiday_date TEXT NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS user_leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                leave_date TEXT NOT NULL,
                status TEXT DEFAULT 'approved',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, leave_date)
            );

            CREATE TABLE IF NOT EXISTS holiday_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                leaves_used INTEGER NOT NULL,
                consecutive_days INTEGER NOT NULL,
                efficiency REAL NOT NULL,
                recommended_dates TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        # Seed users if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, role, available_leaves) VALUES 
                (1, 'Test User', 'testuser', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', 'user', 10),
                (2, 'System Admin', 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 20)
            """)

        # Seed holidays if table is empty
        cursor.execute("SELECT COUNT(*) FROM public_holidays")
        if cursor.fetchone()[0] == 0:
            holidays = [
                ('New Year\'s Day', '2026-01-01', 'First day of the year'),
                ('Republic Day', '2026-01-26', 'Republic Day of India'),
                ('Maha Shivratri', '2026-02-17', 'Festival of Shiva'),
                ('Holi', '2026-03-04', 'Festival of Colors'),
                ('Good Friday', '2026-04-03', 'Christian Holiday'),
                ('Eid al-Fitr', '2026-04-20', 'Islamic Holiday'),
                ('Independence Day', '2026-08-15', 'National Independence Day'),
                ('Gandhi Jayanti', '2026-10-02', 'Mahatma Gandhi Birthday'),
                ('Dussehra', '2026-10-20', 'Vijayadashami'),
                ('Diwali', '2026-11-08', 'Festival of Lights'),
                ('Christmas Day', '2026-12-25', 'Christmas Celebration')
            ]
            cursor.executemany("INSERT INTO public_holidays (holiday_name, holiday_date, description) VALUES (?, ?, ?)", holidays)
            
        self._conn.commit()
        cursor.close()

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self._conn.cursor(), self._conn)

    def commit(self):
        self._conn.commit()

    def is_connected(self):
        return True

    def close(self):
        self._conn.close()


class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.engine_type = None
        return cls._instance
    
    def get_connection(self):
        # 1. Try MySQL first if available
        if MYSQL_AVAILABLE:
            try:
                if self.connection is None or not hasattr(self.connection, 'is_connected') or not self.connection.is_connected():
                    self.connection = mysql.connector.connect(
                        host='localhost',
                        database='holiday_hacker',
                        user='root',
                        password='',
                        connection_timeout=2
                    )
                    self.engine_type = 'mysql'
                return self.connection
            except Exception as e:
                # MySQL failed or not running, fall back to SQLite below
                pass
        
        # 2. Seamless SQLite Embedded Fallback (zero configuration on any PC)
        if self.connection is None or self.engine_type != 'sqlite':
            # Store db file alongside app
            app_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(app_dir, "holiday_hacker.db")
            self.connection = SQLiteConnectionWrapper(db_path)
            self.engine_type = 'sqlite'
        return self.connection
            
    def test_connection(self):
        conn = self.get_connection()
        if conn and conn.is_connected():
            return True
        return False
