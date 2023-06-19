from loader import bot
from telebot.types import Message
from states.search_info import UserStates
from handlers import survey_handlers  # noqa


@bot.message_handler(commands=['highprice'])
def bot_high_price(message: Message) -> None:
    """
    Функция, реагирующая на команду "highprice".
    Записывает состояние пользователя 'last_command' и предлагает ввести город для поиска отелей.
    Args:
        message: Сообщение Telegram

    Returns:None
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, UserStates.cities, message.chat.id)
    bot.send_message(message.from_user.id, "Введите город:")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['last_command'] = 'highprice'
