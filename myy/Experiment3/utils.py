import base64
import random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
'''
    description  : ...
    Author       : @devon
    Date         : 2022-06-03 17:56:53
    LastEditors  : @devon
    Version      : 2.0
    GitHub       : https://github.com/devon-dlq?tab=repositories&type=source
    LastEditTime : 2022-06-05 19:31:21
    FilePath     : \\Python\\myy\\Experiment3\\utils.py
    Copyright (C) 2022 devon. All rights reserved.
'''
"""
开源项目代码部分声明:
utils文件及login函数来源于github开源项目-每日自动健康打卡程序中的登录部分略作改动
原作者:kirainmoe
源项目链接:https://github.com/kirainmoe/auto-daily-health-report
"""


def get_wrapped_url(url, webvpn=False):
    if not webvpn:
        return url
    if "ids.xmu.edu.cn" in url:
        return url.replace(
            "ids.xmu.edu.cn",
            '''webvpn.xmu.edu.cn/https/77726476706e697374686562
                           65737421f9f352d23f3d7d1e7b0c9ce29b5b''')
    if "xmuxg.xmu.edu.cn" in url:
        return url.replace(
            "xmuxg.xmu.edu.cn",
            '''webvpn.xmu.edu.cn/https/77726476706e6973746865626573742
                           1e8fa5484207e705d6b468ca88d1b203b''')


def encryptAES(data: str, salt: str):
    salt = salt.encode('utf-8')
    iv = randstr(16).encode('utf-8')
    cipher = AES.new(salt, AES.MODE_CBC, iv)
    data = randstr(64) + data
    data = data.encode('utf-8')
    data = pad(data, 16, 'pkcs7')
    cipher_text = cipher.encrypt(data)
    encoded64 = str(base64.encodebytes(cipher_text),
                    encoding='utf-8').replace("\n", "")
    return encoded64


def randstr(num):
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt
