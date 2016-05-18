from bs4 import BeautifulSoup
import urllib2

def CrawlNext(nexturl):
    url = urllib2.urlopen(nexturl).read()
    soup = BeautifulSoup(url, "html.parser")

    for link in soup.findAll('a'):
        if link.get('href') not in waiting:
            #if link.get('href').startswith('https://www.'):
            waiting.append(link.get('href'))

    crawled.add(url)
    urltext.add(soup.get_text)
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
