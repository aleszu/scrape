import csv
import requests
import threading
import os
import sys
from Queue import Queue
from bs4 import BeautifulSoup as bs

# Globals
q = Queue()
lock = threading.Lock()
total_articles = 0
cur_article = 0
TARGET_PATH = ''

# Represents Article
class Article():
    def __init__(self, name, link):
        self.headline = name 
        self.link = link
        self.text = None
        self.done = False
        self.trys = 0

    # Returns article text
    def parse_text(self, html):
        soup = bs(html, 'html.parser')
        for remove in soup(["script", "stylings", "style"]):
            remove.decompose()
        text = soup.get_text()
        text = ''.join([c for c in text if ord(c) < 128])
        text = text.translate({ord(c):None for c  in u'\r\n\t'})
        if len(text):
            self.done = True
        return text

    # Gets the text for a given article
    def getText(self):
        try:
            r = requests.get(self.link)
            self.text = self.parse_text(r.content)
        except:
            pass # ignore
        self.trys += 1
        if self.trys >= 2:
            self.done = True
        return self.done

    # saves the article to s3 bucket
    def save(self):
        fname = (''.join([c for c in self.headline.split(' ')])).replace('/', '').replace('.', '').replace("'", "") + '.txt'
        # write text to file
        try:
            f = open(TARGET_PATH + fname, 'w')
            f.write(self.text)
            f.close()
        except:
            pass

# Attempt to open file
def openFile(path):
    try:
        f = open(path, 'r')
        return f
    except:
        print 'file open failed, please check path.'

# skip headers if csv file has column headers
def skipHeaders(reader):
    x = raw_input('does file have column headers(y/n): ')
    if x == 'y' or x == '':
        next(reader) # skip headers

# build queue
def init():
    global total_articles 
    f = openFile(raw_input('relative path to the file: '))
    reader = csv.reader(f)
    skipHeaders(reader) # skip headers
    url_col = int(raw_input('which column has the url [0-n]: '))
    name_col = raw_input('which column has article name (press enter if none): ')
    name_col = int(name_col) if name_col != '' else url_col
    for row in reader:
        if row[url_col]:
            article = Article(row[name_col], row[url_col])
            q.put(article)
            total_articles += 1

# Set data destination
def setDestination():
    global TARGET_PATH
    dst = raw_input('path of where to store text files: ')
    if not os.path.exists(dst):
        os.makedirs(dst)
    TARGET_PATH = dst

# updates task done count and prints update on progress
def updateQueue():
    global cur_article
    global total_articles
    with lock:
        q.task_done()
        cur_article += 1
        s = '%d/%d articles complete' % (cur_article, total_articles)
        sys.stdout.write('\r' + s)
        if cur_article == total_articles:
            sys.stdout.write('\n')
        sys.stdout.flush()

# thread function
def worker():
    while not q.empty():
        article = q.get()
        resp = article.getText()
        if resp:
            updateQueue()
            article.save()
        else:
            q.task_done()
            q.put(article)

# build the threads
def initThreads():
    for i in range(30):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

def main():
    init()
    total_articles = q.qsize()
    setDestination()
    initThreads()
    q.join()

main()
