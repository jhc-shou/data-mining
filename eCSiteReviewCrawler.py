#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import json
import csv
import re
from selectorlib import Extractor
from dateutil import parser as dateparser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from impReviewProperty import ReviewProperty


class ReviewAPI:
    def __init__(self):
        self.__reviewProperty = ReviewProperty()

        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument("start-maximized")
        self.__options.add_argument("disable-infobars")
        self.__options.add_argument("--disable-extensions")
        self.__options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        self.__driver = driver = webdriver.Chrome(chrome_options=self.__options,
                                                  executable_path=ChromeDriverManager().install())

    # extract html to dict
    # Create an Extractor by reading from the YAML file
    def __extractUrl(self):
        e = Extractor.from_yaml_file(self.__reviewProperty.getSiteSelector)
        html = self.__driver.page_source.replace('\n', '')
        self.__reviewProperty.setDictComm(e.extract(html))

    # goto next page
    def __NextPage(self):
        try:
            # wait page load
            time.sleep(3)
            if self.__reviewProperty.getECSite == 'rakuten':
                element = WebDriverWait(
                    self.__driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '次の15件 >>')))
                element.click()
            elif self.__reviewProperty.getECSite == 'amazon':
                self.__driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(
                    self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a"))))
                self.__driver.find_element_by_xpath(
                    "//li[@class='a-last']/a").click()
            print("Navigating to Next Page")
            return True
        except (TimeoutException, WebDriverException) as e:
            print("Last page reached")
            return False

    # write dict to scv file
    def __writeToCSV(self, writer):
        try:
            if self.__reviewProperty.getECSite == 'rakuten':
                for (r, rr) in zip(self.__reviewProperty.getDictComm['reviews'], self.__reviewProperty.getDictComm['reviewers']):
                    r["product"] = self.__reviewProperty.getDictComm["product_title"]
                    r['rating'] = r['rating'].split('つ')[0] if r['rating'] else 'N/A'
                    r['author'] = rr['name']
                    writer.writerow(r)
            elif self.__reviewProperty.getECSite == 'amazon':
                for r in self.__reviewProperty.getDictComm['reviews']:
                    if '日本' in r['date']:
                        r["product"] = self.__reviewProperty.getDictComm["product_title"]
                        r['verified'] = 'Yes' if r['verified'] else 'No'
                        r['rating'] = r['rating'].split('つ')[0] if r['rating'] else 'N/A'
                        # r['images'] = " ".join(r['images']) if r['images'] else 'N/A'
                        # r['date'] = dateparser.parse(r['date'].split('に')[0]).strftime('%d %b %Y')
                        year = r['date'].split('年')[0]
                        month = r['date'].split('年')[1].split('月')[0]
                        day = r['date'].split('年')[1].split('月')[1].split('日')[0]
                        r['date'] = '-'.join((year, month, day))

                        writer.writerow(r)
                    else:
                        break
        except Exception as e:
            print('[{1}] Error : {0}'.format(e, ReviewAPI.__writeToCSV.__name__))

    # product_data = []

    def reviewCrawler(self):
        try:
            with open("urls.txt", 'r') as urllist:
                for url in urllist.readlines():

                    # check EC site source
                    if url.find('rakuten') != -1:
                        self.__reviewProperty.setECSite("rakuten")
                    elif url.find('amazon') != -1:
                        self.__reviewProperty.setECSite('amazon')
                    else:
                        print('wrong url: ', url, '\n')
                        continue

                    self.__driver.get(url)
                    self.__extractUrl()
                    if self.__reviewProperty.getDictComm:
                        productTittle = re.findall(
                            r'[^\*"/:?\\|<>]', self.__reviewProperty.getDictComm["product_title"].replace(' ', '_'), re.S)
                        csvFileName = '{0}_{1}.csv'.format(
                            self.__reviewProperty.getECSite, "".join(productTittle))
                        try:
                            with open('comm/'+csvFileName, 'w', encoding='UTF-8', errors='ignore') as outfile:
                                writer = csv.DictWriter(outfile, fieldnames=["title", "content", "date", "variant", "verified", "author", "rating", "product"], quoting=csv.QUOTE_ALL)
                                writer.writeheader()
                                # self.__writeToCSV(writer)
                                while True:
                                    if self.__NextPage():
                                        self.__extractUrl()
                                        self.__writeToCSV(writer)
                                    else:
                                        break
                        except IOError as ioe:
                            print('file error:', ioe)
        except Exception as e:
            print('[{1}] Error : {0}'.format(e, ReviewAPI.reviewCrawler.__name__))

        self.__driver.close()
