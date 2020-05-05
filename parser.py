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
        ans = soup.find('div', class_='masstransit-route-snippet-view__route-duration')
        ans = ans[ans[:-1].rfind('>') + 1:-6]
        time = 0
        if 'ч' in ans:
            time += 60 * int(ans[:ans.find('ч') - 1])
        if 'мин' in ans:
            time += int(ans[max(0, ans.find('мин') - 3):ans.find('мин') - 1])
        return time
    except Exception:
        if response:
            print('Ошибка нахождения пути')
        else:
            print('Код состояния: ' + str(response.status_code))
        return None
