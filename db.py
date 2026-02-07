import aiosqlite

DB = "data.db"

async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            tg_id INTEGER PRIMARY KEY,
            name TEXT,
            bank TEXT,
            bank_acc TEXT,
            points INTEGER DEFAULT 0,
            today_withdraw INTEGER DEFAULT 0,
            last_daily TEXT
        )
        """)
        await db.commit()

async def get_user(tg_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
        return await cur.fetchone()

async def add_user(tg_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users(tg_id) VALUES(?)", (tg_id,))
        await db.commit()

async def set_bank(tg_id, name, bank, acc):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET name=?, bank=?, bank_acc=? WHERE tg_id=?",
                         (name, bank, acc, tg_id))
        await db.commit()

async def add_points(tg_id, p):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE tg_id=?", (p, tg_id))
        await db.commit()

async def sub_points(tg_id, p):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET points = points - ? WHERE tg_id=?", (p, tg_id))
        await db.commit()

async def set_withdraw_today(tg_id, val):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET today_withdraw=? WHERE tg_id=?", (val, tg_id))
        await db.commit()
