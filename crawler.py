from bs4 import BeautifulSoup
import urllib2
import re

def CrawlNext(nexturl):
    try:
        url = urllib2.urlopen(nexturl).read()
        soup = BeautifulSoup(url, "html.parser")
        print(" crawling", nexturl)
        for link in soup.findAll('a', attrs={'href': re.compile("^https://www.")}):
            href = link.get('href')
            if href not in waiting and href not in crawled:
                waiting.append(href)

        crawled.add(url)
        urltext.add(soup.get_text)
        waiting.remove(nexturl)
    except:
        print("error with url",  nexturl)
        waiting.remove(nexturl)

waiting = []
crawled = set()
urltext = set()

url = 'https://www.google.com'
waiting.append(url)

while len(waiting) > 0 or len(waiting) < 500:
    CrawlNext(waiting[0])

for i in range(0, len(waiting)):
    print waiting[i]
    print ("pass" , i)
