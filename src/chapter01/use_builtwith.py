import builtwith


# builtwith模块: 识别网站所用技术

baidu = 'http://www.baidu.com'
music_163 = 'http://music.163.com/#/friend'
exsample = 'http://example.webscraping.com'
uez = 'http://sxeccellentdriving.com/'


if __name__ == '__main__':
    d = builtwith.parse(exsample)
    print d
