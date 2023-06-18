import re
from loader import bot
from states.search_info import UserStates
from telebot.types import Message, CallbackQuery
from utils.get_cityes import parse_cities_dict
from keyboards.inline.cities_for_choice import print_cities
from utils.factories import for_city


@bot.message_handler(state=UserStates.cities, is_digit=True)  # Если название города - цифры
def get_city_incorrect(message: Message) -> None:
    """
    Функция, ожидающая некорректный ввод города. Если название города - цифры - выводит сообщение об ошибке.

    :param message: Сообщение Telegram
    """
    print("Сработал обработчик некорректного ввода города")
    bot.send_message(message.from_user.id, 'Название города должно состоять из букв.')


@bot.message_handler(state=UserStates.cities, is_digit=False)  # Если название города - не цифры
def get_city(message: Message) -> None:
    """
    Функция, ожидающая корректный ввод города.
    Записывает состояние пользователя 'cities' и показывает клавиатуру с выбором конкретного города для уточнения.

    :param message: Сообщение Telegram
    """
    print("Сработал обработчик корректного ввода города", message.text)
    cities_dict = parse_cities_dict(message.text)
    if cities_dict:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cities'] = cities_dict
        bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=print_cities(cities_dict))
    else:
        bot.send_message(message.from_user.id, 'Не нахожу такой город. Введите ещё раз.')


@bot.callback_query_handler(func=None, city_config=for_city.filter())
def clarify_city(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие кнопки с выбором конкретного города.
    Записывает состояние пользователя 'city_id' и 'city' выбранного города.
    Предлагает ввести количество отелей.
    :param call:  Отклик клавиатуры.
    :return: Сообщение Telegram
    """
    print(call.data)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.chat.id, reply_markup=None)
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)

    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        data['city_id'] = re.search(r'\d+', call.data).group()
        data['city'] = [city for city, city_id in data['cities'].items() if city_id == data['city_id']][0]
    bot.set_state(call.from_user.id, UserStates.amount_hotels, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько отелей нужно найти?')
