import os
import time
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from datetime import datetime, time as dtime
import pytz

TOKEN = os.getenv("BOT_TOKEN")
ALERT_TIMES = [
    os.getenv("ALERT_TIME_1", "09:00"),
    os.getenv("ALERT_TIME_2", "18:00"),
]

bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def get_cardano_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data["cardano"]["usd"]
        return price
    except:
        return None

def send_price_alert(context):
    chat_id = context.job.context
    price = get_cardano_price()
    if price:
        context.bot.send_message(chat_id=chat_id, text=f"Harga Cardano (ADA) saat ini: ${price}")
    else:
        context.bot.send_message(chat_id=chat_id, text="Gagal mengambil harga ADA.")

def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Bot aktif. Kamu akan menerima notifikasi harga Cardano (ADA) setiap hari.")

    # Jadwalkan notifikasi harian
    tz = pytz.timezone("Asia/Makassar")
    for alert_time in ALERT_TIMES:
        hour, minute = map(int, alert_time.split(":"))
        context.job_queue.run_daily(
            send_price_alert,
            time=dtime(hour=hour, minute=minute, tzinfo=tz),
            context=chat_id,
            name=f"daily_alert_{alert_time}"
        )

start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()
