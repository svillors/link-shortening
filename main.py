import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import argparse


class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f'Ошибка: {code}, {message}')


def short_link(token, url):
    params = {
        'access_token': token,
        'v': '5.199',
        'url': url
    }
    response = requests.get('https://api.vk.ru/method/utils.getShortLink',
                            params=params)
    response.raise_for_status()
    api_response = response.json()
    if 'error' in api_response:
        error_code = api_response['error']['error_code']
        error_message = api_response['error']['error_msg']
        raise APIError(error_code, error_message)
    return api_response['response']['short_url']


def count_clicks(token, url):
    url = urlparse(url)
    params = {
        'access_token': token,
        'v': '5.199',
        'key': url.path.replace('/', ''),
        'interval': 'forever'
    }
    response = requests.get('https://api.vk.ru/method/utils.getLinkStats',
                            params=params)
    response.raise_for_status()
    api_response = response.json()
    if 'error' in api_response:
        error_code = api_response['error']['error_code']
        error_message = api_response['error']['error_msg']
        raise APIError(error_code, error_message)
    return api_response['response']['stats'][0]['views']


def is_link_short(url):
    url = urlparse(url)
    return url.netloc == 'vk.cc'


def main():
    load_dotenv()
    token = os.environ['VK_SERVICE_ACCESS_KEY']
    parser = argparse.ArgumentParser(
        description='Сокращение ссылки или подсчёт количества переходов по ней'
    )
    parser.add_argument('url', help='Введите ссылку')
    args = parser.parse_args()
    url = args.url
    try:
        if is_link_short(url):
            print('Количество переходов по ссылке:', count_clicks(token, url))
        else:
            print('Сокращенная ссылка:', short_link(token, url))
    except requests.exceptions.HTTPError as error:
        print(f'ошибка {error}')
    except APIError as error:
        print(error)


if __name__ == "__main__":
    main()
