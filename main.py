from aiogram import Bot, Dispatcher, F, types
import asyncio, random, time, string
import db
from config import BOT_TOKEN, ADMIN_ID
from keyboards import main_menu

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

QUESTIONS = [
    ("Vua đầu tiên nhà Nguyễn?", ["Gia Long","Minh Mạng","Tự Đức","Bảo Đại"], 0),
    ("World Cup 2022 vô địch?", ["Pháp","Argentina","Brazil","Đức"], 1)
]

# START
@dp.message(F.text.startswith("/start"))
async def start(msg: types.Message):
    db.get_user(msg.from_user.id)
    await msg.answer("🤖 BOT GAME KIẾM XU", reply_markup=main_menu())

# SỐ DƯ
@dp.callback_query(F.data=="bal")
async def bal(call):
    await call.message.edit_text(f"💰 Số dư: {db.balance(call.from_user.id):,} Xu", reply_markup=main_menu())

# ĐIỂM DANH
@dp.callback_query(F.data=="daily")
async def daily(call):
    u = db.cur.execute("SELECT last_daily FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()
    if time.time() - u[0] < 86400:
        await call.answer("Bạn đã điểm danh hôm nay!", show_alert=True)
        return
    reward = random.randint(5000,20000)
    db.add(call.from_user.id, reward)
    db.cur.execute("UPDATE users SET last_daily=? WHERE user_id=?", (time.time(), call.from_user.id))
    db.conn.commit()
    await call.message.edit_text(f"🎉 +{reward:,} Xu", reply_markup=main_menu())

# MỜI BẠN
@dp.callback_query(F.data=="ref")
async def ref(call):
    link = f"https://t.me/{(await bot.me()).username}?start={call.from_user.id}"
    await call.message.edit_text(f"👥 LINK MỜI BẠN\n\n{link}", reply_markup=main_menu())

# NHIỆM VỤ
@dp.callback_query(F.data=="task")
async def task(call):
    q,ans,ok = random.choice(QUESTIONS)
    kb = []
    for i in range(4):
        kb.append([types.InlineKeyboardButton(text=ans[i], callback_data=f"q_{ok}_{i}")])
    await call.message.edit_text(f"🧠 {q}\n⏳ 20s", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("q_"))
async def quiz(call):
    _,a,b = call.data.split("_")
    if a==b:
        db.add(call.from_user.id,5000)
        await call.message.edit_text("✅ Đúng +5k", reply_markup=main_menu())
    else:
        db.sub(call.from_user.id,10000)
        await call.message.edit_text("❌ Sai -10k", reply_markup=main_menu())

# ĐUA TOP
@dp.callback_query(F.data=="top")
async def top(call):
    names = ["Nguyễn Văn A","Trần Minh B","Lê Quốc C","Phạm Gia D","Hải Hoàng"]
    text="🏆 BXH\n\n"
    for i,n in enumerate(names,1):
        text+=f"{['🥇','🥈','🥉','🏅','🏅'][i-1]} {n} - {random.randint(5,20)}tr\n"
    text+=f"\n👤 Bạn: #{random.randint(1200,3000)} - {db.balance(call.from_user.id):,}"
    await call.message.edit_text(text, reply_markup=main_menu())

# SỰ KIỆN
@dp.callback_query(F.data=="event")
async def event(call):
    await call.message.edit_text(
        "🎁 SỰ KIỆN\n\n"
        "🔥 Nạp lần 1 +100%\n"
        "⚡ Nạp lần 2 +50%\n"
        "✨ Nạp lần 3 +25%\n\n"
        "🎉 Chủ nhật +50%\n"
        "🎁 Thành viên mới +88k\n"
        "🎟 Giftcode +58k\n",
        reply_markup=main_menu()
    )

# GIFTCODE
@dp.message()
async def gift(msg: types.Message):
    code = msg.text.strip()
    r = db.cur.execute("SELECT used FROM giftcodes WHERE code=?", (code,)).fetchone()
    if not r: return
    if r[0]==1:
        await msg.answer("❌ Code đã dùng")
        return
    db.cur.execute("UPDATE giftcodes SET used=1 WHERE code=?", (code,))
    db.add(msg.from_user.id,58000)
    db.conn.commit()
    await msg.answer("🎁 +58,000 Xu", reply_markup=main_menu())

# AUTO TẠO 30 GIFTCODE / NGÀY
async def auto_gift():
    while True:
        db.cur.execute("DELETE FROM giftcodes")
        for _ in range(30):
            c=''.join(random.choices(string.ascii_uppercase+string.digits,k=8))
            db.cur.execute("INSERT INTO giftcodes(code) VALUES(?)",(c,))
        db.conn.commit()
        await asyncio.sleep(86400)

async def main():
    asyncio.create_task(auto_gift())
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())

