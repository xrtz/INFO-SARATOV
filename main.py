from flask import Flask, request
from flask_ngrok import run_with_ngrok
import logging
import json
import os


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
        'response': {}
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


proof_describe = False
proof_describe1 = False
proof_describe2 = False
proof_describe3 = False
proof_describe4 = False
proof_describe5 = False
work = False
address1 = ""
address2 = ""
time_to_pack = 0
time = ""
transport = ""


def handle_dialog(req, res):
    global proof_describe, proof_describe1, proof_describe2, proof_describe3, proof_describe4, address1, \
        address2, time_to_pack, transport, work, time, proof_describe5
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {'suggests': ["Включить будильник", "Помощь"]}
        res['response']['text'] = '\"Включить будильник\" - начать использование программы. ' \
                                  '\"Изменить\" - обнуление и замена данных. ' \
                                  '\"Выключить будильник\" - прекратить использование программы. ' \
                                  '\"Отменить ввод\" - если вы вводите данные, чтобы прекратить ввод. '
        res['response']['buttons'] = get_suggests(user_id)
        return
# sessionStorage[user_id] = {'suggests': ["Включить будильник", "Изменить", "Выключить будильник",
#                                             "Помощь", "Отменить ввод"]}
    if (req['request']['original_utterance'].lower().strip() == "включить будильник" and not proof_describe and
            (not proof_describe4 and not proof_describe1 and not proof_describe2 and not proof_describe3 and
             not proof_describe5)):
        res['response']['text'] = "Сначала впишите нужные данные. " \
                                  "Откуда вы собираетесь отправляться? " \
                                  "Пишите через пробел: <город> <улица> <здание>. " \
                                  "Например: \"Саратов Московская 143\". "\
                                  "Если хотите прекратить ввод данных, то " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся). "
        sessionStorage[user_id] = {'suggests': ["Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        proof_describe1 = True
        return

    elif proof_describe1 and not proof_describe2 and len(req['request']['original_utterance'].split()) == 3:
        address1 = req['request']['original_utterance'].strip()
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Куда вы собираетесь отправляться? " \
                                  "Пишите через пробел: <город> <улица> <здание>. " \
                                  "Например: \"Саратов Московская 143\". "\
                                  "Если хотите прекратить ввод данных, то " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся). "
        sessionStorage[user_id] = {'suggests': ["Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        proof_describe2 = True

    elif proof_describe2 and not proof_describe3 and len(req['request']['original_utterance'].split()) == 3:
        address2 = req['request']['original_utterance'].strip()
        proof_describe3 = True
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Сколько времени вам понадобится на сборы? " \
                                  "Пишите в минутах. " \
                                  "Например: \"5\". " \
                                  "Если хотите прекратить ввод данных " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся). "
        sessionStorage[user_id] = {'suggests': ["Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif proof_describe3 and not proof_describe4 and len(req['request']['original_utterance'].split()) == 1:
        time_to_pack = req['request']['original_utterance'].strip()
        proof_describe4 = True
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Во сколько вам надо прибыть? " \
                                  "Напишите точное время, например: \"8:00\". " \
                                  "Если хотите прекратить ввод данных " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся)."
        sessionStorage[user_id] = {'suggests': ["Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif proof_describe4 and not proof_describe5 and len(req['request']['original_utterance'].split()) == 1:
        time = req['request']['original_utterance'].strip()
        proof_describe5 = True
        res['response']['text'] = "Впишите нужные данные. " \
                                  "Какой способ передвижения вы выберете? " \
                                  "Выберете любой из предложенных: велосипед, пешком, " \
                                  "машина, общественный транспорт, такси. " \
                                  "Например: \"общественный транспорт\". " \
                                  "Если хотите прекратить ввод данных " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся)."
        sessionStorage[user_id] = {'suggests': ["Машина", "Общественный транспорт", "Такси", "Пешком",
                                                "Велосипед", "Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif (proof_describe5 and not transport and req['request']['original_utterance'].lower() in
          ["машина", "общественный транспорт", "такси", "пешком", "велосипед"]):
        transport = req['request']['original_utterance'].strip()
        res['response']['text'] = "Будильник включен. Мы приняли. " \
                                  f"Откуда: {address1}. " \
                                  f"Куда: {address2}. " \
                                  f"Время на сборы: {time_to_pack}. " \
                                  f"Время прибытия: {time}. " \
                                  f"Способ передвижения: {transport}. "
        sessionStorage[user_id] = {'suggests': ["Изменить", "Выключить будильник", "Помощь"]}
        res['response']['buttons'] = get_suggests(user_id)
        proof_describe = True
        work = True
        return

    elif req['request']['original_utterance'].strip().lower() == "изменить":
        res['response']['text'] = 'Ваши данные обнулились, будильник выключен. ' \
                                  'После того как вы заполните все пунткы, будильник автоматически включится. ' \
                                  "Впишите нужные данные. " \
                                  "Откуда вы собираетесь отправляться? " \
                                  "Пишите через пробел: <город> <улица> <здание>. " \
                                  "Например: \"Саратов Московская 143\". " \
                                  "Если хотите прекратить ввод данных, то " \
                                  "напишите \"Отменить ввод\"(все данные обнулятся)."
        work = False
        proof_describe = False
        proof_describe1 = True
        proof_describe2 = False
        proof_describe3 = False
        proof_describe4 = False
        proof_describe5 = False
        transport = ""
        sessionStorage[user_id] = {'suggests': ["Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "включить будильник" and proof_describe:
        if not work:
            res['response']['text'] = "Хорошо"
        else:
            res['response']['text'] = "Уже рабоатет!"
        work = True
        sessionStorage[user_id] = {'suggests': ["Изменить", "Выключить будильник", "Помощь"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "отменить ввод" and proof_describe1 and not transport:
        res['response']['text'] = "Хорошо. " \
                                  '\"Включить будильник\" - начать использование программы. ' \
                                  '\"Изменить\" - обнуление и замена данных. ' \
                                  '\"Выключить будильник\" - прекратить использование программы. ' \
                                  '\"Отменить ввод\" - если вы вводите данные, чтобы прекратить ввод. '
        proof_describe = False
        proof_describe1 = False
        proof_describe2 = False
        proof_describe3 = False
        proof_describe4 = False
        proof_describe5 = False
        sessionStorage[user_id] = {'suggests': ["Включить будильник", "Помощь"]}
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif req['request']['original_utterance'].lower().strip() == "помощь":
        res['response']['text'] = '\"Включить будильник\" - начать использование программы. ' \
                                  '\"Изменить\" - обнуление и замена данных. ' \
                                  '\"Выключить будильник\" - прекратить использование программы. ' \
                                  '\"Отменить ввод\" - если вы вводите данные, чтобы прекратить ввод. '
        sessionStorage[user_id] = {'suggests': ["Включить будильник", "Изменить", "Выключить будильник",
                                                "Помощь", "Отменить ввод"]}
        res['response']['buttons'] = get_suggests(user_id)
        return
    elif req['request']['original_utterance'].lower().strip() == "выключить будильник":
        if work:
            res['response']['text'] = "Будильник выключен!"
        else:
            res['response']['text'] = "Будильник уже выключен!"
        sessionStorage[user_id] = {'suggests': ["Включить будильник", "Изменить", "Помощь"]}
        res['response']['buttons'] = get_suggests(user_id)
        work = False
        return
    else:
        res['response']['text'] = "Извините, мы вас не поняли, нажмите \"Помошь\" если что-то не понятно"
        sessionStorage[user_id] = {'suggests': ["Помощь"]}
        res['response']['buttons'] = get_suggests(user_id)
        return


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:7]
    ]
    return suggests


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)