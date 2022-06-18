'''
    description  : ...
    Author       : @devon
    Date         : 2022-06-03 17:56:53
    LastEditors  : @devon
    Version      : 2.0
    GitHub       : https://github.com/devon-dlq?tab=repositories&type=source
    LastEditTime : 2022-06-05 18:38:04
    FilePath     : \\Python\\myy\\Experiment1\\main.py
    Copyright (C) 2022 devon. All rights reserved.
'''

import re

# 文件读入
f = open("words.txt", mode="r", encoding="UTF-8")
strr = f.read()
f.close()

# 归属地匹配
keyaddress = "(([\u4e00-\u9fa5]*\d*[a-zA-Z]*)*[厦][门]([\u4e00-\u9fa5]*\d*[a-zA-Z]*)*)"
address = re.findall(keyaddress, strr)
for i in address:
    print(i[0], end=" ")
print("")

# 文字说明及号码匹配
keynum = "([\u4e00-\u9fa5a-zA-Z][\u4e00-\u9fa5a-zA-Z ]*[：:]*\+*(\d{1,}(-\d*){1,}([，,]*\+*\d*(-\d){1,})*|\d{7,}([，," \
         "]*\+*\d*)*)) "
#                  中英文文字说明                     +::可有可无                     号码及多个号码识别处理
ans = re.findall(keynum, strr)
# 去除特殊账号及输出
for i in ans:
    if (i[0].find("电子邮箱", 0, len(
            i[0])) == -1 & i[0].find("邮政编码", 0, len(i[0])) ==
            -1 & i[0].find("mail", 0, len(i[0])) ==
            -1 & i[0].find("微信", 0, len(i[0])) ==
            -1 & i[0].find("vx", 0, len(i[0])) ==
            -1 & i[0].find("备", 0, len(i[0])) ==
            -1 & i[0].find("QQ", 0, len(i[0])) ==
            -1 & i[0].find("qq", 0, len(i[0])) == -1):
        # 排除电子邮箱、邮箱、微信号、备案号、QQ号
        print(i[0])
