# coding:utf-8
import re
from src.chapter01 import link_crawler


def scrape(html):
    if html:
        # result = re.findall('<td class="w2p_fw">(.*?)</td>', html)[1]  # 根据td class="w2p_fw"匹配

        # 根据tr *** td class="w2p_fw"匹配
        result = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)
        print result


if __name__ == '__main__':
    url = 'http://example.webscraping.com/view/United-Kingdom-239'
    html = link_crawler.download(url, 2, 'wswp', None)
    scrape(html)
