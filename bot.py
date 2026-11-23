import asyncio
import logging
import os
import aiosqlite
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
DB_PATH = "bot_users.db"

logging.basicConfig(level=logging.INFO)
router = Router()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)"
        )
        await db.commit()


async def save_user(user_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username or "unknown"),
        )
        await db.commit()


def main_keyboard() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="ℹ️ О боте")
    kb.button(text="📊 Мой профиль")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await save_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Шаблон бота на <b>aiogram 3 + aiosqlite</b> успешно запущен.",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "ℹ️ О боте")
async def about_handler(message: types.Message):
    await message.answer("Базовый каркас Telegram-бота для быстрого прототипирования на хакатонах.")


@router.message(F.text == "📊 Мой профиль")
async def profile_handler(message: types.Message):
    await message.answer(
        f"🆔 Твой ID: <code>{message.from_user.id}</code>\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}",
        parse_mode="HTML",
    )


async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
