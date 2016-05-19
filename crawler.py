import bs4
import urllib2
import re

def crawlnext(nexturl):
    try:
        url = urllib2.urlopen(nexturl).read()
        soup = bs4.BeautifulSoup(url, "html.parser")

        results = soup.body.find_all(string=re.compile('.*{0}.*'.format('the')), recursive=True)

        print 'Found the word "{0}" {1} times\n'.format('the', len(results))

        print(" crawling", nexturl)
        for link in soup.findAll('a', attrs={'href': re.compile("^https://www.")}):
            href = link.get('href')
            title = link.get('title')
            if href not in waiting and href not in crawled:
                waiting.append(href)
                # waiting.append(title)
        crawled.append(url)
        urltext.append(soup.get_text)
        waiting.remove(nexturl)
    except:
        # print("error with url",  nexturl)
        waiting.remove(nexturl)


def indexdata (crawled_urls, url_text):
    dfd = 0



waiting = []
crawled = []
urltext = []
seed = 'https://www.google.com'

waiting.append(seed)

while len(waiting) > 0 or len(waiting) < 500:
    crawlnext(waiting[0])
    indexdata(crawled,urltext)

for i in range(0, len(waiting)):
    print waiting[i]
    print ("pass" , i)
