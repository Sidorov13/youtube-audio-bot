from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp as youtube_dl
import os
import asyncio

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет hello! Отправь мне ссылку на видео с YouTube, и я скачаю аудио для тебя.")

# Обработчик сообщений
async def handle_message(update: Update, context):
    url = update.message.text
    await update.message.reply_text("Скачиваю аудио... Подождите.")

    try:
        # Параметры для скачивания аудио
        ydl_opts = {
            'format': 'bestaudio/best',  # Лучшее доступное аудио
            'outtmpl': '%(title)s.%(ext)s',  # Используем название видео как имя файла
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Постпроцессор для конвертации в mp3
                'preferredcodec': 'mp3',      # Формат конвертации
                'preferredquality': '192',    # Качество конвертированного аудио
            }],
            'ffmpeg_location': '/usr/bin/ffmpeg',  # Путь к ffmpeg
            'noplaylist': True,  # Если ссылка на плейлист, скачиваем только один трек
        }

        # Скачиваем аудио с YouTube
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'downloaded_audio')  # Получаем название видео для файла
            audio_filename = f"{title}.mp3"  # Название файла с расширением mp3

        # Отправляем пользователю скачанное аудио
        await update.message.reply_text(f"Аудио '{title}' скачано! Отправляю...")

        # Открываем и отправляем скачанный файл
        with open(audio_filename, "rb") as audio:
            await update.message.reply_audio(audio)

        # Удаляем файл после отправки
        os.remove(audio_filename)

    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основная функция запуска бота
async def main():
    # Получение токена из переменных окружения
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Ошибка: Токен Telegram не найден в переменных окружения!")
        return

    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    await app.run_polling()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
