#Adrian Braemer
  
import bs4
import urllib.request
import sys
  
tableHeaders = ['Language','Entries','Definitions',
                'Appendix entries','Appendix definitions',
                'Gloss definitions','Form definitions']
  
def quickSearch(language):
    if not language.istitle():
        language = language.capitalize()
    page = loadSite('http://en.wiktionary.org/wiki/Special:Statistics')
    if page == None:
        print('Could not access statistics page.')
        sys.exit()
    soup = bs4.BeautifulSoup(page)
    elem = soup.find(name = 'a', text = language)
    if elem == None:
        print('Language '+language+' not found.')
        print('Please check your spelling or try an exact search.')
        sys.exit()
    elem = elem.parent #td element
    counter = 0
    while elem != None:
        if isinstance(elem, bs4.Tag):
            print(tableHeaders[counter]+": "+elem.text)
            counter += 1
        elem = elem.next_sibling
      
  
def loadSite(site, retries = 5):
    if not site.startswith('http://'):
        site = 'http://'+site
    tries = 0
    while tries < retries:
        tries += 1
        try:  
            return urllib.request.urlopen(site)
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        except Exception as e:
            print("Unknown Exception:"+str(type(e))+' : '+str(e)+"\n")
        print('Retry')
    return None

def searchAllCategories(page, language):
    req = loadSite(page)
    if req == None:
        print('Could not load Special:Categories page')
        return (None, None)
    soup = bs4.BeautifulSoup(req)
    ul = soup.find('ul')
    items = ul.find_all('li')
    categoryPages = []
    goOn = True
    for item in items:
        members = item.text
        goOn = language in members
        if not goOn:
            break
        left = members.rindex('(')+1
        right = members.rindex(' ')
        members = members[left:right]
        categoryPages.append(item.find('a')['href'])
    if goOn:
        nextPage = 'en.wiktionary.org'+soup.find('a', attrs={'class':'mw-nextlink'})['href']
        nextCategories = searchAllCategories(nextPage, language)
        categoryPages += nextCategories
    return categoryPages

def getAllWordsForCategory(categoryPage):
    wordPages = []
    categoryCount = []
    req = loadSite('en.wiktionary.org'+categoryPage)
    if not req:
        print('Could not load: '+categoryPage)
        return categoryCount
    soup = bs4.BeautifulSoup(req)
    div = soup.find('div', attrs={'id':'mw-pages'})
    if div == None:
        return wordPages
    lis = div.find_all('li')
    for li in lis:
        wordPages.append(li.find('a')['href'])
    if len(lis)%200 == 0:
        elem = soup.find('div', attrs={'id':'mw-pages'})
        links = elem.find_all('a', recursive=False)
        nextLink = None
        for link in links:
            if link.text == 'next 200':
                nextLink = link['href']
                break
        if nextLink:
            newWordPages = getAllWordsForCategory(nextLink)
            wordPages += newWordPages
    return wordPages

def exactSearch(language):
    if not language.istitle():
        language = language.capitalize()
    categoryList = searchAllCategories('en.wiktionary.org/w/index.php?title=Special%3ACategories&from='+language, language)
    print('Found '+str(len(categoryList))+' categories')
    pageList = []
    for category in categoryList:
        print(category)
        words = getAllWordsForCategory(category)
        for word in words:
            if not word in pageList:
                pageList.append(word)
    print(len(pageList))
  
def main():
    if len(sys.argv) < 3:
        print("Not enough arguments.")
        print("Usage: python3 wikPageCounter.py [quick|exact] LANGUAGE")
        sys.exit()
    if sys.argv[1] == 'quick':
        quickSearch(sys.argv[2])
    elif sys.argv[1] == 'exact':
        exactSearch(sys.argv[2])
    else:
        print("Unrecognized parameter.")
        print("Usage: python3 wikPageCounter.py [quick|exact] LANGUAGE")
        sys.exit()
      
  
if __name__ == '__main__':
    main()
