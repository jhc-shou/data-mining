import asyncio
import base64
import requests

from python3_anticaptcha import ImageToTextTask, CallbackClient
from python3_anticaptcha import errors

ANTICAPTCHA_KEY = ""


result = ImageToTextTask.ImageToTextTask(
    anticaptcha_key=ANTICAPTCHA_KEY, save_format="const"
).captcha_handler(captcha_link="https://images-na.ssl-images-amazon.com/captcha/cdkxpfei/Captcha_nxsfmrtgdz.jpg")
print(result)

# Пример который показывает работу антикапчи при решении капчи-изображением и сохранением её в качестве ВРЕМЕННОГО файла
# Протестировано на Линуксах. Не используйте данный вариант на Windows! Возможно починим, но потом.
# Example for working with captcha-image like a temporary file. Tested on UNIX-based systems. Don`t use it on Windows!
result = ImageToTextTask.ImageToTextTask(anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(
    captcha_link="https://images-na.ssl-images-amazon.com/captcha/cdkxpfei/Captcha_nxsfmrtgdz.jpg"
)
print(result)