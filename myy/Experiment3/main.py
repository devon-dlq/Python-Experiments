"""
程序说明:因爬虫爬取的为厦大相关网站,故特别依赖网络环境
建议使用校园网或VPN
如网络情况较差请将main.py line56中的timeout适当做修改,
否则部分含有较大文件、图片的网页将有可能超时跳过(当然这些网站基本无联系信息)
经测试,正常平均速度为:每10min约1w有效网页(不含被过滤掉的网页)
"""
import bloom
import Func_html
from queue import Queue
import requests
import threading
import re
from LAC import LAC
import time

print("Program started, initializing components...")
lac = LAC(mode="lac")
# 姓名识别模式
dic = {}  # 存放一级网站对应单位的字典 11
first_html = Queue()  # 用于存放一级网页
q_html = Queue()  # 用于存放待访问网站的队列
cnt_html = 0  # 记录网页访问个数
cnt_info = 0  # 记录信息条数
bloom_html = bloom.bloom()  # 布隆过滤器对象，网页去重过滤
bloom_ans = bloom.bloom()  # 布隆过滤器对象，信息去重过滤
lock = threading.RLock()  # 线程锁，用于解决多线程访问冲突
http_header = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \ '
    'Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.77',
    'Accept':
    'text/html,application/xhtml+xml,*/*'
}
session = requests.Session()
isPaused = False  # 暂停标志
isStopped = False  # 终止标志

# 创建一级网站title的字典信息


def first_visit():
    global first_html, dic
    global lock, csv, http_header, session
    while (True):
        try:
            with lock:
                assert first_html.unfinished_tasks > 0
                now_html = first_html.get(timeout=10)
        except:
            while (first_html.unfinished_tasks):
                first_html.task_done()
            return

        # 获取当前网页源代码
        try:
            html_content = session.get(now_html,
                                       headers=http_header,
                                       allow_redirects=False,
                                       timeout=(0.5, 1)).content.decode()
        except requests.exceptions.ConnectionError:  # 部分网站年久废弃无法访问
            first_html.task_done()
            continue
        except UnicodeDecodeError:  # 无法处理的异常
            first_html.task_done()
            continue
        except requests.exceptions.MissingSchema:  # 所获链接不一定是网页链接，需跳过
            first_html.task_done()
            continue
        except requests.exceptions.ReadTimeout:  # 部分网页耗时过长无响应
            first_html.task_done()
            continue

        # 获取页面最核心最靠前的title,非贪婪匹配第一个title标签内的title
        title = re.findall(
            '((?<=title\>)(.*?)(?=</title))|((?<=TITLE\>)(.*?)(?=</TITLE))',
            html_content, re.S)

        # 去除空格换行符等
        final_title = ''
        if title:
            temp_title = (title[0][0].replace('\n', '').replace(
                '\r', '').replace('\t', '').replace('\r\n', '').replace(
                    ' ', '').replace(' ', '').replace(',', '').replace(
                        '，', '').replace('\'', '').replace('\"', '').replace(
                            '&amp;', '').replace('nbsp;', '').splitlines())
            for a_title in temp_title:
                if a_title:
                    final_title = a_title

        # 存入一级网站title
        dic[now_html] = final_title
        first_html.task_done()


# 遍历待访问网页


def visit():
    global q_html, cnt_html, cnt_info, dic
    global bloom_html, bloom_ans, lock, csv, http_header, session
    global isPaused, isStopped
    while (True):
        if isPaused:  # 每5秒检测一次是否需要暂停
            time.sleep(5)
            continue
        if isStopped:  # 检测是否要终止
            q_html.task_done()
            print("Thread %d stopped." %
                  threading.current_thread().native_id)  # 打印终止进程
            break

        try:
            with lock:
                assert q_html.unfinished_tasks > 0
                now_html = q_html.get(timeout=10)
        except:
            while (q_html.unfinished_tasks):
                q_html.task_done()
            return

        if ('xmu.edu.cn' in now_html) and ('xmu.edu.my' not in now_html) and (
                'news' not in now_html):
            # 当前网页中若不属于厦门大学即不包含xmu.edu.cn, 或属于马来西亚分校(不再属于xmu.edu.cn)或者是
            # 网页多、几乎无信息含量的厦大新闻网(news.xmu.edu.cn)则跳过
            with lock:
                cnt_html += 1  # 访问网页数+1
                if cnt_html % 1 == 0:
                    print('访问网页: 第%d个' % cnt_html)
            # 获取当前网页源代码
            try:
                all_html_content = session.get(now_html,
                                               headers=http_header,
                                               allow_redirects=False,
                                               timeout=(0.5, 1))
                html_content = all_html_content.content.decode()
            except requests.exceptions.ConnectionError:
                # 部分网站年久废弃无法访问
                q_html.task_done()
                continue
            except UnicodeDecodeError:
                # 无法处理的异常
                q_html.task_done()
                continue
            except requests.exceptions.MissingSchema:
                # 所获链接不一定是网页链接，需跳过
                q_html.task_done()
                continue
            except requests.exceptions.ReadTimeout:
                # 部分网页耗时过长无响应
                q_html.task_done()
                continue

            # 获取当前页面链接并加入待访问(若已重复则不加入)
            child_htmls = Func_html.get_sub_domain_list(now_html, html_content)
            if child_htmls:
                with lock:
                    for child_html in child_htmls:
                        if bloom_html.Bloom(child_html):
                            q_html.put(child_html)

            # 获取页面最核心最靠前的title,非贪婪匹配第一个title标签内的title
            title = re.findall(
                '((?<=title\>)(.*?)(?=</title))|((?<=TITLE\>)(.*?)(?=</TITLE))',
                html_content, re.S)

            # 去除空格换行符等
            final_title = ''
            if title:
                temp_title = (title[0][0].replace('\n', '').replace(
                    '\r', '').replace('\t', '').replace('\r\n', '').replace(
                        ' ', '').replace(' ', '').replace(',', '').replace(
                            '，',
                            '').replace('\'', '').replace('\"', '').replace(
                                '“', '').replace('”', '').replace(
                                    '&amp;', '').replace('nbsp;',
                                                         '').splitlines())
                for a_title in temp_title:
                    if a_title:
                        final_title = a_title

            # 如果为通知新闻页
            if Func_html.news_check(final_title):
                q_html.task_done()
                # 结束当前任务
                continue

            # 获取单位title:
            depart_title = ''
            root_html = re.findall('(https?://.*xmu\.edu\.cn)', now_html)
            # 正则匹配截取一级网页
            if root_html[0] in dic:
                # 如果当前标题未囊括一级网页标题
                depart_title = dic[root_html[0]]  # 进行补充

            # 电话信息去重加入结果
            tele_informations = Func_html.get_telephone(html_content)
            if tele_informations:
                for information in tele_informations:
                    a_information = (information[0].replace('\n', '').replace(
                        '\r', '').replace('\t',
                                          '').replace('\r\n', '').replace(
                                              ' ', ' ').replace(' ', ' '))
                    a_information = repr(
                        re.sub(r'(\s|\x00)', '',
                               a_information)).replace('\'', '')
                    # 一种特殊的去除不可见字符的方法
                    with lock:
                        index = a_information.find(':') + a_information.find(
                            '：') + 1
                        # 找到冒号位置用于拆分
                        if index == -1:
                            # 如果没有冒号则不需要拆分
                            tele = a_information
                            # 存储电话
                            name = ''
                            # 存储电话说明
                        else:
                            tele = a_information[index + 1:].replace(
                                ',', ' or ').replace('，', ' or ')
                            name = a_information[:index].replace(',',
                                                                 ' ').replace(
                                                                     '，', ' ')
                    with lock:
                        flag = bloom_ans.Bloom(tele)
                        # 如果当前电话未重复
                    # 抓取电话主人姓名
                    if flag:
                        connect_html_content = (('').join(html_content.split(
                        )).replace('&nbsp;', '').replace('white', '').replace(
                            'black', '').replace('check', '').replace(
                                '王亚南', '').replace('习近平', '').replace(
                                    'teacher', '').replace('┊', '').replace(
                                        '凌云', '').replace('White', '').replace(
                                            'Members',
                                            '').replace('origin', '').replace(
                                                'min-height', '').replace(
                                                    'Professor', '').replace(
                                                        '陈嘉庚',
                                                        '').replace('马克思', ''))
                        pos = str(connect_html_content).find(tele)
                        # 在信息位置前2000内的字符内抓取人名，如没抓到再去title里抓
                        if pos < 2000:
                            get_name = Func_html.extract_name(
                                str(connect_html_content)[:pos], 'lac')
                            if get_name:
                                new_name = get_name[-1]  # 取离当前位置最近的
                            else:
                                if final_title:
                                    get_name = Func_html.extract_name(
                                        final_title, 'lac')  # 去title里抓
                                if get_name:
                                    new_name = get_name[-1]
                                else:
                                    new_name = name
                        else:
                            get_name = Func_html.extract_name(
                                str(connect_html_content)[pos - 2000:pos],
                                'lac')
                            if get_name:
                                new_name = get_name[-1]
                            else:
                                if final_title:
                                    get_name = Func_html.extract_name(
                                        final_title, 'lac')
                                if get_name:
                                    new_name = get_name[-1]
                                else:
                                    new_name = name
                        # 电话信息写入
                        if final_title:  # 有title的写入
                            with lock:
                                cnt_info += 1
                                if depart_title in final_title:
                                    (csv.write(
                                        str(cnt_info) + ',' + final_title +
                                        ' ,' +
                                        new_name.replace(',', ' ').replace(
                                            '，', ' ').replace('\n', '').
                                        replace('\r', '').replace('\t', '').
                                        replace('\r\n', '').replace('\'', '').
                                        replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                        ' ,TEL/FAX,' + tele + '\n'))
                                else:
                                    (csv.write(
                                        str(cnt_info) + ',' + depart_title +
                                        '-' + final_title + ' ,' +
                                        new_name.replace(',', ' ').replace(
                                            '，', ' ').replace('\n', '').
                                        replace('\r', '').replace('\t', '').
                                        replace('\r\n', '').replace('\'', '').
                                        replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                        ' ,TEL/FAX,' + tele + '\n'))
                        else:  # 无title的写入
                            with lock:
                                cnt_info += 1
                                (csv.write(
                                    str(cnt_info) + ',' + depart_title + ' ,' +
                                    new_name.replace(',', ' ').replace(
                                        '，', ' ').replace('\n', '').replace(
                                            '\r', '').replace('\t', '').
                                    replace('\r\n', '').replace(
                                        '\'', '').replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                    ' ,TEL/FAX,' + tele + '\n'))

            # E-mail信息去重加入结果
            email_informations = Func_html.get_email(html_content)
            # 页面包含E-mail信息
            if email_informations:
                for information in email_informations:
                    # 处理信息
                    a_information = (information[0].replace('\n', '').replace(
                        '\r', '').replace('\t',
                                          '').replace('\r\n', '').replace(
                                              ' ', '').replace(' ', ''))
                    a_information = repr(
                        re.sub(r'(\s|\x00)', '',
                               a_information)).replace('\'', '')
                    with lock:
                        index = a_information.find(':') + a_information.find(
                            '：') + 1
                        if index == -1:
                            email = a_information  # 存储E-mail
                            name = ''  # 存储E-mail说明
                        else:
                            email = a_information[index + 1:].replace(
                                ',', ' or ').replace('，', ' or ')
                            name = a_information[:index].replace(',',
                                                                 ' ').replace(
                                                                     '，', ' ')
                    with lock:
                        flag = bloom_ans.Bloom(email)  # 如果当前E-mail未重复
                    # 抓取E-mail主人姓名
                    if flag:
                        connect_html_content = (('').join(html_content.split(
                        )).replace('&nbsp;', '').replace('white', '').replace(
                            'White', '').replace('black', '').replace(
                                'check', '').replace('teacher', '').replace(
                                    '王亚南', '').replace('凌云', '').replace(
                                        '习近平',
                                        '').replace('Members', '').replace(
                                            'origin',
                                            '').replace('┊', '').replace(
                                                'min-height', '').replace(
                                                    'Professor', '').replace(
                                                        '陈嘉庚',
                                                        '').replace('马克思', ''))
                        pos = str(connect_html_content).find(email)
                        # 在pos位置前2000的字符内抓取人名并取最后一个，抓不到则再去title里抓
                        if pos < 2000:
                            get_name = Func_html.extract_name(
                                str(connect_html_content)[:pos], 'lac')
                            if get_name:
                                new_name = get_name[-1]  # 取离当前位置最近的一个
                            else:  # 抓不到再去title里抓
                                if final_title:
                                    get_name = Func_html.extract_name(
                                        final_title, 'lac')
                                if get_name:
                                    new_name = get_name[-1]
                                else:
                                    new_name = name
                        else:
                            get_name = Func_html.extract_name(
                                str(connect_html_content)[pos - 2000:pos],
                                'lac')
                            if get_name:
                                new_name = get_name[-1]
                            else:
                                if final_title:
                                    get_name = Func_html.extract_name(
                                        final_title, 'lac')
                                if get_name:
                                    new_name = get_name[-1]
                                else:
                                    new_name = name
                        # 写入E-mail信息
                        if final_title:
                            with lock:
                                cnt_info += 1
                                if depart_title in final_title:
                                    (csv.write(
                                        str(cnt_info) + ',' + final_title +
                                        ' ,' +
                                        new_name.replace(',', ' ').replace(
                                            '，', ' ').replace('\n', '').
                                        replace('\r', '').replace('\t', '').
                                        replace('\r\n', '').replace('\'', '').
                                        replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                        ' ,E-mail,' + email + '\n'))
                                else:
                                    (csv.write(
                                        str(cnt_info) + ',' + depart_title +
                                        '-' + final_title + ' ,' +
                                        new_name.replace(',', ' ').replace(
                                            '，', ' ').replace('\n', '').
                                        replace('\r', '').replace('\t', '').
                                        replace('\r\n', '').replace('\'', '').
                                        replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                        ' ,E-mail,' + email + '\n'))
                        else:
                            with lock:
                                cnt_info += 1
                                (csv.write(
                                    str(cnt_info) + ',' + depart_title + ' ,' +
                                    new_name.replace(',', ' ').replace(
                                        '，', ' ').replace('\n', '').replace(
                                            '\r', '').replace('\t', '').
                                    replace('\r\n', '').replace(
                                        '\'', '').replace('\"', '').replace(
                                            '“', '').replace('”', '').replace(
                                                ':', '').replace('：', '') +
                                    ' ,E-mail,' + email + '\n'))
        q_html.task_done()


if __name__ == "__main__":
    print("Initialize complete.")

    # 登录厦门大学信息门户以获取更多访问权限
    username = input('Please input your school ID number:')
    password = input('Please input your password:')
    print("Trying to log in...")
    Func_html.login(session, username, password, http_header)
    print("Success to log in, initializing html dict...")

    # 从查子域网站爬取福建省备案过的合法一级网站主页并加入待访问队列及网页去重的布隆过滤器
    htmls_datas = Func_html.get_htmls(session, http_header,
                                      "https://chaziyu.com/ipchaxun.do")
    for each_html in htmls_datas:
        q_html.put(each_html)  # 加入待访问网页队列
        first_html.put(each_html)  # 加入字典创建待访问一级网页队列
        bloom_html.Bloom(each_html)  # 加入网页布隆过滤器

    # 开启字典初始化多线程
    for i in range(10):
        task = threading.Thread(target=first_visit, args=())
        task.start()
    first_html.join()  # 字典初始化多线程队列任务执行，直至为空
    print("Success!")

    # 以写入模式打开csv文件
    csv = open('Final_ans.csv', 'w', encoding='utf-8-sig')
    # 写入csv表头
    csv.write('序号,所属单位,姓名/具体信息,联系方式属性,联系方式\n')

    # 开启网页遍历多线程并写入信息
    for i in range(10):
        task = threading.Thread(target=visit, args=())
        task.start()

    print("All threads have been started, listening user input...")

    # 用户操作
    while True:
        opt = input().strip().lower()
        if opt == 'pause':
            print("Trying to pause the task...")
            isPaused = True
        elif opt == 'resume':
            print("Trying to resume the task...")
            isPaused = False
        elif (opt == 'stop' and cnt_html > 50000):  # 大于五万才可以手动停止，不然直接结束进程更划算
            print("Trying to stop the task...")
            isStopped = True
            break

    while (q_html.unfinished_tasks):
        q_html.task_done()

    # 遍历网页多线程队列任务执行，直至为空
    q_html.join()

    # 关闭csv文件
    if isStopped is False:
        csv.close()

    print("Bye~")
