import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp as youtube_dl
import os
import re

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
        download_path = "./downloads"  # Указываем директорию для скачивания
        if not os.path.exists(download_path):
            os.makedirs(download_path)  # Создаем директорию, если ее нет

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Скачиваем в нужную папку
            'restrictfilenames': True,  # Используем безопасные названия
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
            # Очистка имени файла от недопустимых символов
            sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            audio_filename = f"{sanitized_title}.mp3"

        # Печатаем путь к файлу для отладки
        file_path = os.path.join(download_path, audio_filename)
        print(f"Файл скачан по пути: {file_path}")

        # Отправляем пользователю скачанное аудио
        await update.message.reply_text(f"Аудио '{title}' скачано! Отправляю...")

        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        # Отправляем аудио
        with open(file_path, "rb") as audio:
            await update.message.reply_audio(audio)

        # Удаляем файл после отправки
        os.remove(file_path)

    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основная функция запуска бота
import os

# Основная функция запуска бота
async def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Используем переменную окружения
    if not TOKEN:
        print("Ошибка: переменная окружения TELEGRAM_BOT_TOKEN не установлена.")
        return

    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    await app.run_polling()


# Запуск бота с использованием asyncio.run()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
