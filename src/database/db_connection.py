import sqlite3
import os
from src.config import DB_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # User Table Update: Dropping old table for Schema Migration (Dev Mode)
        # In production, use ALTER TABLE or migration scripts.
        try:
            # Check if 'phone' column exists, if not, we drop/recreate
            cursor.execute("SELECT phone FROM users LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, so we drop the table to recreate it with new schema
            cursor.execute("DROP TABLE IF EXISTS users")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                full_name TEXT,
                dob TEXT,
                phone TEXT,
                password TEXT,
                face_embedding BLOB,
                behavior_baseline TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # KYC Attempts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kyc_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                doc_score REAL,
                face_score REAL,
                behavior_score REAL,
                final_decision TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Create a default Admin user if not exists
        try:
            cursor.execute("INSERT INTO users (username, full_name, password, role) VALUES (?, ?, ?, ?)", 
                          ("admin@kyc.com", "System Admin", "admin123", "admin"))
        except sqlite3.IntegrityError:
            pass # Admin already exists

        self.conn.commit()

    def get_user(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return cursor.fetchone()

    def verify_user(self, username, password):
        """
        Verifies login credentials.
        Returns user data tuple if valid, else None.
        """
        cursor = self.conn.cursor()
        # In production, use hashed passwords!
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()

    def close(self):
        self.conn.close()
