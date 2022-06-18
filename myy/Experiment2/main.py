'''
    description  : ...
    Author       : @devon
    Date         : 2022-06-03 17:56:53
    LastEditors  : @devon
    Version      : 2.0
    GitHub       : https://github.com/devon-dlq?tab=repositories&type=source
    LastEditTime : 2022-06-05 19:17:05
    FilePath     : \\Python\\myy\\Experiment2\\main.py
    Copyright (C) 2022 devon. All rights reserved.
'''
import os
import psutil
from pybloom_live import ScalableBloomFilter


def init_bloom():
    bloom = ScalableBloomFilter(initial_capacity=1e7 + 100, error_rate=0.001)
    file_data = open("randomstr.txt", "r")
    while True:
        cntstr = file_data.readline()
        cntstr = cntstr.rstrip()
        if not cntstr:
            break
        bloom.add(cntstr)
    file_data.close()
    return bloom


if __name__ == '__main__':
    file_data = open("randomstr.txt", "a")
    strr = input("请输入一串字符(输入回车结束)：")
    bloom = init_bloom()
    while strr != "":
        if strr in bloom:
            print("False 数据已存在。")
        else:
            bloom.add(strr)
            file_data.write(strr + '\n')
            print("True 数据存入成功")
        strr = input()
    file_data.close()
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    print(info.uss / 1024. / 1024. / 1024.)
