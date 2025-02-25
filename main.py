import flet as ft
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo

# === НАСТРОЙКИ ===
BOT_TOKEN = "7703347356:AAER4OQMdYQjE8mxUo9NSvg_aX-ARAqthec"  # 🔴 Укажите токен Telegram-бота
WEB_APP_URL = "https://your-deployment-url.com"  # 🔴 Укажите URL мини-приложения (Flet)

# === БАЗА ДАННЫХ ===
conn = sqlite3.connect("clicker.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, clicks INTEGER)")
conn.commit()

# === FLET (Мини-приложение) ===
async def main(page: ft.Page):
    page.title = "Кликер"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    user_id = None  # ID пользователя (получим через Telegram)
    counter = ft.Text("0", size=30)

    async def load_clicks():
        """Загрузка количества кликов пользователя"""
        cursor.execute("SELECT clicks FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    async def save_clicks(clicks):
        """Сохранение кликов в БД"""
        cursor.execute("INSERT INTO users (user_id, clicks) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET clicks=?", (user_id, clicks, clicks))
        conn.commit()

    async def on_click(e):
        """Обработка клика"""
        clicks = int(counter.value) + 1
        counter.value = str(clicks)
        await save_clicks(clicks)
        await page.update_async()

    async def on_page_load(e):
        """Обработка загрузки страницы"""
        nonlocal user_id
        user_id = int(page.client_storage.get("user_id") or 0)
        if user_id:
            counter.value = str(await load_clicks())
            await page.update_async()

    btn_click = ft.ElevatedButton("Клик!", on_click=on_click)
    page.add(counter, btn_click)
    page.on_connect = on_page_load

    await page.update_async()

ft.app(target=main, view=ft.WEB_BROWSER)

# === AIROGRAM (Бот) ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    """Обработчик /start - отправляет кнопку с мини-приложением"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.KeyboardButton(text="Запустить игру", web_app=WebAppInfo(url=WEB_APP_URL))
    keyboard.add(web_app)
    await message.answer("Нажмите кнопку ниже, чтобы играть в кликер!", reply_markup=keyboard)

async def main_bot():
    """Запуск бота"""
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main_bot())


