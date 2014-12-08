# python3
# WikiScratcher
#
# created by __vlad__, 2014
# http://www.google-melange.com/gci/task/view/google/gci2014/5222762809393152



#Modules
import urllib.request
import re
import sys
import argparse
#


#Predefined constants
TYPE_ERROR = 0
TYPE_SUBCATEGORIES = 1
TYPE_PAGES = 2
TYPE_SUBCATEGORIES_PAGES = 3
#


#Initializing variables
is_not_imported = 0
parser = 0
args = 0
link = 0
output_to_stderr = 0
display_duplicates = 0
output_to_file = 0
duplicates = []
total_URLs = 0
URL_list = []
#


#Help
def help():
    print("Call 'main('category.com', bool(optional)")
#


#Incremet total_URLs
def update_total_urls():
    global total_URLs
    total_URLs += 1
#


#Check if the link is invalid
def error_check(link):
    try:
        data = urllib.request.urlopen(link).readlines()
        for i in range(len(data)):
            data[i] = data[i].decode("utf-8")
        return data
    except:
        return 0
#


#Get the type of a webpage
def get_type(data):
    subcategories_type_pattern = '<h2>Subcategories</h2>'
    pages_type_pattern = '<h2>Pages in category'
    patterns_type_1 = re.findall(subcategories_type_pattern, '/n'.join(map(str, data)))
    patterns_type_2 = re.findall(pages_type_pattern, '/n'.join(map(str, data)))
    empty_flag_1 = bool(len(patterns_type_1) == 0)
    empty_flag_2 = bool(len(patterns_type_2) == 0)
    if empty_flag_1 == 0 and empty_flag_2 == 1:
        return TYPE_SUBCATEGORIES
    elif empty_flag_2 == 0 and empty_flag_1 == 1:
        return TYPE_PAGES
    elif empty_flag_1 == 0 and empty_flag_2 == 0:
        return TYPE_SUBCATEGORIES_PAGES
    return TYPE_ERROR
#


#Get list of links from a webpage with subcategories
def get_links_from_subcategoriesType_webpage(data):
    result = []
    pattern_1 = '<ul><li><div class="CategoryTreeSection">'
    pattern_1_len = len(pattern_1)
    pattern_2 = '<li><div class="CategoryTreeSection">'
    pattern_2_len = len(pattern_2)
    href_pattern = 'href="/wiki/Category:'
    href_pattern_len = len(href_pattern)
    for elem in data:
        if elem[:pattern_1_len] == pattern_1 or elem[:pattern_2_len] == pattern_2:
            intermediate_result = ''
            if href_pattern not in elem:
                continue
            href_index = elem.find(href_pattern)
            i = href_index + href_pattern_len
            while elem[i] != '"':
                intermediate_result += elem[i]
                i += 1
            result.append(intermediate_result)
    for i in range(len(result)):
        result[i] = "http://en.wiktionary.org/wiki/Category:" + result[i]
    return result
#


#Check if the specified HTML part is not a category
def check_for_non_category(str_):
    pattern = 'Category:'
    pattern_len = len(pattern)
    return str_[:pattern_len] != pattern
#


#Get list of links from a webpage with pages
def print_links_from_pagesType_webpage(data):
    global total_URLs
    global URL_list
    global output
    result = []
    pattern_1 = '<ul><li><a href="/wiki/'
    pattern_1_len = len(pattern_1)
    pattern_2 = '<li><a href="/wiki/'
    pattern_2_len = len(pattern_2)
    href_pattern = 'href="/wiki/'
    href_pattern_len = len(href_pattern)
    for elem in data:
        if elem[:pattern_1_len] == pattern_1 or elem[:pattern_2_len] == pattern_2:
            intermediate_result = ''
            href_index = elem.find(href_pattern)
            i = href_index + href_pattern_len
            while elem[i] != '"':
                intermediate_result += elem[i]
                i += 1
            if check_for_non_category(intermediate_result):
                result.append(intermediate_result)
    for i in range(len(result)):
        result[i] = "http://en.wiktionary.org/wiki/" + result[i]
        if result[i] not in URL_list:
            URL_list.append(result[i])
            if is_not_imported:
                if output_to_file:
                    output.write(result[i] + '\n')
                else:
                    sys.stdout.write(result[i] + '\n')
            update_total_urls()
        else:
            if result[i] not in duplicates:
                duplicates.append(result[i])
    return
#


#Identify if there are more than 200 pages in this category (since not all are displayed in one page then)
def identify_if_more_than_200_pages(data):
    pattern_1 = '<p>The following'
    pattern_2 = 'pages are in this category, out of'
    for elem in data:
        if pattern_1 in elem and pattern_2 in elem:
            mid = elem.split()
            number = int(mid[-2])
            if number > 200:
                return 1
            return 0
    return 0
#


#Find the next url (when more than 200 pages on page)
def find_next_url_on_page_with_data(data):
    pattern_1 = 'previous'
    pattern_2 = 'next'
    pattern_3 = '</p>'
    beginning_pattern = '<a href="'
    enclosing_pattern = '</a>'
    for elem in data:
        if pattern_1 in elem and pattern_2 in elem and elem[:len(pattern_3)] == pattern_3:
            _link = ''
            i = elem.rfind(beginning_pattern) + len(beginning_pattern)
            while elem[i] != '"':
                _link += elem[i]
                i += 1
            if _link.find('&amp;') != -1:
                _link = _link[:_link.index('&amp;')] + '&' + _link[_link.index('&amp;') + 5:]
            i = elem.rfind(enclosing_pattern) - 1
            link_word = ''
            while elem[i] != '>':
                link_word = elem[i] + link_word
                i -= 1
            link_word = link_word.split()
            if link_word[0] == 'next':
                result = 'http://en.wiktionary.org' + _link
                return result
    return 0
#


#Find all links and duplicates
def recursive_pages(link):
    data = error_check(link)
    if data == 0:
        print("The specified category does not exist.")
        sys.exit(0)
    type = get_type(data)
    if type == TYPE_SUBCATEGORIES:
        links = get_links_from_subcategoriesType_webpage(data)
        for elem in links:
            recursive_pages(elem)
    elif type == TYPE_PAGES:
        print_links_from_pagesType_webpage(data)
        if identify_if_more_than_200_pages(data):
            _link = find_next_url_on_page_with_data(data)
            while _link != 0:
                _data = error_check(_link)
                print_links_from_pagesType_webpage(_data)
                _link = find_next_url_on_page_with_data(_data)
    elif type == TYPE_SUBCATEGORIES_PAGES:
        if identify_if_more_than_200_pages(data):
            _link = find_next_url_on_page_with_data(data)
            while _link != 0:
                _data = error_check(_link)
                print_links_from_pagesType_webpage(_data)
                _link = find_next_url_on_page_with_data(_data)
        print_links_from_pagesType_webpage(data)
        links = get_links_from_subcategoriesType_webpage(data)
        for elem in links:
            recursive_pages(elem)


#Reset
def reset_vars():
    global is_not_imported
    global parser
    global args
    global output
    global link
    global output_to_stderr
    global display_duplicates
    global output_to_file
    global duplicates
    global total_URLs
    global is_not_imported
    global URL_list
    parser = 0
    args = 0
    link = 0
    output_to_stderr = 0
    display_duplicates = 0
    output_to_file = 0
    duplicates = []
    total_URLs = 0
    URL_list = []
    return
#

def main(link_ = None, return_duplicates = 0):
    global parser
    global args
    global output
    global link
    global output_to_stderr
    global display_duplicates
    global output_to_file
    global duplicates
    global total_URLs
    global URL_list
    if link_ == None:
        parser = argparse.ArgumentParser(description='This program can be used in order to find all URLs related to the specified category link')
        parser.add_argument("link", help='URL for the category')
        parser.add_argument("-d", action='store_true', help="a switch that allows duplicated URLs to be displayed (will be displayed as a separate list)")
        parser.add_argument("-e", action="store_true", help="output additional information to stderr")
        parser.add_argument("-o", help = "write data to file with a specified filename", type=str)
        args = parser.parse_args()
        if args.o or args.o == '':
            output_to_file = 1
        if output_to_file:
            if args.o == '':
                output = open("output.txt", 'w')
            else:
                output = open(args.o, 'w')
        link = args.link
        if args.d:
            display_duplicates = 1
        if args.e:
            output_to_stderr = 1
    else:
        link = link_
        display_duplicates = int(return_duplicates)
    recursive_pages(link)

    if not is_not_imported:
        a, b = URL_list, duplicates
        reset_vars()
        if return_duplicates:
            return [a, b]
        return a

    if output_to_file:
        if output_to_stderr:
            sys.stderr.write(str(total_URLs) + " URLs found in total.\n")
        else:
            output.write(str(total_URLs) + " URLs found in total.\n")
        if display_duplicates:
            if output_to_stderr:
                sys.stderr.write("=" * 10 + "DUPLICATES" + "=" * 10 + '\n')
                for elem in duplicates:
                    sys.stderr.write(elem + '\n')
                sys.stderr.write(str(len(duplicates)) + " duplicates found." + '\n')
                sys.stderr.write("=" * 30 + '\n')
            else:
                output.write("=" * 10 + "DUPLICATES" + "=" * 10 + '\n')
                for elem in duplicates:
                    output.write(elem + '\n')
                output.write(str(len(duplicates)) + " duplicates found." + '\n')
                output.write("=" * 30 + '\n')
        output.close()
    else:
        if output_to_stderr:
            sys.stderr.write(str(total_URLs) + " URLs found in total.\n")
            if display_duplicates:
                sys.stderr.write("=" * 10 + "DUPLICATES" + "=" * 10 + '\n')
                for elem in duplicates:
                    sys.stderr.write(elem + '\n')
                sys.stderr.write(str(len(duplicates)) + " duplicates found.\n")
                sys.stderr.write("=" * 30 + '\n')
        else:
            sys.stdout.write(str(total_URLs) + " URLs found in total.\n")
            if display_duplicates:
                sys.stdout.write("=" * 10 + "DUPLICATES" + "=" * 10 + '\n')
                for elem in duplicates:
                    sys.stdout.write(elem + '\n')
                sys.stdout.write(str(len(duplicates)) + " duplicates found.\n")
                sys.stdout.write("=" * 30 + '\n')
    reset_vars()


if __name__ == "__main__":
    is_not_imported = 1
    main()
