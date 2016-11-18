# coding: utf-8
import lxml.html
from src.chapter01 import link_crawler


def scrape_test():
    broken_html = '<ul class=country><li>Area<li>Population</ul>'
    # 解析字符串
    tree = lxml.html.fromstring(broken_html)
    # 字符串解析为html文档格式，pretty_print=True转换成缩进格式
    fixed_html = lxml.html.tostring(tree, pretty_print=True)
    print fixed_html


def scrape_css3(html):
    tree = lxml.html.fromstring(html)
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    area = td.text_content()
    print area


if __name__ == '__main__':
    # scrape_test()

    url = 'http://example.webscraping.com/view/United-Kingdom-239'
    html = link_crawler.download(url, 2, 'wswp', None)
    if html:
        scrape_css3(html)


