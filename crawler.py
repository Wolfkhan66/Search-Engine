import bs4
import urllib2
import re
import string
import pickle

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
        index_data(next_url, soup)
    except:
        # print("error with url",  next_url)
        waiting.remove(next_url)


def index_data(url , soup):
    url_dict = {}
    dict = {}
    stuff = soup.get_text()

    try:
        for i in stuff.split():
            i.strip(string.punctuation + string.digits + string.whitespace)
            if i not in stop_list and i not in url_dict and len(i) > 3:
                search_term = str(i)
                search_term.strip(string.punctuation)

                results = soup.find_all(string=re.compile('.*{0}.*'.format(search_term)), recursive=True)
                print 'Found the word "{0}" {1} times\n'.format(search_term, len(results))
                if len(results) >= 1:
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
max_crawl_length = 10


with open('Stop_Words.txt', 'r') as f:
    stop_list = f.readlines()

'''''''''''
with open('Waiting_list.txt', 'r') as f:
    waiting = f.readlines()

with open('Crawled_list.txt', 'r') as f:
    crawled = f.readlines()

with open('index_file.txt', 'rb') as f:
    index_list = pickle.load(f)
'''''''''''

waiting.append(seed)

while len(waiting) > 0 and len(crawled) < max_crawl_length:
    crawl_next(waiting[0])


with open('index_file.txt', 'wb') as f:
    pickle.dump(index_list, f)

with open('Waiting_list.txt', 'wb') as f:
    pickle.dump(waiting, f)

with open('Crawled_list.txt', 'wb') as f:
    pickle.dump(crawled, f)

