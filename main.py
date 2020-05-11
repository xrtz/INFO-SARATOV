from flask import Flask, request
from bs4 import BeautifulSoup
from random import randint
import logging
import requests
import json
import datetime
import os


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}
@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


TRANSLATOR = {'пешком': 'pd', 'велосипед': 'bc', 'на велосипеде': 'bc',
              'общественный транспорт': 'mt', 'на общественном транспорте': 'mt',
              'машина': 'auto', 'на машине': 'auto', 'такси': 'taxi', 'на такси': 'taxi'}

TRANSPORT = ['пешком', 'велосипед', 'на велосипеде', 'общественный транспорт',
             'на общественном транспорте', 'машина', 'на машине', 'такси', 'на такси']
UNIVERSAL_BUTTONS = ['помощь']
YES_BUTTONS = ['да', 'ок', 'давай', 'ладно', 'хорошо', 'го']
OFF_BUTTONS = ['отключить', 'выключить']
BACK_BUTTONS = ["Назад"]
MAIN_BUTTONS = ["Саратов", "Достопримичательности", "Поесть", "Отели и хостелы", "Сколько ехать"]
ATTRACTIONS_BUTTONS = ["Парк победы", "Проспект кирова", "Набережная космонавтов", "Назад"]
TO_EAT_BUTTONS = ["Узбечка", "Soho", "Назад"]
HOTEL_BUTTONS = ["Вишневая гора", "Wild West", "Назад"]

HELP = ''
MAIN = 'Здравствуйте, мы хотим вам рассказать о Саратове. \n ' \
       'Напишите: \n ' \
       '"Саратов" - если хотите информацию про Саратов, \n' \
      '"Достопримичательности" - если хотите узнать про достопримичательности ' \
      'Саратова,\n' \
      '"Поесть" - если хотите узнать где можно поесть,\n' \
      '"Отели и хостелы" - если хотите узнать где можно переночевать,\n' \
      '"Сколько ехать" - если хотите узнать сколько времени займет добраться ' \
      'из вашего города в наш.'
SARATOV = "Саратов основали в 2030 году, мэр - собянин. \nЕсли хотите вернуться назад, то напишите 'Назад'"
ATTRACTIONS = "По нашему мнению в Саратове самые главные достопримечательности это:\n" \
              "Парк победы \n" \
              "Проспект кирова \n" \
              "Набережная космонавтов. \nЕсли хотите вернуться назад, то напишите 'Назад'"
TO_EAT = "По нашему мнению в Саратове самые лучшие рестораны это: \n" \
         "Узбечка \n" \
         "Soho \n" \
         "Однако сейчас разгар пандемии, и лучше всего заказывать онлайн через develery club или яндекс еду" \
         ". \nЕсли хотите вернуться назад, то напишите 'Назад'"
HOTEL = "По нашему мнению в Саратове самые основные отели и хостелы это:\n" \
        "Вишневая гора \n" \
        "Wild West. \nЕсли хотите вернуться назад, то напишите 'Назад'"
TIME_ = "Чтобы узнать сколько времени займет путешевствие от вашего города до Саратова, напишите через пробел:" \
        "<ваш город> <машина или пешком или велосипед>. \nЕсли хотите вернуться назад, то напишите 'Назад'"
VISHNEVAYA_GORA = "Местоположение: 2-й Аптечный пр. 11. \nЕсли хотите вернуться назад, то напишите 'Назад'"
WILD_WEST = "Местоположение: 1-й пр. Танкистов, 40. \nЕсли хотите вернуться назад, то напишите 'Назад'"
YSBECHKA = "Местоположение: ул. Соколовая 10/16. \nЕсли хотите вернуться назад, то напишите 'Назад'"
SOHO = "Местоположение: ул. Октябрьская 5. \nЕсли хотите вернуться назад, то напишите 'Назад'"
PARK_POBEDA = "Здесь есть военная техника. \nЕсли хотите вернуться назад, то напишите 'Назад'"
PROSPECT_KIROVA = "Тут можно погулять. \nЕсли хотите вернуться назад, то напишите 'Назад'"
NABEREJNAYA_KOSMONAVTOV = "Тут можно погулять около реки. \nЕсли хотите вернуться назад, то напишите 'Назад'"

MAIN_PHOTO_SARATOV = "1652229/9e3b6f2c648a56c4988d"

stage = 0


def handle_dialog(req, res):
    global stage
    user_id = req['session']['user_id']
    if stage == 1:
        if req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = SARATOV
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
    elif stage == 2:
        if req['request']['original_utterance'].lower().strip() == "парк победы":
            res['response']['text'] = PARK_POBEDA
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "проспект кирова":
            res['response']['text'] = PROSPECT_KIROVA
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "набережная космонавтов":
            res['response']['text'] = NABEREJNAYA_KOSMONAVTOV
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = ATTRACTIONS
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
    elif stage == 3:
        if req['request']['original_utterance'].lower().strip() == "узбечка":
            res['response']['text'] = YSBECHKA
            res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "soho":
            res['response']['text'] = SOHO
            res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = TO_EAT
            res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
            return
    elif stage == 4:
        if req['request']['original_utterance'].lower().strip() == "вишневая гора":
            res['response']['text'] = VISHNEVAYA_GORA
            res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "wild west":
            res['response']['text'] = WILD_WEST
            res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = HOTEL
            res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
            return
    elif stage == 5:
        if req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        elif req['request']['original_utterance'].lower().strip() == "помощь":
            res['response']['text'] = TIME_
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
        else:
            res['response']['text'] = TIME_
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
    elif req['request']['original_utterance'].lower().strip() == "саратов":
        stage = 1
        res['response']['text'] = SARATOV
        res['response']['buttons'] = get_buttons(BACK_BUTTONS)
        return
    elif req['request']['original_utterance'].lower().strip() == "достопримичательности":
        stage = 2
        res['response']['text'] = ATTRACTIONS
        res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
        return
    elif req['request']['original_utterance'].lower().strip() == "поесть":
        stage = 3
        res['response']['text'] = TO_EAT
        res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
        return
    elif req['request']['original_utterance'].lower().strip() == "отели и хостелы":
        stage = 4
        res['response']['text'] = HOTEL
        res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
        return
    elif req['request']['original_utterance'].lower().strip() == "сколько ехать":
        stage = 5
        res['response']['text'] = TIME_
        res['response']['buttons'] = get_buttons(BACK_BUTTONS)
        return
    elif req['session']['new']:
        res['response']['text'] = MAIN
        res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
        return
    else:
        res['response']['text'] = MAIN
        res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
        return


def get_buttons(cur):
    if cur:
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in list(map(lambda x: x[0].upper() + x[1:],
                                    UNIVERSAL_BUTTONS + cur))
        ]
    else:
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in list(map(lambda x: x[0].upper() + x[1:], UNIVERSAL_BUTTONS))
        ]
    return suggests


def existing_object(adress):
    try:
        url = 'http://geocode-maps.yandex.ru/1.x?'
        params = {'geocode': ','.join([''.join(adress[:2]), adress[2]]),
                  'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                  'format': 'json'
                  }
        response = requests.get(url, params=params).json()
        ans1 = response['response']['GeoObjectCollection']['featureMember']
        ans = ans1[0]['GeoObject']['Point']['pos'].split()
        return ans
    except Exception:
        return None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)