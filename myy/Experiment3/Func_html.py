from typing import List
from urllib import response
from bs4 import BeautifulSoup
import requests
import json
import re
import sys
from urllib.parse import urljoin
from utils import get_wrapped_url, encryptAES
'github开源项目'
from LAC import LAC
lac = LAC(mode="lac")
'姓名识别模式'


def get_htmls(session: requests.session, http_header, ip: str) -> List[str]:
    '获取福建省已备案的域名为xmu.edu.cn的各类主网页'
    """
    针对 https://chaziyu.com/xmu.edu.cn/ 特别编写的函数(可通过自动下拉加载完全)
    用于获取福建省已备案的域名为xmu.edu.cn的各类主网页
    """
    result = []
    params = {
        'domain': 'xmu.edu.cn',
        'page': 1
    }
    while True:
        params['page'] += 1
        resp = session.get(ip, params=params, headers=http_header).content
        resp_json = json.loads(resp)
        if len(resp_json['data']['result']) == 0:
            break
        result += ['https://' + i for i in resp_json['data']['result']]
    return result


def get_sub_domain_list(ip: str, html: response) -> List[str]:
    # 获取特定网页ip页面中的链接并补充完整
    """
    获取特定网页ip页面中的链接并补充完整
    """
    result = []
    key = r'((https?://[\w-]+(/[\w-]+)*(\.\w+){1,}(/[\w-]+)*(\.\w+)*/{0,1})|((\.\./){1,}[\w-]+(/[\w-]+){0,}(\.[\w-]+)*)|((\./){1,}[\w-]+(/[\w-]+){0,}(\.[\w-]+)*)|((/){1,}[\w-]+(/[\w-]+){1,}(\.[\w-]+)*)|([\w-]+(/[\w-]+){1,}(\.[\w-]+)*))'
    result = re.findall(key, html)
    final_result = []
    for i in result:
        # 过滤掉必然无用的链接
        if (('.css' not in i[0].lower()) and ('.js' not in i[0].lower()) and ('.jpg' not in i[0].lower())
           and ('.png' not in i[0].lower()) and ('.gif' not in i[0].lower()) and ('.jpeg' not in i[0].lower())
           and ('.docx' not in i[0].lower()) and ('.pdf' not in i[0].lower()) and ('.xlsx' not in i[0].lower())
           and ('.doc' not in i[0].lower()) and ('.mp4' not in i[0].lower()) and ('.mp3' not in i[0].lower())
           and ('.zip' not in i[0].lower()) and ('.rar' not in i[0].lower()) and ('.wav' not in i[0].lower())
           and ('.mov' not in i[0].lower()) and ('.bmp' not in i[0].lower())):
            try:
                final_result.append(urljoin(ip, i[0]))
                # 调库函数补充完整链接
                # 相对链接->完整链接  空链接->原ip链接  完整链接->该完整链接
            except:
                pass
    return final_result


def get_telephone(content: str):
    # 正则匹配电话号码
    """
    匹配格式:
    1.常见手机号: 11位数字 or +86-xxxxxxxxxxx 且需要符合运营商号码段
    2.常见座机 xxx-xxxxxxx or xxxx-xxxxxxx or xxxxxxx or +86-xxxxxxx等
    """
    keynum = r"([\u4e00-\u9fa5a-zA-Z  ]+ * *[:：] * *((\+86-)* * *((\d{7})|(\d{3,4}-\d{5,8}))| ((\+86)? ^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}))(([,，] * *((\+86-)* * *((\d{7})|(\d{3,4}-\d{5,8}))|((\+86)?^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}))))*(?!\d))"
    return re.findall(keynum, content)

# 正则匹配邮箱


def get_email(content: str):
    """
    匹配格式:
    1.常见邮箱: 数字/字母/下划线 + @ + (qq/163/126/…) + .com
    2.厦大等企业邮箱: 数字/字母/下划线 + @ + xxx.xxx.xx
    3.特殊抽查到的邮箱:用'#'或'(AT)'等替代'@', dot或。代替.等
    """
    keynum = r"(([\u4e00-\u9fa5a-zA-Z  ]+ * *[:：]){0,1} * *[a-zA-Z0-9_-]+ *(@|(\(AT\))|#|(（AT）)|(\[AT\])|(\(at\))|(\[at\])) *[a-zA-Z0-9_-]+((\.|。|(\[dot\])|(\(dot\)))[a-zA-Z0-9_-]+)+)"
    return re.findall(keynum, content)

# LAC匹配姓名


def extract_name(sentence: str, type='lac'):
    user_name_lis = []
    if type == 'lac':
        try:
            _result = lac.run(sentence)
        except:
            return None
        for _index, _label in enumerate(_result[1]):
            if _label == "PER":
                user_name_lis.append(_result[0][_index])
    else:
        return None
    return user_name_lis


# 检测字符串是否疑似新闻


def news_check(sentence: str):
    if (('通知' in sentence) or ('关于' in sentence) or ('举办' in sentence) or ('公告' in sentence)
            or ('简章' in sentence) or ('开展' in sentence) or ('名单' in sentence) or ('推荐' in sentence)
            or ('启事' in sentence) or ('方案' in sentence) or ('公示' in sentence) or ('规定' in sentence)
            or ('证明' in sentence) or ('可以' in sentence) or ('怎么' in sentence) or ('召开' in sentence)
            or ('第' in sentence and '届' in sentence) or ('可以' in sentence) or ('报名指南' in sentence)
            or ('举行' in sentence) or ('发文' in sentence) or ('揭示' in sentence) or ('专场' in sentence)
            or ('主题教育' in sentence) or ('征文' in sentence) or ('征稿' in sentence) or ('获得' in sentence)
            or ('案例' in sentence) or ('论文' in sentence) or ('主讲' in sentence) or ('使用' in sentence)
            or ('大数据技术原理与应用' in sentence) or ('需求' in sentence) or ('预告' in sentence)
            or ('办法' in sentence) or ('年会' in sentence) or ('讲座' in sentence) or ('一封信' in sentence)
            or ('blog' in sentence) or ('联谊' in sentence) or ('招募' in sentence) or ('招聘' in sentence)
            or ('预告' in sentence) or ('邀请' in sentence) or ('名单' in sentence) or ('说明' in sentence)
            or ('课堂' in sentence) or ('开班' in sentence) or ('开始' in sentence) or ('手册' in sentence)
            or ('宣传册' in sentence) or ('截止' in sentence) or ('如何' in sentence) or ('发布' in sentence)
            or ('分享' in sentence) or ('温馨提示' in sentence) or ('流程' in sentence) or ('工程建设' in sentence)
            or ('宣讲' in sentence) or ('实习' in sentence) or ('分享' in sentence) or ('基金' in sentence)
            or ('双选会' in sentence) or ('什么' in sentence) or ('申请指南' in sentence) or ('考试' in sentence)
            or ('学期' in sentence) or ('措施' in sentence) or ('诚聘' in sentence) or ('班级主页' in sentence)
            or ('申请材料' in sentence) or ('倡议' in sentence) or ('总结' in sentence) or ('解答' in sentence)
            or ('问题' in sentence) or ('上线' in sentence) or ('须知' in sentence) or ('细则' in sentence)
            or ('奖学金' in sentence) or ('助学金' in sentence) or ('校招' in sentence) or ('招收' in sentence)
            or ('通告' in sentence) or ('浅谈' in sentence) or ('试谈' in sentence) or ('报到' in sentence)
            or ('征求' in sentence) or ('讲述' in sentence) or ('交流项目' in sentence) or ('暑期项目' in sentence)
            or ('研究生项目' in sentence) or ('当代' in sentence) or ('办事指南' in sentence) or ('相关信息' in sentence)
            or ('聚焦' in sentence) or ('整改' in sentence) or ('故事' in sentence) or ('博客' in sentence)
            or ('实例' in sentence) or ('援教' in sentence) or ('报考' in sentence) or ('寄语' in sentence)
            or ('公派项目' in sentence) or ('住宿申请' in sentence) or ('庆贺' in sentence) or ('快讯' in sentence)
            or ('庆贺' in sentence) or ('讣告' in sentence) or ('【' in sentence) or ('庆贺' in sentence)
            or ('主题系列活动' in sentence) or ('防灾' in sentence) or ('中文版' in sentence) or ('回执' in sentence)
            or ('总有' in sentence) or ('课表' in sentence) or ('庆贺' in sentence) or ('注意' in sentence)
            or ('审批' in sentence) or ('难忘' in sentence) or ('毕业季' in sentence) or ('参著' in sentence)
            or ('学刊' in sentence) or ('简讯' in sentence) or ('年庆' in sentence) or ('征集' in sentence)
            or ('快讯' in sentence) or ('最新' in sentence) or ('审批' in sentence) or ('启动' in sentence)
            or ('精彩' in sentence) or ('表彰' in sentence) or ('调剂' in sentence) or ('情缘' in sentence)
            or ('初试' in sentence) or ('复试' in sentence) or ('启动' in sentence) or ('期刊' in sentence)
            or ('古籍' in sentence) or ('诚邀' in sentence) or ('文献' in sentence) or ('选拔' in sentence)
            or ('党课' in sentence) or ('党史' in sentence) or ('党建' in sentence) or ('落幕' in sentence)
            or ('圆满' in sentence) or ('全新' in sentence) or ('等你' in sentence) or ('基于' in sentence)
            or ('返校' in sentence) or ('开学' in sentence) or ('假期' in sentence) or ('招租' in sentence)
            or ('洞悉' in sentence) or ('好专业' in sentence)):
        return 1
    return 0


# 用于登录厦门大学信息门户
"""
开源项目代码部分声明:
本部分函数及utils文件来源于github开源项目-每日自动健康打卡程序中的登录部分略作改动
原作者:kirainmoe
源项目链接:https://github.com/kirainmoe/auto-daily-health-report
"""


def login(session, username, password, http_header, use_webvpn=False):
    """
    用于登录厦门大学信息门户（部分网站页面访问需要登录）
    https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu
    """
    try:
        oauth_login_url = get_wrapped_url(
            "https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu", use_webvpn)
        resp = session.get(oauth_login_url, headers=http_header)

        soup = BeautifulSoup(resp.text, 'html.parser')  # 把网页解析为BeautifulSoup对象
        # 获取对应位置信息
        lt = soup.select('input[name="lt"]')[0]["value"]
        dllt = soup.select('input[name="dllt"]')[0]['value']
        execution = soup.select('input[name="execution"]')[0]['value']
        salt = soup.select('input#pwdDefaultEncryptSalt')[0]['value']
        # 登录信息
        login_data = {
            "username": username,
            "password": encryptAES(password, salt),
            "lt": lt,
            "dllt": dllt,
            "execution": execution,
            "_eventId": "submit",
            "rmShown": 1
        }
        # 请求登录
        session.post(oauth_login_url, login_data, headers=http_header, allow_redirects=True)
        # will redirect to https://xmuxg.xmu.edu.cn
    except KeyError:
        print(json.dumps({
            "status": "failed",
            "reason": "Login failed (server error)"
        }, indent=4))  # 服务器异常，学工系统可能又双叒叕崩溃了
        sys.exit(1)
