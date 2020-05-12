from flask import Flask, request
from d import get_distance
import logging
import requests
import json
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


# заготовки кнопок
BACK_BUTTONS = ["Меню"]
MAIN_BUTTONS = ["Саратов", "Достопримечательности", "Поесть", "Отели и хостелы", "Сколько ехать"]
ATTRACTIONS_BUTTONS = ["Журавли (памятник)", "Саратовская консерватория", "Храм «Утоли мои печали»", "Меню"]
TO_EAT_BUTTONS = ["Узбечка", "Soho", "Панорама", "Меню"]
HOTEL_BUTTONS = ["Вишневая гора", "Wild West", "Бутик-Отель Абсолют", "Отель Богемия на Вавилова", "Меню"]
SARATOV_BUTTONS = ["Информация про Саратов", "Фотография", "Меню"]
FORM_BUTTONS = ["Информация", "Фотография", "Местоположение", "Назад"]


# некоторая информация об объектах
gps = {"Журавли (памятник)": 'Парк Победы', "Саратовская консерватория": "просп. Кирова, 1",
       "Узбечка": "ул. Соколовая 10/16",
       "Soho": "ул. Октябрьская 5",
       "Вишневая гора": "2-й Аптечный пр. 11",
       "Wild West": "1-й пр. Танкистов, 40",
       "Отель Богемия на Вавилова": "Железнодорожная ул.72",
       "Бутик-Отель Абсолют": "Мясницкая Улица 128",
       "Панорама": "улица Аэропорт, 5А",
       "Храм «Утоли мои печали»": "Радищева, дом 24"}
photo = {'Саратов': "213044/5d64c2229eb3dde015f5",
         "Журавли (памятник)": '937455/74579a8293399813c897',
         "Саратовская консерватория": "1652229/1a6ceb58ab1693a20527",
         "Узбечка": "1521359/4ededc1bc94cca81579b",
         "Soho": "1521359/18170c9855850ad3d69f",
         "Вишневая гора": "965417/bbb43db199b7437db171",
         "Wild West": "1540737/dbd7b29d347117f91879",
         "Отель Богемия на Вавилова": "1030494/6b2c82ccd987ac067adb",
         "Бутик-Отель Абсолют": "1540737/181911d79350d1dc38d5",
         "Панорама": "1030494/abdea09c18845d8ef0ae",
         "Храм «Утоли мои печали»": "1030494/26d637967131f6269ae2"}
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
        "Храм «Утоли мои печали»": "Церковь возведена в 1906 году. Внешний вид её напоминает столичный собор Василия "
                                   "Блаженного. Благодаря своей красоте храм не был разрушен во времена советского "
                                   "союза — большевики не стали сносить здание, решив открыть в нём планетарий, который"
                                   " просуществовал до конца ХХ века. В 2008 году церковь была отреставрирована и "
                                   "сейчас в ней ведутся богослужения. Архитектор Зыбин, при строительстве этого храма"
                                   " взял за основу московский Собор Василия Блаженного, в конечном итоге у него "
                                   "получилась уменьшенная, но не менее эффектная копия этого столичного собора.",
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
        "Панорама": "Панорамный ресторан занял первое место в нашем списке. Своей популярностью он обязан удачному "
                    "расположению рядом со смотровой площадкой. Из окон открывается вид на город, который особенно "
                    "завораживает вечером, когда загораются тысячи огней, и на мосту через Волгу включается подсветка."
                    " Помещение разделено на 5 залов. Есть открытая терраса. Здесь проводят любые мероприятия: отмечают"
                    " помолвки и выпускные вечера, справляют юбилеи, ужинают в семейном кругу. Интерьер в пастельных"
                    " тонах, выполнен в современном стиле. Кухня смешанная, многонациональная. В меню представлены "
                    "европейские, кавказские, итальянские, русские блюда. Не обходится и без авторских деликатесов "
                    "от известного саратовского шеф-повара. Большое разнообразие крепких алкогольных напитков и "
                    "коктейлей позволит отдохнуть и расслабиться. В заведении есть сцена для выступления "
                    "профессиональных музыкантов, танцпол, караоке. «Панорама» − очень популярное место, где "
                    "празднуется большое количество свадеб. Ресторан располагает собственной охраняемой территорией, на"
                    " которой предусмотрены парковочные места. Он открыт с 11 до полуночи, но если клиент "
                    "задерживается, то продолжает работу. Телефон администратора: 8 8452 75 40 65.",
        "Soho": "Ресторан находится в старинном особняке XIX века. Если снаружи "
                "сохранился стиль той эпохи, то попадая внутрь, поражает ультрасовременный дизайн. Шеф-повар сочетает "
                "несколько кухонь, постоянно экспериментирует и создает оригинальные блюда, которых нет ни в одном"
                "другом ресторане Саратова. Авторские десерты вызовут незабываемый гастрономический "
                "восторг. Мясо и рыба жарятся в углевой печи. В меню включены пицца и бургеры, горячие закуски, салаты."
                "Алкогольная карта обширна. Развлекательные мероприятия проводятся регулярно. Это выступления "
                "известных диджеев страны, яркие шоу-программы, конкурсы, мастер-классы. Для гостей есть караоке и "
                "ночной танцпол. Цены достаточно высокие, но всегда можно воспользоваться действующими предложениями. "
                "Так, в день рождения именинник получает 20% скидки.  Оно работает ежедневно с 12 часов до 00.00."
                "В пятницу и субботу закрывается в 03.00. Телефон для бронирования столика: 8 8452 71 71 71.",
        "Вишневая гора": "Парк-отель «Вишневая гора» расположен в Саратове. К услугам гостей сауна, оздоровительный и "
                         "спа-центр, бесплатный Wi-Fi и ресторан, где подают блюда украинской, венгерской и европейской"
                         " кухни. Гостям предлагаются номера с кондиционером, телевизором с плоским экраном и "
                         "кабельными каналами, сейфом, холодильником и собственной ванной комнатой с душем. Среди "
                         "прочих удобств отеля — бар, круглосуточная стойка регистрации, турецкая паровая баня, "
                         "банкетный зал и боулинг. Расстояние до железнодорожного вокзала и аэропорта Саратова "
                         "составляет 4 км, а до центр города — 6 км.",
        "Wild West": "Отель Wild West расположен в городе Саратов. К услугам гостей бар и бесплатная частная парковка "
                     "на территории отеля. Предоставляется бесплатный Wi-Fi.В номерах в распоряжении гостей телевизор "
                     "с плоским экраном и собственная ванная комната с халатами и тапочками. В улучшенных номерах "
                     "установлена гидромассажная ванна. В гостинице Wild West работает круглосуточная стойка "
                     "регистрации.",
        "Отель Богемия на Вавилова": "Этот отель расположен в Саратове, всего в 300 метрах от Драматического театра. "
                                     "В каждом номере есть телевизор с плоским экраном. Места на бесплатной парковке "
                                     "предоставляются по предварительному запросу.В номерах отеля «Богемия на Вавилова»"
                                     " есть рабочий стол, холодильник и собственная ванная комната. В некоторых номерах"
                                     " установлена гидромассажная ванна. В отеле «Богемия на Вавилова» сервируют сытный"
                                     " завтрак «шведский стол». В ресторане отеля можно отведать блюда местной кухни. "
                                     "Отель «Богемия на Вавилова» находится всего в нескольких минутах ходьбы от "
                                     "Детского парка.",
        "Бутик-Отель Абсолют": "Отель «Абсолют» расположен в Саратове. В отеле оборудованы сауна и хаммам, работает "
                               "ресторан. Во всех номерах установлены телевизоры с плоским экраном и спутниковыми "
                               "каналами. Гостям предоставляют халаты и тапочки."
        }


# заготовки частоиспользуемых фраз
MAIN = 'Я хочу вам рассказать о Саратове. \n ' \
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
              "Журавли (памятник),\n" \
              "Саратовская консерватория. \n" \
              "Храм «Утоли мои печали» \n" \
              "Если хотите вернуться в меню, то напишите 'Меню'"
TO_EAT = "По моему мнению в Саратове самые лучшие рестораны это: \n" \
         "Узбечка \n" \
         "Soho \n" \
         "Панорама \n" \
         "Так как сейчас разгар пандемии, то возможны некоторые корректировки в работе этих заведений, а также " \
         "лучше всего заказывать онлайн: через develery club или яндекс еду" \
         ". \nЕсли хотите вернуться в меню, то напишите 'Меню'"
HOTEL = "По моему мнению в Саратове самые основные отели и хостелы это:\n" \
        "Вишневая гора \n" \
        "Wild West. \n" \
        "Бутик-Отель Абсолют \n" \
        "Отель Богемия на Вавилова \n" \
        "Если хотите вернуться в меню, то напишите 'Меню'"
TIME_ = "Чтобы узнать, насколько далеко до Саратова, напишите город или" \
        " адрес, откуда вы планируете отправляться. \nЕсли хотите вернуться в меню, то напишите 'Меню'"
FORM = "Напишите: \n" \
          "'Информация' - если хотите узнать информацию про этот объект, \n" \
          "'Фотография' - если хотите увидеть фотографию этого объекта,\n" \
          "'Местоположение' - если хотите узнать где это находится." \
          "\nЕсли хотите вернуться назад, то напишите 'Назад'"


# важные переменные, следящие за ходом диалога
stage = 0
into = False
last_text = ""


# функция формирующая ответы
def handle_dialog(req, res):
    global stage, into, last_text
    user_id = req['session']['user_id']
    # саратов
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
            res['response']['text'] = ' '
            res['response']['card']['image_id'] = photo['Саратов']
            res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
            return
        else:
            res['response']['text'] = SARATOV
            res['response']['buttons'] = get_buttons(SARATOV_BUTTONS)
            return
    # достопримечательности
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
            res['response']['card']['image_id'] = photo[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into:
            res['response']['text'] = last_text + ". \n" + FORM
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif (req['request']['original_utterance'].lower().strip() in ["журавли (памятник)",
                                                                       "саратовская консерватория"]):
            name = req['request']['original_utterance'].lower().strip()[0].upper() + \
                   req['request']['original_utterance'].lower().strip()[1:]
            res['response']['text'] = f"{name}. \n" + FORM
            last_text = f"{name}"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "храм «утоли мои печали»":
            res['response']['text'] = "Храм «Утоли мои печали». \n" + FORM
            last_text = "Храм «Утоли мои печали»"
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
    # поесть
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
            res['response']['card']['image_id'] = photo[last_text]
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif into:
            res['response']['text'] = last_text + ". \n" + FORM
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() in ["узбечка", "soho", "панорама"]:
            name = req['request']['original_utterance'].lower().strip()[0].upper() + \
                   req['request']['original_utterance'].lower().strip()[1:]
            res['response']['text'] = f"{name}. \n" + FORM
            last_text = f"{name}"
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
    # отели и хостелы
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
            res['response']['card']['image_id'] = photo[last_text]
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
        elif req['request']['original_utterance'].lower().strip() == "отель богемия на вавилова":
            res['response']['text'] = "Отель Богемия на Вавилова. \n" + FORM
            last_text = "Отель Богемия на Вавилова"
            into = True
            res['response']['buttons'] = get_buttons(FORM_BUTTONS)
            return
        elif req['request']['original_utterance'].lower().strip() == "бутик-отель абсолют":
            res['response']['text'] = "Бутик-Отель Абсолют. \n" + FORM
            last_text = "Бутик-Отель Абсолют"
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
    # сколько ехать
    elif stage == 5:
        coords1 = existing_object(req['request']['original_utterance'].lower().strip())
        distance = get_distance(coords1, coords2)
        if req['request']['original_utterance'].lower().strip() == "меню":
            res['response']['text'] = MAIN
            res['response']['buttons'] = get_buttons(MAIN_BUTTONS)
            stage = 0
            return
        elif req['request']['original_utterance'].lower().strip() == "помощь":
            res['response']['text'] = TIME_
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
            return
        elif not (coords1 is None):
            res['response']['text'] = 'До Саратова ' + str(int(distance)) + 'км.'
            res['response']['buttons'] = get_buttons(BACK_BUTTONS)
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
    # функция, дающая кнопки по их заголовкам
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in list(map(lambda x: x[0].upper() + x[1:], cur))]
    return suggests


def existing_object(adress):
    # функция, находящая координаты объекта, если он существует
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


# координаты Саратова
coords2 = existing_object('Саратов')
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
