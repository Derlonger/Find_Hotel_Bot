import json
from telebot.types import Dict


def get_city(response_text: str) -> Dict:
    """
    Функция принимает ответ от сервера с возможным вариантами городов. Возвращает словарь
    с названиями городов и их индетификатором.
    :param response_text: Ответ от сервера
    :return: Словарь с вариантами городов
    """
    possible_cities = {}
    data = json.loads(response_text)
    if not data:
        raise LookupError("Запрос пуст.:(")
    for id_place in data['sr']:
        try:
            possible_cities[id_place['gaiaId']] = {
                'gaiaId': id_place['gaiaId'],
                'regionNames': id_place['regionNames']['fullName']
            }
        except KeyError:
            continue
    return possible_cities


def get_hotels(
        response_text: str,
        command: str,
        landmark_in: str,
        landmark_out: str
) -> Dict:
    """
    Функция принимает ответ от сервера, выбранную команду сортировки, а так же приделы диапазона
    расстояния от центра города. Возвращает отсортированный словарь, в зависимости от команды сортировки.
    :param response_text: Ответ от сервера, в котором содержится информация об отелях
    :param command: Команда сортировки
    :param landmark_in: Начало диапазона расстояния до центра
    :param landmark_out: Конец диапазона расстояния до центра
    :return: None
    """
    data = json.loads(response_text)
    if not data:
        raise LookupError('Запрос пуст...')
    # При поиске в некоторых городах выдается ошибка, я не очень понимаю из-за чего она.
    # Дабы ее исключить - эта проверка:
    if 'errors' in data.keys():
        return {'error': data['errors'][0]['message']}

    hotels_data = {}
    for hotel in data['data']['propertySearch']['properties']:
        try:
            hotels_data[hotel['id']] = {
                'name': hotel['name'], 'id': hotel['id'],
                'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                'price': hotel['price']['lead']['amount']
            }
        except (KeyError, TypeError):
            continue
    # Сортируем по цене, от высокой стоимости, к меньшей.
    if command == '/highprice':
        sorted_data = sorted(hotels_data.items(), key=lambda x: (x[1]['price'], x[1]['distance']), reverse=True)
        # Преобразование отсортированных данных обратно в словарь
        hotels_data = {k: v for k, v in sorted_data}
    # Сортируем по наилучшим показателям стоимость и расстояние от центра.
    elif command == 'bestdeal':
        sorted_data = sorted(hotels_data.items(), key=lambda x: (x[1]['price'], x[1]['distance']))
        # Преобразование отсортированных данных обратно в словарь
        hotels_data = {k: v for k, v in sorted_data}
    print(hotels_data)
    return hotels_data


def hotel_info(hotels_request: str) -> Dict:
    """
    Функция принимает ответ от сервера с детальной информацией об отеле и возвращает словарь с данными отеля.
    :param hotels_request: Ответ от сервера с детальной информацией об отеле.
    :return: Возвращает словарь с отфильтрованной информацией об отеле.
    """
    data = json.loads(hotels_request)
    if not data:
        raise LookupError('Запрос Пуст...')
    hotel_data = {'id': data['data']['propertyInfo']['summary']['id'],
                  'name': data['data']['propertyInfo']['summary']['name'],
                  'address': data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
                  'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
                  'images': [
                      url['image']['url'] for url in data['data']['propertyInfo']['propertyGallery']['images']

                  ]
                  }

    return hotel_data
