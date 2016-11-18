from bs4 import BeautifulSoup
from src.chapter01 import link_crawler


def scrape_test():
    broken_html = '<ul class=country><li>Area<li>Population</ul>'
    soup = BeautifulSoup(broken_html, 'html.parser')
    fixed_html = soup.prettify()
    print fixed_html

    ul = soup.find('ul', attrs={'class': 'country'})
    print ul.find('li')
    print ul.find_all('li')


def scrape(html):
    soup = BeautifulSoup(html, 'html.parser')
    fixed_html = soup.prettify()
    print fixed_html

    tr = soup.find(attrs={'id': 'places_area__row'})
    if tr:
        td = tr.find(attrs={'class': 'w2p_fw'})
        area = td.text
        print 'area: [%s]' % area


if __name__ == '__main__':
    scrape_test()

    url = 'http://example.webscraping.com/view/United-Kingdom-239'
    html = link_crawler.download(url, 2, 'wswp', None)
    if html:
        scrape(html)
