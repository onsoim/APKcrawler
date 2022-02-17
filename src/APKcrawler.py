
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ADB.ADB import ADB                         #
from configparser import ConfigParser
from datetime import datetime
from GooglePlay.GooglePlay import GOOGLEPLAY    #
from multiprocessing import Process, Manager
from SQLite.SQLite import SQLITE                #
from time import *


def jobA():
    adb = ADB()
    sqlite = SQLITE()

    while True:
        for package in sqlite.read({"extract_date": None, "install_date": "NOT NULL"}):
            adb.setAPK(package)
            if adb.is_installed() and adb.pull() and adb.uninstall():
                sqlite.update(
                    set = {
                        "extract_date": datetime.now()
                    }, 
                    where = {
                        "package_name": package
                    }
                )
                print(f"[3/3] Done {package}")
        sleep(3)

def main():
    parser = ConfigParser()
    parser.read('./GooglePlay/config.ini')

    gp = GOOGLEPLAY(parser['GOOGLE'])

    packages = Manager().Queue()
    traversal = Process(target=gp.traversal, args = (packages,))
    traversal.start()

    adb = Process(target=jobA)
    adb.start()

    sqlite = SQLITE()

    while True:
        for package in packages.get():
            sqlite.create(package)
        # for package in sqlite.read({"install_date": None}):
            if gp.install(package):
                sqlite.update(
                    set = {
                        "install_date": datetime.now()
                    },
                    where = {
                        "package_name": package
                    }
                )

if __name__ == "__main__":
    while True:
        try: main()
        except Exception as e: print(e)
