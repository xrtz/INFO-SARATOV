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
BACK_BUTTONS = ["назад"]
MAIN_BUTTONS = ["Саратов", "Достопримичательности", "Поесть", "Отели и хостелы", "Сколько ехать"]

HELP = ''
MAIN = 'Здравствуйте, мы хотим вам рассказать о Саратове. \n' \
                                  'Напишите "Саратов", если хотите информацию про Саратов. \n' \
                                  'Напишите "Достопримичательности", если хотите узнать про достопримичательности ' \
                                  'Саратова. \n' \
                                  'Напишите "Поесть", если хотите узнать где можно поесть. \n' \
                                  'Напишите "Отели и хостелы", если хотите узнать где можно переночевать. \n' \
                                  'Напишите "Сколько ехать", если хотите узнать сколько времени займет добраться ' \
                                  'из вашего города в наш'


saratov = False
attractions = False
to_eat = False
to_stay = False
to_move = False


def handle_dialog(req, res):
    global saratov, attractions, to_eat, to_stay, to_move
    user_id = req['session']['user_id']
    if saratov:
        Saratov(req, res)
        return
    if req['session']['new']:
        res['response']['text'] = MAIN
        res['response']['buttons'] = get_buttons([MAIN_BUTTONS[randint(0, len(MAIN_BUTTONS) - 1)]])
        return
    elif req['request']['original_utterance'].lower().strip() == "Саратов":
        saratov = True
        Saratov(req, res)
        return


def Saratov(req, res):
    global saratov
    res['response']['text'] = 'Саратов основан в 2030 году, наш мэр Володин, рядом есть волга, если хотите вернуться ' \
                              'назад, то напишите "Назад"'
    if req['request']['original_utterance'].lower().strip() == "назад":
        saratov = False
        res['response']['text'] = MAIN
        res['response']['buttons'] = get_buttons([MAIN_BUTTONS[randint(0, len(MAIN_BUTTONS) - 1)]])
    else:
        res['response'][
            'text'] = 'Саратов основан в 2030 году, наш мэр Володин, рядом есть волга, если хотите вернуться ' \
                      'назад, то напишите "Назад"'
        res['response']['buttons'] = get_buttons([BACK_BUTTONS[randint(0, len(BACK_BUTTONS) - 1)]])


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
