from loader import bot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from telebot.types import Message, Dict


def show_buttons_photo_need_yes_no(message: Message) -> None:
    """
    Функция для вывода инлайн клавиатуры с вопросом нужны ли фотографии да или нет.
    :param message: Сообщение Telegram
    :return: None
    """
    logger.info(f'Вывод кнопок о необходимости фотографии пользователю. User_id: {message.chat.id} ')
    keyboard_yes_no = InlineKeyboardMarkup()
    keyboard_yes_no.add(InlineKeyboardButton(text="Да", callback_data='yes'))
    keyboard_yes_no.add(InlineKeyboardButton(text="Нет", callback_data='no'))
    bot.send_message(message.chat.id, "Нужно вывести фотографии?", reply_markup=keyboard_yes_no)


def show_cities_buttons(message: Message, possible_cities: Dict) -> None:
    """
    Функция из словаря возможных городов, формирует инлайн-клавиатуры с вариантами городов, и посылает ее в чат
    :param message: Message
    :param possible_cities: Словарь с возможными городами
    :return: None
    """
    logger.info(f"Вывод кнопок с вариантами городов пользователя. User_id: {message.chat.id}")
    keyboards_cities = InlineKeyboardMarkup()
    for key, value in possible_cities.items():
        keyboards_cities.add(InlineKeyboardButton(text=value['regionNames'], callback_data=value['gaiaId']))
    bot.send_message(message.from_user.id, "Пожалуйста, выберите город", reply_markup=keyboards_cities)
