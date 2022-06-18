'''
    description  : ...
    Author       : @devon
    Date         : 2022-06-03 17:56:53
    LastEditors  : @devon
    Version      : 2.0
    GitHub       : https://github.com/devon-dlq?tab=repositories&type=source
    LastEditTime : 2022-06-05 19:18:35
    FilePath     : \\Python\\myy\\Experiment3\\bloom.py
    Copyright (C) 2022 devon. All rights reserved.
'''
from pybloom_live import ScalableBloomFilter


class bloom():
    '可自动变长伸缩的布隆过滤器,用于网页去重及信息去重'

    def __init__(self) -> None:
        self.bloom = ScalableBloomFilter(initial_capacity=1e7 + 100,
                                         error_rate=0.001)

    def Bloom(self, cntstr: str):
        if cntstr not in self.bloom:
            '如当前字符串不在布隆过滤器中'
            self.bloom.add(cntstr)
            '加入布隆过滤器'
            return 1
            '返回1'
        return 0
        '重复则返回0'
