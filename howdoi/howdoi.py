#!/usr/bin/env python

##################################################
#
# howdoi - a code search tool.
# written by Benjamin Gleitzman (gleitz@mit.edu)
# inspired by Rich Jones (rich@anomos.info)
#
##################################################

import urllib.request, urllib.parse, urllib.error
import sys
import argparse
import re
import os.path
import textwrap
import lxml.html

__version__ = "1.0"


GOOGLE_SEARCH_URL = "https://www.google.com/search?q=site:stackoverflow.com%20{0}"
DUCK_SEARCH_URL = "http://duckduckgo.com/html?q=site%3Astackoverflow.com%20{0}"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0"
CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.howdoi')



def print_help():
    print("""Howdoi is a code search tool. It answers any kind of query but perfect precision is not guaranteed

USAGE:
    howdoy.py your query""")


def get_terminal_width():
    stty = os.popen('stty -a', 'r').read()
    columns = re.search("columns ([0-9]+)\;", stty)
    return columns.group(1)


def wrap_text(text, cols):
    t = textwrap.TextWrapper()
    t.width = int(cols)
    t.break_long_words=False

    wrapped_text = t.fill(text)
    return wrapped_text


def get_result(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', USER_AGENT)]
    result = opener.open(url)
    return result.read()


def is_question(link):
    return re.search("^http\:\/\/stackoverflow\.com\/questions/\d+/", link)


def get_google_links(query):
    links = []
    url = GOOGLE_SEARCH_URL.format(urllib.parse.quote(query))
    result = get_result(url)
    html = lxml.html.document_fromstring(result)
    for l in html.iterlinks():
        if is_question(l[2]):
            links.append(l[2])
            
    return links


def get_duck_links(query):
    url = DUCK_SEARCH_URL.format(urllib.parse.quote(query))
    result = get_result(url)
    html = lxml.html.document_fromstring(result)
    links = html.xpath("//a[@href]")
    return [l.get('href', None) for l in links]


def get_link_at_pos(links, pos):
    pos = int(pos) - 1
    for link in links:
        if is_question(link):
            if pos == 0:
                break
            else:
                pos = pos - 1
                continue
    return link


def get_instructions(args, position):
    text = []
    links = get_google_links(args['query'])
#    links = get_duck_links(args['query'])
    if not links:
        return ''

    link = get_link_at_pos(links, position)
    if args.get('link'):
        return link

    link = link + '?answertab=votes'
    page = get_result(link)
    html = lxml.html.document_fromstring(page)
    first_answer = html.xpath("//td[@class='answercell']")
    tags = first_answer[0].xpath("code") or first_answer[0].xpath("//pre")
    if tags:
        for t in tags[0]:
            text.append(t.text_content())
    else:
        post_text = first_answer[0].xpath("div[@class='post-text']/p")
        if post_text:
            for t in post_text:
                text.append(t.text_content())

    columns = get_terminal_width()
    return wrap_text("\n".join(text), columns)


def save_query(qry):
    with open(CONFIG_FILE, "w") as c:
        try:
            c.write(qry)
        except OSError:
            # something went wrong while accessing the config file
            pass


def read_last_query():
    with open(CONFIG_FILE, "r") as c:
        try:
            first_line = c.readline()
            return first_line
        except OSError:
            pass


def howdoi(args):
    if not len(args['query']) and not args['again']:
        print_help()
        sys.exit(1)
    else:
        # do we want the last query again?
        if args['again']:
            args['query'] = read_last_query()
        else:
            args['query'] = ' '.join(args['query']).replace('?', '')
        # save the query for later reuse
        save_query(args['query'])
        instructions = get_instructions(args, args['pos']) or 'Sorry, couldn\'t find any help with that topic'
        print(instructions)


def command_line_runner():
    parser = argparse.ArgumentParser(description='code search tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='+',
                        help='the question to answer')
    parser.add_argument('-p','--pos', help='select answer in specified position (default: 1)', default=1)
    parser.add_argument('-a','--all', help='display the full text of the answer',
                        action='store_true')
    parser.add_argument('-g','--again', help='display the last query again',
                        action='store_true')
    parser.add_argument('-l','--link', help='display only the answer link',
                        action='store_true')
    args = vars(parser.parse_args())
    return args

if __name__ == '__main__':
    cli_args = command_line_runner()
    howdoi(cli_args)
