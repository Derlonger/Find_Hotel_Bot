from loader import bot
from states.search_info import UserStates
from telebot.types import Message


@bot.message_handler(state=UserStates.cities, is_digit=True)
def get_city_incorrect(message: Message) -> None:
    """
    Функция, ожидающая некорректный ввод города. Если название города - цифры - выводить сообщение об ошибке.
    :param message: Сообщение Telegram
    :return: Сообщение об Ошибке.
    """
    bot.send_message(message.from_user.id, "Ошибка ввода! Название города должно состоять только из текста.")
