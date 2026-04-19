import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import logging
from dotenv import load_dotenv
import re  # Модуль для работы с регулярными выражениями

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настройка логирования для вывода информации о работе бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в .env файле. Убедитесь, что файл .env существует и содержит строку BOT_TOKEN='ваш_токен'.")

# Словарь для хранения истории сообщений.
# Ключ: chat_id (идентификатор чата).
# Значение: список словарей, где каждый словарь представляет сообщение
# (с ключами 'role' - роль отправителя и 'content' - текст сообщения).
user_message_history = {}

# --- Функции для работы с интерфейсом ---

# Функция создания главного меню
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🚴 Каталог электровелосипедов", callback_data="catalog")],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton("📞 Консультация", callback_data="consult")],
        [InlineKeyboardButton("🌐 Перейти на сайт", url="http://electrodvigg.ru")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для отображения карточки товара
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE, name, price, desc):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    initialize_history(chat_id) # Инициализация истории, если не существует

    text = f"*{name}*\nЦена: {price}\n\n{desc}"
    keyboard = [
        [InlineKeyboardButton("🌐 Узнать на сайте", url="http://electrodvigg.ru")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="catalog")] # Кнопка возврата в каталог
    ]
    # Добавляем сообщение бота в историю
    user_message_history[chat_id].append({"role": "assistant", "content": text})
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# --- Обработчики команд и сообщений ---

# Инициализация истории сообщений для нового чата
def initialize_history(chat_id):
    if chat_id not in user_message_history:
        user_message_history[chat_id] = []
        logger.info(f"Инициализирована история сообщений для chat_id: {chat_id}")

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    initialize_history(chat_id) # Инициализируем историю

    text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в *ElectroDvigg* — магазин современных электровелосипедов.\n\n"
        "Выберите действие из меню ниже:"
    )
    # Добавляем системное сообщение в историю
    user_message_history[chat_id].append({"role": "system", "content": text})
    logger.debug(f"Сохранено системное сообщение для chat_id {chat_id}")

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu())

# Обработчик callback-запросов (нажатий кнопок)
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    initialize_history(chat_id)

    # Добавляем действие пользователя в историю
    user_message_history[chat_id].append({"role": "user", "content": f"Нажал кнопку: {data}"})
    logger.debug(f"Сохранено действие пользователя (кнопка {data}) для chat_id {chat_id}")

    # Логика обработки нажатых кнопок
    if data == "catalog":
        keyboard = [
            [InlineKeyboardButton("Kugoo C1 PRO PLUS — 45 000 ₽", callback_data="bike_x1")],
            [InlineKeyboardButton("ElectroBike FRIKE — 45 000 ₽", callback_data="bike_pro")],
            [InlineKeyboardButton("ElectroBike CAJODEMA — 42 000 ₽", callback_data="bike_ultra")],
            [InlineKeyboardButton("ElectroBike XINFEI — 58 000 ₽", callback_data="bike_ultra1")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")]
        ]
        text = "🚴 *Каталог электровелосипедов*\n\nВыберите модель:"
        user_message_history[chat_id].append({"role": "assistant", "content": text})
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "faq":
        text = (
            "❓ *Частые вопросы*\n\n"
            "• Пробег на одном заряде: 40–70 км\n"
            "• Вес велосипеда: 18–24 кг\n"
            "• Гарантия: 1 год\n\n"
            "Нужна консультация? Нажмите кнопку ниже."
        )
        keyboard = [
            [InlineKeyboardButton("📞 Получить консультацию", callback_data="consult")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")]
        ]
        user_message_history[chat_id].append({"role": "assistant", "content": text})
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "consult":
        text = (
            "📞 *Консультация*\n\n"
            "Напишите ваш номер телефона и вопрос — менеджер свяжется с вами."
        )
        context.user_data['awaiting_phone'] = True # Устанавливаем флаг, что ждем номер телефона
        user_message_history[chat_id].append({"role": "assistant", "content": text})
        await query.edit_message_text(text, parse_mode="Markdown")

    elif data == "back_to_main_menu":
        await query.edit_message_text("Главное меню:", reply_markup=main_menu())
        user_message_history[chat_id].append({"role": "assistant", "content": "Главное меню:"})

    # Обработка кнопок товаров - вызывает show_product
    elif data == "bike_x1":
        await show_product(update, context, "Kugoo C1 PRO PLUS", "45 000 ₽", "Лёгкий, быстрый, до 50 км на одном заряде.")
    elif data == "bike_pro":
        await show_product(update, context, "ElectroBike FRIKE", "45 000 ₽", "Усиленная рама, пробег до 60 км, мощный мотор.")
    elif data == "bike_ultra":
        await show_product(update, context, "ElectroBike CAJODEMA", "42 000 ₽", "Премиум модель, до 40 км пробега, амортизация.")
    elif data == "bike_ultra1":
        await show_product(update, context, "ElectroBike XINFEI", "58 000 ₽", "3 колеса, до 40 км пробега.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    user_data = context.user_data
    initialize_history(chat_id) # Убеждаемся, что история инициализирована

    # Сохраняем сообщение пользователя в историю
    user_message_history[chat_id].append({"role": "user", "content": text})
    logger.debug(f"Сохранено сообщение пользователя для chat_id {chat_id}: {text}")

    # Если бот ожидает номер телефона (после нажатия кнопки "Консультация")
    if user_data.get('awaiting_phone'):
        # Используем улучшенное регулярное выражение для проверки номера телефона
        # Оно ищет номера в форматах +7 XXX XXX XX XX или 8 XXX XXX XX XX,
        # допускает пробелы, тире и скобки.
        phone_match = re.search(r'^\+7[\d\s\-()]?(\d{3})[\d\s\-()]?(\d{3})[\d\s\-()]?(\d{2})[\d\s\-()]?(\d{2})$|^(8)[\d\s\-()]?(\d{3})[\d\s\-()]?(\d{3})[\d\s\-()]?(\d{2})[\d\s\-()]?(\d{2})$', text)

        if phone_match:
            # Получаем и нормализуем номер телефона
            phone_number = phone_match.group()
            if phone_match.group(1): # Если номер начинался с +7
                phone_number = re.sub(r'[^\d]', '', phone_number) # Удаляем все нецифровые символы
            elif phone_match.group(6): # Если номер начинался с 8
                phone_number = '+7' + re.sub(r'[^\d]', '', phone_number[1:]) # Заменяем 8 на +7 и удаляем нецифровые символы

            logger.info(f"Новая заявка на консультацию. Телефон: {phone_number}")

            context.user_data['awaiting_phone'] = False # Сбрасываем флаг ожидания номера

            response_text = "Спасибо! Мы получили ваш номер. Менеджер свяжется с вами."
            await update.message.reply_text(response_text)
            # Сохраняем ответ бота в историю
            user_message_history[chat_id].append({"role": "assistant", "content": response_text})
            logger.debug(f"Сохранен ответ бота для chat_id {chat_id}: {response_text}")
        else:
            # Если номер введен некорректно
            response_text = "Не удалось распознать номер. Пожалуйста, введите номер телефона в формате +7 (XXX) XXX-XX-XX или 8 XXX XXX XX XX."
            await update.message.reply_text(response_text)
            # Сохраняем ответ бота в историю
            user_message_history[chat_id].append({"role": "assistant", "content": response_text})
            logger.debug(f"Сохранен ответ бота для chat_id {chat_id}: {response_text}")
    else:
        # Если бот не ожидает номер телефона, отправляем стандартное сообщение
        response_text = "Используйте меню для связи. Для консультации нажмите «📞 Получить консультацию»."
        await update.message.reply_text(response_text)
        # Сохраняем ответ бота в историю
        user_message_history[chat_id].append({"role": "assistant", "content": response_text})
        logger.debug(f"Сохранен ответ бота для chat_id {chat_id}: {response_text}")

    # Опционально: вывод всей истории для отладки
    # logger.debug(f"Текущая история сообщений для chat_id {chat_id}:\n{user_message_history[chat_id]}")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Произошла ошибка: {context.error}") # Логируем ошибку
    if update and update.effective_message:
        await update.effective_message.reply_text("Что-то пошло не так. Попробуйте еще раз позже.")

# --- Точка входа в программу ---
# --- Точка входа в программу ---
def main():
    # Создаем экземпляр Application с токеном бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # --- КЛЮЧЕВОЙ ИЗМЕНЕНИЕ: ЗАПУСК НА RENDER ЧЕРЕЗ WEBHOOK ---
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 10000))

    if WEBHOOK_URL:
        print("🚀 Запуск бота в режиме webhook (для Render)...")
        # Удаляем старый вебхук (на всякий случай)
        application.bot.delete_webhook()
        # Устанавливаем новый вебхук
        application.bot.set_webhook(url=WEBHOOK_URL)
        # Запускаем веб-сервер на порту 10000 (Render требует именно этот порт)
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,  # Путь для безопасности: /<BOT_TOKEN>
            webhook_url=WEBHOOK_URL
        )
    else:
        print("⚠️ WEBHOOK_URL не задан. Запуск в режиме polling (только для локального тестирования)...")
        application.run_polling()


if __name__ == "__main__":
    main() # Вызываем функцию main при запуске скрипта
