import asyncio, random, datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
import db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: types.Message):
    await db.add_user(m.from_user.id)
    await m.answer("Nhập TÊN THẬT:")

@dp.message()
async def setup(m: types.Message):
    user = await db.get_user(m.from_user.id)
    if not user[1]:
        await db.set_bank(m.from_user.id, m.text, "", "")
        await m.answer("Nhập TÊN NGÂN HÀNG:")
        return
    if not user[2]:
        await db.set_bank(m.from_user.id, user[1], m.text, "")
        await m.answer("Nhập SỐ TÀI KHOẢN:")
        return
    if not user[3]:
        await db.set_bank(m.from_user.id, user[1], user[2], m.text)
        await m.answer("✅ Hoàn tất! Gõ /menu")
        return

@dp.message(Command("menu"))
async def menu(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Nạp tiền", callback_data="deposit")],
        [InlineKeyboardButton(text="💸 Rút tiền", callback_data="withdraw")],
        [InlineKeyboardButton(text="🎯 Điểm danh", callback_data="daily")],
        [InlineKeyboardButton(text="💼 Số dư", callback_data="balance")]
    ])
    await m.answer("📋 MENU", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "balance")
async def balance(c: types.CallbackQuery):
    user = await db.get_user(c.from_user.id)
    await c.message.answer(f"💰 Số dư: {user[4]} điểm")

@dp.callback_query(lambda c: c.data == "daily")
async def daily(c: types.CallbackQuery):
    user = await db.get_user(c.from_user.id)
    today = str(datetime.date.today())
    if user[6] == today:
        await c.message.answer("❌ Hôm nay bạn đã điểm danh rồi")
        return
    p = random.randint(20,100)
    await db.add_points(c.from_user.id, p)
    async with __import__("aiosqlite").connect("data.db") as dbs:
        await dbs.execute("UPDATE users SET last_daily=? WHERE tg_id=?", (today, c.from_user.id))
        await dbs.commit()
    await c.message.answer(f"🎁 Điểm danh: +{p} điểm")

@dp.callback_query(lambda c: c.data == "deposit")
async def deposit(c: types.CallbackQuery):
    await c.message.answer("📸 Gửi ảnh bill nạp ≥50 điểm")

@dp.message(lambda m: m.photo)
async def auto_deposit(m: types.Message):
    await asyncio.sleep(5)
    await db.add_points(m.from_user.id, 50)
    await m.answer("✅ Nạp thành công +50 điểm")

@dp.callback_query(lambda c: c.data == "withdraw")
async def withdraw(c: types.CallbackQuery):
    user = await db.get_user(c.from_user.id)
    if user[4] < 10:
        await c.message.answer("❌ Tối thiểu 10 điểm")
        return
    if user[5] >= 100:
        await c.message.answer("❌ Hôm nay bạn đã rút tối đa")
        return
    await db.sub_points(c.from_user.id, 10)
    await db.set_withdraw_today(c.from_user.id, user[5] + 10)
    await c.message.answer("✅ Rút thành công 10 điểm")

async def main():
    await db.init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
