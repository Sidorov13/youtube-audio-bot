import os
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp as youtube_dl
import os


# Применяем nest_asyncio для разрешения работы с асинхронными задачами
nest_asyncio.apply()

# Получаем токен из переменной окружения
token = os.getenv("TELEGRAM_BOT_TOKEN")
if token is None:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден. Убедитесь, что переменная окружения добавлена.")

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне ссылку на видео с YouTube, и я скачаю аудио для тебя.")

# Обработчик сообщений
async def handle_message(update: Update, context):
    url = update.message.text
    await update.message.reply_text("Скачиваю аудио... Подождите.")

    try:
        ydl_opts = {
            
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
           'ffmpeg_location': '/home/Sidorov/ffmpeg/ffmpeg-7.1.tar.xz',  # Путь к ffmpeg на сервере
            'noplaylist': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'downloaded_audio')
            audio_filename = f"{title}.mp3"

        with open(audio_filename, "rb") as audio:
            await update.message.reply_audio(audio)

        os.remove(audio_filename)

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основная функция
async def main():
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
