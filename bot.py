import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import aiohttp

TOKEN = "8844658209:AAH41cGWIdMiSLQq8PO5VNU_qds7vWJpmmE"

router = Router()

# وضعیت‌های ربات برای ثبت نام فایل و لینک
class UploadStates(StatesGroup):
    waiting_for_file_name = State()
    waiting_for_new_link = State()

# دیتابیس‌ها
user_files_db = {}
user_temp_file = {}
shared_files_db = {}

# دیتابیس موقت برای لینک‌های کاربران (user_id -> لیست لینک‌ها یا دیکشنری)
user_links_db = {}
user_temp_link = {}

# --- کیبوردها ---

# منوی اصلی
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 خدمات لینک"), KeyboardButton(text="🗂️ مدیریت فایل‌ها")],
        [KeyboardButton(text="👤 حساب کاربری")]
    ],
    resize_keyboard=True,
    input_field_placeholder="لطفاً یکی از گزینه‌های زیر را انتخاب کنید... 👇"
)

# منوی بخش خدمات لینک (طبق درخواست: لینک‌های من سمت چپ، افزودن لینک جدید سمت راست)
link_services_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ افزودن لینک جدید"), KeyboardButton(text="📋 لینک‌های من")],
        [KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
    ],
    resize_keyboard=True
)

# منوی مدیریت فایل‌ها (زیرشاخه منوی اصلی)
file_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 آپلود فایل و دریافت لینک"), KeyboardButton(text="📂 فایل‌های من")],
        [KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
    ],
    resize_keyboard=True
)

# منوی زمان آپلود یا افزودن لینک (فقط دکمه بازگشت)
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)

# منوی پس از دریافت فایل و نام‌گذاری
file_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 دریافت لینک دانلود")],
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("file_"):
        file_key = args[1].replace("file_", "")
        if file_key in shared_files_db:
            file_data = shared_files_db[file_key]
            if file_data.get("deleted", False):
                await message.answer("⚠️ متأسفانه فایل مورد نظر توسط کاربر حذف شده است. ❌")
            else:
                await message.answer("🎁 این هم فایل درخواستی شما: 👇")
                if file_data["type"] == "document":
                    await message.answer_document(file_data["file_id"])
                elif file_data["type"] == "video":
                    await message.answer_video(file_data["file_id"])
                elif file_data["type"] == "audio":
                    await message.answer_audio(file_data["file_id"])
                elif file_data["type"] == "photo":
                    await message.answer_photo(file_data["file_id"])
        else:
            await message.answer("⚠️ متأسفانه فایل مورد نظر پیدا نشد یا منقضی شده است. ❌")

        await message.answer(
            "🏠 به منوی اصلی برگشتید: 👇",
            reply_markup=main_menu_keyboard
        )
        return

    await message.answer(
        f"سلام {message.from_user.first_name}! 👋 به ربات مگابات خوش آمدید. 🤖\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید: 👇",
        reply_markup=main_menu_keyboard
    )


@router.message(F.text == "🗂️ مدیریت فایل‌ها")
async def management_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🛠️ به بخش مدیریت فایل‌ها خوش آمدید. 📂\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید: 👇",
        reply_markup=file_management_keyboard
    )


@router.message(F.text == "📁 آپلود فایل و دریافت لینک")
async def upload_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "📂 لطفاً فایل خود را با هر فرمت دلخواهی که دارید ارسال کنید! 📎✨",
        reply_markup=back_keyboard
    )


# --- بخش خدمات لینک (به همراه دو کلید درخواستی) ---

@router.message(F.text == "🔗 خدمات لینک")
async def link_services_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🔗 به بخش خدمات لینک و کوتاه‌کننده خوش آمدید. 🌐\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید: 👇",
        reply_markup=link_services_keyboard
    )


@router.message(F.text == "➕ افزودن لینک جدید")
async def add_new_link_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(UploadStates.waiting_for_new_link)
    await message.answer(
        "🔗 لطفاً لینک طولانی خود را ارسال کنید تا آن را کوتاه کنم و در لیست شما ذخیره کنم: 📝✨",
        reply_markup=back_keyboard
    )


async def shorten_url(long_url: str) -> str:
    api_url = f"https://is.gd/create.php?format=simple&url={long_url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                short_url = await response.text()
                return short_url.strip()
            else:
                return None


@router.message(UploadStates.waiting_for_new_link, F.text)
async def process_new_link(message: Message, state: FSMContext) -> None:
    user_link = message.text.strip()
    
    if user_link == "🔙 بازگشت":
        await state.clear()
        await message.answer(
            "🔙 به بخش خدمات لینک برگشتید: 👇",
            reply_markup=link_services_keyboard
        )
        return

    if not (user_link.startswith("http://") or user_link.startswith("https://") or user_link.startswith("www.")):
        await message.answer("⚠️ لطفاً یک لینک معتبر (شروع شده با http یا https) ارسال کنید: ❌")
        return

    waiting_msg = await message.answer("⏳ در حال کوتاه کردن لینک... 🔄")
    short_result = await shorten_url(user_link)

    if short_result and short_result.startswith("http"):
        user_id = message.from_user.id
        if user_id not in user_links_db:
            user_links_db[user_id] = []
        
        # ذخیره لینک کوتاه شده در دیتابیس کاربر
        link_item = {"long": user_link, "short": short_result}
        user_links_db[user_id].append(link_item)

        await state.clear()
        await waiting_msg.edit_text(
            f"🎉 لینک شما با موفقیت کوتاه و ذخیره شد! ✅\n\n🔗 لینک کوتاه شده:\n`{short_result}`\n\n✨ می‌توانید از این لینک در پیامک یا هر جای دیگری استفاده کنید.",
            parse_mode="Markdown"
        )
        await message.answer(
            "🔙 بازگشت به بخش خدمات لینک: 👇",
            reply_markup=link_services_keyboard
        )
    else:
        await waiting_msg.edit_text("❌ خطا در کوتاه‌کردن لینک. لطفاً دوباره تلاش کنید.")


@router.message(F.text == "📋 لینک‌های من")
async def list_user_links(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    if user_id not in user_links_db or not user_links_db[user_id]:
        await message.answer(
            "📭 شما هنوز هیچ لینکی در ربات ذخیره نکرده‌اید. ⚠️",
            reply_markup=link_services_keyboard
        )
        return

    links_text = "📋 لیست لینک‌های کوتاه شده‌ی شما: 👇\n\n"
    for idx, item in enumerate(user_links_db[user_id], 1):
        links_text += f"{idx}. اصلی: {item['long']}\n   کوتاه: `{item['short']}`\n\n"

    await message.answer(
        links_text,
        parse_mode="Markdown",
        reply_markup=link_services_keyboard
    )


@router.message(F.text == "👤 حساب کاربری")
async def user_account_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👤 **اطلاعات حساب کاربری شما:** 📊\n\n✨ وضعیت اشتراک: عادی 🌟\n🎁 موجودی ترافیک: رایگان 🚀",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard
    )


@router.message(F.text == "🔙 بازگشت")
async def back_action(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🔙 به بخش مدیریت فایل‌ها برگشتید: 👇",
        reply_markup=file_management_keyboard
    )


@router.message(F.text == "🔙 بازگشت به منوی اصلی")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🏠 به منوی اصلی برگشتید: 👇",
        reply_markup=main_menu_keyboard
    )


# دریافت فایل از کاربر
@router.message(F.document | F.video | F.audio | F.photo)
async def handle_files(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    else:
        return

    user_temp_file[user_id] = {
        "file_id": file_id,
        "type": file_type
    }

    await state.set_state(UploadStates.waiting_for_file_name)
    await message.answer(
        "✅ فایل با موفقیت دریافت شد. 📁\n\n✍️ لطفاً یک نام (فقط به صورت متن) برای این فایل انتخاب و ارسال کنید: 👇",
        reply_markup=back_keyboard
    )


@router.message(UploadStates.waiting_for_file_name, F.text)
async def save_file_name(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    file_name = message.text.strip()

    if file_name == "🔙 بازگشت":
        await state.clear()
        await message.answer(
            "🔙 به بخش مدیریت فایل‌ها برگشتید: 👇",
            reply_markup=file_management_keyboard
        )
        return

    if user_id not in user_temp_file:
        await message.answer("⚠️ خطایی رخ داد. لطفاً دوباره فایل خود را ارسال کنید. ❌", reply_markup=file_management_keyboard)
        await state.clear()
        return

    file_info = user_temp_file.pop(user_id)
    file_key = f"{user_id}_{len(shared_files_db) + 1}"

    file_data = {
        "file_id": file_info["file_id"],
        "type": file_info["type"],
        "name": file_name,
        "deleted": False
    }

    shared_files_db[file_key] = file_data

    if user_id not in user_files_db:
        user_files_db[user_id] = {}
    user_files_db[user_id][file_key] = file_data

    await state.update_data(current_file_key=file_key)
    await state.set_state(None)

    await message.answer(
        f"🎉 نام فایل با موفقیت ثبت شد: <b>{file_name}</b> ✅\n\nحالا روی دکمه‌ی زیر کلیک کنید تا لینک دانلود را دریافت کنید: 👇",
        reply_markup=file_received_keyboard
    )


@router.message(UploadStates.waiting_for_file_name)
async def invalid_file_name(message: Message) -> None:
    await message.answer("⚠️ لطفاً نام فایل را **فقط به صورت متن** ارسال کنید: ❌")


@router.message(F.text == "📥 دریافت لینک دانلود")
async def get_download_link(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    file_key = data.get("current_file_key")

    if file_key and file_key in shared_files_db and not shared_files_db[file_key]["deleted"]:
        bot_info = await message.bot.get_me()
        share_link = f"https://t.me/{bot_info.username}?start=file_{file_key}"
        file_name = shared_files_db[file_key]["name"]

        await message.answer(
            f"🔗 لینک اختصاصی دانلود فایل (<b>{file_name}</b>): 📥\n{share_link}\n\n✨ هرکس روی این لینک کلیک کند، ربات مستقیماً فایل را به او تحویل می‌دهد! 🚀",
            reply_markup=file_management_keyboard
        )
        await state.clear()
    else:
        await message.answer(
            "⚠️ ابتدا یک فایل جدید ارسال کنید و برای آن نام انتخاب کنید. ❌",
            reply_markup=file_management_keyboard
        )


@router.message(F.text == "📂 فایل‌های من")
async def list_user_files(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    if user_id not in user_files_db or not user_files_db[user_id]:
        await message.answer(
            "📭 شما هنوز هیچ فایلی در ربات آپلود نکرده‌اید. ⚠️",
            reply_markup=file_management_keyboard
        )
        return

    inline_keyboard = []
    for file_key, f_data in user_files_db[user_id].items():
        if f_data["deleted"]:
            continue
        btn_view = InlineKeyboardButton(text=f"📄 {f_data['name']}", callback_data=f"view_{file_key}")
        btn_delete = InlineKeyboardButton(text="🗑️ حذف فایل", callback_data=f"del_{file_key}")
        inline_keyboard.append([btn_view, btn_delete])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await message.answer(
        "📋 فایل‌های شما به شرح زیر است: 📂\n\nبرای مشاهده هر فایل روی نام آن و برای حذف روی دکمه‌ی مربوطه کلیک کنید: 👇",
        reply_markup=keyboard
    )
    await message.answer(
        "🔙 برای بازگشت از منوی زیر استفاده کنید: 👇",
        reply_markup=file_management_keyboard
    )


@router.callback_query(F.data.startswith("view_") | F.data.startswith("del_"))
async def process_file_callback(callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    action, file_key = data.split("_", 1)

    if file_key not in shared_files_db:
        await callback_query.answer("⚠️ این فایل دیگر وجود ندارد. ❌", show_alert=True)
        return

    file_data = shared_files_db[file_key]

    if action == "view":
        if file_data["deleted"]:
            await callback_query.answer("⚠️ این فایل حذف شده است. ❌", show_alert=True)
            return
        
        await callback_query.message.answer(f"📦 فایل درخواستی شما (نام: {file_data['name']}): 📥")
        if file_data["type"] == "document":
            await callback_query.message.answer_document(file_data["file_id"])
        elif file_data["type"] == "video":
            await callback_query.message.answer_video(file_data["file_id"])
        elif file_data["type"] == "audio":
            await callback_query.message.answer_audio(file_data["file_id"])
        elif file_data["type"] == "photo":
            await callback_query.message.answer_photo(file_data["file_id"])
            
        await callback_query.answer("✅ فایل ارسال شد. 🚀")

    elif action == "del":
        file_data["deleted"] = True
        if user_id in user_files_db and file_key in user_files_db[user_id]:
            del user_files_db[user_id][file_key]

        await callback_query.answer("🗑️ فایل با موفقیت حذف شد. ✅", show_alert=True)
        try:
            await callback_query.message.edit_text("✅ این فایل از لیست شما حذف شد. 🗑️")
        except Exception:
            pass


async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
