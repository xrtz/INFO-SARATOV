from flask import Flask, request
from flask_ngrok import run_with_ngrok
from bs4 import BeautifulSoup
from random import randint
import logging
import requests
import json
import datetime


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
delay = False
time = False
TRANSLATOR = {'пешком': 'pd', 'велосипед': 'bc', 'на велосипеде': 'bc',
              'общественный транспорт': 'mt', 'на общественном транспорте': 'mt',
              'машина': 'auto', 'на машине': 'auto', 'такси': 'taxi', 'на такси': 'taxi'}
TRANSPORT = ['пешком', 'велосипед', 'на велосипеде', 'общественный транспорт',
             'на общественном транспорте', 'машина', 'на машине', 'такси', 'на такси']
UNIVERSAL_BUTTONS = ['помощь']
YES_BUTTONS = ['да', 'ок', 'давай', 'ладно', 'хорошо', 'го']
QUESTION_BUTTONS = ['изменить']
HELP = 'Это приложение \'Умный будильник\', вам осталось только вбить данные, а будильник сам' \
       ' позаботится о продолжительности вашего сна. Если вы уже его завели, то ждите, когда ' \
       'он прозвенит, или отмените. Будильник предназначен для поездок внутри населённого пункта. '
CHANGE = 'Все данные, что вы ввели обнулились. Начнём опрос сначала. '
DONTUNDERSTAND = 'Извините, мы вас не поняли. '
MESSAGE0 = 'Давайте заведём будильник.'
MESSAGE1 = 'Откуда вы собираетесь отправляться? Пишите через пробел: <улица> <здание> <город>.' \
           ' Например: \'Московская 143 Саратов\'.'
MESSAGE2 = 'Куда вы собираетесь отправляться? Пишите через пробел: <улица> <здание> <город>. ' \
           'Например: \'Саратов Московская 143\'.'
MESSAGE3 = 'Сколько времени для сборов вам понадобится. Напишите в минутах, например: \'12 мин\'.'
MESSAGE4 = 'Напишите день(сегодня или завтра) и время ко скольки вам нужно быть на месте через' \
           ' пробел без секунд: <день> <время> например: \'сегодня 21:40\'.'
MESSAGE5 = 'Выберите ваш способ передвижения из списка: пешком, на велосипеде, на общественном' \
           ' транспорте, на машине или на такси.'
MESSAGE6 = 'Будильник заведён'


def handle_dialog(req, res):
    global time, work, stage, coords1, coords2, delay, type
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Здравствуйте, заведём будильник?'
        res['response']['buttons'] = get_buttons([YES_BUTTONS[randint(0, len(YES_BUTTONS) - 1)]])
        return

    if stage == 0:
        if req['request']['original_utterance'].lower().strip() in YES_BUTTONS:
            res['response']['text'] = MESSAGE1
            res['response']['buttons'] = get_buttons(False)
            stage += 1
        elif req['request']['original_utterance'].lower().strip() == 'помощь':
            res['response']['text'] = HELP + MESSAGE0
            res['response']['buttons'] = get_buttons([YES_BUTTONS[randint(0, len(YES_BUTTONS) - 1)]])
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = HELP + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE0
            res['response']['buttons'] = get_buttons(False)
        return

    if stage == 1:
        if existing_object(req['request']['original_utterance'].strip()):
            coords1 = existing_object(req['request']['original_utterance'].strip())
            res['response']['text'] = MESSAGE2
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
            stage += 1
        elif req['request']['original_utterance'].strip().lower() == 'помощь':
            res['response']['text'] = HELP + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = CHANGE + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE1
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        return

    if stage == 2:
        if existing_object(req['request']['original_utterance'].strip()):
            coords2 = existing_object(req['request']['original_utterance'].strip())
            res['response']['text'] = MESSAGE3
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
            stage += 1
        elif req['request']['original_utterance'].strip().lower() == 'помощь':
            res['response']['text'] = HELP + MESSAGE2
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = CHANGE + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
            stage = 1
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE2
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        return

    if stage == 3:
        if check3(req['request']['original_utterance'].strip()):
            delay = check3(req['request']['original_utterance'].strip())
            res['response']['text'] = MESSAGE4
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
            stage += 1
        elif req['request']['original_utterance'].strip().lower() == 'помощь':
            res['response']['text'] = HELP + MESSAGE3
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = CHANGE + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
            stage = 1
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE3
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        return

    if stage == 4:
        if check4(req['request']['original_utterance'].strip().lower):
            time = check4(req['request']['original_utterance'].strip().lower)
            res['response']['text'] = MESSAGE5
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS + TRANSPORT[::2])
            stage += 1
        elif req['request']['original_utterance'].strip().lower() == 'помощь':
            res['response']['text'] = HELP + MESSAGE4
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = CHANGE + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
            stage = 1
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE4
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS)
        return

    if stage == 5:
        if req['request']['original_utterance'].strip().lower() in TRANSPORT:
            type = TRANSLATOR[req['request']['original_utterance'].strip().lower()]
            res['response']['text'] = MESSAGE5
            res['response']['buttons'] = get_buttons(False)
            stage += 1
        elif req['request']['original_utterance'].strip().lower() == 'помощь':
            res['response']['text'] = HELP + MESSAGE5
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS + TRANSPORT[::2])
        elif req['request']['original_utterance'].strip().lower() == 'изменить':
            res['response']['text'] = CHANGE + MESSAGE1
            res['response']['buttons'] = get_buttons(False)
            stage = 1
        else:
            res['response']['text'] = DONTUNDERSTAND + MESSAGE5
            res['response']['buttons'] = get_buttons(QUESTION_BUTTONS + TRANSPORT[::2])
        return


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
        ans = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        return ans
    except Exception:
        return None


def check3(arg):
    try:
        return int(arg.split()[0])
    except Exception:
        return None


def check4(arg):
    try:
        arg = arg.split()
        today = datetime.date.today()
        if arg[0] == 'сегодня':
            return int(today.strftime('%d')), \
                   (int(arg[1].split(':')[0]) * 60 + int(arg[1].split(':')[1]))
        elif arg[0] == 'завтра':
            tomorrow = today + datetime.timedelta(days=1)
            return int(tomorrow.strftime('%d')), \
                   (int(arg[1].split(':')[0]) * 60 + int(arg[1].split(':')[1]))
        else:
            return None
    except Exception:
        return None


if __name__ == '__main__':
    app.run()
