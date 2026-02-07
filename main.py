from aiogram import Bot, Dispatcher, F, types
import asyncio, random, time, string
import db
from config import BOT_TOKEN
from keyboards import main_menu

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

QUESTIONS = [
    ("Vua đầu tiên nhà Nguyễn?", ["Gia Long","Minh Mạng","Tự Đức","Bảo Đại"], 0),
    ("World Cup 2022 vô địch?", ["Pháp","Argentina","Brazil","Đức"], 1)
]

@dp.message(F.text.startswith("/start"))
async def start(msg: types.Message):
    db.get_user(msg.from_user.id)
    await msg.answer("BOT ONLINE", reply_markup=main_menu())

@dp.callback_query(F.data=="bal")
async def bal(call):
    await call.message.edit_text(f"Số dư: {db.balance(call.from_user.id):,}", reply_markup=main_menu())

@dp.callback_query(F.data=="daily")
async def daily(call):
    u = db.cur.execute("SELECT last_daily FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()
    if time.time() - u[0] < 86400:
        await call.answer("Đã điểm danh hôm nay", show_alert=True)
        return
    reward = random.randint(5000,20000)
    db.add(call.from_user.id, reward)
    db.cur.execute("UPDATE users SET last_daily=? WHERE user_id=?", (time.time(), call.from_user.id))
    db.conn.commit()
    await call.message.edit_text(f"+{reward:,}", reply_markup=main_menu())

@dp.callback_query(F.data=="task")
async def task(call):
    q,a,ok = random.choice(QUESTIONS)
    kb=[]
    for i in range(4):
        kb.append([types.InlineKeyboardButton(text=a[i], callback_data=f"q_{ok}_{i}")])
    await call.message.edit_text(q, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("q_"))
async def quiz(call):
    _,a,b = call.data.split("_")
    if a==b:
        db.add(call.from_user.id,5000)
        await call.message.edit_text("+5000", reply_markup=main_menu())
    else:
        db.sub(call.from_user.id,10000)
        await call.message.edit_text("-10000", reply_markup=main_menu())

@dp.callback_query(F.data=="top")
async def top(call):
    await call.message.edit_text("🏆 TOP DEMO", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
