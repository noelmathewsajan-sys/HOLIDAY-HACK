import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def get_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host='localhost',
                    database='holiday_hacker',
                    user='root',
                    password=''
                )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
            
    def test_connection(self):
        conn = self.get_connection()
        if conn and conn.is_connected():
            return True
        return False
