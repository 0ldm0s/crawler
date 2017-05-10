# -*- coding:utf-8 -*-
import urllib.request
import re
import os
from bs4 import BeautifulSoup


def crawler():
    data = "libra-horoscope-10-may-2017"
    url = 'https://www.horoscope-day.com/' + data + '/'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    file_content = "faild"
    strs = []
    os.mkdir(data)
    os.chdir(data)

    try:

        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        # print(response.read())

        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find(name="h1", attrs={"class": "entry-title"})
        print("title:", title.string)

        body = soup.find(name="div", attrs={"class": "entry-summary"})
        for child in body.children:
            try:
                if child.script['async'] is None and child['script'] is None:
                    break
            except (AttributeError, TypeError) as e:
                None

            str = child.string
            if str is None:
                str = child.text

            if str is not None and str != '\n' and str.strip() != '(adsbygoogle = window.adsbygoogle || []).push({});':
                print(str)
                with open(data + '.txt', 'a') as f:
                    f.writelines('\n' + str)
                    f.close()

        # pattern = re.compile(r'<h1.*?class ="entry-title">(.*?)< / h1 >', re.S)
        # items = re.findall(pattern, content)
        # for item in items:
        #     haveImg = re.search("img", item[3])
        #     if not haveImg:
        #         print(item[0], item[1], item[2], item[4])

    except urllib.request.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)


def str1():
    # s_list = []
    # str = 's'
    # for s in range(4):
    #     s_list.append("1")
    # str.join(s_list)
    # print(str)

    var_list = ['tom', 'david', 'john']
    a = '###'
    a.join(var_list)
    print(var_list)

if __name__ == '__main__':
    # str1()
    crawler()

