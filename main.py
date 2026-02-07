from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio, random, time, string
from config import BOT_TOKEN, ADMIN_ID
import db
from keyboards import main_menu

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# START
@dp.message(F.text.startswith("/start"))
async def start(msg: types.Message):
    args = msg.text.split()
    db.get_user(msg.from_user.id)
    if len(args) == 2:
        ref = int(args[1])
        if ref != msg.from_user.id:
            db.cur.execute("UPDATE users SET ref_by=? WHERE user_id=?", (ref, msg.from_user.id))
            db.conn.commit()
    await msg.answer("🤖 BOT GAME & KIẾM XU", reply_markup=main_menu())

# SỐ DƯ
@dp.callback_query(F.data=="bal")
async def bal(call):
    await call.message.edit_text(f"💰 Số dư: {db.balance(call.from_user.id):,} Xu", reply_markup=main_menu())

# ĐIỂM DANH
@dp.callback_query(F.data=="daily")
async def daily(call):
    u = db.get_user(call.from_user.id)
    if time.time() - u[5] < 86400:
        await call.answer("Bạn đã điểm danh hôm nay!", show_alert=True)
        return
    reward = random.randint(5000,20000)
    db.add_balance(call.from_user.id, reward)
    db.cur.execute("UPDATE users SET last_daily=? WHERE user_id=?", (time.time(), call.from_user.id))
    db.conn.commit()
    await call.message.edit_text(f"🎉 Điểm danh thành công\n+{reward:,} Xu", reply_markup=main_menu())

# MỜI BẠN
@dp.callback_query(F.data=="ref")
async def ref(call):
    link = f"https://t.me/{(await bot.me()).username}?start={call.from_user.id}"
    await call.message.edit_text(
        f"👥 MỜI BẠN\n\nLink:\n{link}\n\n🎁 99k/người khi bạn được mời nạp ≥50k\n⛔ Tối đa 3/ngày",
        reply_markup=main_menu()
    )

# QUIZ
QUESTIONS = [
    ("Ai là vua đầu tiên nhà Nguyễn?", ["Gia Long","Minh Mạng","Tự Đức","Bảo Đại"], 0),
    ("World Cup 2022 vô địch?", ["Pháp","Argentina","Brazil","Đức"], 1)
]

@dp.callback_query(F.data=="task")
async def task(call):
    q,a,ans = random.choice(QUESTIONS)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=a[0], callback_data=f"q_{ans}_0"),
         InlineKeyboardButton(text=a[1], callback_data=f"q_{ans}_1")],
        [InlineKeyboardButton(text=a[2], callback_data=f"q_{ans}_2"),
         InlineKeyboardButton(text=a[3], callback_data=f"q_{ans}_3")]
    ])
    await call.message.edit_text(f"🧠 {q}\n⏳ 20 giây", reply_markup=kb)

@dp.callback_query(F.data.startswith("q_"))
async def quiz(call):
    _,ans,choose = call.data.split("_")
    if ans == choose:
        db.add_balance(call.from_user.id, 5000)
        await call.message.edit_text("✅ Đúng! +5,000 Xu", reply_markup=main_menu())
    else:
        db.sub_balance(call.from_user.id, 10000)
        await call.message.edit_text("❌ Sai! -10,000 Xu", reply_markup=main_menu())

# ĐUA TOP
@dp.callback_query(F.data=="top")
async def top(call):
    names = ["Nguyễn Minh Quân","Trần Hoàng Long","Phạm Gia Huy","Lê Tuấn Kiệt","Hải Hoàng"]
    txt="🏆 BXH TUẦN\n\n"
    for i,n in enumerate(names,1):
        txt+=f"{['🥇','🥈','🥉','🏅','🏅'][i-1]} {n} - {random.randint(5,15)}tr\n"
    txt+=f"\n👤 Bạn: #{random.randint(1200,3000)} - {db.balance(call.from_user.id):,}"
    await call.message.edit_text(txt, reply_markup=main_menu())

# GIFTCODE
@dp.message()
async def gift(msg: types.Message):
    code = msg.text.strip()
    db.cur.execute("SELECT used FROM giftcodes WHERE code=?", (code,))
    r = db.cur.fetchone()
    if not r: return
    if r[0]==1:
        await msg.answer("❌ Code đã dùng!"); return
    db.cur.execute("UPDATE giftcodes SET used=1 WHERE code=?", (code,))
    db.add_balance(msg.from_user.id,58000)
    db.conn.commit()
    await msg.answer("🎁 +58,000 Xu", reply_markup=main_menu())

# AUTO 30 GIFTCODE / NGÀY
async def auto_code():
    while True:
        db.cur.execute("DELETE FROM giftcodes")
        for _ in range(30):
            c=''.join(random.choices(string.ascii_uppercase+string.digits,k=8))
            db.cur.execute("INSERT INTO giftcodes(code) VALUES(?)",(c,))
        db.conn.commit()
        await bot.send_message(ADMIN_ID,"🎟 Đã tạo 30 giftcode hôm nay")
        await asyncio.sleep(86400)

async def main():
    asyncio.create_task(auto_code())
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())

