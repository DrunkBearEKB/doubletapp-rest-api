import sys
import os
import configparser
import argparse
import requests
import json


FILE_CONFIG = 'config.ini'


def parse_config():
    config = configparser.ConfigParser()

    if not os.path.exists(FILE_CONFIG):
        config['Settings'] = {
            'address': 'http://127.0.0.1:9090/',
            'api_key': '830s9R7fo8Ew704nz03xBCf489mZ3mx8Dsf23DNo'
        }
        with open(FILE_CONFIG, mode='w') as file_config:
            config.write(file_config)
    else:
        config.read(FILE_CONFIG)

    return config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('has_photos', nargs='?', action='store',
                        help='')

    return parser.parse_args()


def send_request(address, api_key, has_photos=None):
    try:
        resp = requests.get(
            f'{address}pets/',
            params={
                'has_photos': has_photos
            },
            headers={
                'Accept': 'application/json',
                'X-Api-Key': api_key
            })

        return resp.json()

    except requests.exceptions.ConnectionError:
        return None


def print_response(response):
    if response is None:
        print('An error occurred while trying to connect! '
              'Please try again later or check your internet connection.')
        sys.exit()

    response = {
        'pets': response['items']
    }
    for item in response['pets']:
        for index, _ in enumerate(item['photos']):
            item['photos'][index] = item['photos'][index]['url']

    print(json.dumps(response, indent=4))


def main():
    config = parse_config()
    args = parse_args()

    has_photos = args.has_photos
    if has_photos is None:
        pass
    elif has_photos.lower() == 'true':
        has_photos = 'true'
    elif has_photos.lower() == 'false':
        has_photos = 'false'
    else:
        print('Parameter `has_photos` is not in a correct form! '
              'Possible values for parameter: None/true/false.')
        sys.exit()

    print_response(send_request(config['Settings']['address'],
                                config['Settings']['api_key'],
                                has_photos))


if __name__ == '__main__':
    main()
