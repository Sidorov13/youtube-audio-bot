import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp as youtube_dl
import os

# Применяем nest_asyncio для корректной работы асинхронного кода в окружении
nest_asyncio.apply()

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне ссылку на видео с YouTube, и я скачаю аудио для тебя.")

# Обработчик сообщений
async def handle_message(update: Update, context):
    url = update.message.text
    await update.message.reply_text("Скачиваю аудио... Подождите.")

    try:
        # Параметры для скачивания аудио
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': '/usr/bin/ffmpeg',
            'noplaylist': True,
        }

        # Скачиваем аудио с YouTube
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'downloaded_audio')
            audio_filename = f"{title}.mp3"

        # Отправляем пользователю скачанное аудио
        await update.message.reply_text(f"Аудио '{title}' скачано! Отправляю...")

        # Отправляем аудио
        with open(audio_filename, "rb") as audio:
            await update.message.reply_audio(audio)

        # Удаляем файл после отправки
        os.remove(audio_filename)

    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основная функция запуска бота
async def main():
    TOKEN = "Ваш_токен_бота"
    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    await app.run_polling()

# Запуск бота с использованием asyncio.run()
if __name__ == '__main__':
    asyncio.run(main())
