from flask import Flask, request
from flask_ngrok import run_with_ngrok
import logging
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
            'end_session': False,
            "work_session": False,
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


proof_describe = False
proof_describe1 = False
proof_describe2 = False
proof_describe3 = False
proof_describe4 = False
work = False
address1 = ""
address2 = ""
time = 0
transport = ""


def handle_dialog(req, res):
    global proof_describe, proof_describe1, proof_describe2, proof_describe3, proof_describe4, address1, \
        address2, time, transport, work
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Начать",
                "Изменить",
                "Выйти",
                "Помощь",
                "Отменить"
            ]
        }
        res['response']['text'] = '\"Начать\" - начать использование программы. ' \
                                  '\"Изменить\" - обнуление и замена данных. ' \
                                  '\"Выйти\" - прекратить использование программы. ' \
                                  '\"Отменить\" - если вы вводите данные, чтобы прекратить ввод. '
        res['response']['buttons'] = get_suggests(user_id)
        return

    if (req['request']['original_utterance'].lower().strip() == "начать" and not proof_describe and
            (not proof_describe4 and not proof_describe1 and not proof_describe2 and not proof_describe3)):
        res['response']['text'] = "Сначала впишите нужные данные. " \
                                  "Откуда вы собираетесь отправляться? " \
                                  "Пишите через пробел: <город> <улица> <здание>. " \
                                  "Например: \"Саратов Московская 143\". "\
                                  "Если хотите прекратить ввод данных, то " \
                                  "напишите \"Отменить\"(все данные обнулятся). "
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
                                  "напишите \"Отменить\"(все данные обнулятся). "
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
        for suggest in session['suggests'][:5]
    ]
    return suggests


if __name__ == '__main__':
    app.run()