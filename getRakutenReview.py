#!/usr/bin/python
# -*- coding: utf-8 -*-
# get commends from Amazon
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
def writeToCSV(dictComm, writer):
    for r in dictComm['reviews']:
        r["product"] = dictComm["product_title"]
        r['verified'] = 'Yes' if r['verified'] else 'No'
        r['rating'] = r['rating'].split(
            ' out of')[0] if r['rating'] else 'N/A'
        r['images'] = " ".join(
            r['images']) if r['images'] else 'N/A'
        r['date'] = dateparser.parse(
            r['date'].split('on ')[-1]).strftime('%d %b %Y')
        writer.writerow(r)

# product_data = []
def getRakutenReview():
    with open("urls.txt", 'r') as urllist:
        for url in urllist.readlines():
            driver.get(url)
            html = driver.page_source.replace('\n', '')
            dictComm = e.extract(html)
            print(dictComm)

    driver.close()


if __name__ == '__main__':
    getRakutenReview()
