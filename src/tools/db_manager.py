import sqlite3
import os

# Load database path from environment variable or configuration file
DB_PATH = os.getenv('DB_PATH', '/Users/span/Projects/ScrapyProjects/LoLFandomWiki/db/service.db')

class SingletonDatabaseConnection:
    _instance = None

    def __new__(cls, db_path=DB_PATH):
        if cls._instance is None:
            cls._instance = super(SingletonDatabaseConnection, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.conn = sqlite3.connect(db_path)
            cls._instance.cursor = cls._instance.conn.cursor()
        return cls._instance

    def query(self, query: str, params: tuple):
        try:
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            results = self.cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def query_one(self, query: str, params: tuple):
        try:
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            result = self.cursor.fetchone()
            return dict(zip(columns, result)) if result else {}
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            SingletonDatabaseConnection._instance = None