import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters

TEXTS_PATH = '/Users/mikhailf/PycharmProjects/bot_tg/texts'
IMAGES_PATH = '/Users/mikhailf/PycharmProjects/bot_tg/images'

TOKEN = ''

author_dict = {
    "Чудесный доктор": "Куприн Александр Иванович",
    "Золотой петух": "Куприн Александр Иванович",
    "Шинель": "Гоголь Николай Васильевич",
    "Три вора": "Толстой Лев Николаевич",
    "Тупейный художник": "Лесков Николай Семенович",
    "Беседа пьяного с трезвым чертом": "Чехов Антон Павлович",
    "Телеграмма": "Паустовский Константин Георгиевич",
    "Бродяга и начальник тюрьмы": "Грин Александр Степанович",
    "Дикий помещик": "Салтыков-Щедрин Михаил Евграфович",
    "Двойной выстрел": "Пришвин Михаил Михайлович",
    "Приключения обезьяны": "Зощенко Михаил Михайлович",
    "Кактус": "Фет Афанасий Афанасьевич",
    "У белой воды": "Есенин Сергей Александрович",
    "Очень коротенький роман": "Гаршин Всеволод Михайлович",
    "Господин из Сан-Франциско": "Бунин Иван Алексеевич",
}


CHOOSING, TYPING_TITLE, TYPING_WORD = range(3)

def normalize_string(s):
    return re.sub(r'\W+', '', s.lower())

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("О чат-боте", callback_data='about')],
        [InlineKeyboardButton("Поиск произведения по названию", callback_data='search_by_title')],
        [InlineKeyboardButton("Поиск произведения по словам", callback_data='search_by_word')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Этот бот служит для поиска произведений по названию.",
        reply_markup=main_menu_keyboard()
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Бот остановлен. Для перезапуска используйте команду /start.")
    await context.application.stop()

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Этот бот создан Михаилом Филатовым, студентом группы 8К22 Томского Политехнического Университета. Он предназначен для поиска произведений по названию",
        reply_markup=main_menu_keyboard()
    )

async def search_by_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Введите название произведения:")
    return TYPING_TITLE

async def search_by_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Введите слово для поиска в произведениях:")
    return TYPING_WORD

async def received_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = normalize_string(update.message.text)
    normalized_author_dict = {normalize_string(k): v for k, v in author_dict.items()}
    author_name = normalized_author_dict.get(title, "Автор не найден")

    file_name = next((fname for fname in os.listdir(TEXTS_PATH) if normalize_string(os.path.splitext(fname)[0]) == title), None)

    if file_name:
        file_path = os.path.join(TEXTS_PATH, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                sentences = text.split('.')
                fragment = '. '.join(sentences[:2]).strip() + '.'
                if len(fragment) > 1024:
                    fragment = fragment[:1020] + "..."
        except Exception:
            await update.message.reply_text("Ошибка при чтении файла.")
            await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text("Произведение не найдено.")
        await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    image_path = next((os.path.join(IMAGES_PATH, fname) for fname in os.listdir(IMAGES_PATH) if normalize_string(os.path.splitext(fname)[0]) == title), None)

    if image_path:
        try:
            await update.message.reply_photo(photo=open(image_path, 'rb'), caption=fragment)
        except Exception:
            await update.message.reply_text("Ошибка при отправке фото произведения.")
            await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text(fragment)

    author_image_path = next((os.path.join(IMAGES_PATH, fname) for fname in os.listdir(IMAGES_PATH) if normalize_string(os.path.splitext(fname)[0]) == normalize_string(author_name)), None)

    if author_image_path:
        try:
            await update.message.reply_photo(photo=open(author_image_path, 'rb'), caption=author_name)
        except Exception:
            await update.message.reply_text("Ошибка при отправке фото автора.")
            await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text(f"Изображение для автора '{author_name}' не найдено.")

    await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def received_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    word = normalize_string(update.message.text)
    found_titles = []
    for file_name in os.listdir(TEXTS_PATH):
        try:
            with open(os.path.join(TEXTS_PATH, file_name), 'r', encoding='utf-8') as file:
                if word in normalize_string(file.read()):
                    found_titles.append(os.path.splitext(file_name)[0])
        except Exception:
            continue
    if found_titles:
        await update.message.reply_text(f"Произведения, содержащие слово '{word}':\n" + "\n".join(found_titles))
    else:
        await update.message.reply_text(f"Слово '{word}' не найдено ни в одном произведении.")
    await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю вашего сообщения.")
    await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=main_menu_keyboard())

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(search_by_title, pattern='^search_by_title$'),
            CallbackQueryHandler(search_by_word, pattern='^search_by_word$')
        ],
        states={
            TYPING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_title)],
            TYPING_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_word)]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)

    application.add_handler(CallbackQueryHandler(about, pattern='^about$'))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()

if __name__ == '__main__':
    main()
