#!/usr/bin/env python

import os
import cStringIO
import formatter
from htmllib import HTMLParser
import httplib
import sys
import urllib
import urlparse
import re
import shutil
import datetime
from random import randint
import threading
import thread

send2pocket_lock = thread.allocate_lock()

class vote_tag_HTMLParser(HTMLParser):
    # vote-count-post
    def __init__(self):
        HTMLParser.__init__(self, '')
        self.vote_tag_count = 0
        self.votes_items = []
        
    def handle_starttag(self, tag, method, attrs):
        # TODO: why span is not a tag
        if tag != 'strong':
            return

        # only fetch the first script tag
        self.vote_tag_count += 1
        
    def handle_endtag(self, tag, method):
        return
    
    def handle_data(self, data):
        if self.vote_tag_count == 1:
            self.vote_tag_count = 0
            self.votes_items.append(data)

class Retriever(object):
    def __init__(self, url, save_file):
        self.url = url
        self.save_file = save_file
        
    def fetch_page(self):
        """
        """
        try:
            retval = urllib.urlretrieve(self.url, self.save_file)
        except (IOError, httplib.InvalidURL) as e:
            retval = (('*** ERROR: bad URL "%s": %s' % (self.url, e)),)
        return retval

    def parse_links(self):
        """fetch all links from page
        """
        f = open(self.save_file, 'r')
        data = f.read()
        f.close()
        parser = HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(cStringIO.StringIO())))
        parser.feed(data)
        parser.close()
        return parser.anchorlist

    def parse_votes(self):
        """fetch the names of images and path
        """
        f = open(self.save_file, 'r')
        data = f.read()
        f.close()
        parser = vote_tag_HTMLParser()
        parser.feed(data)
        parser.close()
        return parser.votes_items

def hackernews():
    """news.ycombinator.com
       fetch all hacker news links
    """
    hackernews_addr = "http://news.ycombinator.com"
    hackernews_tmp = "/tmp/hackernews.html"
    
    r = Retriever(hackernews_addr, hackernews_tmp)
    hackernews_file = r.fetch_page()

    if hackernews_file[0] == '*':
        print "Fetch hackernews file fails"
        sys.exit()

    print "Fetch hackernews file, YEAH"
    # TDDO: differnt way of import packages

    hackernews_links = []
    hackernews_filter_out = "http://ycombinator.com"
    for link in r.parse_links():
        if link.startswith("http://") and not link.startswith(hackernews_filter_out):
            hackernews_links.append(link)

    return hackernews_links

def xbcd():
    """xbcd.com
       fetch xbcd links, just return the link
       xkcd.com updates without fail every Monday, Wednesday and Friday.
       And there is Spanish, Russian, German version
    """
    weekday_now = datetime.datetime.now().strftime("%w")
    
    if weekday_now == '0' or weekday_now == '2' or weekday_now == '4':
        print "xkcd, YEAH"
        return ["http://xkcd.com"]
    else:
        return []

def douban():
    """douban.com
       add the account to pocket ==
    """
    douban_links = []
    for link_num in range(1, 7):
        douban_links.append('http://www.douban.com/update/?p='+ str(link_num) +'&tag=0')

    return douban_links

def twitter():
    """TODO: first need to proxy for it to add account to pocket
    """
    

def send2pocket(links):
    """add@getpocket.com
       one link per email is required.
    """
    send2pocket_lock.acquire()

    # links = links_tuple[0]
    from_addr = "lou.0211@gmail.com"
    to_addr = "add@getpocket.com"
    # better not provide subject, use the web name
    subject = "send to my pocket"

    for link in links:
        delay_time = randint(2,10)
        command = 'echo "'+ link + '" | mail ' + to_addr
        print "------------" + command
        os.system(command)
        
    send2pocket_lock.release()
    
def stackoverflow():
    """stackoverflow.com
       only the algorithm tag is fetched this time
    """
    stackoverflow_addr = "http://stackoverflow.com/questions/tagged/algorithm?page=1&sort=newest&pagesize=50"
    stackoverflow_tmp = "/tmp/stackoverflow_algorithm.html"
    
    r = Retriever(stackoverflow_addr, stackoverflow_tmp)
    stackoverflow_file = r.fetch_page()

    if stackoverflow_file[0] == '*':
        print "Fetch stackoverflow file fails"
        sys.exit()

    print "Fetch stackoverflow file, YEAH"
    # TDDO: differnt way of import packages

    stackoverflow_links = []
    stackoverflow_filter_out = "/questions/tagged/"
    stackoverflow_filter_out2 = "/questions/ask"
    stackoverflow_filter_in = "/questions/"
    for link in r.parse_links():
        if link.startswith(stackoverflow_filter_in) and not link.startswith(stackoverflow_filter_out)\
               and not link.startswith(stackoverflow_filter_out2):
            stackoverflow_links.append(link)

    votes = r.parse_votes()
    questions = []
    
    assert(len(votes) == 2 * len(stackoverflow_links))
    
    for i in xrange(0, len(votes), 2):
        questions.append([int (votes[i]) + int (votes[i+1]), stackoverflow_links[i/2]])

    sorted_questions = sorted(questions, key=lambda tup: tup[0])

    questions_top_10 = []
    top_10 = 0
    for question in reversed(sorted_questions):
        if top_10 > 10 :
            break
        questions_top_10.append("http::/stackoverflow.com" + question[1])
        top_10 += 1

    return questions_top_10
    
def main():

    # stackoverflow_thread = threading.Thread(target = send2pocket, args = (stackoverflow(), ))    
    # hackernews_thread = threading.Thread(target = send2pocket, args = (hackernews(), ))
    # xbcd_thread = threading.Thread(target = send2pocket, args = (xbcd(), ))

    # stackoverflow_thread.start()
    # hackernews_thread.start()
    # xbcd_thread.start()

    # stackoverflow_thread.join()
    # hackernews_thread.join()
    # xbcd_thread.join()
    send2pocket(hackernews())
    send2pocket(xbcd()) 
    send2pocket(stackoverflow())   
        
if __name__ == '__main__':
    main()
