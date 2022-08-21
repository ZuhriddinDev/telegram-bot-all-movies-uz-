
    # AFTARITE17_ tominidan yasalgan telegram bot !!.........

import os
import subprocess
import sys

import requests

HEADERS = {'Host': 'allplay.uz',
           'Accept': 'application/json',
           'x-allplay-brand': 'Apple',
           'x-allplay-version': '3.25',
           'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
           'x-allplay-device-id': 'hj32hj42hgh3gh2g3h1g4h21',
           'Accept-Language': 'ru',
           'x-allplay-app': 'ios',
           'User-Agent': 'Allplay/3.25 (uz.allplay.app; build:1; iOS 14.0.0) Alamofire/4.9.1',
           'x-allplay-model': 'iPhone 12 Pro Max'
           }

FFMPEG_COMMAND = 'ffmpeg -i {0} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {1}'

EMAIL = ''
PASSWORD = ''


def main(movie_link, chosen_quality):
    api_token = auth(EMAIL, PASSWORD)
    movie_id = get_movie_id(movie_link)
    movie_name = get_movie_info(movie_id)
    request_movie_id, quality = get_movie_qualities(movie_id, chosen_quality, api_token)
    m3u8_url = get_m3u8_url(request_movie_id, api_token)
    print(f'Начинаю скачивание фильма: {movie_name} в качестве {quality}')
    download_movie(m3u8_url, movie_name, quality)


def auth(email, password):
    data = {'email': email, 'password': password, 'device_id': 'hj32hj42hgh3gh2g3h1g4h21'}
    request_url = 'https://allplay.uz/api/v1/login'
    get_request = requests.post(request_url, headers=HEADERS, data=data)
    response = get_request.json()

    if 'errors' in response.keys():
        print(response['errors']['email'][0])
        sys.exit(1)

    api_token = response['api_token']
    return api_token


def get_movie_id(movie_link):
    movie_id = str(movie_link).split('movie/')[1].split('/')[0]
    return movie_id


def get_movie_info(movie_id):
    request_url = f'https://allplay.uz/api/v1/movie/1/{movie_id}'
    get_request = requests.get(request_url, headers=HEADERS)
    response = get_request.json()

    movie_name = response['data']['title']
    return movie_name


def get_movie_qualities(movie_id, quality, api_token):
    if quality not in ['sd', 'hd', 'fullhd']:
        quality = 'sd'

    HEADERS['Authorization'] = 'Bearer {}'.format(api_token)
    request_url = f'https://allplay.uz/api/v1/files/1/{movie_id}'
    get_request = requests.get(request_url, headers=HEADERS)
    response = get_request.json()

    list_data = response['data']
    all_qualities = {}
    for data in list_data:
        movie_id = data['id']
        request_movie_quality = data['quality']
        all_qualities[request_movie_quality] = movie_id

    if quality in all_qualities.keys():
        request_movie_id = all_qualities[quality]
    else:
        request_movie_id = all_qualities['sd']
        quality = 'sd'

    return request_movie_id, quality


def get_m3u8_url(request_movie_id, api_token):
    HEADERS['Authorization'] = 'Bearer {}'.format(api_token)
    request_url = f'https://allplay.uz/api/v1/file/play/1/{request_movie_id}?support_trial=2&type=hls'
    get_request = requests.get(request_url, headers=HEADERS)
    response = get_request.json()

    if 'errors' in response.keys():
        print(response['errors']['default'][0])
        sys.exit(1)

    m3u8_url = response['data']['url']
    return m3u8_url


def download_movie(m3u8_url, movie_name, quality):
    if not os.path.exists('movies'):
        os.mkdir('movies')

    file_dir = 'movies/{0}_{1}.mp4'.format(movie_name, quality).replace(' ', '-')
    command = FFMPEG_COMMAND.format(m3u8_url, file_dir, quality).split(' ')
    subprocess.call(command)


if __name__ == '__main__':
    # All qualities: sd, hd, fullhd
    main('https://allmovies.uz/movie/823/fast-and-furious', 'fullhd')
