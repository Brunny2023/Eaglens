import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH
import os

def get_db_connection():
    # Check if we are in GitHub Actions and have a persistent DB URL (optional future-proofing)
    # For now, we use the local SQLite file but ensure it's handled correctly
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table (updated for visitor tracking and persistent access)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            invite_code TEXT,
            is_verified BOOLEAN DEFAULT 0,
            is_subscribed BOOLEAN DEFAULT 0,
            expiry_date TEXT,
            trial_used BOOLEAN DEFAULT 0,
            first_seen TEXT
        )
    ''')
    
    # Create invite_codes table (updated for multi-use)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_codes (
            code TEXT PRIMARY KEY,
            max_uses INTEGER DEFAULT 1,
            current_uses INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Create a table to track which user used which code
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            telegram_id INTEGER,
            used_at TEXT,
            FOREIGN KEY(code) REFERENCES invite_codes(code)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_invite_code(code, max_uses=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO invite_codes (code, max_uses, current_uses, created_at) VALUES (?, ?, 0, ?)', 
            (code, max_uses, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def log_visitor(telegram_id, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, username, first_seen) 
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET username = excluded.username
    ''', (telegram_id, username, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def verify_invite_code(telegram_id, code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user is already verified
    cursor.execute('SELECT is_verified FROM users WHERE telegram_id = ?', (telegram_id,))
    res = cursor.fetchone()
    if res and res[0]:
        conn.close()
        return True

    # Check if code exists and has remaining uses
    cursor.execute('SELECT max_uses, current_uses FROM invite_codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    
    if result:
        max_uses, current_uses = result
        if current_uses < max_uses:
            # Record usage
            cursor.execute(
                'INSERT INTO invite_usage (code, telegram_id, used_at) VALUES (?, ?, ?)',
                (code, telegram_id, datetime.now().isoformat())
            )
            # Increment current uses
            cursor.execute('UPDATE invite_codes SET current_uses = current_uses + 1 WHERE code = ?', (code,))
            # Mark user as verified and record code
            cursor.execute('''
                UPDATE users 
                SET is_verified = 1, invite_code = ? 
                WHERE telegram_id = ?
            ''', (code, telegram_id))
            conn.commit()
            conn.close()
            return True
    
    conn.close()
    return False
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def check_user_access(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_verified, is_subscribed, expiry_date FROM users WHERE telegram_id = ?', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False, "not_registered"
    
    is_verified, is_subscribed, expiry_date = result
    if is_verified == 0:
        return False, "not_verified"
    
    if not is_subscribed:
        return False, "not_subscribed" 
    if expiry_date and datetime.fromisoformat(expiry_date) < datetime.now():
        return False, "expired"
    
    return True, "active"

if __name__ == "__main__":
    init_db()
    # Add a test invite code
    add_invite_code("EAGLE-2026-TEST")
    print("Database initialized and test invite code added.")
