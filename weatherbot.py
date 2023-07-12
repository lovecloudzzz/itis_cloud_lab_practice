import requests
import json
import datetime
import os


token = os.environ['token']
OpenWeather_token = os.environ['OpenWeather_token']
YandexSpeechKit_token = os.environ['YandexSpeechKit_token']
text_to_voice_url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
yandex_storage_token = os.environ['yandex_storage_token']
ApiKey = os.environ['ApiKey']
bucket = 'https://storage.yandexcloud.net/itiscl-spr23-07-weather/'
Auth = f'Api-Key {ApiKey}'
Auth_Header = {'Authorization': Auth}
BearerToken = os.environ['BearerToken']
BearerTokenHead = f'Bearer {BearerToken}'
BearerHeader = {'Authorization': BearerTokenHead}
folderId = os.environ['folderId']
folderId = f'{folderId}'


def handler(event, context):
    body = json.loads(event['body'])
    chat_id = body['message']['from']['id']
    command = body['message'].get('text')

    if command == '/start' or command == '/help':
        send_message(chat_id, 'Я сообщу вам о погоде в том месте, которое сообщите мне.\n'
                              'Я могу ответить на:\n'
                              '- Текстовое сообщение с названием населенного пункта.\n'
                              '- Голосовое сообщение с названием населенного пункта.\n'
                              '- Сообщение с точкой на карте.')
    else:
        if 'text' not in body['message'] and 'voice' not in body['message'] and 'location' not in body['message']:
            send_message(chat_id, 'Я не могу ответить на такой тип сообщения.')
        else:
            if 'text' in body['message']:
                weather = get_weather_by_type('text', body['message']['text'])
                if weather:
                    send_message(chat_id, weather)
                else:
                    text = body['message']['text']
                    send_message(chat_id, f'Я не нашел населенный пункт {text}')

            elif 'voice' in body['message']:
                voice_duration = body['message']['voice']['duration']
                if int(voice_duration) <= 30:
                    file_id = body['message']['voice']['file_id']
                    text = voice_to_text(file_id)
                    weather = get_weather_by_type('voice', text)
                    if weather:
                        response = text_to_voice(weather)
                        send_voice(chat_id, response)
                    else:
                        send_message(chat_id, f'Я не нашел населенный пункт {text}')
                else:
                    send_message(chat_id, 'Я не могу понять голосовое сообщение длительностью более 30 секунд.')

            elif 'location' in body['message']:
                weather = get_weather_by_type('location', body['message']['location'])
                if weather:
                    send_message(chat_id, weather)
                else:
                    send_message(chat_id, 'Я не знаю какая погода в этом месте.')


def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot' + token + '/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=data)


def send_voice(chat_id, voice):
    url = 'https://api.telegram.org/bot' + token + '/sendVoice'
    files = {'voice': voice}
    data = {'chat_id': chat_id}
    r = requests.post(url, data=data, files=files)


def get_weather_by_type(type, type_content):
    if type == 'text':
        response = get_weather(type_content, type)
    elif type == 'voice':
        response = get_weather(type_content, type)
    elif type == 'location':
        lat = type_content['latitude']
        lon = type_content['longitude']
        response = get_weather_by_location(lat, lon)

    return response


def get_weather(text, type):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={text}&appid={OpenWeather_token}&units=metric'
    response = requests.get(url).json()

    if response['cod'] == 200:
        description = response['weather'][0]['description']
        temperature = response['main']['temp']
        feels_like = response['main']['feels_like']
        pressure = round(response['main']['pressure'] * 0.75006375541921)
        humidity = response['main']['humidity']
        visibility = response['visibility']
        wind_speed = response['wind']['speed']
        wind_direction = response['wind']['deg']
        sunrise = response['sys']['sunrise']
        sunset = response['sys']['sunset']
        weather_description = weather_translations[description]
        temperature_str = str(round(temperature)) if type == 'voice' else str(temperature)
        feels_like_str = str(round(feels_like)) if type == 'voice' else str(feels_like)
        pressure_str = str(round(pressure)) if type == 'voice' else str(pressure)
        humidity_str = str(round(humidity)) if type == 'voice' else str(humidity)
        weather_message = f" Населенный пункт {text}.\n"
        weather_message += f"{weather_description}.\n"
        weather_message += f"Температура: {temperature_str} °C, ощущается как {feels_like_str} °C.\n" if type == 'text' else f"Температура {temperature_str}.\nОщущается как {feels_like_str}.\n"
        weather_message += f"Атмосферное давление: {pressure_str} мм рт. ст.\n" if type == 'text' else f"Давление {pressure_str}.\n"
        weather_message += f"Влажность: {humidity_str} %.\n" if type == 'text' else f"Влажность {humidity_str}.\n"
        if  type  == 'text':
            weather_message +=  f"Видимость: {visibility} метров.\n"
            weather_message += f"Ветер: {wind_speed} м/с {get_wind_direction(wind_direction)}.\n"
            weather_message += f"Восход солнца: {get_time_from_timestamp(sunrise)} МСК. Закат: {get_time_from_timestamp(sunset)} МСК."

        return weather_message
    else:
        return None


def get_weather_by_location(latitude, longitude):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OpenWeather_token}&units=metric'
    response = requests.get(url).json()

    if response['cod'] == 200:
        city = response['name']
        description = response['weather'][0]['description']
        temperature = response['main']['temp']
        feels_like = response['main']['feels_like']
        pressure = round(response['main']['pressure'] * 0.75006375541921)
        humidity = response['main']['humidity']
        weather_description = weather_translations[description]
        weather_message = f"Населенный пункт: {city}.\n"
        weather_message += f"{weather_description}.\n"
        weather_message += f"Температура: {temperature} °C, ощущается как {feels_like} °C.\n"
        weather_message += f"Давление: {pressure} мм рт. ст.\n"
        weather_message += f"Влажность: {humidity} %."

        return weather_message
    else:
        return None
    

def get_wind_direction(degree):
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    index = round(degree / 45) % 8

    return directions[index]



def get_time_from_timestamp(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    formatted_time = dt.strftime('%H:%M')

    return formatted_time



def voice_to_text(file_id):
    url = 'https://api.telegram.org/bot' + token + '/getFile'

    response = requests.post(url=url, json={'file_id': file_id})
    resp = response.json()['result']
    path = resp['file_path']
    file = requests.get(url=f'https://api.telegram.org/file/bot{token}/{path}')
    audio = file.content
    text = requests.post(url='https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
                          headers=Auth_Header,
                          data = audio)
    if text.ok:
        result = text.json()['result']

        return result
    else:
        return 'Ошибка'


def text_to_voice(text):
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": "alena",
        "emotion": "good",
        "speed": "1.0",
        "format": "oggopus",
        "folderId": folderId
    }

    response = requests.post(url, headers=BearerHeader, data=data)

    if response.status_code == 200:
        return response.content 
    else:
        return None  


weather_translations = {
    'thunderstorm with light rain': 'гроза с небольшим дождем',
    'thunderstorm with rain': 'гроза с дождем',
    'thunderstorm with heavy rain': 'гроза с сильным дождем',
    'light thunderstorm': 'легкая гроза',
    'thunderstorm': 'гроза',
    'heavy thunderstorm': 'сильная гроза',
    'ragged thunderstorm': 'рваная гроза',
    'thunderstorm with light drizzle': 'гроза с легкой моросью',
    'thunderstorm with drizzle': 'гроза с моросью',
    'thunderstorm with heavy drizzle': 'гроза с сильной моросью',
    'light intensity drizzle': 'легкая морось',
    'drizzle': 'морось',
    'heavy intensity drizzle': 'сильная морось',
    'light intensity drizzle rain': 'легкая моросящая дождь',
    'drizzle rain': 'моросящий дождь',
    'heavy intensity drizzle rain': 'сильный моросящий дождь',
    'shower rain and drizzle': 'проливной дождь и морось',
    'heavy shower rain and drizzle': 'сильный проливной дождь и морось',
    'shower drizzle': 'проливная морось',
    'light rain': 'легкий дождь',
    'moderate rain': 'умеренный дождь',
    'heavy intensity rain': 'сильный дождь',
    'very heavy rain': 'очень сильный дождь',
    'extreme rain': 'экстремальный дождь',
    'freezing rain': 'ледяной дождь',
    'light intensity shower rain': 'легкий дождь с прояснениями',
    'shower rain': 'ливень',
    'heavy intensity shower rain': 'сильный ливень',
    'ragged shower rain': 'ливень с порывами ветра',
    'light snow': 'небольшой снег',
    'snow': 'снег',
    'heavy snow': 'сильный снег',
    'sleet': 'дождь со снегом',
    'light shower sleet': 'небольшой дождь со снегом',
    'shower sleet': 'дождь со снегом',
    'light rain and snow': 'небольшой дождь со снегом',
    'rain and snow': 'дождь со снегом',
    'light shower snow': 'небольшой снегопад',
    'shower snow': 'снегопад',
    'heavy shower snow': 'сильный снегопад',
    'mist': 'дымка',
    'smoke': 'дым',
    'haze': 'туман',
    'sand/dust whirls': 'песчаные/пыльные вихри',
    'fog': 'туман',
    'sand': 'песок',
    'dust': 'пыль',
    'volcanic ash': 'вулканический пепел',
    'squalls': 'шквалы',
    'tornado': 'торнадо',
    'clear sky': 'ясное небо',
    'few clouds': 'небольшая облачность',
    'scattered clouds': 'рассеянная облачность',
    'broken clouds': 'облачно с прояснениями',
    'overcast clouds': 'пасмурно',
}
