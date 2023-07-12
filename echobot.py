import requests
import json
import os

token = os.environ['token']


def handler(event, context):
    body = json.loads(event['body'])
    message = body['message']

    if 'text' in message:
        process_text_message(message)
    elif 'photo' in message:
        process_photo_message(message)
    elif 'document' in message:
        process_document_message(message)
    elif 'voice' in message:
        process_voice_message(message)


def process_text_message(message):
    chat_id = message['from']['id']
    text = message['text']
    send_message(chat_id, text)


def process_photo_message(message):
    chat_id = message['from']['id']
    photo = message['photo'][-1]  # Получаем последнюю доступную фотографию (самую большую)
    photo_id = photo['file_id']
    send_photo(chat_id, photo_id)


def process_document_message(message):
    chat_id = message['from']['id']
    document = message['document']
    document_id = document['file_id']
    send_document(chat_id, document_id)


def process_voice_message(message):
    chat_id = message['from']['id']
    voice = message['voice']
    voice_id = voice['file_id']
    send_voice(chat_id, voice_id)


def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot' + token + '/' + 'sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, data=data)


def send_photo(chat_id, photo_id):
    url = 'https://api.telegram.org/bot' + token + '/' + 'sendPhoto'
    data = {'chat_id': chat_id, 'photo': photo_id}
    r = requests.post(url, data=data)


def send_document(chat_id, document_id):
    url = 'https://api.telegram.org/bot' + token + '/' + 'sendDocument'
    data = {'chat_id': chat_id, 'document': document_id}
    r = requests.post(url, data=data)


def send_voice(chat_id, voice_id):
    url = 'https://api.telegram.org/bot' + token + '/' + 'sendVoice'
    data = {'chat_id': chat_id, 'voice': voice_id}
    r = requests.post(url, data=data)
