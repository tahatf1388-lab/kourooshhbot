import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# توکن ربات خودت
TOKEN = "8517015536:AAGoPOUXHAJkWVhCD813cTpJWSnqcWd8jBQ"
BOT_USERNAME = "kourooshh_bot"  # آیدی یوزرنیم رباتت بدون @

router = Router()

# موقتاً برای ذخیره آخرین فایل دریافتی کاربر (در حافظه)
user_last_file = {}

# منوی اصلی
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 آپلود فایل و دریافت لینک"), KeyboardButton(text="👤 حساب کاربری")]
    ],
    resize_keyboard=True
)

# منوی بازگشت
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
    # بررسی اینکه آیا کاربر با لینک مخصوص فایل وارد شده یا خیر (Deep Linking)
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("file_"):
        file_id = args[1].replace("file_", "")
        await message.answer("🎁 این هم فایل درخواستی شما:")
        await message.answer_document(document=file_id)
        await message.answer(
            "به منوی اصلی برگشتید:",
            reply_markup=main_menu_keyboard
        )
        return

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

@router.message(F.text.in_(["🔙 بازگشت", "🔙 بازگشت به صفحه اصلی"]))
async def back_to_home(message: Message) -> None:
    await message.answer(
        "به منوی اصلی برگشتید:",
        reply_markup=main_menu_keyboard
    )

@router.message(F.text == "📥 دریافت لینک دانلود")
async def get_download_link(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_last_file:
        file_id = user_last_file[user_id]
        share_link = f"https://t.me/{BOT_USERNAME}?start=file_{file_id}"
        await message.answer(
            f"🔗 لینک اختصاصی دانلود فایل شما:\n{share_link}\n\nهرکس روی این لینک کلیک کند، ربات مستقیماً فایل را به او تحویل می‌دهد!",
            reply_markup=main_menu_keyboard
        )
    else:
        await message.answer(
            "⚠️ ابتدا یک فایل ارسال کنید تا بتوانیم لینک آن را بسازیم.",
            reply_markup=main_menu_keyboard
        )

@router.message(F.document | F.video | F.audio | F.photo)
async def handle_files(message: Message) -> None:
    # ذخیره مشخصات فایل بر اساس آیدی کاربر
    user_id = message.from_user.id
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    else:
        return

    user_last_file[user_id] = file_id
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
