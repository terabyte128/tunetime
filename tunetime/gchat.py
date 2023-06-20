import requests
import uuid

from tunetime.settings import SETTINGS


def send_chat_message(message: str):
    id = uuid.uuid4()
    url = f"{SETTINGS.chat_url}&threadKey={id}&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"

    requests.post(url, json={"text": message})
