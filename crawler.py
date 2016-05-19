import bs4
import urllib2
import re
import string
import sqlite3 as lite
import sys
import pickle

con = lite.connect('indexed_urls.db')

with con:
    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    print "SQLite version: %s" % data

'''
Pass in a url
Create a connection
Find and store all the links on that url
Pass data to indexer
'''
def crawl_next(next_url):
    try:
        url = urllib2.urlopen(next_url).read()
        soup = bs4.BeautifulSoup(url, "html.parser")
        print(" crawling", next_url)
        for link in soup.findAll('a', attrs={'href': re.compile("^https://www.")}):
            href = link.get('href')
            if href not in waiting and href not in crawled:
                waiting.append(href)
        crawled.append(next_url)
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
                    #print(dict)

                    try:
                        con = lite.connect('indexed_urls.db')

                        cur = con.cursor()

                        cur.execute("DROP TABLE IF EXISTS URLs")
                        cur.execute("CREATE TABLE IF NOT EXISTS URLs(Id INT, Url TEXT, Words TEXT, WordCount INT);")
                        cur.execute("INSERT INTO URLs VALUES (?, ?, ?, ?);", (len(crawled), url, search_term, len(results)))
                        cur.execute("SELECT * FROM URLs")
                        print(cur.fetchall())

                        con.commit()

                    except lite.Error, e:

                        if con:
                            con.rollback()

                        print "Error %s:" % e.args[0]
                        sys.exit(1)

                    finally:

                        if con:
                            con.close()
    except:
        print ("error")


index_list = []

seed = 'https://www.google.com'
search_term = 'age'
max_crawl_length = 20


with open('Stop_Words.txt', 'r') as f:
    stop_list = f.readlines()


with open('Waiting_list.txt', 'r') as f:
    waiting = pickle.load(f)

if len(waiting) > 1:
    with open('Crawled_list.txt', 'r') as f:
        crawled = pickle.load(f)
else:
    crawled = []

waiting.append(seed)

while len(waiting) > 0 and len(crawled) < max_crawl_length:
    crawl_next(waiting[0])


with open('Waiting_list.txt', 'wb') as f:
    pickle.dump(waiting, f)

with open('Crawled_list.txt', 'wb') as f:
    pickle.dump(crawled, f)
