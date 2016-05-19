import bs4
import urllib2
import re
import string


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
    url_dict = {}
    dict = {}
    stuff = soup.get_text()

    try:
        for i in stuff.split():
            i.strip(string.punctuation + string.digits + string.whitespace)
            if i not in stop_list and i not in url_dict and len(i) > 3:
                search_term = i

                results = soup.find_all(string=re.compile('.*{0}.*'.format(search_term)), recursive=True)
                print 'Found the word "{0}" {1} times\n'.format(search_term, len(results))

                url_dict.update({search_term : len(results)})
                dict.update({url : url_dict})
                index_list.append(dict)
                print(dict)
    except:
        print ("error")



waiting = []
crawled = []
index_list = []

seed = 'https://www.google.com'
search_term = 'age'
max_crawl_length = 30

with open('Stop_Words.txt', 'r') as f:
    stop_list = f.readlines()


waiting.append(seed)

while len(waiting) > 0 or len(crawled) < max_crawl_length:
    crawl_next(waiting[0])

