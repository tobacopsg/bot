from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Nạp tiền", callback_data="nap"),
         InlineKeyboardButton(text="🏦 Rút tiền", callback_data="rut")],
        [InlineKeyboardButton(text="📅 Điểm danh", callback_data="daily"),
         InlineKeyboardButton(text="👥 Mời bạn", callback_data="ref")],
        [InlineKeyboardButton(text="🎯 Nhiệm vụ", callback_data="task"),
         InlineKeyboardButton(text="🏆 Đua top", callback_data="top")],
        [InlineKeyboardButton(text="🎁 Sự kiện", callback_data="event"),
         InlineKeyboardButton(text="💰 Số dư", callback_data="bal")],
        [InlineKeyboardButton(text="⚙️ Cài đặt", callback_data="setting")]
    ])
