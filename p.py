from bs4 import BeautifulSoup
import requests


def parsing(coords1, coords2, type):
    url = 'https://yandex.ru/maps/?'
    params = {'ll': '37.833217,55.659301',
              'mode': 'routes',
              'rtext': '~'.join([','.join(coords1[::-1]), ','.join(coords2[::-1])]),
              'rtt': type,
              'ruri': '~',
              'z': '9.25'}
    try:
        response = requests.get(url, params=params).text
        soup = BeautifulSoup(response, 'html.parser')
        ans1 = str(soup.find('div', class_='auto-route-snippet-view__route-title-primary'))
        ans = ans1[ans1[:-1].rfind('>') + 1:-6]
        return ans
    except Exception:
        if response:
            print('Ошибка нахождения пути')
        else:
            print('Код состояния: ' + str(response.status_code))
        return None
