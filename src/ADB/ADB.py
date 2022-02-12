
from time import *

# pip3 install pure-pyton-adb
from ppadb.client import Client


class ADB:
    def __init__(self):
        client = Client(
            host="127.0.0.1",
            port=5037
        )
        devices = client.devices()
        self.device0 = devices[0]

        self.timeout = 60
        self.APK = None

    def is_installed(self):
        print(f"[0/3] Wait for {self.APK}")

        cnt = 0
        while cnt < self.timeout:
            if self.device0.is_installed(self.APK): return True
            cnt += 1
            sleep(1)

        return False
    
    def pull(self):
        print(f"[1/3] Pull {self.APK}")

        import os.path
        import re

        dPath = re.findall(
            r"(?=:)(.+)(?==)", 
            self.device0.shell(f"pm list packages -f | grep {self.APK}")
        )[0][1:]
        hPath = f"{self.APK}.apk"

        while not os.path.isfile(hPath):
            self.device0.pull(dPath, hPath)

        return True

    def setAPK(self, APK):
        self.APK = APK

    def uninstall(self):
        print(f"[2/3] Uninstall {self.APK}")

        cnt = 0
        while cnt < self.timeout:
            if self.device0.uninstall(self.APK): return True
            cnt += 1
            sleep(1)
        return False


if __name__ == "__main__":
    adb = ADB()
    adb.setAPK(
        "com.higames.grounddigger"
    )

    if adb.is_installed():
        if adb.pull():
            if adb.uninstall(): print(f"[3/3] Done with `{adb.APK}`")
            else: print(f"[!] Fail to uninstall `{adb.APK}`")
        else: print(f"[!] Fail to pull `{adb.APK}`")
    else: print(f"[!] `{adb.APK}` is not installed")
