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
    conn = sqlite3.connect(DB_PATH)
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

def verify_invite_code(telegram_id, code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user already used a code
    cursor.execute('SELECT 1 FROM invite_usage WHERE telegram_id = ?', (telegram_id,))
    if cursor.fetchone():
        conn.close()
        return True # Already verified

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
