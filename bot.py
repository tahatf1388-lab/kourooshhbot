import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8517015536:AAGoPOUXHAJkwVhCD813cTpJWSnqcWd8jBQ"

# روی سرور ابری نیازی به پروکسی نیست و مستقیماً متصل می‌شود
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📤 آپلود فایل و دریافت لینک", callback_data="upload_file"),
                types.InlineKeyboardButton(text="حساب کاربری 👤", callback_data="user_account")
            ]
        ]
    )
    
    await message.answer(
        f"سلام {message.from_user.first_name}! به ربات خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("ربات روشن شد و در حال دریافت پیام است...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
