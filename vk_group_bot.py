import time
import requests
import urllib.request

def main():
    # токен
    token = 'твой токен'

    # максимальная разница во времени между опубликованным постом и настоящим временем в секундах (1 час - 3600 сек)
    time_for_parsing = 3600
    # время ожидания после публикации поста, чтобы постить посты с интервалами во времени
    time_for_sleep = 3300
    # время ожидания после неудачного парсинга группы
    time_for_before_post = 300

    # список групп для парсинга
    groups = ['group1', 'group2', 'group3'] #vk.com/group1, vk.com/group2, vk.com/group3

    # id группы
    number_group = 0

    # бессконечный цикл
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

                    # если пост был опубликован не более time_for_parsing секунд назад
                    if delta_time <= time_for_parsing:
                        img_url = result['response']['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
                        download_photo(img_url)
                        img_url = upload_image('img.jpg', token)
                        if result['response']['items'][0]['text'] == '':
                            wall_post('',token,img_url)
                        else:
                            wall_post(result['response']['items'][0]['text'],token,img_url)
                        time.sleep(time_for_sleep)

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
                                    # если пост был опубликован не более time_for_parsing секунд назад
                                    if delta_time <= time_for_parsing:
                                        img_url = result['response']['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
                                        download_photo(img_url)
                                        img_url = upload_image('img.jpg', token)
                                        if result['response']['items'][0]['text'] == '':
                                            wall_post('', token ,img_url)
                                        else:
                                            wall_post(result['response']['items'][0]['text'], token, img_url)
                                        time.sleep(time_for_sleep)
                                    else:
                                        log('vk.com/' + groups[number_group] + ' превышен лимит по времени (2) на ' + str(delta_time))
                                        time.sleep(time_for_before_post)

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
        'owner_id': -id_твоей_группы,
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
                            'group_id': id_твоей_группы
                        })
    url = server.json()['response']['upload_url']
    data = requests.post(url, files = { 'photo': open('img/'+ img,'rb')}).json()
    response = (requests.post('https://api.vk.com/method/photos.saveWallPhoto',
                        params={
                            'access_token': token,
                            'v': version,
                            'group_id': id_твоей_группы,
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