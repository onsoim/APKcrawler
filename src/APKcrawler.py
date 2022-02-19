
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ADB.ADB import ADB                         #
from configparser import ConfigParser
from datetime import datetime
from GooglePlay.GooglePlay import GOOGLEPLAY    #
from multiprocessing import Manager, Process
from SQLite.SQLite import SQLITE                #
from time import *


def jobA(extracts, extracts_t):
    adb = ADB()

    while True:
        if not extracts.empty():
            for package in extracts.get():
                adb.setAPK(package)
                if adb.is_installed() and adb.pull() and adb.uninstall():
                    print(f"[3/3] Done {package}")
                    extracts_t.put([(
                        package,
                        datetime.now()
                    )])
        else: sleep(3)

def main():
    parser = ConfigParser()
    parser.read('./config.ini')

    iINF = int(parser['GOOGLEPLAY']['installs'])
    gp = GOOGLEPLAY(parser['GOOGLE'])

    packages    = Manager().Queue()
    extracts    = Manager().Queue()
    extracts_t  = Manager().Queue()

    Process(target = gp.traversal, args = (packages,)).start()
    Process(target = jobA, args = (extracts, extracts_t)).start()

    sqlite = SQLITE()

    while True:
        if not packages.empty():
            for package, cnt in packages.get():
                if cnt >= iINF:
                    if sqlite.create(package, cnt):
                        res, t = gp.install(package)
                        if res:
                            print(f"[I] {package}")
                            sqlite.update(
                                set     = { "install_date": t },
                                where   = { "package_name": package }
                            )

        for package in sqlite.read({"install_date": "NOT NULL", "extract_date": None}):
            if package not in extracts:
                extracts.put([package])

        if not extracts_t.empty():
            for package, t in extracts_t.get():
                sqlite.update(
                    set     = { "extract_date": t },
                    where   = { "package_name": package }
                )

if __name__ == "__main__":
    while True:
        try: main()
        except Exception as e:
            import inspect, os
            print(f"[*] {os.path.abspath(__file__)} > {inspect.stack()[0][3]}")
            print(e)
