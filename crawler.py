import bs4
import urllib2
import re
import string
import sqlite3 as lite
import sys
import pickle
from Tkinter import *
import operator


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
        for link in soup.findAll('a', attrs={'href': re.compile("^http")}):
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
    exclude = set(string.punctuation)
    print(stuff)
    stuff = ''.join(ch for ch in stuff if ch not in exclude)
    print (stuff)
    try:
        for i in stuff.split():
            if i not in url_dict and len(i) >= 3:
                search_term = str(i)
                results = soup.find_all(string=re.compile('.*{0}.*'.format(search_term)), recursive=True)
                print 'Found the word "{0}" {1} times\n'.format(search_term, len(results))
                if len(results) >= 1:
                    url_dict.update({search_term : len(results)})

                    try:
                        con = lite.connect('indexed_urls.db')
                        cur = con.cursor()

                        cur.execute("CREATE TABLE IF NOT EXISTS URLs(Id INTEGER PRIMARY KEY, UrlNumber INT, Url TEXT, UrlText TEXT, Words TEXT, WordCount INT);")
                        cur.execute("INSERT INTO URLs VALUES (NULL, ?, ?, ?, ?, ?);",(len(crawled), url, stuff, search_term, len(results)))

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

    try:
        ranking_dict = {}
        del console_list[:]
        console_list.append("###############################")
        console_list.append("###############################")
        console_list.append("Querying Database for " + search_term)

        for i in search_term.split():
            con = lite.connect('indexed_urls.db')
            cur = con.cursor()
            cur.execute("SELECT Url FROM URLs WHERE Words LIKE ? ORDER BY WordCount DESC LIMIT 5;",('%'+i+'%',))
            urls = cur.fetchall()
            cur.execute("SELECT WordCount FROM URLs WHERE Words LIKE ? ORDER BY WordCount DESC LIMIT 5;", ('%' + i + '%',))
            wordcount = cur.fetchall()

            if len(urls) >= 1:
                for lines in urls:
                    print lines
                    if lines not in ranking_dict:
                        ranking_dict[lines] = wordcount[urls.index(lines)]
                    else:
                        ranking_dict[lines] = ranking_dict[lines] + wordcount[urls.index(lines)]

            else:
                console_list.append("no results found for " + i)
                console_list.append("")
                console_list.append("###############################")
                console_list.append("###############################")

        for item in ranking_dict:
            ranking_dict[item] = sum(ranking_dict[item])

        sorted_x = sorted(ranking_dict.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        for item in sorted_x:
            console_list.append(item)
            console_list.append("")

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

    def start_query(search_term):
        query_database(search_term)
        console.delete('1.0', END)
        for i in range(0 , len(console_list)):
            console.insert(END, console_list[i])
            console.insert(END, '\n')

    def start_crawl(crawl_length):
        console.delete('1.0', END)
        console.insert(END, "Starting Crawl \n")
        search_engine.update()
        count = int(crawl_length)
        while len(waiting) > 0 and count > 0:
            crawl_next(waiting[0])
            count -= 1
            console.insert(END, "Crawling ")
            console.insert(END, waiting[0])
            console.insert(END, "\n")
            search_engine.update()
        console.insert(END, "Crawl Finished! \n")

    search_engine = Tk()
    search_engine.title("Simple Search Engine")
    search_engine.geometry("640x480")

    app = Frame(search_engine)
    app.grid()

    label = Label(app, text="Enter Max Pages to Crawl and Index")
    label.pack()
    label.grid()

    index_length = Entry(app)
    index_length.insert(END, '0')
    index_length.pack()
    index_length.grid()

    crawl_button = Button(app, text="Start Crawl", command=lambda: start_crawl(index_length.get()))
    crawl_button.pack()
    crawl_button.grid()

    label2 = Label(app, text="Enter a Search Term to Query the Database")
    label2.pack()
    label2.grid()

    search_term = Entry(app)
    search_term.insert(END, 'Google')
    search_term.pack()
    search_term.grid()

    search_button = Button(app, text="Search", command=lambda: start_query(search_term.get()))
    search_button.pack()
    search_button.grid()

    console = Text(app)
    console.pack()
    console.grid()

    search_engine.mainloop()


'''
The start of the program
Load stop list , crawling and waiting list from file
Launch the Gui
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

console_list = []
console_list.append("Welcome to my simple Search Engine \n")
init_gui()
save_crawl_lists(crawled, waiting)
sys.exit(1)