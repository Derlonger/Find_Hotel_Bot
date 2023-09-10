import random
from loader import bot
from telebot.types import Message, Dict, InputMediaPhoto
from loguru import logger
from config_data.config import RAPID_ENDPOINT
from utils.api_request import request
from utils.processing_json import get_hotels, hotel_info
import database.add_to_bd
import database
import time


def print_data(message: Message, data: Dict):
    """
    Функция вывода в Telegram-чат, всю информацию которую собрали от пользователя и передаем это в функцию поиска
    :param message: Сообщение Telegram
    :param data: Dict собранные данные от пользователя
    :return: None
    """
    # Отправляем в базу данных собранные данные, а там уже выберу что нужно
    database.add_to_bd.add_query(data)

    logger.info(f'Вывод суммарной информации о параметрах запроса пользователя. User_id: {message.chat.id}')
    text_message = ('Исходные данные: \n'
                    f'Дата и время запроса: {data["date_time"]}\n'
                    f'Введенная команда: {data["command"]}\n'
                    f'Вы ввели город: {data["input_city"]}\n'
                    f'Выбранный город с id: {data["destination_id"]}\n'
                    f'Количество отелей: {data["quantity_hotels"]}\n'
                    f'Количество взрослы от 17 лет: {data["travellers_adults"]}\n'
                    f'Количество детей до 17 лет: {data["children_count"]}\n'
                    f'Нужны ли фотографии? {data["photo_need"]}\n'
                    f'Количество фотографий: {data["photo_count"]}\n'
                    f'Дата заезда: {data["start_date"]}\n'
                    f'Дата выезда: {data["end_date"]}\n')
    if data['sort'] == 'DISTANCE':
        bot.send_message(message.chat.id, text_message +
                         f'Минимальный ценник: {data["price_min"]}\n'
                         f'Максимальный ценник: {data["price_max"]}\n'
                         f'Начало диапазона от центра: {data["landmark_in"]}\n'
                         f'Конец диапазона от центра: {data["landmark_out"]}')
    else:
        bot.send_message(message.chat.id, text_message)
    find_and_show_hotels(message, data)


def find_and_show_hotels(message: Message, data: Dict) -> None:
    """
    Функция для формирования запросов на поиск отелей, и детальной информации он них.
    Вывод полученных данных в час.
    :param message: Сообщение Telegram
    :param data: Dict данные, собранные от пользователя.
    :return: None
    """
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": data['destination_id']},
        "checkInDate": {
            "day": int(data['start_date'].day),
            "month": int(data['start_date'].month),
            "year": int(data['start_date'].year)
        },
        "checkOutDate": {
            "day": int(data['end_date'].day),
            "month": int(data['end_date'].month),
            "year": int(data['end_date'].year)
        },
        "rooms": [
            {
                "adults": int(data['travellers_adults']),
                "children": data['children_ages']
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 30,
        "sort": data['sort'],
        "filters": {"price": {
            "max": int(data['price_max']),
            "min": int(data['price_min'])
        }}
    }
    url = RAPID_ENDPOINT['search_hotels']
    # Отправка запроса серверу на поиск отелей
    response_hotels = request("POST", url, payload)
    logger.info(f'Сервер вернул ответ {response_hotels.status_code}. User_id: {message.chat.id}')
    # Если сервер возвращает статус-код не 200, то все остальные действия будут бессмысленными.
    if response_hotels.status_code == 200:
        # Обработка полученного ответа от сервера и формирование отсортированного словаря с отелями
        hotels = get_hotels(response_text=response_hotels.text,
                            command=data['command'],
                            landmark_in=data['landmark_in'],
                            landmark_out=data['landmark_out']
                            )
        if 'error' in hotels:
            bot.send_message(message.chat.id, hotels['error'])
            bot.send_message(message.chat.id, 'Попробуйте осуществить поиск с другими параметрами')
            bot.send_message(message.chat.id, '')
        count = 0
        for hotel in hotels.values():
            # Нужен дополнительный запрос, чтобы получить детальную информацию об отеле.
            # Цикл будет выполняться, пока не достигнет числа отелей, которое запросил пользователь.
            try:
                if count < int(data['quantity_hotels']):
                    summary_payload = {
                        "currency": "USD",
                        "eapid": 1,
                        "locale": "ru_RU",
                        "siteId": 300000001,
                        "propertyId": hotel['id']
                    }
                    summary_url = RAPID_ENDPOINT['hotel_info']
                    get_summary = request("POST", summary_url, summary_payload)
                    logger.info(f'Сервер вернул ответ {get_summary.status_code}. User_id: {message.chat.id}')
                    if get_summary.status_code == 200:
                        summary_info = hotel_info(get_summary.text)
                        hotel_url = f"https://www.hotels.com/h{hotel['id']}.Hotel-Information"
                        total_price = round(hotel["price"] * (data["end_date"] - data["start_date"]).days, 2)
                        caption = f'🏠Название: {hotel["name"]}\n' \
                                  f'📬Адрес: {summary_info["address"]}\n' \
                                  f'💲Стоимость проживания в сутки: {round(hotel["price"], 2)} $\n' \
                                  f'💲💲Стоимость проживания за период: {total_price} $\n' \
                                  f'🚗Расстояние до центра: {round(hotel["distance"], 2)} mile\n' \
                                  f'🪧Узнать более точную информацию об отеле: {hotel_url}'
                        medias = []
                        links_to_images = []
                        # сформируем рандомный список из ссылок на фотографии, ибо фоток много, а надо только 10
                        try:
                            for random_url in range(int(data['photo_count'])):
                                links_to_images.append(summary_info['images']
                                                       [random.randint(0, len(summary_info['images']) - 1)])
                        except IndexError:
                            continue

                        # Не важно, нужны пользователю фотографии или нет ссылки на них мы передаем в функцию
                        # для сохранения в базе данных
                        data_to_db = {
                            hotel['id']: {
                                'name': hotel['name'], 'address': summary_info['address'], 'user_id': message.chat.id,
                                'price': hotel['price'], 'total_price_day': total_price,
                                'distance': round(hotel['distance'], 2),
                                'date_time': data['date_time'], 'images': links_to_images, 'url_hotel': hotel_url
                            }
                        }
                        database.add_to_bd.add_response(data_to_db)
                        if int(data['photo_count']) > 0:
                            # формируем MediaGroup с фотографиями и описанием отеля и посылаем в чат
                            for number, url in enumerate(links_to_images):
                                if number == 0:
                                    medias.append(InputMediaPhoto(media=url, caption=caption))
                                else:
                                    medias.append(InputMediaPhoto(media=url))

                            logger.info(f"Выдаю найденную информацию в чат. User_id: {message.chat.id}")
                            bot.send_media_group(message.chat.id, medias)

                        else:
                            # если фотки не нужны, то просто выводим данные об отеле
                            logger.info(f"Выдаю найденную информацию в чат. User_id: {message.chat.id}")
                            bot.send_message(message.chat.id, caption)
                    else:
                        bot.send_message(message.chat.id, f'Что-то пошло не так, код ошибки: {get_summary.status_code}')
                time.sleep(1)  # задержку для того чтобы сервера телеграм успевали дать ответ и не выдавали ошибку 429
                count += 1
            except Exception as error:
                bot.retrieve_data(message.chat.id, None)
                bot.send_message(message.chat.id, f"Произошла ошибка при обработке данных об отелях: {str(error)}\n"
                                                  f"Попробуйте повторить ваш запрос.")
            else:
                break
        if count < int(data['quantity_hotels']):
            bot.send_message(message.chat.id,
                             f'Не удалось найти {data["quantity_hotels"]} отелей. Найдено только {count}.\n'
                             f'Попробуйте поменять параметры для поиска отеля.')
    else:
        bot.send_message(message.chat.id, f'Что-то пошло не так, код ошибки: {response_hotels.status_code}')
    logger.info(f"Поиск окончен. User_id: {message.chat.id}")
    bot.send_message(message.chat.id, f"Вот как-то так.\nМожете ввести ещё какую-нибудь команду!\n"
                                      f"Например: <b>/help</b>", parse_mode="html")
    bot.set_state(message.chat.id, None)
