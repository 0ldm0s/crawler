# -*- coding:utf-8 -*-
import json
import logging
import os
import random
import urllib.request
from datetime import date, datetime, timezone, timedelta

from bs4 import BeautifulSoup

logging.basicConfig(
        filename='horoscope-crawler.log',
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )

# 从 https://www.horoscope.com/us/horoscopes/money/horoscope-money-weekly.aspx?sign=12 抓取星座数据
# 保存至文件中，每天上传至fireBase上
# 因为fireBase不支持Python操作实时数据库，而用Java服务每天定时上传。

parent_dir = 'horoscope-crawler'
horoscopes = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
              'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

failds = []  # 失败记录

types = ('general', 'love', 'wellness', 'money', 'career')
signs = (1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
lucy_colors = ('purple', 'argentine', 'blue', 'yellow', 'orange', 'pink', 'red', 'green', 'black', 'white', 'gray', 'golden')
url = 'https://www.horoscope.com/us/horoscopes/%s/horoscope-%s-%s.aspx?sign=%s'
upload_data = {}


def get_today():
    """
    获取西七区当天时间
    :return: 
    """
    _timezone = timezone(timedelta(hours=-7))
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(_timezone).strftime('%Y-%m-%d')


def crawler_today_date():
    """
    抓取当天星座信息
    :return: 
    """
    global url

    for sign in signs:
        horoscope_name = horoscopes[sign-1]

        horoscope = Horoscope()
        for c_type in types:
            crawler(c_type, sign, horoscope)
            lucy_number = random.randint(1, 9)
            horoscope.lucyNumber = str(lucy_number)
            lucy_color = random.randint(1, len(lucy_colors))
            lucy_color = lucy_colors[lucy_color - 1]
            horoscope.lucyColor = lucy_color

        horoscope_json = json.dumps(horoscope, default=horoscope2dict)
        upload_data[horoscope_name] = horoscope_json

    # 用json.jumps会出现反义字符，因此改为手动生成json
    # json_str = json.dumps(upload_data)

    json_str = ''
    for key, value in upload_data.items():
        json_str += ',"' + key + '":' + value + ''
    json_str = '{' + json_str[1:] + '}'

    logging.debug(json_str)

    storage_json(json_str)


# 存储json串
def storage_json(json_str):
    module_path = os.path.dirname(__file__)
    p_dir = module_path + os.path.sep + parent_dir
    os.chdir(p_dir)
    with open(get_today() + '.txt', 'w') as f:
        f.writelines(json_str)
        f.close()


# 根据类型和星标识(sign)抓取星座数据
def crawler(c_type, sign, horoscope):

    d = 'daily-today'
    if c_type == 'money':
        d = 'weekly'
    download_url = url % (c_type, c_type, d, sign)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    try:
        request = urllib.request.Request(download_url, headers=headers)
        print('downing: %s' % download_url)
        response = urllib.request.urlopen(request)
        # print(response.read())

        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, "html.parser")

        body = soup.find(name="div", attrs={"class": "horoscope-content"})
        for child in body.children:
            if child != '\n':
                content_text = str(child.contents[2])
        if content_text.startswith(' - '):
            content_text = content_text[3:]
        content_text.replace('\n', '')
        # print(content_text)

        if c_type == 'general':
            horoscope.shortDes = content_text
        elif c_type == 'love':
            horoscope.loveDes = content_text
        elif c_type == 'money':
            horoscope.wealthDes = content_text
        elif c_type == 'wellness':
            horoscope.healthDes = content_text
        else:
            get_ratings(soup, horoscope)
            get_match(soup, horoscope)
            horoscope.careerDes = content_text

    except Exception as e:
        faild = 'failed download: %s code %s reason %s', sign
        if hasattr(e, "code"):
            faild += 'code %s', e.code
        if hasattr(e, "reason"):
            faild += 'reason %s', e.reason
        failds.append(faild)

    for fa in failds:
        logging.error(fa)

    return horoscope


# 获取(爱情)匹配星座
def get_match(soup, horoscope):
    body = soup.findAll(name='div', attrs={"class": "span-4 col"})
    if len(body) > 0:
        match = body[0].a.h4.text
        horoscope.loveMatch = match


# 获取排名
def get_ratings(soup, horoscope):
    body = soup.findAll(name='div', attrs={"class": "span-5 col"})
    index = 0
    total_score = 0
    for b in body:
        alt = b.img['alt']
        alt_int = str(alt).split(' ')[0]
        total_score += int(alt_int)

        if index == 0:
            horoscope.loveScore = alt_int
        elif index == 1:
            horoscope.healthScore = alt_int
        elif index == 2:
            horoscope.wealthScore = alt_int
        else:
            horoscope.careerScore = alt_int

        index += 1

    rank = int(total_score/4/0.5)/2
    horoscope.rank = rank

    return horoscope


class Horoscope(object):

    loveDes = ''
    wealthDes = ''
    careerDes = ''
    healthDes = ''
    shortDes = ''

    loveScore = ''
    healthScore = ''
    wealthScore = ''
    careerScore = ''

    lucyNumber = ''
    lucyColor = ''
    loveMatch = ''

    rank = ''

    def __init__(self):
        pass


def horoscope2dict(horoscope):
    return{
        'loveDes': horoscope.loveDes,
        'careerDes': horoscope.careerDes,
        'wealthDes': horoscope.wealthDes,
        'healthDes': horoscope.healthDes,
        'shortDes': horoscope.shortDes,
        'loveScore': horoscope.loveScore,
        'healthScore': horoscope.healthScore,
        'wealthScore': horoscope.wealthScore,
        'careerScore': horoscope.careerScore,
        'lucyColor': horoscope.lucyColor,
        'lucyNumber': horoscope.lucyNumber,
        'loveMatch': horoscope.loveMatch,

        'rank': horoscope.rank
    }


# 生成目录，捕获异常信息
def h_mkdir(path):
    try:
        os.mkdir(path)
    except Exception as e:
        pass

if __name__ == '__main__':
    get_today()
    h_mkdir(parent_dir)
    # crawler_by_horoscope(1)
    crawler_today_date()
