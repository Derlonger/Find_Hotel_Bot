import requests
from loguru import logger


@logger.catch
def request_to_api(url, headers, querystring):
    response = requests.get(url, headers=headers, params=querystring, timeout=5)
    if response.status_code == requests.codes.ok:
        return response
    else:
        raise ConnectionError
