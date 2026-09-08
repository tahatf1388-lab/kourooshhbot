import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

# توکن ربات خودت را اینجا بگذار
TOKEN = "8517015536:AAGoPOUXHAJkwVhCD813cTpJWSnqcWd8jBQ"

router = Router()

# منوی اصلی (دو کلید پایین صفحه)
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 آپلود فایل و دریافت لینک"), KeyboardButton(text="👤 حساب کاربری")]
    ],
    resize_keyboard=True
)

# منوی زمان آپلود (فقط دکمه بازگشت)
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)

# منوی پس از دریافت فایل
file_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 دریافت لینک دانلود")],
        [KeyboardButton(text="🔙 بازگشت به صفحه اصلی")]
    ],
    resize_keyboard=True
)

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"سلام {message.from_user.first_name}! به ربات خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu_keyboard
    )

@router.message(F.text == "📁 آپلود فایل و دریافت لینک")
async def upload_menu(message: Message) -> None:
    await message.answer(
        "📂 فایل خود را آپلود کنید با هر فرمت دلخواهی که دارین! 📎✨",
        reply_markup=back_keyboard
    )

@router.message(F.text == "🔙 بازگشت" or F.text == "🔙 بازگشت به صفحه اصلی")
async def back_to_home(message: Message) -> None:
    await message.answer(
        "به منوی اصلی برگشتید:",
        reply_markup=main_menu_keyboard
    )

@router.message(F.text == "📥 دریافت لینک دانلود")
async def get_download_link(message: Message) -> None:
    # اینجا می‌توانی بعداً لینک واقعی تولید شده را بدهی
    await message.answer(
        "🔗 لینک دانلود فایل شما:\nhttps://t.me/example_download_link",
        reply_markup=main_menu_keyboard
    )

@router.message(F.document | F.video | F.audio | F.photo)
async def handle_files(message: Message) -> None:
    await message.answer(
        "✅ فایل با موفقیت دریافت شد.",
        reply_markup=file_received_keyboard
    )

async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
