from flask import Flask, request
from bs4 import BeautifulSoup
from random import randint
from p import parsing
from flask_ngrok import run_with_ngrok
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


TRANSPORT = ['пешком', 'велосипед', 'на велосипеде', 'общественный транспорт',
             'на общественном транспорте', 'машина', 'на машине', 'такси', 'на такси']
UNIVERSAL_BUTTONS = ['помощь']
BACK_BUTTONS = ["Меню"]
MAIN_BUTTONS = ["Саратов", "Достопримечательности", "Поесть", "Отели и хостелы", "Сколько ехать"]
ATTRACTIONS_BUTTONS = ["Журавли (памятник)", "Саратовская консерватория", "Меню"]
TO_EAT_BUTTONS = ["Узбечка", "Soho", "Меню"]
HOTEL_BUTTONS = ["Вишневая гора", "Wild West", "Меню"]
SARATOV_BUTTONS = ["Информация про Саратов", "Фотография", "Меню"]
FORM_BUTTONS = ["Информация", "Фотография", "Местоположение", "Назад"]

gps = {"Журавли (памятник)": 'Парк Победы', "Саратовская консерватория": "просп. Кирова, 1",
       "Узбечка": "ул. Соколовая 10/16",
       "Soho": "ул. Октябрьская 5",
       "Вишневая гора": "2-й Аптечный пр. 11",
       "Wild West": "1-й пр. Танкистов, 40"}
photo = {'Саратов': "213044/5d64c2229eb3dde015f5", "Журавли (памятник)": '937455/74579a8293399813c897',
         "Саратовская консерватория": "1652229/1a6ceb58ab1693a20527",
         "Узбечка": "1521359/4ededc1bc94cca81579b",
         "Soho": "1521359/18170c9855850ad3d69f",
         "Вишневая гора": "965417/bbb43db199b7437db171",
         "Wild West": "1540737/dbd7b29d347117f91879"}
info = {'Саратов': "Саратов — город на юго-востоке европейской части России, "
                   "административный центр Саратовской области и Саратовского района, "
                   "находится на правом берегу Волгоградского водохранилища реки Волги "
                   "напротив устья реки Саратовки и города Энгельс, расположенных на противоположном берегу. "
                   "Основан как сторожевая крепость для охраны южных рубежей Русского государства в 1590 году. "
                   "\nНаселение: 838 042 чел. (2020 г.)"
                   "\nТелефонный код: +7 8452"
                   "\nПлощадь: 394 км²"
                   "\nЕсли хотите вернуться в меню, то напишите 'Меню'",
        "Журавли (памятник)": 'Мемориальный комплекс «Журавли» в парке Победы на Соколовой горе '
                              'г. Саратова — памятник саратовцам, погибшим во время Великой Отечественной '
                              'войны 1941—1945 годов. Мемориальный комплекс «Журавли», один из символов Саратова. '
                              '\nВоздвигнутый на Соколовой горе на высоте 160 метров над уровнем моря, имеющий '
                              'рукотворный холм высотой 100 метров и установленные на нём сорокаметровые пилоны, '
                              'позволяют видеть силуэт «Журавлей» из многих точек Саратова.',
        "Саратовская консерватория": "Саратовская государственная консерватория имени Л. В. Собинова - высшее "
                                     "музыкальное учебное заведение в Саратове, третья по счёту консерватория в "
                                     "России. Одно из ведущих музыкальных ВУЗов России и мира. Основана в 1912 году "
                                     "на базе музыкального училища.",
        "Узбечка": "Популярный ресторан среди молодежи и людей постарше."
                   " Восточный интерьер с мягкими диванами и креслами, расшитыми подушками, приглушенным светом, "
                   "негромкой музыкой создают позитивный настрой на весь день. Все блюда готовятся по традиционным "
                   "рецептам, сохранившимся до наших дней. Шеф-повар строго их придерживается, создавая шедевры для "
                   "настоящих гурманов: манты, ханум, кутаб, шурпу, плов, кустыбай, самсу, лагман, хачапури. Особый "
                   "аромат и вкус придают пряности и специи. Свежие травы делают подачу более аппетитной. Сладкоежки "
                   "останутся довольны: в ассортименте более 15 видов десертов. Барная карта представлена чаем, "
                   "фрешами, айраном, домашними лимонадами, авторскими коктейлями. Они открыты каждый день с 11 до "
                   "00.00. В четверг, пятницу, субботу закрываются в 02.00. Несмотря на большое количество посадочных "
                   "мест, столики необходимо бронировать заранее, особенно в праздничные дни. Контактный номер "
                   "телефона: 8 8452 322444.",
        "Soho": "ресторан находится в старинном особняке XIX века. Если снаружи "
                "сохранился стиль той эпохи, то попадая внутрь, поражает ультрасовременный дизайн. Шеф-повар сочетает "
                "несколько кухонь, постоянно экспериментирует и создает оригинальные блюда, которых нет ни в одном"
                "другом ресторане Саратова. Авторские десерты вызовут незабываемый гастрономический "
                "восторг. Мясо и рыба жарятся в углевой печи. В меню включены пицца и бургеры, горячие закуски, салаты."
                "Алкогольная карта обширна. Развлекательные мероприятия проводятся регулярно. Это выступления "
                "известных диджеев страны, яркие шоу-программы, конкурсы, мастер-классы. Для гостей есть караоке и "
                "ночной танцпол. Цены достаточно высокие, но всегда можно воспользоваться действующими предложениями. "
                "Так, в день рождения именинник получает 20% скидки.  Оно работает ежедневно с 12 часов до 00.00."
                "В пятницу и субботу закрывается в 03.00. Телефон для бронирования столика: 8 8452 71 71 71.",
        "Вишневая гора": "Хороший отель у всех девочек из моей старой школы были оттуда фотографии, а у меня нет(",
        "Wild West": "Находиться на молочке расположение самое отстойное из списка"
        }

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
SARATOV = "Саратов. \n " \
          "Напишите: \n" \
          "'Информация про Саратов' - если хотите узнать про Саратов,\n" \
          "'Фотография' - если хотите увидеть фотографию Саратова" \
          "\nЕсли хотите вернуться в меню, то напишите 'Меню'"
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
TIME_ = "Чтобы узнать сколько времени займет путешевствие от вашего города до Саратова, напишите город или" \
        " адрес, откуда вы планируете отправляться на машине. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# VISHNEVAYA_GORA = "Местоположение: 2-й Аптечный пр. 11. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# WILD_WEST = "Местоположение: 1-й пр. Танкистов, 40. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# YSBECHKA = "Местоположение: ул. Соколовая 10/16. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# SOHO = "Местоположение: ул. Октябрьская 5. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# PARK_POBEDA = "Здесь есть военная техника. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# PROSPECT_KIROVA = "Тут можно погулять. \nЕсли хотите вернуться назад, то напишите 'Назад'"
# NABEREJNAYA_KOSMONAVTOV = "Тут можно погулять около реки. \nЕсли хотите вернуться назад, то напишите 'Назад'"
FORM = "Напишите: \n" \
          "'Информация' - если хотите узнать информацию про этот объект, \n" \
          "'Фотография' - если хотите увидеть фотографию этого объекта,\n" \
          "'Местоположение' - если хотите узнать где это находится." \
          "\nЕсли хотите вернуться в меню, то напишите 'Меню'"


stage = 0
into = False
last_text = ""


def handle_dialog(req, res):
    global stage, into, last_text
    user_id = req['session']['user_id']
    if stage == 1:
        if req['request']['original_utterance'].lower().strip() == "меню":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        elif req['request']['original_utterance'].lower().strip() == "информация про саратов":
            res['response']['text'] = info['Саратов']
            res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "фотография":
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['image_id'] = photo['Саратов']
            res['response']['text'] = ' '
            res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
            return
        else:
            res['response']['text'] = SARATOV
            res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
            return
    elif stage == 2:
        if into and req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = ATTRACTIONS
            into = False
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "информация":
            res['response']['text'] = info[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "местоположение":
            res['response']['text'] = gps[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "фотография":
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['text'] = ' '
            res['response']['image_id'] = photo[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into:
            res['response']['text'] = last_text + ". \n" + FORM
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "журавли (памятник)":
            res['response']['text'] = "Журавли (памятник). \n" + FORM
            last_text = "Журавли (памятник)"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "саратовская консерватория":
            res['response']['text'] = "Саратовская консерватория. \n" + FORM
            last_text = "Саратовская консерватория"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "меню":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = ATTRACTIONS
            res['response']['buttons'] = get_buttons(ATTRACTIONS_BUTTONS)
            return
    elif stage == 3:
        if into and req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = TO_EAT
            into = False
            res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "информация":
            res['response']['text'] = info[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "местоположение":
            res['response']['text'] = gps[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "фотография":
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['text'] = ' '
            res['response']['image_id'] = photo[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into:
            res['response']['text'] = last_text + ". \n" + FORM
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "узбечка":
            res['response']['text'] = "Узбечка. \n" + FORM
            last_text = "Узбечка"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "soho":
            res['response']['text'] = "Soho. \n" + FORM
            last_text = "Soho"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "меню":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = TO_EAT
            res['response']['buttons'] = get_buttons(TO_EAT_BUTTONS)
            return
    elif stage == 4:
        if into and req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = HOTEL
            into = False
            res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "информация":
            res['response']['text'] = info[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "местоположение":
            res['response']['text'] = gps[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into and req['request']['original_utterance'].lower().strip() == "фотография":
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['text'] = ' '
            res['response']['image_id'] = photo[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into:
            res['response']['text'] = last_text + ". \n" + FORM
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "вишневая гора":
            res['response']['text'] = "Вишневая гора. \n" + FORM
            last_text = "Вишневая гора"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "wild west":
            res['response']['text'] = "Wild West. \n" + FORM
            last_text = "Wild West"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "меню":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = HOTEL
            res['response']['buttons'] = get_buttons(HOTEL_BUTTONS)
            return
    elif stage == 5:
        coords1 = existing_object(req['request']['original_utterance'].lower().strip())
        if req['request']['original_utterance'].lower().strip() == "назад":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        elif req['request']['original_utterance'].lower().strip() == "помощь":
            res['response']['text'] = TIME_
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
        elif not (coords1 is None):
            time = parsing(coords1, coords2, 'auto')
            if time:
                res['response']['text'] = 'Предполагаемое время пути: ' + time + '.\nМ' + MAIN[15:]
                res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            else:
                res['response']['text'] = 'Произошла ошибка.\nМ' + MAIN[15:]
                res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        else:
            res['response']['text'] = TIME_
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
    elif req['request']['original_utterance'].lower().strip() == "саратов":
        stage = 1
        res['response']['text'] = SARATOV
        res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
        return
    elif req['request']['original_utterance'].lower().strip() == "достопримечательности":
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
        params = {'geocode': adress,
                  'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                  'format': 'json'
                  }
        response = requests.get(url, params=params).json()
        ans1 = response['response']['GeoObjectCollection']['featureMember']
        ans = ans1[0]['GeoObject']['Point']['pos'].split()
        return ans
    except Exception:
        return None


coords2 = existing_object('Саратов')
if __name__ == '__main__':
    app.run()
