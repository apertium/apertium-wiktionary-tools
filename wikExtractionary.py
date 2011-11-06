#!/usr/bin/python
'''
This script analyses results from spidering wiktionary and converts them to speling format
'''
import os
import sys
import lxml.etree

#Used to find the correct language section of page
LANG = "Dutch"
#Used to find the section corresponding to the correct part of speech
POS = "Noun"
#Used when recording in speling-format
POSCODE = 'n'
#Maps wiki-genders to speling genders. If multiple genders should be concatenated, use the tuple of the seperate elements
genders = {'m':'m', 'f':'f', 'n':'nt', 'c':'mf', ('m','f'):'mf', ('f','m'):'mf'}
#Maps the class-tags of forms that should be recorded to the code it should get in speling-format
forms = {'DEFAULT':'sg','plural-form-of':'pl'}

def doExtraction(inpath, outpath):
    with open(outpath, 'w') as f:
        f.write("")
    for fname in os.listdir(inpath):
        with open(os.path.join(inpath, fname)) as f:
            curSource = f.read()
        result = parse(curSource)
        #print "result: ", result
        with open(outpath, 'a') as f:
            f.write(result)

def parse(curSource):
    #Wrap the source in a wrapper for xml validity
    elTree = lxml.etree.fromstring("<doc>" + curSource + "</doc>")
    #Extract the informational section by looking for the language and then the 
    #section belonging to the specific part of speech. The smallest element that
    #contains all information should be a <p>
    infoEl = None
    foundLang = False
    for el in elTree.iter():
        if el.tag == 'h2':
            for el2 in el.findall('span'):
                if el2.text == LANG:
                    foundLang = True
        if foundLang:
            #print "test2"
            if el.tag == 'h3' or el.tag == 'h4':
                for el2 in el.findall('span'):
                    if el2.text == POS:
                        #print "test1"
                        if el.getnext().tag == 'p':
                            infoEl = el.getnext()
        if infoEl != None:
            break
    #Analyse the informational element
    if infoEl == None:
        return ""
    else:
        result = ""
        gList = []
        #Find spans with class gender 
        for genderSpan in infoEl.iter('span'):
            if genderSpan.get('class') != None:
                splitSpan = genderSpan.get('class').split()
                if 'gender' in splitSpan:
                    for part in splitSpan:
                        if genders.get(part) != None:
                            gList.append(part)
        #If one gender try to find code, else try to convert
        #to tuple and convert that
        if len(gList) == 1:
            gender = genders[gList[0]]
        else:
            gender = genders.get(tuple(set(gList)), 'GD')
        #print "gender:", gender
        #Record base form
        word = lxml.etree.tostring(infoEl.find('b'),method='text',with_tail=False)
        resList = [word, word, forms['DEFAULT'], 'n.' + gender]
        result += "; ".join(resList) + '\n'
        #Record inflections
        for form in forms.keys():
            for span in infoEl.iter('span'):
                if span.get('class') != None:
                    #Found a span with a class attribute
                    splitSpan = span.get('class').split()
                    #Check if this span signifies a form-of
                    if 'form-of' in splitSpan:
                        #Check if it's a form we want to use
                        if form in splitSpan:
                            #Extract inflection and add to results
                            inflection = lxml.etree.tostring(span,method='text',with_tail=False)
                            resList = [inflection, word, forms[form], POSCODE + '.' + gender]
                            result += "; ".join(resList) + '\n'
        return result
        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        doExtraction(os.path.realpath(sys.argv[1]), os.path.realpath(sys.argv[2]))
    else:
        print "USAGE: python wikExtractionary.py INPUTPATH OUTPUTPATH"
        print "Example: python wikExtractionary.py /tmp/wiki /tmp/test.txt"
        print "This analyses all the files in /tmp/wiki as wiktionary html and puts the resulting"
        print "speling-format data in /tmp/test.txt"