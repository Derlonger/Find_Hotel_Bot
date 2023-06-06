from config_data.config import RAPID_API_KEY
import requests

headers_api = {"X-RapidAPI-Key": RAPID_API_KEY,
               "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}


def request_to_api(url: str, headers: dict, querystring: dict):
    response = requests.get(url=url, headers=headers, params=querystring, timeout=2)
    if response.status_code == requests.codes.ok:
        return response
    else:
        raise ConnectionError


def city_founding(city_name: str) -> list:
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city_name, "locale": "ru_RU", "currency": "RUB"}
    response = request_to_api(url, headers_api, querystring)
    response = response.json()['sr']
    cityes = list()
    for result in response:
        if result["type"] != "HOTEL" and result["type"] != "AIRPORT":
            cityes.append({"Region": result["regionNames"]["shortName"], "Id": result["gaiaId"]})
    return cityes

#
# print([city_founding("New York")[i]["Region"] for i in range(len(city_founding("New York")))])
#
# print(city_founding("New York"))
