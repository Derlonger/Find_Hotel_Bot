from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from loader import bot


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call, message: Message):
    # Получаем выбранный ответ
    selected_option = call.data
    bot.send_message(message.chat.id, f"Вы выбрали {selected_option}")


def start_message(message: Message, options):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for option in options:
        button = InlineKeyboardButton(option, callback_data=option)
        keyboard.add(button)

    bot.send_message(message.chat.id, 'Выберите нужный район:', reply_markup=keyboard)
