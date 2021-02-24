#!/usr/bin/python
# -*- coding: utf-8 -*-
# get reviews from Rakuten ichiba
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


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('rakutenSelectors.yml')
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = driver = webdriver.Chrome(chrome_options=options,
                                   executable_path=ChromeDriverManager().install())

# extract html to dict


def getDictComm():
    html = driver.page_source.replace('\n', '')
    return e.extract(html)

# goto next page


def NextPage():
    try:
        # wait page load
        time.sleep(3)
        element = WebDriverWait(
            driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '次の15件 >>')))
        element.click()
        print("Navigating to Next Page")
        return True
    except (TimeoutException, WebDriverException) as e:
        print("Last page reached")
        return False

# write dict to scv file


def writeToCSV(dictComm, writer):
    for (r, rr) in zip(dictComm['reviews'], dictComm['reviewers']):
        r["product"] = dictComm["product_title"]
        r['rating'] = r['rating'] if r['rating'] else 'N/A'
        r['author'] = rr['name']
        writer.writerow(r)

# product_data = []


def getRakutenReview():
    with open("urls.txt", 'r') as urllist:
        for url in urllist.readlines():
            driver.get(url)
            html = driver.page_source.replace('\n', '')
            dictComm = e.extract(html)
            if dictComm:
                productTittle = re.findall(
                    r'[^\*"/:?\\|<>]', dictComm["product_title"].replace(' ', '_'), re.S)
                csvFileName = "".join(productTittle) + '.csv'
                with open('comm/'+csvFileName, 'w', encoding='UTF-8', errors='ignore') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=[
                                            "title", "content", "date", "variant", "images", "verified", "author", "rating", "product"], quoting=csv.QUOTE_ALL)
                    writer.writeheader()
                    writeToCSV(dictComm, writer)
                    while True:
                        if NextPage():
                            writeToCSV(getDictComm(), writer)
                        else:
                            break

    driver.close()


if __name__ == '__main__':
    getRakutenReview()
