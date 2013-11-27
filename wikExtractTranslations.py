import os
import urllib.request
import sys
import argparse

def getURL(url):
    """Takes a url and returns the source contained at that page"""

    page = urllib.request.urlopen(url)
    return page.read().decode('utf-8')

                                                                               
#################################################################################
## File: TranslationScraper.py                                                 ##
##                                                                             ##
## File contains a class for scraping the http://en.wiktionary.org/ website    ##
## word pages for translations if you just wish to see a test run, for         ##
## implementation into your own program see the Usage                          ##
## section                                                                     ##
##                                                                             ##
## Usage:                                                                      ##
##                                                                             ##
## import TranslationScraper object into your program                          ##
##  "from TranslationScraper import TranslationScraper"                        ##
##                                                                             ##
## create a new instance of the TranslationScraper object                      ##
##  "translationScraper = TranslationScraper(<parts of speach to exclude>,     ##
##                                                <languages to exclude>),     ##
##                                                silent"                      ##
##                                                                             ##
## the <parts of speach to collect> and <languages to collect> paramaters      ##
## should be strings containing all the parts of speach/languages ( the        ##
## languages will be in pairs for example you might only want to collect       ##
## english to french so you would put 'en-fr' ) to collect, if there are       ##
## multiple seperate with comma. by default it collect everything.             ##
##                                                                             ##
## run the parsing function of the Translation Scraper                         ##
##  "translationScraper.parsePage(<html of page>)"                             ##
##                                                                             ##
## USAGE: Commandline Interface                                                ##
## InflectionScraper.py -u <URL for the page to crawl> -p <part of text>       ##
##                                                     -o <output file>        ##
## --help   ( -h ) brings up this menu                                         ##
##                                                                             ##
## Input:                                                                      ##
## --url    ( -u ) folowed by url to crawl                                     ##
## --part   ( -p ) the part of text that these pages will belong to,           ##
##                 see list below                                              ##
## --output ( -o ) the name of the output file e.g. output.txt                 ##
##                                                                             ##
##                                                                             ##
#################################################################################


class TranslationScraper(object):

    # If you leave the paramaters partsOfSpeach and languange as empty strings the
    # program will collect everything, otherwise add comma seperated language pairs or
    # speach parts to there retraspetive paramater.
    def __init__(self, partsOfSpeach, languages):
        """Initilizes all the global functions"""
        
        # Stores all the diffrent types of word the translations can be
        self.typesOfWord = ['Noun', 'Adjective', 'Verb']

        # allowed parts of speach
        self.allowedPartsOfSpeach = None
        if partsOfSpeach != "":
            self.allowedPartsOfSpeach = []
            self.allowedPartsOfSpeach = partsOfSpeach.split(',')

        # allowed languages
        self.allowedLanguages = None
        if languages != "":
            self.allowedLanguages = []
            for pair in languages.split(','):
                split = pair.split('-')
                self.allowedLanguages.append(sorted(split, key=str.lower))

        ## Various Global Variables ##
        self.documentLanguage = ""
        self.documentWord = ""
        self.wordType = ""
        self.context = ""

        self.translations = []
        
        
    
    def parsePage(self, html):
        """takes the HTML of a page as input and returns the parsed into translations"""

        # Get document language
        self.documentLanguage = html[html.find('lang="')+6:html.find('"', html.find('lang="')+6)]

        # Get document word
        self.documentWord = html[html.find('<title>')+7:html.find('</title>')].split(' ')[0]

        # Split the page at a string that occors before every set of tables
        tableSections = html.split('<span class="mw-headline" id="Translations')

        # Skip the first becasue it contains all the HTML leading up to the first table
        for i in range(1, len(tableSections)):
            
            # Determine what type of word we are reading in by looking at prevous section
            for t in self.typesOfWord:
                if tableSections[i-1].find('<span class="mw-headline" id="' + t) != -1:
                    self.wordType = t.lower()
                    break

            # Check to make sure we are actually collecting this type of word
            # if not just return to top of loop
            if self.allowedPartsOfSpeach != None:
                if self.wordType not in self.allowedPartsOfSpeach: continue

            # Split this section into its tables
            tables = tableSections[i].split('<table class="translations" role="presentation" style="width:100%;">')

            # Skip the first row again becasuse it dosnt contain actual table data
            for table in range(1, len(tables)):
                # Find the end of the table
                closedTable = tables[table][0:tables[table].find('</table>')]

                # Get the context of the translations in the table
                self.context = tables[table-1][tables[table-1].rfind('<div class="NavHead" style="text-align:left;">')+46:tables[table-1].rfind('</div>')]

                # Make sure the context isnt 'Translations to be checked' we dont want these because they arnt approuved or sorted
                if self.context == 'Translations to be checked': continue
                
                # Split the table into rows
                rows = closedTable.split('<tr>')

                # Skip first becasue its usefull
                for i in range(1, len(rows)):
                    # Split at new line charactors
                    words = rows[i].split('<li>')

                    for word in words:
                        # Determine if this line has a word on it
                        if word.find('lang="') != -1:
                            # Remove occorences of '<td' and take the first bit becasue we dont want
                            # the extra
                            word = word.split('<td')[0]
                            
                            # Remove extra unwanted HTML tags
                            word = self.removeExtraTags(word)

                            # Check to see if its actually more than one words under one language
                            if word.find('<dd>') != -1:
                                self.processMultipleWords(word)
                            else:
                                self.processSingleWord(word)


                # Now we want to run the process translations function
                self.processTranslations()

    def processTranslations(self):
        # You can assume that sinse all the translated words mean the same thing
        # they are all translations of each other, this function puts them all together and puts them into 

                
        # Loop throught all the translations
        for i in range(0, len(self.translations)):
            
            # Loop throught all the translations with an index greater than i
            # because all the ones before it will of allready been inserted
            for j in range(i+1, len(self.translations)):
                
                # Sort the two languages to find which one goes first
                langs = [self.translations[i][0], self.translations[j][0]]
                langs = sorted(langs)

                # Check to see if the words are from the same language, if so continue to next
                if langs[0] == langs[1]: continue

                # If they both have atleast one gender
                if self.translations[i][1][1] != [] and self.translations[j][1][1] != []:
                    for g1 in range(0, len(self.translations[i][1][1])):
                        for g2 in range(0, len(self.translations[j][1][1])):
                            translation = self.compileTranslation(langs, self.translations[i], g1, self.translations[j], g2)

                # Else if only the first one has a gender or more
                elif self.translations[i][1][1] != []:
                    for g in range(0, len(self.translations[i][1][1])):
                        translation = self.compileTranslation(langs, self.translations[i], g, self.translations[j], -1)

                # Else if only the second one has a gender or more
                elif self.translations[j][1][1] != []:
                    for g in range(0, len(self.translations[j][1][1])):
                        translation = self.compileTranslation(langs, self.translations[i], -1, self.translations[j], g)

                # Else nether have a gender
                else:
                    translation = self.compileTranslation(langs, self.translations[i], -1, self.translations[j], -1)
                    #f.write(translation)
                        

        # Reset the translations array
        self.translations = []
                

    def processMultipleWords(self, word):
        """If a section contains sub-languages this function breaks them apart"""
    
        # Break it up into the two words
        wordSplit = word.split('<dd>')

        for s in range(0, len(wordSplit)):
            # Check to see if what we are looking at contains a word
            if wordSplit[s].find('lang="') == -1: continue

            self.processSingleWord(wordSplit[s])
            
    
    def processSingleWord(self, word):
        """This function takes a string of HTML that contains word data and saves it"""
        
        worddata = self.getWordData(word)

        # Insert the translated word into the global variable 'translation'
        for w in worddata[1]:
            self.translations.append([worddata[0], w])

        # Write to screen
        self.printToScreen(worddata)
        

    def printToScreen(self, worddata):
        """Takes information about a translation and writes it to the screen"""

        # Sort the two languages to find which one goes first
        langs = [self.documentLanguage, worddata[0]]
        langs = sorted(langs, key=str.lower)

        # Check to make sure that the language is allowed, if not, do nothing
        
        for i in range(0, len(worddata[1])):

            if worddata[1][i][1] != []:
                # We want to put each gender on a seperate line
                for g in range(0, len(worddata[1][i][1])):
                    translation = self.compileTranslation(langs, [self.documentLanguage, [self.documentWord], []], -1, [worddata[0], worddata[1][i]], g)
            else:
                translation = self.compileTranslation(langs, [self.documentLanguage, [self.documentWord], []], -1, [worddata[0], worddata[1][i]], -1)
                

    def compileTranslation(self, languages, word1, genPos1, word2, genPos2):
        """Takes a bunch of information and compiles it into a translation string"""

        if self.checkIfAllowed(languages) == True:
        
            # Create the string to append to the file
            translation = ""

            # Insert the languages at the beginning
            translation += languages[0] + "; " + languages[1] + "; "

            # Insert the word data into the translation string
            # in the order they should be 
            for l in languages:
                if l == word1[0]:
                    translation += word1[1][0] + '; '
                    translation += self.wordType
                    if genPos1 != -1:
                        translation += '.' + word1[1][1][genPos1]
                    translation += '; '
                    
                else:
                    translation += word2[1][0] + '; '
                    translation += self.wordType
                    if genPos2 != -1:
                        translation += '.' + word2[1][1][genPos2]        
                    translation += '; '
                    

            translation += "english/gloss; "

            # Insert the context
            translation += self.context

            # For Windows
            #print(translation.encode(sys.stdout.encoding, errors='replace'))

            # For Linux
            print(translation)

    def getWordData(self, wordHTML):
        """Function takes a word + data wrapped in html and parses it into an array"""

        # Store all the results in here, just in case there is more than one way of saying
        # a word. format - language, words + data
        results = ['', []]

        # Stores all the possible genders of words
        g = ['n', 'f', 'm', 'mf', 'fn', 'mfn']

        # Remove everything leading up to the ':' because this is all garbage
        wordHTML = wordHTML[wordHTML.find(':')+1:]

        # Remove 'aprox.' because we dont want it
        wordHTML = wordHTML.replace('approx.', "")
            
        # Get language
        language = wordHTML[wordHTML.find('lang="')+6:wordHTML.find('"', wordHTML.find('lang="')+6)]
        results[0] = language

        # Remove the html from word
        wordHTML = self.htmlStrip(wordHTML)

        # Remove the brackets from word
        wordHTML = self.removeBrackets(wordHTML)

        # Split at ',' to get both ways of saying something if there are two
        splitHTML = wordHTML.split(',')

        # Keeps track of the last index where we inserted a word
        lastInserted = -1

        for w in splitHTML:
            # If the comma was really dividing two genders, append the gender
            # to the gender array in the prevously inserted word and return to top of loop
            if w.strip() in g:
                results[1][lastInserted][1].append(w.strip())
                continue
            
            # Get word data
            data = self.htmlStrip(w).strip().split(' ')
            
            # Find genders of word
            genders = []
            for d in data:
                # Remove leading and traling white space
                d = d.strip()
            
                # Determine if it is a gender
                if d in g: genders.append(d)

            results[1].append([data[0].strip(), genders])
            lastInserted += 1


        # Return in format language, words
        return results

    def removeBrackets(self, data):
        """Some translations have extra information contained between brakets, this function removes that"""

        while data.find('(') != -1:
            data = data[0:data.find('(')] + data[data.find(')')+1:len(data)]

        return data

    def htmlStrip(self, html):
        """Returns the string html with all the HTML removed"""

        # List of HTML charactors that need to be replaced, there are
        # alot but this is all i need for now
        specialHTMLChars = {'&#160;': ' '}

        for char in specialHTMLChars:
            html = html.replace(char, specialHTMLChars[char])
        
        start = 0
        close = 0

        # Make sure there is some HTML
        if html.find('<') != -1:

            # While there is HTML in the text
            start = html.find('<', start)
            while start != -1:
                # If the html string is empty then return an empty string, otherwise
                # an infinit loop occors
                if html == "": return ""
                
                close = html.find('>', start)

                tag = html[start+1:close].split(' ')[0]
                closeTag = ""

                closeTagOpen = start
                closeTagClose = 0

                # Special cases for html tags that will cause the loop to run indefanitly,
                # while i dont expect to encounter these when parsing tables i thought i would
                # include this anyway
                if tag =='br' or tag == 'br/':
                    html = html[0:start] + "\n" + html[close+1:]
                    continue

                elif tag == 'img':
                    html = html[0:start] + html[close+1:]
                    continue

                elif tag == '!--':
                    html = html[0:start] + " " + html[html.find('-->')+3:]
                    continue

                elif tag == 'script':
                    html = html[0:start] + " " + html[html.find('</script>', start)+9:]

                # Find the location of the close tag, using a while loop for this because
                # there can be tags inside tags

                # Keep track of nested tags
                sameTagsOpen = 0
                h = 0
                while closeTag != ("/" + tag):
                    closeTagOpen = html.find('<', closeTagOpen+1)
                    closeTagClose = html.find('>', closeTagOpen)

                    closeTag = html[closeTagOpen+1:closeTagClose].split(' ')[0]
                    h += 1

                    # If the possible close tag is really just another operning tag same as the one we are
                    # trying to close increment count
                    if closeTag == tag:
                        sameTagsOpen += 1

                    # If the close tag the one we are looking for but sameTagsOpen is greater than 0
                    # then its the close tag for a nested tag and not what we want
                    if closeTag == ("/" + tag) and sameTagsOpen > 0:
                        closeTag = ""
                        sameTagsOpen -= 1
                        continue
                    


                # Assign the text inbetween the close of the open tag and the open of the close tag
                # to rem and recursivly call htmlStrip
                rem = html[close+1:closeTagOpen]
                html = html[0:start] + self.htmlStrip(rem) + html[closeTagClose+1:]

                start = html.find('<', start)


        return html

    def removeExtraTags(self, word):
        """Removes all the unwanted tags from the HTML passed to it"""
        
        # Remove the opening tags '<td>', '<ul>', '<tr>'
        # because they will never be in the same section as there closing tags
        word = word.replace('<td>', "")
        word = word.replace('<ul>', "")
        word = word.replace('<tr>', "")
        
        # Remove closing list element tags '</li>', '</ul>', '</td>', '</tr>' to avoide infinit loop becasue when
        # splitting up the HTML there operning tags are removed
        word = word.replace('</li>', "")
        word = word.replace('</ul>', "")
        word = word.replace('</td>', "")
        word = word.replace('</tr>', "")

        # Then we want to remove the closing tags for '<dd>' and '<dl>'
        word = word.replace('</dd>', "")
        word = word.replace('</dl>', "")
        word = word.replace('<dl>', "")

        return word


    def checkIfAllowed(self, langs):
        """Checks to see if a translation is an allowrd language pair"""
        if self.allowedLanguages == None: return True

        
        for pair in self.allowedLanguages:
            if langs[0] == pair[0] and langs[1] == pair[1]:
                return True

        return False

############################
## Command Line Interface ##
############################

def main():
    parser = argparse.ArgumentParser(description='Takes a url as input and scrapes all the translations from that page')
    parser.add_argument('--url', '-u', dest='url', help='the url to the page you want to collect the translations from')
    parser.add_argument('--languages', '-l', dest='languages', default='', help='the language pairs you want to collect e.g. en-fr,en-sw , leave blank if you want to collect all')
    parser.add_argument('--part', '-p', dest='part', default='', help='the parts of text that you want to collect, comma seperated, leave blank if you want to collect all')

    args = parser.parse_args()

    if args.url == None:
        parser.error('You must add a url argument')
        parser.print_help()
        return 1

    source = getURL(args.url)

    # paramaters partsOfSpeach, languages. leave as empty strings if you want to collect all
    ts = TranslationScraper(args.part, args.languages)

    ts.parsePage(source)

    
# If this script is being run as its self execute the main function
if __name__ == '__main__':
    main()

# If run as its own program and not imported, run the testing function
#if __name__ == "__main__":
    #print('[*] Running Testing...')
    #source = getURL('http://en.wiktionary.org/wiki/key')
    #source = getURL('http://en.wiktionary.org/wiki/teacher')

    # paramaters partsOfSpeach, languages. leave as empty strings if you want to collect all
    #ts = TranslationScraper("", "af-am")

    #ts.parsePage(source)




