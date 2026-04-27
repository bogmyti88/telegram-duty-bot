import os
import json
from datetime import datetime
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

DATA_FILE = "duty_data.json"
CHAT_ID = "1003870235172"

DUTY_MEMBERS = [
    "Денис",
    "Алексей",
    "Иван",
    "Сергей",
    "Антон"
]

API_ID = "28057795"
API_HASH = "c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6"
BOT_TOKEN = "8718391899:AAGgKS1Kj1auTf0dkENYs6RYI9lBpTKBfE0"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_index": 0, "date": str(datetime.now().date())}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_current_duty():
    data = load_data()
    today = str(datetime.now().date())

    if data.get("date") != today:
        data["current_index"] = (data.get("current_index", 0) + 1) % len(DUTY_MEMBERS)
        data["date"] = today
        save_data(data)

    return DUTY_MEMBERS[data["current_index"]]


async def send_daily_duty(app: Client):
    duty = get_current_duty()
    try:
        await app.send_message(CHAT_ID, f"🔔 Дежурный на сегодня: {duty} 🎯")
    except Exception as e:
        print(f"Ошибка отправки: {e}")


async def main():
    app = Client(
        name="duty_bot",
        bot_token=BOT_TOKEN,
        api_id=API_ID,
        api_hash=API_HASH
    )

    @app.on_message(filters.command("start"))
    async def cmd_start(client, message):
        await message.reply(
            "🤖 Бот дежурного\n\n"
            "Команды:\n"
            "/who - узнать кто дежурный\n"
            "/next - следующий по очереди\n"
            "/list - список участников"
        )

    @app.on_message(filters.command("who"))
    async def cmd_who(client, message):
        duty = get_current_duty()
        await message.reply(f"Сегодня дежурный: {duty} 🎯")

    @app.on_message(filters.command("next"))
    async def cmd_next(client, message):
        data = load_data()
        data["current_index"] = (data["current_index"] + 1) % len(DUTY_MEMBERS)
        data["date"] = str(datetime.now().date())
        save_data(data)
        duty = get_current_duty()
        await message.reply(f"Дежурный изменён на: {duty} ✅")

    @app.on_message(filters.command("list"))
    async def cmd_list(client, message):
        duty = get_current_duty()
        text = "Список участников:\n"
        for i, member in enumerate(DUTY_MEMBERS):
            marker = " 👈" if member == duty else ""
            text += f"{i+1}. {member}{marker}\n"
        await message.reply(text)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: send_daily_duty(app), "cron", hour=9, minute=0)
    scheduler.start()

    print("🤖 Бот запущен...")
    await app.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())