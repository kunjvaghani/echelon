import os
import pymongo
from dotenv import load_dotenv
import datetime
import dns.resolver

# Load env variables
load_dotenv()

# --- DNS FIX FOR VPN/RESTRICTED NETWORKS ---
# Force dnspython to use Google DNS instead of failing local DNS
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4'] 

class Database:
    def __init__(self):
        # MongoDB Connection
        self.uri = os.getenv("MONGODB_URI")
        if not self.uri:
             raise ValueError("MONGODB_URI not found in .env file")
        
        self.client = pymongo.MongoClient(self.uri)
        self.db = self.client["kyc_fraud_detection"]
        self.users = self.db["users"]
        self.kyc_attempts = self.db["kyc_attempts"]
        
        # Create Indexes for uniqueness and speed
        self.users.create_index("email", unique=True)

    def create_user(self, user_data):
        """
        Inserts a new user into MongoDB.
        user_data: dict containing full_name, email, dob, phone, password, 
                   face_embedding (binary), behavior_baseline, role, created_at
        """
        user_data['created_at'] = datetime.datetime.now()
        try:
            self.users.insert_one(user_data)
            return True
        except pymongo.errors.DuplicateKeyError:
            return False

    def get_user(self, email):
        """
        Fetches user by email (username).
        Returns: dict or None
        """
        return self.users.find_one({"email": email})

    def verify_user(self, email, password):
        """
        Verifies login credentials.
        Returns: dict user object or None
        """
        # In production, use hashed passwords!
        return self.users.find_one({"email": email, "password": password})
    
    def get_all_users(self):
        """Returns list of all users for Admin Dashboard"""
        return list(self.users.find({}, {"_id": 0, "face_embedding": 0})) # Exclude binary data for display

    def log_kyc_attempt(self, attempt_data):
        """
        Logs a verification attempt.
        attempt_data: dict
        """
        attempt_data['timestamp'] = datetime.datetime.now()
        self.kyc_attempts.insert_one(attempt_data)

    def get_all_logs(self):
        return list(self.kyc_attempts.find({}, {"_id": 0}))

    def close(self):
        self.client.close()


# ==============================================================================
# 🚫 LEGACY SQLITE IMPLEMENTATION (COMMENTED OUT)
# ==============================================================================
# import sqlite3
# from src.config import DB_PATH
# 
# class Database:
#     def __init__(self):
#         self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#         self.create_tables()
# 
#     def create_tables(self):
#         cursor = self.conn.cursor()
#         
#         # User Table Update: Dropping old table for Schema Migration (Dev Mode)
#         # In production, use ALTER TABLE or migration scripts.
#         try:
#             # Check if 'phone' column exists, if not, we drop/recreate
#             cursor.execute("SELECT phone FROM users LIMIT 1")
#         except sqlite3.OperationalError:
#             # Column doesn't exist, so we drop the table to recreate it with new schema
#             cursor.execute("DROP TABLE IF EXISTS users")
#         
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT UNIQUE,
#                 full_name TEXT,
#                 dob TEXT,
#                 phone TEXT,
#                 password TEXT,
#                 face_embedding BLOB,
#                 behavior_baseline TEXT,
#                 role TEXT DEFAULT 'user',
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#         
#         # KYC Attempts Table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS kyc_attempts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER,
#                 doc_score REAL,
#                 face_score REAL,
#                 behavior_score REAL,
#                 final_decision TEXT,
#                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY(user_id) REFERENCES users(id)
#             )
#         ''')
#         
#         # Create a default Admin user if not exists
#         try:
#             cursor.execute("INSERT INTO users (username, full_name, password, role) VALUES (?, ?, ?, ?)", 
#                           ("admin@kyc.com", "System Admin", "admin123", "admin"))
#         except sqlite3.IntegrityError:
#             pass # Admin already exists
# 
#         self.conn.commit()
# 
#     def get_user(self, username):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT * FROM users WHERE username=?", (username,))
#         return cursor.fetchone()
# 
#     def verify_user(self, username, password):
#         """
#         Verifies login credentials.
#         Returns user data tuple if valid, else None.
#         """
#         cursor = self.conn.cursor()
#         # In production, use hashed passwords!
#         cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#         return cursor.fetchone()
# 
#     def close(self):
#         self.conn.close()
