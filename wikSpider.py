#!/usr/bin/python
'''
This script spiders a single category of words on Wiktionary.
'''
#How long the spider waits until fetching another page as not to anger
#Wiktionary people
TIMEOUT = 3
#Directory where spidered partial-html is stored
OUTPUTDIR = "/tmp/wiki/"
#Url used to fetch pages
BASEURL = 'http://en.wiktionary.org/w/index.php?action=render&title=' 
#String used to find links
WORDBASEURL = "//en.wiktionary.org/wiki/"

import urllib2
import time
import os
import sys

#Initialize fetcher, urllib2 is used over urllib specifically because 
#it allows to specify a User-agent
fetcher = urllib2.build_opener()
#Specify unique User-agent, as per wikimedia guidelines
fetcher.addheaders = [('User-agent', 'ApertiumFetcher/0.1')]




#create output directory if it does not exist
if not os.path.exists(os.path.abspath(OUTPUTDIR)):
    os.makedirs(OUTPUTDIR)
     

def spider(categoryName):
    """Spiders all words from a Wiktionary category and
    saves the html in OUTPUTDIR
    """
    lastFetch = time.time()-TIMEOUT
    categoryUrl = BASEURL + categoryName 
    print categoryUrl
    overviewPage = fetcher.open(categoryUrl)
    while True:
        #Read the overview page and find the linktable
        overviewSource = overviewPage.read()
        overviewPage.close()
        overviewSource = overviewSource[overviewSource.rfind("<table"):]
        minDex = 0
        #while links are in the table
        while overviewSource.find(WORDBASEURL, minDex) != -1:
            #Find the start of the link
            urlStart = overviewSource.find(WORDBASEURL, minDex)
            #Find the word that it belongs to
            wordStart = overviewSource.find("title=",urlStart)+7
            word = overviewSource[wordStart:overviewSource.find("\"", wordStart)]
            #Check if this file has already been spidered
            if not os.path.exists(os.path.join(OUTPUTDIR,word+'.xml')):    
                #Find url        
                wordUrl = BASEURL + overviewSource[urlStart+len(WORDBASEURL):
                                                   overviewSource.find("\"", urlStart)]
                #Wait long enough
                if time.time() - lastFetch < TIMEOUT:
                    time.sleep(TIMEOUT- (time.time() - lastFetch))
                #Fetch url
                wordPage = fetcher.open(wordUrl)
                wordSource = wordPage.read()
                wordPage.close()
                #Record fetching time
                lastFetch = time.time()
                #Save url
                with open(os.path.join(OUTPUTDIR,word+".xml"), 'w') as f:
                    f.write(wordSource)
            minDex = urlStart + 1
        #Test if there is a next overview page. 
        #(If not, there is no closing </a> tag
        if overviewSource.find("next 200</a>") == -1:
            break
        else:
            #Find url of next page
            urlStart = overviewSource.rfind("href=")+6
            url = overviewSource[urlStart:overviewSource.find("\" ", urlStart)]
            
            if not url.find("http") == 0:
                url = "http:" + url.replace("&amp;","&")
            print url
            overviewPage = fetcher.open(url)
if __name__ == "__main__":
    if len(sys.argv) == 2:
        spider(sys.argv[1])
    elif len(sys.argv) == 3:
        OUTPUTDIR = os.path.realpath(sys.argv[2])
        spider(sys.argv[1])
    else:
        print "Usage: python wikSpider.py CategoryName [OUTPUTPATH]"
        print "Example: python wikSpider.py Category:Spanish_nouns"
        print "This spiders the Category Spanish nouns and puts the resulting"
        print "files in the default OUTPUTPATH /tmp/wiki"
            
        
