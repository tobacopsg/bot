import sqlite3, time

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    ref_by INTEGER DEFAULT 0,
    ref_valid INTEGER DEFAULT 0,
    deposit_count INTEGER DEFAULT 0,
    weekly_deposit INTEGER DEFAULT 0,
    last_daily INTEGER DEFAULT 0,
    newbie_claimed INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS deposits(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS withdrawals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS giftcodes(
    code TEXT PRIMARY KEY,
    used INTEGER DEFAULT 0
)
""")

conn.commit()

def get_user(uid):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    u = cur.fetchone()
    if not u:
        cur.execute("INSERT INTO users(user_id) VALUES(?)", (uid,))
        conn.commit()
    return u

def add_balance(uid, amt):
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amt, uid))
    conn.commit()

def sub_balance(uid, amt):
    cur.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amt, uid))
    conn.commit()

def balance(uid):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    return cur.fetchone()[0]
