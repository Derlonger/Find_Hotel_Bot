from loader import bot
from telebot.types import Message
from states.search_info import UserStates


@bot.message_handler(commands=['lowprice'])
def bot_low_price(message: Message) -> None:
    """
    Функция, реагирующая на команду 'lowprice'.
    Записывает состояние пользователя 'last_command' и предлагает ввести город для поиска отелей.
    :param message: Сообщение Telegram
    """
    bot.delete_state(message.from_user.id, message.chat.id)  # Перед начало опроса зачищаем все собранные состояния.
    bot.set_state(message.from_user.id, UserStates.cities, message.chat.id)  # Устанавливаем состояние для ответа
    bot.send_message(message.from_user.id, "Введите город: ")  # Отправляем сообщение пользователю
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:  # Записываем состояние пользователя
        data['last_command'] = 'lowprice'
