'''
    description  : ...
    Author       : @devon
    Date         : 2022-06-03 17:56:53
    LastEditors  : @devon
    LastEditTime : 2022-06-05 18:33:37
    FilePath     : \\Python\\myy\\Experiment2\\get_data.py
    Copyright (C) 2022 devon. All rights reserved.
'''
import random

chars = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm0123456789.,/?+=-!@#$%^&*()><:;"
"""字符库：字母数字以及一些常用符号"""


def random_str(length):
    """单字符串生成函数，生成随即长度的str"""
    target = ""
    chars_length = len(chars) - 1
    if length > 0:
        for _ in range(length):
            tmp_str = chars[random.randint(0, chars_length)]
            target += tmp_str
        return target
    else:
        raise IndexError()


def random_strfile(n):
    """生成n行字符串并写入文件中"""
    file = open("randomstr.txt", 'w')
    for _ in range(1, n + 1):
        cntstr = random_str(random.randint(1, 31))
        file.write(cntstr + '\n')
    file.close()


if __name__ == '__main__':
    n = int(input("请输入要生成的字符串数量： "))
    random_strfile(n)
