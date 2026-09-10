import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

# توکن ربات خود را اینجا قرار دهید
TOKEN = "8844658209:AAH41cGWIdMiSLQq8PO5VNU_qds7vWJpmmE"

router = Router()


# تابع ساخت کیبورد اصلی (دقیقاً همان منوی قبلی‌ات به همراه اضافه شدن خدمات لینک)
def get_main_keyboard():
  keyboard = ReplyKeyboardMarkup(
      keyboard=[
          [
              KeyboardButton(text="📥 دانلودر شبکه اجتماعی"),
              KeyboardButton(text="🤖 آزمایشگاه هوش مصنوعی"),
          ],
          [
              KeyboardButton(text="🛠 ابزارهای کاربردی"),
              KeyboardButton(text="☕️ کافه برنامه‌نویسی و فناوری"),
          ],
          [
              KeyboardButton(text="🎨 استودیو جادویی عکس و ویدئو"),
              KeyboardButton(text="🏆 لیست بهترین افراد"),
          ],
          [
              KeyboardButton(text="🔗 خدمات لینک"),
              KeyboardButton(text="📁 مدیریت فایل‌ها"),
          ],
          [
              KeyboardButton(text="👤 حساب کاربری"),
          ],
      ],
      resize_keyboard=True,
      input_field_placeholder="لطفاً یکی از گزینه‌های زیر را انتخاب کنید...",
  )
  return keyboard


# تابع کمکی برای کوتاه‌کردن لینک با سرویس آنلاین
async def shorten_url(long_url: str) -> str:
  api_url = f"https://is.gd/create.php?format=simple&url={long_url}"
  async with aiohttp.ClientSession() as session:
    async with session.get(api_url) as response:
      if response.status == 200:
        short_url = await response.text()
        return short_url.strip()
      else:
        return None


# هندلر دستور استارت
@router.message(CommandStart())
async def cmd_start(message: Message):
  await message.answer(
      "سلام! به مگابات خوش آمدید. 🤖\nبرای شروع، یکی از گزینه‌های منوی زیر را"
      " انتخاب کنید:",
      reply_markup=get_main_keyboard(),
  )


# هندلر دکمه خدمات لینک
@router.message(F.text == "🔗 خدمات لینک")
async def link_services_menu(message: Message):
  await message.answer(
      "بخش **خدمات لینک** فعال شد. 🔗\nلینک طولانی خود را بفرستید تا آن را به"
      " یک لینک کوتاه و قابل استفاده در پیامک تبدیل کنم:",
      parse_mode="Markdown",
  )


# هندلر دریافت لینک و کوتاه کردن خودکار آن
@router.message(
    F.text.startswith("http://")
    | F.text.startswith("https://")
    | F.text.startswith("www.")
)
async def handle_url_input(message: Message):
  user_link = message.text.strip()
  waiting_msg = await message.answer("⏳ در حال کوتاه کردن لینک...")

  short_result = await shorten_url(user_link)

  if short_result and short_result.startswith("http"):
    await waiting_msg.edit_text(
        f"🔗 **لینک کوتاه شده‌ی شما آماده است:**\n\n`{short_result}`\n\nپ.ن:"
        " می‌توانید این لینک را کپی کرده و در پیامک یا هر جای دیگری استفاده"
        " کنید.",
        parse_mode="Markdown",
    )
  else:
    await waiting_msg.edit_text(
        "❌ خطا در کوتاه‌کردن لینک. لطفاً لینک معتبری بفرستید."
    )


# هندلر دکمه حساب کاربری (کلید بزرگ پایینی)
@router.message(F.text == "👤 حساب کاربری")
async def user_account_handler(message: Message):
  await message.answer(
      "👤 **اطلاعات حساب کاربری شما:**\n\nوضعیت اشتراک: عادی\nموجودی ترافیک:"
      " رایگان",
      parse_mode="Markdown",
  )


# اینجا می‌توانی هندلرهای سایر دکمه‌های منوی اصلی خودت را هم قرار دهی...


# تابع اصلی اجرای ربات
async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(router)

  print("Bot is running...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
