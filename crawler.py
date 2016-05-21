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
    #stuff = ''.join(ch for ch in stuff if ch not in exclude)
    for char in string.punctuation:
        stuff = stuff.replace(char," ")

    try:
        for i in stuff.split():
            # if the word i is not already in the temporary dictionary or in the stop list and is over 3 characters long and less than 35 characters in length
            # then i will be our search term
            if i not in url_dict and i not in stop_list and len(i) >= 3 and len(i) <= 35:
                search_term = str(i)
                #results = soup.find_all(string=re.compile('.*{0}.*'.format(search_term)), recursive=True)
                #print 'Found the word "{0}" {1} times\n'.format(search_term, len(results))

                # count how many times this word appears on the page
                word_count = stuff.count(i)
                print("found " + i + " " + str(word_count) + " times")
                # if the word appears at least once update the temporary dictionary and open the database
                if word_count >= 1:
                    url_dict.update({search_term : word_count})
                    title = soup.title.string

                    try:
                        con = lite.connect('indexed_urls.db')
                        cur = con.cursor()

                        cur.execute("CREATE TABLE IF NOT EXISTS URLs(Id INTEGER PRIMARY KEY, UrlNumber INT, Url TEXT, Title TEXT, UrlText TEXT, Words TEXT, WordCount INT);")
                        cur.execute("INSERT INTO URLs VALUES (NULL, ?, ?, ?, ?, ?, ?);",(len(crawled), url, title, stuff, search_term, word_count))

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

    with open('Stop_Words.txt', 'wb') as f:
        pickle.dump(stop_list, f)

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
            cur.execute("SELECT Url FROM URLs WHERE Url LIKE ? ORDER BY WordCount DESC LIMIT 5;", ('%' + i + '%',))
            urls_with_term = cur.fetchall()
            cur.execute("SELECT Url FROM URLs WHERE Title LIKE ? ORDER BY WordCount DESC LIMIT 5;", ('%' + i + '%',))
            titles_with_term = cur.fetchall()

            if len(urls) >= 1:
                for lines in urls:
                    print lines
                    if lines not in ranking_dict:
                        ranking_dict[lines] = wordcount[urls.index(lines)]
                    else:
                        ranking_dict[lines] = ranking_dict[lines] + wordcount[urls.index(lines)]

            if len(urls_with_term) >= 1:
                for lines in urls_with_term:
                    if lines not in ranking_dict:
                        ranking_dict[lines] = (5,)
                    else:
                        ranking_dict[lines] = ranking_dict[lines] + (5,)

            if len(titles_with_term) >= 1:
                for lines in urls_with_term:
                    if lines not in ranking_dict:
                        ranking_dict[lines] = (5,)
                    else:
                        ranking_dict[lines] = ranking_dict[lines] + (5,)

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
            temp = str(item)
            temp.split(',')
            console_list.append(temp)
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
    stop_list = pickle.load(f)

with open('Waiting_list.txt', 'r') as f:
    waiting = pickle.load(f)

if len(waiting) > 1:
    with open('Crawled_list.txt', 'r') as f:
        crawled = pickle.load(f)
else:
    crawled = []

print(stop_list)
console_list = []
console_list.append("Welcome to my simple Search Engine \n")
init_gui()
save_crawl_lists(crawled, waiting)


sys.exit(1)