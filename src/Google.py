
import undetected_chromedriver.v2 as uc     # pip3 install undetected-chromedriver
from selenium.webdriver.common.by import By # pip3 install selenium


class GOOGLE:
    def __init__(self):
        self.driver = uc.Chrome()
        self.driver.get("https://accounts.google.com/signin/v2/identifier?continue=https://www.google.com")

    def login(self, config):
        self.ID = config['ID']
        self.PW = config['PW']

        self.setIdentifierId()
        self.setPassword()

    def setIdentifierId(self):
        self.driver.find_element(By.XPATH, '//*[@id="identifierId"]').send_keys(self.ID)
        self.driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button').click()
        self.driver.implicitly_wait(2)

    def setPassword(self):
        self.driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.PW)
        self.driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button').click()
        self.driver.implicitly_wait(2)


if __name__ == "__main__":
    from configparser import ConfigParser
    import time

    parser = ConfigParser()
    parser.read('config.ini')

    google = GOOGLE()

    google.login(parser['GOOGLE'])
    time.sleep(10)  # google.driver.implicitly_wait(10)

    google.driver.quit()
