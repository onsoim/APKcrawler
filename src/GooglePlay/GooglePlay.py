
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
import re
import requests                         # pip3 install requests


class GOOGLEPLAY:
    def __init__(self, config):
        self.bURL   = "https://play.google.com"
        self.pkl    = PICKLE("./urls.pickle")
        self.config = config

    def install(self, package_name):
        self.google = GOOGLE()
        self.google.login(self.config)

        self.driver = self.google.driver
        self.wait   = WebDriverWait(self.driver, 60)

        self.driver.get(f"{self.bURL}/web/store/apps/details?id={package_name}&hl=en_US")

        self.driver.implicitly_wait(5)
        self.driver.find_element(By.XPATH, '//*[@id="kO001e"]/header/nav/div/c-wiz/div/div/div[1]/button').click()
        self.driver.find_element(By.XPATH, '//*[@id="kO001e"]/header/nav/div/c-wiz/div/div/div[2]/div/ul/li[1]').click()

        # Check already installed or not
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Install"]')))
            self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Install"]').click()
            sleep(5)

            # pyautogui.press('enter')//*[@id="yDmH0d"]/div/div/div[2]/div[3]/span/button
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            # sleep(3)

            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
            self.google.setPassword()
            sleep(10)

            return (True, datetime.now())

        # If package installed before
        except Exception as e:
            import inspect, os
            print(f"[*] {os.path.abspath(__file__)} > {inspect.stack()[0][3]}")
            print(e)
            return (False, None)
        finally: self.driver.quit()

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
        urls = self.pkl.load()
        re_package = re.compile(r'details\?id=[^&\n]*')

        while urls:
            url = f"{self.bURL}{urls.pop()}"
            if '?' in url:
                url += "&hl=en_US&gl=US"
                package_name = re_package.findall(url)
                if len(package_name): 
                    packages.put([(
                        package_name[0][11:],
                        self.parser(url)
                    )])

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
                    urls.add(href)

            self.pkl.dump(urls)


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

