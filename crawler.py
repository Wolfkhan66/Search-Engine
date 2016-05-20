import bs4
import urllib2
import re
import string
import sqlite3 as lite
import sys
import pickle
from Tkinter import *


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


'''
Pass in a url and soup object
find and count word occurence in soup object
save information to a database
'''
def index_data(url , soup):
    url_dict = {}
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

                    try:
                        con = lite.connect('indexed_urls.db')
                        cur = con.cursor()

                        cur.execute("CREATE TABLE IF NOT EXISTS URLs(Id INTEGER PRIMARY KEY, UrlNumber INT, Url TEXT, Words TEXT, WordCount INT);")
                        cur.execute("INSERT INTO URLs VALUES (NULL, ?, ?, ?, ?);",(len(crawled), url, search_term, len(results)))
                        cur.execute("SELECT * FROM URLs ORDER BY Id DESC LIMIT 1")
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


'''
save the waiting and crawled list to file
'''
def save_crawl_lists(crawled, waiting):
    with open('Waiting_list.txt', 'wb') as f:
        pickle.dump(waiting, f)

    with open('Crawled_list.txt', 'wb') as f:
        pickle.dump(crawled, f)


'''
query the database for a term
'''
def query_database(search_term):

    print("###############################")
    print("###############################")
    print("Querying Database for the word ", search_term)
    print("The top 5 urls for this word are: ")
    print("")

    try:
        con = lite.connect('indexed_urls.db')
        cur = con.cursor()
        cur.execute("SELECT Url, Words, WordCount FROM URLs WHERE Words=? ORDER BY WordCount DESC LIMIT 5;",(search_term,))
        #print(cur.fetchall())
        output = cur.fetchall()
        for lines in output:
            print lines

        print("")
        print("###############################")
        print("###############################")

    except lite.Error, e:
        if con:
            con.rollback()

        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if con:
            con.close()


'''
initialize the Graphical User Interface
'''
def init_gui():
    root = Tk()
    root.title("Simple Search Engine")
    root.geometry("640x480")

    app = Frame(root)
    app.grid()
    button1 = Button(app, text="button 1")
    button1.grid()

    label = Label(app, text=" label 1!!!")
    label.grid()
    root.mainloop()


'''
The start of the program
'''
seed = 'https://www.google.com'
search_term = 'age'
max_crawl_length = 5


'''
Load stop list , crawling and waiting list from file
'''
with open('Stop_Words.txt', 'r') as f:
    stop_list = f.readlines()

with open('Waiting_list.txt', 'r') as f:
    waiting = pickle.load(f)

if len(waiting) > 1:
    with open('Crawled_list.txt', 'r') as f:
        crawled = pickle.load(f)
else:
    crawled = []


init_gui()

#waiting.append(seed)

while len(waiting) > 0 and max_crawl_length > 0:
    crawl_next(waiting[0])
    max_crawl_length -= 1

save_crawl_lists(crawled,waiting)
query_database('Google')