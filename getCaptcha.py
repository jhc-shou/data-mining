#!/usr/bin/python
# -*- coding: utf-8 -*-
# google search results crawler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import NoSuchElementException
import os
import urllib.request as urllib2
import socket
import time
import gzip
from io import BytesIO
import re
import random
import types
from dotenv import load_dotenv, find_dotenv
import operator

import sys


# Load config from .env file
try:
    load_dotenv(find_dotenv(usecwd=True))
    base_url = os.environ.get('BASE_URL')
    results_per_page = int(os.environ.get('RESULTS_PER_PAGE'))
except:
    print("ERROR: Make sure you have .env file with proper config")
    sys.exit(1)

user_agents = list()

# results from the search engine
# basically include url, title,content


class SearchResult:
    def __init__(self):
        self.url = ''
        self.title = ''
        self.content = ''

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix=''):
        print('url\t->', self.url, '\n',
              'title\t->', self.title, '\n',
              'content\t->', self.content)

    def writeFile(self, filename):
        try:
            with open(filename, 'a') as f:
                f.write('url:' + self.url + '\n')
                f.write('title:' + self.title + '\n')
                f.write('content:' + self.content + '\n\n')
        except IOError as e:
            print('file error:', e)


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime = random.randint(60, 120)
        time.sleep(sleeptime)

    def extractDomain(self, url):
        """Return string

        extract the domain of a url
        """
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)

        return domain

    def extractUrl(self, href):
        """ Return a string

        extract a url from a link
        """
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url

    def extractSearchResults(self, html):
        """
        Return a list
        extract serach results list from downloaded html file
        """
        results = list()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', id='main')
        if (type(div) == type(None)):
            div = soup.find('div', id='center_col')
        if (type(div) == type(None)):
            div = soup.find('body')
        if (type(div) != type(None)):
            lis = div.findAll('a')
            if(len(lis) > 0):
                for link in lis:
                    if (type(link) == type(None)):
                        continue

                    url = link['href']
                    if url.find(".google") > 6:
                        continue
                    if url.find("http") == -1:
                        continue

                    url = self.extractUrl(url)
                    if(operator.eq(url, '') == 0):
                        continue
                    title = link.renderContents().decode('utf-8')
                    title = re.sub(r'<.+?>', '', title)
                    result = SearchResult()
                    result.setURL(url)
                    result.setTitle(title)
                    span = link.find('div')
                    if (type(span) != type(None)):
                        content = span.renderContents().decode('utf-8')
                        content = re.sub(r'<.+?>', '', content)
                        result.setContent(content)
                    results.append(result)
        return results

    def search(self, query, lang='jp', num=results_per_page):
        """Return a list of lists

        search web
        @param query -> query key words
        @param lang -> language of search results
        @param num -> number of search results to return
        """
        search_results = list()
        query = urllib2.quote(query)
        if(num % results_per_page == 0):
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1

        for p in range(0, int(pages)):
            start = p * results_per_page
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (
                base_url, lang, results_per_page, start, query)
            retry = 3
            while(retry > 0):
                try:
                    # driver = webdriver.Edge(executable_path=r'.venv\\Scripts\\msedgedriver.exe')
                    driver = webdriver.Edge(EdgeChromiumDriverManager().install())
                    driver.get(url)
                    html = driver.page_source.replace('\n', '')
                    results = self.extractSearchResults(html)
                    search_results.extend(results)
                    driver.close()
                    break
                except urllib2.URLError as e:
                    print('url error:', e)
                    self.randomSleep()
                    retry = retry - 1
                    continue

                except Exception as e:
                    print('error:', e)
                    retry = retry - 1
                    self.randomSleep()
                    continue
        return search_results


def load_user_agent():
    with open('./user_agents', 'r') as fp:
        for line in fp.readlines():
            user_agents.append(line.strip('\n'))


def crawler():
    # Load use agent string from file
    load_user_agent()

    # Create a GoogleAPI instance
    api = GoogleAPI()

    # set expect search results to be crawled
    expect_num = 10
    # if no parameters, read query keywords from file
    if(len(sys.argv) < 2):
        keywords = open('./keywords', 'r', encoding="utf-8")
        keyword = keywords.readline()
        while(keyword):
            results = api.search(keyword, num=expect_num)
            for r in results:
                r.printIt()
            keyword = keywords.readline()
        keywords.close()
    else:
        keyword = sys.argv[1]
        results = api.search(keyword, num=expect_num)
        for r in results:
            r.printIt()


if __name__ == '__main__':
    crawler()



