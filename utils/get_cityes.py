from typing import Dict, Union
from utils.api_reqwest import request_to_api
from config_data.config import RAPID_API_HEADERS
from loguru import logger

headers = RAPID_API_HEADERS


@logger.catch
def parse_cities_dict(city: str) -> Union[Dict[str, str], None]:
    """
        Функция делает запрос в request_to_api и десериализирует результат. Если запрос получен и десериализация прошла -
        возвращает обработанный результат в виде словаря - подходящие города и их id, иначе None.

        :param city: Город для поиска.
        :return: None или словарь с результатом: {'city_name': 'city_id'}
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
    response = request_to_api(url, headers=headers, querystring=querystring)
    json_data = response.json()
    cityes = dict()
    for result in json_data["sr"]:
        if result.get("type") in ["CITY", "NEIGHBORHOOD"]:
            short_name = result["regionNames"].get("shortName")
            id = result["gaiaId"]
            if short_name:
                cityes[short_name] = id

    return cityes
