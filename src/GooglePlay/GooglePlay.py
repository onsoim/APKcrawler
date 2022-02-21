
from bs4 import BeautifulSoup           # pip3 install beautifulsoup4
from configparser import ConfigParser
from datetime import datetime
from Google import GOOGLE               #
from PICKLE import PICKLE               #

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import *

import json
import heapq
import re
import requests                         # pip3 install requests


class GOOGLEPLAY:
    def __init__(self, config):
        self.bURL   = "https://play.google.com"
        self.pkl    = PICKLE("./urls.pickle")
        self.config = config

        self.init_driver()

    def init_driver(self):
        try: self.driver.quit()
        except: pass

        self.google = GOOGLE()
        self.google.login(self.config)

        self.driver = self.google.driver
        self.wait   = WebDriverWait(self.driver, 30)

    def install(self, package_name):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Search"]')))
        self.driver.get(f"{self.bURL}/web/store/apps/details?id={package_name}&hl=en_US")

        # Check already installed or not
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[jscontroller="soHxf"]')))
            msg = self.driver.find_element(By.CSS_SELECTOR, '[class="AqX8Cf"]').text
            if msg == "This app is available for your device":

                self.driver.find_element(By.CSS_SELECTOR, '[class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc MjT6xe sOCCfd brKGGd BhQfub  zwjsl"]').click()
                sleep(15)

                ActionChains(self.driver).send_keys(Keys.ENTER).perform()

                self.google.setPassword()
                sleep(20)

                return (True, datetime.now())
            print(f"[e] {package_name}: {msg}")

        # If package installed before
        except Exception as e:
            import inspect, os
            print(f"[*] {os.path.abspath(__file__)} > {inspect.stack()[0][3]}")
            print(e)

            self.init_driver()

        return (False, None)

    def parser(self, url):
        SCRIPT  = re.compile("AF_initDataCallback[\s\S]*?<\/script")
        KEY     = re.compile("(ds:.*?)'")
        VALUE   = re.compile("data:([\s\S]*?), sideChannel: {}}\);<\/")

        for match in SCRIPT.findall(requests.get(url).text):
            key_match = KEY.findall(match)
            value_match = VALUE.findall(match)

            if key_match and value_match:
                value = json.loads(value_match[0])

                try:
                    if key_match[0] == "ds:5":
                        return value[0][12][9][2]
                except Exception as e: print(e)
        return -1

    def traversal(self, packages):
        try:
            urls = self.pkl.load()
            if urls == None:
                urls = []
                heapq.heappush(urls, (2, ""))
            re_package = re.compile(r'details\?id=[^&\n]*')

            while urls:
                url = f"{self.bURL}{heapq.heappop(urls)[1]}"

                soup = BeautifulSoup(
                    requests.get(
                        url
                    ).text,
                    'html.parser'
                )

                for a in soup.find_all('a', href=True):
                    href = a['href']

                    if not href.startswith("/"):
                        if href.startswith(self.bURL):
                            href = href.split(".com")[1]
                        else: continue

                    if href.startswith("/store/apps") or href.startswith("/store/games"):
                        if '?' in href:
                            package_name = re_package.findall(href)
                            if len(package_name):
                                href += "&hl=en_US&gl=US"
                                packages.put([(
                                    package_name[0][11:],
                                    self.parser(f"{self.bURL}{href}")
                                )])
                                heapq.heappush(urls, (0, href))
                            else: heapq.heappush(urls, (1, href))
                        else: heapq.heappush(urls, (2, href))

                self.pkl.dump(urls)
        except Exception as e: print(e)


if __name__ == "__main__":
    from multiprocessing import Process, Manager

    parser = ConfigParser()
    parser.read('../config.ini')

    gp = GOOGLEPLAY(parser['GOOGLE'])

    packages = Manager().Queue()
    traversal = Process(target=gp.traversal, args = (packages,))
    traversal.start()

    install = Process(target=gp.install, args=("com.supercell.brawlstars", ))
    install.start()

    while True:
        if not packages.empty():
            print(packages.get())
        else: sleep(10)
