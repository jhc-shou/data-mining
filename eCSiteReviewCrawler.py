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

reviewProperty = ReviewProperty()

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = driver = webdriver.Chrome(chrome_options=options,
                                   executable_path=ChromeDriverManager().install())


class ReviewAPI:

    def __init__(self):
        pass

    # extract html to dict
    # Create an Extractor by reading from the YAML file
    def extractUrl(self):
        e = Extractor.from_yaml_file(reviewProperty.getSiteSelector)
        html = driver.page_source.replace('\n', '')
        reviewProperty.setDictComm(e.extract(html))

    # goto next page
    def NextPage(self):
        try:
            # wait page load
            time.sleep(3)
            if reviewProperty.getECSite == 'rakuten':
                element = WebDriverWait(
                    driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '次の15件 >>')))
                element.click()
            elif reviewProperty.getECSite == 'amazon':
                driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(
                    driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a"))))
                driver.find_element_by_xpath(
                    "//li[@class='a-last']/a").click()
            print("Navigating to Next Page")
            return True
        except (TimeoutException, WebDriverException) as e:
            print("Last page reached")
            return False

    # write dict to scv file
    def writeToCSV(self, writer):
        if reviewProperty.getECSite == 'rakuten':
            for (r, rr) in zip(reviewProperty.getDictComm['reviews'], reviewProperty.getDictComm['reviewers']):
                r["product"] = reviewProperty.getDictComm["product_title"]
                r['rating'] = r['rating'] if r['rating'] else 'N/A'
                r['author'] = rr['name']
        elif reviewProperty.getECSite == 'amazon':
            for r in reviewProperty.getDictComm['reviews']:
                r["product"] = reviewProperty.getDictComm["product_title"]
                r['verified'] = 'Yes' if r['verified'] else 'No'
                r['rating'] = r['rating'].split(' out of')[0] if r['rating'] else 'N/A'
                r['images'] = " ".join(r['images']) if r['images'] else 'N/A'
                # r['date'] = dateparser.parse(r['date'].split('に')[0]).strftime('%d %b %Y')
                year = r['date'].split('年')[0]
                month = r['date'].split('年')[1].split('月')[0]
                day = r['date'].split('年')[1].split('月')[1].split('日')[0]
                r['date'] = '-'.join((year,month,day))
        writer.writerow(r)


# product_data = []
def reviewCrawler():
    api = ReviewAPI()
    with open("urls.txt", 'r') as urllist:
        for url in urllist.readlines():

            # check EC site source
            if url.find('rakuten') != -1:
                reviewProperty.setECSite("rakuten")
            elif url.find('amazon') != -1:
                reviewProperty.setECSite('amazon')
            else:
                print('wrong url: ', url,'\n')
                continue

            driver.get(url)
            api.extractUrl()
            if reviewProperty.getDictComm:
                productTittle = re.findall(
                    r'[^\*"/:?\\|<>]', reviewProperty.getDictComm["product_title"].replace(' ', '_'), re.S)
                csvFileName = "".join(productTittle) + '.csv'
                with open('comm/'+csvFileName, 'w', encoding='UTF-8', errors='ignore') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=["title", "content", "date", "variant",
                                                                 "images", "verified", "author", "rating", "product"], quoting=csv.QUOTE_ALL)
                    writer.writeheader()
                    api.writeToCSV(writer)
                    while True:
                        if api.NextPage():
                            api.writeToCSV(writer)
                        else:
                            break
    driver.close()


if __name__ == '__main__':
    reviewCrawler()
