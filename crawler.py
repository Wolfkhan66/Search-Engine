import bs4
import urllib2
import re


def crawl_next(next_url):
    try:
        url = urllib2.urlopen(next_url).read()
        soup = bs4.BeautifulSoup(url, "html.parser")

        print(" crawling", next_url)
        for link in soup.findAll('a', attrs={'href': re.compile("^https://www.")}):
            href = link.get('href')
            if href not in waiting and href not in crawled:
                waiting.append(href)
        crawled.append(url)
        waiting.remove(next_url)
    except:
        # print("error with url",  next_url)
        waiting.remove(next_url)
    index_data(next_url, soup)

def index_data(url , soup):
    results = soup.find_all(string=re.compile('.*{0}.*'.format(search_term)), recursive=True)
    print 'Found the word "{0}" {1} times\n'.format(search_term, len(results))

    urldict = {}
    urldict.update({search_term : len(results)})
    dict = {}
    dict.update({url : urldict})
    index_list.append(dict)
    print(dict)
    print(index_list[0])



waiting = []
crawled = []
index_list = []

seed = 'https://en.wikipedia.org/wiki/Main_Page'
search_term = 'age'
max_crawl_length = 30


waiting.append(seed)

while len(waiting) > 0 or len(crawled) < max_crawl_length:
    crawl_next(waiting[0])

