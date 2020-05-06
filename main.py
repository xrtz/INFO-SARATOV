from flask import Flask, request
from flask_ngrok import run_with_ngrok
from bs4 import BeautifulSoup
from random import randint
import logging
import requests
import json


app = Flask(__name__)
run_with_ngrok(app)
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


stage = 0
work = False
coords1 = False
coords2 = False
type = False
time = False
transport = ""
universal_buttons = ['помощь']
yes_buttons = ['да', 'ок', 'давай', 'ладно', 'хорошо', 'го']
question_buttons = ['изменить']


def handle_dialog(req, res):
    global address1, address2, time, transport, work, stage
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Здравствуйте, заведём будильник?'
        res['response']['buttons'] = get_buttons(universal_buttons, yes_buttons)
        return

    if req['request']['original_utterance'].lower().strip() in yes_buttons and stage == 0:
        res['response']['text'] = 'Откуда вы собираетесь отправляться?' \
                                  'Пишите через пробел: <улица> <здание> <город>.' \
                                  'Например: \"Московская 143 Саратов\".'
        res['response']['buttons'] = get_buttons(universal_buttons, question_buttons)
        stage += 1
        return

    if stage == 1 and coords1:
        address1 = req['request']['original_utterance'].strip()
        res['response']['text'] = 'Куда вы собираетесь отправляться?' \
                                  'Пишите через пробел: <улица> <здание> <город>.' \
                                  'Например: \"Саратов Московская 143\".'
        res['response']['buttons'] = get_suggests(user_id)
        proof_describe2 = True
        stage += 1

    elif proof_describe2 and not proof_describe3 and len(req['request']['original_utterance'].split()) == 3:
        address2 = req['request']['original_utterance'].strip()
        proof_describe3 = True
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Сколько времени вам понадобится на сборы? " \
                                  "Пишите в минутах. " \
                                  "Например: \"5\". " \
                                  "Если хотите прекратить ввод данных " \
                                  "напишите \"Отменить\"(все данные обнулятся). "
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif (proof_describe3 and not proof_describe4 and len(req['request']['original_utterance'].split()) == 1 and
            req['request']['original_utterance'].lower().strip() != "отменить"):
        time = req['request']['original_utterance'].strip()
        proof_describe4 = True
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Какой способ передвижения вы выберете? " \
                                  "Выберете любой из предложенных: велосипед, пешком, " \
                                  "машина, общественный транспорт, такси. " \
                                  "Например: \"общественный транспорт\". " \
                                  "Если хотите прекратить ввод данных " \
                                  "напишите \"Отменить\"(все данные обнулятся)."
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif (proof_describe4 and not transport and req['request']['original_utterance'].lower() in
          ["машина", "общественный транспорт", "такси", "пешком", "велосипед"]):
        transport = req['request']['original_utterance'].strip()
        res['response']['text'] = "Мы приняли." \
                                  f"Откуда: {address1}. " \
                                  f"Куда: {address2}. " \
                                  f"Время на сборы: {time}. " \
                                  f"Способ передвижения: {transport}. "
        res['response']['buttons'] = get_suggests(user_id)
        proof_describe = True
        work = True
        return

    elif req['request']['original_utterance'].strip().lower() == "изменить":
        res['response']['text'] = 'Ваши данные обнулились .' \
                                  "Впишите нужные данные ." \
                                  "Откуда вы собираетесь отправляться? " \
                                  "Пишите через пробел: <город> <улица> <здание>. " \
                                  "Например: \"Саратов Московская 143\". " \
                                  "Если хотите прекратить ввод данных, то " \
                                  "напишите \"Отменить\"(все данные обнулятся)."
        work = False
        proof_describe = False
        proof_describe1 = True
        proof_describe2 = False
        proof_describe3 = False
        proof_describe4 = False
        transport = ""
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "начать" and not work and proof_describe:
        res['response']['text'] = "Хорошо"
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "начать" and work and proof_describe:
        res['response']['text'] = "Уже рабоатет!"
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "отменить" and proof_describe1 and not transport:
        res['response']['text'] = "Хорошо."
        proof_describe = False
        proof_describe1 = False
        proof_describe2 = False
        proof_describe3 = False
        proof_describe4 = False
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "помощь":
        res['response']['text'] = '\"Начать\" - начать использование программы. ' \
                                  '\"Изменить\" - обнуление и замена данных. ' \
                                  '\"Выйти\" - прекратить использование программы. ' \
                                  '\"Отменить\" - если вы вводите данные, чтобы прекратить ввод. '
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "выйти" and proof_describe:
        res['response']['text'] = "До свидания!"
        res['response']['buttons'] = get_suggests(user_id)
        work = False
        return
    else:
        res['response']['text'] = "Извините, мы вас не поняли"
        res['response']['buttons'] = get_suggests(user_id)
        return


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


def get_buttons(univ, cur):
    suggests = [
        {'title': suggest, 'hide': False}
        for suggest in list(map(lambda x: x[0].upper() + x[1:], univ + [cur[randint(0, len(cur) - 1)]]))
    ]
    return suggests


def existing_object(adress):
    global coords1
    try:
        url = 'http://geocode-maps.yandex.ru/1.x?'
        params = {'geocode': ','.join([ ''.join(adress[:2]), adress[2]]),
                  'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                  'format': 'json'
                  }
        response = requests.get(url, params=params).json()
        ans = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        return ans
    except Exception:
        return None


if __name__ == '__main__':
    app.run()