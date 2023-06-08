import requests


def request_to_api(url, headers, querystring):
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == requests.codes.ok:
        return response
    else:
        raise ConnectionError
