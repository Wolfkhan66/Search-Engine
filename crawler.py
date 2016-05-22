import bs4
import urllib2
import string
import sqlite3 as lite
import pickle
from Tkinter import *
from collections import OrderedDict

'''
initialize the Graphical User Interface and the main loop
'''
def init_gui():
    '''
    Pass in a url
    Create a connection
    Find and store all the links on that url
    Pass data to indexer
    '''
    def crawl_next(next_url):
        try:
            # open a connection to the next url
            url = urllib2.urlopen(next_url).read()
            # parse the html using beatuifulsoup
            soup = bs4.BeautifulSoup(url, "html.parser")
            #print out the url being crawled
            print(" crawling", next_url)

            # using beautiful soup, find all of the links in the html, as long as they contain http
            for link in soup.findAll('a', attrs={'href': re.compile("^http")}):
                href = link.get('href')
                # if the link found is not already in the waiting or crawled list, add it to the waiting list
                if href not in waiting and href not in crawled:
                    waiting.append(href)

            # now we are done searching for urls, add the url to the crawled list, and remove it from the waiting list
            crawled.append(next_url)
            waiting.remove(next_url)

            #update the gui for good measure
            search_engine.update()
            #now the page has been crawled for urls, pass the html to the indexer
            index_data(next_url, soup)
        except:
            # print("error with url",  next_url)
            waiting.remove(next_url)


    '''
    Pass in a url and soup object
    find and count word occurence in soup object
    save information to a database
    '''
    def index_data(url, soup):
        # create a temporary dict to store data for a url
        url_dict = {}
        # get just the text from the parsed html
        stuff = soup.get_text()
        # replace all punctuation in the text with a space
        for char in string.punctuation:
            stuff = stuff.replace(char," ")

        try:
            # now we are ready to index , open up the database
            con = lite.connect('indexed_urls.db')
            cur = con.cursor()
            try:
                # split the text up by the spaces in the text, so to individual words
                for i in stuff.split():
                    search_engine.update()
                    # if the word i is not already in the temporary dictionary or in the stop list and is over 3 characters long and less than 35 characters in length
                    # then i will be our search term
                    if i not in url_dict and i not in stop_list and len(i) >= 3 and len(i) <= 35:
                        search_term = str(i)

                        # count how many times this word appears on the page
                        word_count = stuff.count(i)
                        stuff = stuff.replace(i ,'')
                        # if the word appears more than once update the temporary dictionary and index data to the database
                        if word_count >= 2:
                            print("found " + i + " " + str(word_count) + " times")
                            url_dict.update({search_term : word_count})
                            title = soup.title.string

                            cur.execute(
                                "CREATE TABLE IF NOT EXISTS URLs(Id INTEGER PRIMARY KEY, UrlNumber INT, Url TEXT, Title TEXT, Words TEXT, WordCount INT);")
                            cur.execute("INSERT INTO URLs VALUES (NULL, ?, ?, ?, ?, ?);",(len(crawled), url, title, search_term, word_count))
                            con.commit()
            except:
                print ("error")

        except lite.Error, e:
            if con:
                con.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()


    '''
    query the database for a term
    '''
    def query_database(search_term):

        try:
            # create temporary dictionary to rank the output from the database queries
            ranking_dict = {}
            # split our search term up if multiple words have been entered, so we can query the database for each word
            for i in search_term.split():
                # update the gui for good measure
                search_engine.update()
                # open the database
                con = lite.connect('indexed_urls.db')
                cur = con.cursor()

                # select all urls where the words indexed are like our searchtime, and order them by the word count
                cur.execute("SELECT Url FROM URLs WHERE Words LIKE ? ORDER BY WordCount DESC LIMIT 6;",('%'+i+'%',))
                urls = cur.fetchall()

                # select the wordcounts for the same query as above
                cur.execute("SELECT WordCount FROM URLs WHERE Words LIKE ? ORDER BY WordCount DESC LIMIT 6;", ('%'+i+'%',))
                wordcount = cur.fetchall()

                # select urls where the search term appears in the url
                cur.execute("SELECT Url FROM URLs WHERE Url LIKE ? ORDER BY WordCount DESC LIMIT 6;", ('%'+i+'%',))
                urls_with_term = cur.fetchall()

                # select urls where the search term appears in the title
                cur.execute("SELECT Url FROM URLs WHERE Title LIKE ? ORDER BY WordCount DESC LIMIT 6;", ('%'+i+'%',))
                titles_with_term = cur.fetchall()

                # Here we do our ranking, the ranking dict contains all the urls found for the above queries.
                # a Url gains a point each time a word from the search term is found on its page
                # 5 additional points are gained if the search term is found in the url and or in the title

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
                    console.insert(END,"no results found for " + i + "\n")
                    console.insert(END,"\n")

            # for each item in the ranking dict, convert the wordcount tuples to an int
            for item in ranking_dict:
                ranking_dict[item] = sum(ranking_dict[item])

            # sort the rank dictionary into descending order
            ranking_dict = OrderedDict(sorted(ranking_dict.items(), key=lambda t: t[1], reverse=True))

            # format entries in the ranking dict into strings to be displayed on the gui terminal
            for item in ranking_dict:
                temp = str(item)
                temp = temp[:-3]
                temp = temp[+3:]
                temp2 = str(ranking_dict[item])
                console.insert(END,"Rank:[ " + temp2 + " ] " + temp + "\n")
                console.insert(END,"\n")

        except lite.Error, e:
            if con:
                con.rollback()

            print "Error %s:" % e.args[0]
            sys.exit(1)

        finally:
            if con:
                con.close()


    def start_query(search_term):
        # binds to the search button and fires off a query
        console.delete('1.0', END)
        console.insert(END,"###############################\n")
        console.insert(END,"###############################\n")
        console.insert(END,"Querying Database for " + search_term + "\n")
        search_engine.update()
        query_database(search_term)


    def start_crawl(crawl_length):
        # binds to the start crawl button and fires off the crawler and indexer
        console.delete('1.0', END)
        console.insert(END, "Starting Crawl \n")
        search_engine.update()

        # count = the max pages to crawl entered by the user
        count = int(crawl_length)
        # while there are pages waiting to be crawled and we havent reached the max pages to crawl
        # crawl the next page in the list
        while len(waiting) > 0 and count > 0:
            console.insert(END, "Crawling ")
            console.insert(END, waiting[0])
            console.insert(END, "\n")
            search_engine.update()
            crawl_next(waiting[0])
            count -= 1
        console.delete('1.0', END)
        console.insert(END, "Crawl Finished! \n")
        console.insert(END, str(len(crawled)) + " Websites have been Indexed\n")
        console.insert(END, str(len(waiting)) + " Websites are waiting to be Crawled\n")


    # the following is the GUI using Tkinter
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
    console.insert(END, "Welcome to my simple Search Engine \n")
    console.insert(END, str(len(crawled)) + " Websites have been Indexed\n")
    console.insert(END, str(len(waiting)) + " Websites are waiting to be Crawled\n")
    console.insert(END, "Please be paitent when running a query :) \n")

    search_engine.mainloop()


'''
save the waiting, crawled and stop list to file
'''
def save_crawl_lists(crawled, waiting):
    with open('Waiting_list.txt', 'wb') as f:
        pickle.dump(waiting, f)

    with open('Crawled_list.txt', 'wb') as f:
        pickle.dump(crawled, f)

    with open('Stop_Words.txt', 'wb') as f:
        pickle.dump(stop_list, f)


'''
The start of the program
Load stop list , crawling and waiting list from file
Launch the Gui thread
When Gui is closed - save the crawled and waiting lists
Then exit the system
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

init_gui()
save_crawl_lists(crawled, waiting)
sys.exit(1)