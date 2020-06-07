import time
import requests
import urllib.request

def main():
    # токен
    token = 'a77ec976edae329e84b4eaaf023e96ff75dc456088a1acad8da4a646248b3c521ef5f0f1d10bbcf8b381f'

    # список групп для парсинга
    groups = ['hist_post', 'historymemestrue', 'historical_memes_ik', 'imperialsmeme', 'yes1488off', 'die_geschichte_fuhrers', 'armyironia', 'sieghoika']

    # id группы
    number_group = 0

    while True:

        # парсинг последнего поста в группе
        result = take_post(groups[number_group],token)

        # если есть вложения к посту
        if 'attachments' in result['response']['items'][0]:
            # если вложение всего одно
            if len(result['response']['items'][0]['attachments']) == 1:
                # если это вложение - фотография
                if 'photo' in result['response']['items'][0]['attachments'][0]:

                    # проверка на время
                    post_date = result['response']['items'][0]['date']
                    time_now = time.time()
                    delta_time = time_now - post_date

                    # если пост был опубликован не более 1800 секунд назад (30 минут)
                    if delta_time <= 3600:
                        img_url = result['response']['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
                        download_photo(img_url)
                        img_url = upload_image('img.jpg', token)
                        if result['response']['items'][0]['text'] == '':
                            wall_post('',token,img_url)
                        else:
                            wall_post(result['response']['items'][0]['text'],token,img_url)
                        time.sleep(3300)

                    # проверка 2 поста в группе (на случай если есть закрепленный пост)
                    else:
                        log('vk.com/' + groups[number_group] + ' превышен лимит по времени (1) на ' + str(delta_time))

                        # парсинг последнего поста в группе
                        result = take_post(groups[number_group],token,1)

                        # если есть вложения к посту
                        if 'attachments' in result['response']['items'][0]:
                            # если вложение всего одно
                            if len(result['response']['items'][0]['attachments']) == 1:
                                # если это вложение - фотография
                                if 'photo' in result['response']['items'][0]['attachments'][0]:

                                    # проверка на время
                                    post_date = result['response']['items'][0]['date']
                                    time_now = time.time()
                                    delta_time = time_now - post_date
                                    # если пост был опубликован не более 1800 секунд назад (30 минут)
                                    if delta_time <= 3600:
                                        img_url = result['response']['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
                                        download_photo(img_url)
                                        img_url = upload_image('img.jpg', token)
                                        if result['response']['items'][0]['text'] == '':
                                            wall_post('', token ,img_url)
                                        else:
                                            wall_post(result['response']['items'][0]['text'], token, img_url)
                                        time.sleep(3300)
                                    else:
                                        log('vk.com/' + groups[number_group] + ' превышен лимит по времени (2) на ' + str(delta_time))
                                        time.sleep(300)

        # если это последний id - обнуление id
        if number_group == len(groups)-1:
            number_group = 0
        else:
            number_group+=1

# введение логов для отслеживания работы программы
def log(message):
    f = open('log.txt', 'a')
    f.write('\n' + str(message) + time.strftime('\n%y.%m.%d %H:%M:%S') + '\n------------------------------------------------------')
    f.close()

# публикация поста на стене
def wall_post(message,token, img_url = ''):
    version = 5.107

    data={
        'access_token': token,
        'from_group': 1,
        'owner_id':-180808101,
        'message': message,
        'signed': 0,
        'attachments': img_url,
        'v':version}

    r = requests.post('https://api.vk.com/method/wall.post', data).json()

    log(r)

# получить пост со стены (по умолчанию первый)
def take_post(domain,token,offset = 0):
    version = 5.107
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'access_token': token,
                                'v': version,
                                'domain': domain,
                                'count' : 1,
                                'offset' : offset
                            })
    data = response.json()
    return data

# загрузка фотографии на сервер vk
def upload_image(img, token):
    version = 5.107
    server = requests.get('https://api.vk.com/method/photos.getWallUploadServer',
                        params={
                            'access_token': token,
                            'v': version,
                            'group_id': 180808101
                        })
    url = server.json()['response']['upload_url']
    data = requests.post(url, files = { 'photo': open('img/'+ img,'rb')}).json()
    response = (requests.post('https://api.vk.com/method/photos.saveWallPhoto',
                        params={
                            'access_token': token,
                            'v': version,
                            'group_id': 180808101,
                            'hash': data['hash'],
                            'server': data['server'],
                            'photo' : data['photo']
                        }).json())

    return 'photo'+ str(response['response'][0]['owner_id']) + '_' + str(response['response'][0]['id'])

# скачать фотографию на устройство
def download_photo(url):
    img = urllib.request.urlopen(url).read()
    out = open("img/img.jpg", "wb")
    out.write(img)
    out.close

if __name__ == '__main__':
   main()