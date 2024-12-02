import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp as youtube_dl
import logging
import asyncio

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Команда /start
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Отправь мне ссылку на видео с YouTube, и я скачаю аудио для тебя."
    )

# Обработка сообщений
async def handle_message(update: Update, context):
    url = update.message.text
    await update.message.reply_text("Скачиваю аудио... Подождите.")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "audio")
            filename = f"{title}.mp3"

        # Отправляем аудио пользователю
        with open(filename, "rb") as audio_file:
            await update.message.reply_audio(audio_file)

        # Удаляем локальный файл
        os.remove(filename)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основная функция
async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
