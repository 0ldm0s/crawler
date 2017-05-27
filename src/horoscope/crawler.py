# -*- coding:utf-8 -*-
import urllib.request
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
import logging

logging.basicConfig(
        filename='horoscope-crawler.log',
        level=logging.ERROR,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )


parent_dir = 'horoscope'
horoscopes = ['Aquarius', 'Aries', 'Cancer', 'Capricorn', 'Gemini', 'Leo',
              'Libra', 'Pisces', 'Sagittarius', 'Scorpio', 'Taurus', 'Virgo']

failds = []  # 失败记录


# 根据星座抓取，mouths表示抓取几个月前的数据
def crawler_by_horoscope(mouths):

    p_dir = os.path.abspath(os.getcwd()) + '\\' + parent_dir
    for hor in horoscopes:
        hor = hor.lower()
        os.chdir(p_dir)
        h_mkdir(hor)
        os.chdir(hor)

        days = get_date_str(mouths)
        for day in days:
            data = hor + '-horoscope-' + day.lower()
            crawler(data)


# 根据日期抓取，mouths表示抓取几个月前的数据
def crawler_by_date(mouths):
    p_dir = os.path.abspath(os.getcwd()) + '\\' + parent_dir
    days = get_date_str(mouths)
    for day in days:
        os.chdir(p_dir)
        h_mkdir(day)
        os.chdir(day)

        for hor in horoscopes:
            hor = hor.lower()
            data = hor + '-horoscope-' + day.lower()
            crawler(data)


# 根据链接后缀抓取星座数据
def crawler(data):
    url = 'https://www.horoscope-day.com/' + data + '/'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    try:
        request = urllib.request.Request(url, headers=headers)
        logging.info('downing: %s' % url)
        response = urllib.request.urlopen(request)
        # print(response.read())

        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, "html.parser")

        # title = soup.find(name="h1", attrs={"class": "entry-title"})
        # print("title:", title.string)

        body = soup.find(name="div", attrs={"class": "entry-summary"})
        for child in body.children:
            try:
                if child.script['async'] is None and child['script'] is None:
                    break
            except (AttributeError, TypeError) as e:
                None

            strs = child.string
            if strs is None:
                strs = child.text

            if strs is not None and strs != '\n' and strs.strip() != '(adsbygoogle = window.adsbygoogle || []).push({});':
                # print(strs)
                with open(data + '.txt', 'a') as f:
                    f.writelines('\n' + strs)
                    f.close()

    except urllib.request.URLError as e:
        faild = 'failed download: %s code %s reason %s', data
        if hasattr(e, "code"):
            faild += 'code %s', e.code
        if hasattr(e, "reason"):
            faild += 'reason %s', e.reason
        failds.append(faild)

    for fa in failds:
        logging.error(fa)


# 获取输入日期所在月份起始日期
def get_month_range(start_date=None):
    if start_date is None:
        start_date = date.today().replace(day=1)
    _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date + timedelta(days=days_in_month)
    return start_date, end_date


# 获取数月内日期集合
def get_date_str(months_num):
    days = []
    a_day = timedelta(days=1)

    end_today = date.today()
    start_day = end_today + relativedelta(months=-months_num)

    while start_day <= end_today:
        d_time = datetime.strptime(str(start_day), '%Y-%m-%d')
        day = d_time.strftime('%d-%B-%Y')
        if day.startswith('0'):
            day = day[1:]
        days.append(day)
        # print(day)
        start_day += a_day
    return days


# 生成目录，捕获异常信息
def h_mkdir(path):
    try:
        os.mkdir(path)
    except Exception as e:
        pass

if __name__ == '__main__':
    h_mkdir(parent_dir)
    # crawler_by_horoscope(1)
    crawler_by_date(1)
