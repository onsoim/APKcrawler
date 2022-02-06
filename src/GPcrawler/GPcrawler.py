
from bs4 import BeautifulSoup

import pickle
import requests


class GPCRAWLER:
    def __init__(self):
        self.pkl = "./urls.pickle"

        import os.path
        if os.path.isfile(self.pkl):
            with open(self.pkl, 'rb') as f:
                self.urls = pickle.load(f)
        else: self.urls = { "" }

        self.traversal()

    def traversal(self):
        import time

        bURL = "https://play.google.com"

        while self.urls:
            url = bURL + self.urls.pop()

            soup = BeautifulSoup(
                requests.get(url).text,
                'html.parser'
            )

            for a in soup.find_all('a', href=True):
                href = a['href']

                if not href.startswith("/"):
                    if href.startswith(bURL):
                        href = href.split(".com")[1]
                    else: continue

                if href.startswith("/store/apps") or href.startswith("/store/games"):
                    self.urls.add(href)

            with open(self.pkl, 'wb') as f:
                pickle.dump(self.urls, f)
            time.sleep(1)


if __name__ == "__main__":
    crawler = GPCRAWLER()
