# coding:utf-8
import re
import urllib2
import itertools
import urlparse
import robotparser
import datetime
import time


class Throttle:
    """
    Add a delay between downloads to the same domain
    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()


def download(url, num_retries, user_agent, proxy):
    """
    下载网页Download web page.

        Download web page by url.

        Args:
            url: download url.
            num_retries: retries times.
            user_agent: agent name.
            proxy: 代理

        Return:
            web page.
    """
    print 'Downloading:', url
    headers = {}
    if user_agent:
        headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # recursively retry 5** HTTP errors
                return download(url, num_retries-1)
    return html


def crawl_sitemap(url):
    """
    网站地图爬虫Crawl sitemap.

     Crawl sitemap by url.

     Args:
         url: download url.
    """
    # download the sitemap file
    sitemap = download(url)
    # extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = download(link)
        # scrape html here
        print html


def crawl_iter():
    """
    遍历爬虫
    根据ID遍历爬虫,连续5次下载失败退出遍历
    """
    # maximum number of consecutive download errors allowed
    max_errors = 5
    # current number of consecutive download errors
    num_errors = 0
    for page in itertools.count(1):
        url = 'http://example/webscraping.com/view/-%d' % page
        html = download(url)
        if html is None:
            # received an error trying to download this webpage
            num_errors += 1
            if num_errors == max_errors:
                # reached maximum number of consecutive download errors
                print 'consecutive download errors, exit iterate'
                break
        else:
            # success - can scrape the result
            num_errors = 0
            print html
            pass


def link_crawler(seed_url, link_regex=None, proxy=None, delay=5, num_reties=1, user_agent='wswp'):
    """
    根据适配规则对链接进行爬虫下载
    """
    crawl_queue = [seed_url]
    rp = get_rotobs(seed_url)
    seen = set(crawl_queue)  # 已发现的链接
    throttle = Throttle(delay)
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, num_reties, user_agent, proxy)
            if html is not None:
                # 根据正则表达式用get_linkes过滤链接
                links = get_linkes(html)
                for link in links:
                    if re.match(link_regex, link):
                        # 将相对路径转为绝对路径
                        link = urlparse.urljoin(seed_url, link)
                        # 校验是否已经存储
                        if link not in seen:
                            crawl_queue.append(link)
        else:
            print 'Blocked by robots.txt:', url
    print crawl_queue


def get_rotobs(url):
    """Initialize robots parser for this domain
        """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_linkes(html):
    """
    从html返回链接集合

        Return: 链接集合
    """
    webapp_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webapp_regex.findall(html)


if __name__ == '__main__':
    # exsample = 'http://example.webscraping.com/sitemap.xml'
    # crawl_sitemap(exsample)

    # crawl_iter()
    proxy = 'localhost:51632'
    link_crawler('http://example.webscraping.com/', '/(index|view)')

