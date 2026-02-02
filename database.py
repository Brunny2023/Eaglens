import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH

import os

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            invite_code TEXT,
            is_subscribed BOOLEAN DEFAULT 0,
            expiry_date TEXT,
            trial_used BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create invite_codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_codes (
            code TEXT PRIMARY KEY,
            is_used BOOLEAN DEFAULT 0,
            used_by INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def add_invite_code(code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO invite_codes (code) VALUES (?)', (code,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def verify_invite_code(telegram_id, code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if code exists and is not used
    cursor.execute('SELECT is_used FROM invite_codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    
    if result and not result[0]:
        # Mark code as used
        cursor.execute('UPDATE invite_codes SET is_used = 1, used_by = ? WHERE code = ?', (telegram_id, code))
        # Add user to users table
        cursor.execute('INSERT OR IGNORE INTO users (telegram_id, invite_code) VALUES (?, ?)', (telegram_id, code))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def check_user_access(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT is_subscribed, expiry_date FROM users WHERE telegram_id = ?', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False, "not_registered"
    
    is_subscribed, expiry_date = result
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
