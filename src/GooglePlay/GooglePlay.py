
from bs4 import BeautifulSoup               # pip3 install beautifulsoup4
from configparser import ConfigParser
from Google import GOOGLE                   #
from PICKLE import PICKLE                   #
from selenium.webdriver.common.by import By # pip3 install selenium
from time import *

import pyautogui                            # pip3 install pyautogui
import re
import requests                             # pip3 install requests


class GOOGLEPLAY:
    def __init__(self):
        self.bURL   = "https://play.google.com"
        self.pkl    = PICKLE("./urls.pickle")

    def install(self, config, package_name):
        google = GOOGLE()
        google.login(config)

        driver = google.driver
        driver.get(f"{self.bURL}/web/store/apps/details?id={package_name}&hl=en_US")
        driver.implicitly_wait(5)

        driver.find_element(By.XPATH, '//*[@id="kO001e"]/header/nav/div/c-wiz/div/div/div[1]/button').click()
        driver.find_element(By.XPATH, '//*[@id="kO001e"]/header/nav/div/c-wiz/div/div/div[2]/div/ul/li[1]').click()

        # Check already installed or not
        try:
            driver.find_element(By.CSS_SELECTOR, '[aria-label="Install"]').click()
            sleep(5)
            
            pyautogui.press('enter')
            sleep(3)

            google.setPassword()
            sleep(10)

            return True
        # If package installed before
        except: return False
        finally: driver.quit()

    def traversal(self, packages):
        urls = self.pkl.load()
        re_package = re.compile(r'details\?id=[^&\n]*')

        while urls:
            url = f"{self.bURL}{urls.pop()}"
            if '?' in url:
                package_name = re_package.findall(url)
                if len(package_name): 
                    packages.put([package_name[0][11:]])
                url += "&hl=en_US&gl=US"

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

    gp = GOOGLEPLAY()

    packages = Manager().Queue()
    traversal = Process(target=gp.traversal, args = (packages,))
    traversal.start()

    parser = ConfigParser()
    parser.read('config.ini')

    install = Process(target=gp.install, args=(parser['GOOGLE'], "com.supercell.brawlstars"))
    install.start()
