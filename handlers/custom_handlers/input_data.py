from loader import bot
from telebot.types import Message
from loguru import logger
import datetime
from datetime import date
from states.user_states import UserInputState
from config_data.config import RAPID_ENDPOINT
from utils.api_request import request
from utils.processing_json import get_city
from keyboards.inline.create_buttons import show_cities_buttons, show_buttons_photo_need_yes_no
from telegram_bot_calendar import DetailedTelegramCalendar
from utils.show_data_and_find_hotels import print_data


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def low_high_best_handler(message: Message) -> None:
    """
    Обработчик команд, срабатывает на три компанды /lowprice, /highprice, /bestdeal
    и запоминает необходимые данные. Спрашивает пользователя - какой искать город.
    :param message:  Сообщение Telegram
    :return: None
    """
    bot.set_state(message.chat.id, UserInputState.command)
    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        logger.info('Запоминаем выбранную команду: ' + message.text + f"User_id: {message.chat.id}")
        data['command'] = message.text
        data['sort'] = check_command(message.text)
        data['date_time'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        data['chat_id'] = message.chat.id
    bot.set_state(message.chat.id, UserInputState.input_city)
    bot.send_message(message.from_user.id, 'Введите город в котором нужно найти отель: ')


@bot.message_handler(state=UserInputState.input_city)
def input_city(message: Message) -> None:
    """
    Ввод пользователем города и отправка запроса серверу на поиск вариантов городов.
    Возможные варианты городов передаются генератору клавиатуры.
    :param message: Сообщение Telegram
    :return: None
    """
    with bot.retrieve_data(message.chat.id) as data:
        data['input_city'] = message.text
        logger.info('Пользователь ввел город: ' + message.text + f' User_id: {message.chat.id}')
        # Создаем запрос для поиска вариантов городов и генерируем клавиатуру
        querystring = {"q": message.text, "locale": "ru_RU"}
        response_cities = request("GET", RAPID_ENDPOINT['search_cities'], querystring)
        if response_cities.status_code == 200:
            logger.info('Сервер ответил: ' + str(response_cities.status_code) + f' User_id: {message.chat.id}')
            possible_cities = get_city(response_cities.text)
            show_cities_buttons(message, possible_cities)
        else:
            bot.send_message(message.chat.id, f"Что-то пошло не так, код ошибки: {response_cities.status_code}\n"
                                              f"Повторите команду еще раз. И введите другой город.")
            data.clear()


@bot.message_handler(state=UserInputState.quantity_hotels)
def input_quantity(message: Message) -> None:
    """
    Ввод количества выдаваемых на странице отелей, а так же проверка, является ли
    введённое число и входит ли оно в заданный диапазон от 1 до 10
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            logger.info('Ввод и запись количества отелей: ' + message.text + f' User_Id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                data['quantity_hotels'] = message.text
                bot.set_state(message.chat.id, UserInputState.travellers_adults)
                bot.send_message(message.chat.id, "Введите количество взрослых от 17 лет (от 1 до 14): ")
        else:
            bot.send_message(message.chat.id,
                             'Ошибка! Это должно быть число в диапазоне от 1 до 10! Повторите попытку!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите попытку!')


@bot.message_handler(state=UserInputState.travellers_adults)
def input_travellers_adults(message: Message) -> None:
    """
    Функция ввода количества взрослых.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        if 1 <= int(message.text) <= 16:
            logger.info('Ввод и запись количества взрослых: ' + message.text + f' User_id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                data['travellers_adults'] = int(message.text)
                bot.set_state(message.chat.id, UserInputState.travellers_children)
                bot.send_message(message.chat.id, "Введите количество детей от 1 до 6: \n"
                                                  "Если детей нет 0.")
        else:
            bot.send_message(message.chat.id, "Ошибка! Вы вышли из диапазона от 0-17! Повторите попытку ввода!")
    else:
        bot.send_message(message.chat.id, "Ошибка! Вы ввели не число! Повторите попытку ввода!")


@bot.message_handler(state=UserInputState.travellers_children)
def input_travellers_children(message: Message) -> None:
    """
    Функция получает количества детей и после чего запускает опрос по возрасту каждого ребенка.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        if int(message.text) == 0:
            with bot.retrieve_data(message.chat.id) as data:
                data['children_count'] = 0
                data['children_ages'] = []
                show_buttons_photo_need_yes_no(message)
                return
        if 1 <= int(message.text) <= 6:
            logger.info('Ввод и запись количества детей: ' + message.text + f' User_id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                data['children_count'] = int(message.text)
                bot.send_message(message.chat.id,
                                 f"Отлично! Теперь необходимо ввести возраст каждого ребенка по очереди!")
                bot.register_next_step_handler(message, get_child_age)
        else:
            bot.send_message(message.chat.id, "Необходимо ввести число от 0 до 6!\n"
                                              "Повторите попытку.")
    else:
        bot.send_message(message.chat.id, "Необходимо ввести число от 0 до 6!\n"
                                          "Повторите попытку.")


children_data = []


def get_child_age(message: Message) -> None:
    """
    Функция ввода и записи возраста каждого ребенка.
    :param message: Сообщение Telegram
    :return: None
    """
    try:
        select_age = int(message.text)
        if 1 <= select_age <= 17:
            logger.info(
                f'Ввод и запись возраст {len(children_data) + 1}-го ребенка: ' + message.text +
                f' User_id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                children_data.append({'age': select_age})
                if len(children_data) < data['children_count']:
                    bot.send_message(message.chat.id, f"Введите возраст {len(children_data) + 1}-го ребенка:")
                    bot.register_next_step_handler(message, get_child_age)
                else:
                    data['children_ages'] = children_data
                    show_buttons_photo_need_yes_no(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, введите возраст от 1 до 17")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста введите возраст с клавиатуры.")


@bot.message_handler(state=UserInputState.photo_count)
def input_photo_quantity(message: Message) -> None:
    """
    Функция для ввода количества фотографий и проверка на число, и на соответствие заданному диапазону от 1 до 10.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            logger.info('Ввод и запись количества фотографий: ' + message.text + f' User_id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                data['photo_count'] = message.text
                calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
                bot.send_message(message.chat.id, "Введите дату заезда", reply_markup=calendar)
        else:
            bot.send_message(message.chat.id, 'Число фотографий должно быть в диапазоне от 1 до 10! Повторите ввод!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


@bot.message_handler(state=UserInputState.priceMin)
def input_price_min(message: Message) -> None:
    """
    Функция для ввода минимальной стоимости отеля и проверка чтобы это было число.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        logger.info(
            'Ввод и запись минимальной стоимости отеля: ' + message.text + f' User_id: {message.chat.id}')
        with bot.retrieve_data(message.chat.id) as data:
            data['price_min'] = message.text
        bot.set_state(message.chat.id, UserInputState.priceMax)
        bot.send_message(message.chat.id, 'Введите максимальную стоимость отеля за сутки в долларах США')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите попытку!')


@bot.message_handler(state=UserInputState.priceMax)
def input_price_max(message: Message) -> None:
    """
    Функция для ввода максимальной стоимости отеля и проверка чтобы это было число.
    Максимальная стоимость не может быть меньше минимальной.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        logger.info('Ввод и запись максимальной стоимости отеля, сравнение с priceMin '
                    + message.text + f' User_id: {message.chat.id}')
        with bot.retrieve_data(message.chat.id) as data:
            if int(data['price_min']) < int(message.text):
                data['price_max'] = message.text
                bot.set_state(message.chat.id, UserInputState.landmarkIn)
                bot.send_message(message.chat.id, f'Введите начало диапазона расстояний от центра(в милях, от 0).')
            else:
                bot.send_message(message.chat.id,
                                 'Максимальная цена должна быть больше минимальной. Повторите попытку ввода!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите попытку ввода!')


@bot.message_handler(state=UserInputState.landmarkIn)
def input_landmark_in(message: Message) -> None:
    """
    Функция ввода начала диапазона расстояние до центра
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        logger.info('Ввод и запись начала диапазона от центра: ' + message.text + f" User_id: {message.chat.id}")
        with bot.retrieve_data(message.chat.id) as data:
            data['landmark_in'] = message.text
        bot.set_state(message.chat.id, UserInputState.landmarkOut)
        bot.send_message(message.chat.id, 'Введите конец диапазона расстояний от центра(в милях, от 0).')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите попытку ввода!')


@bot.message_handler(state=UserInputState.landmarkOut)
def input_landmark_out(message: Message) -> None:
    """
    Функция ввода конца диапазона расстояния до центра. И вызов функции print_data, для вывода выбранной информации.
    :param message: Сообщение Telegram
    :return: None
    """
    if message.text.isdigit():
        logger.info('Ввод и запись конца диапазона от центра: ' + message.text + f' User_id: {message.chat.id}')
        with bot.retrieve_data(message.chat.id) as data:
            data['landmark_out'] = message.text
            print_data(message, data)
    else:
        bot.send_message(message.chat.id, "Ошибка! Вы ввели не число! Повторите попытку ввода!")


def check_command(command: str) -> str:
    """
    Проверка команды и назначения параметра сортировки
    :param command: str команда, выбранная (введенная) пользователем
    :return: str команда сортировки
    """
    if command == '/bestdeal':
        return 'DISTANCE'
    elif command == '/lowprice' or command == '/highprice':
        return 'PRICE_LOW_TO_HIGH'
