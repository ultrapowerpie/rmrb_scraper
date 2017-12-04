from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread
import argparse, random, re, os, sys, time

class number_of_elements_at_least(object):
  def __init__(self, locator, number):
    self.locator = locator
    self.number = number

  def __call__(self, driver):
    elements = driver.find_elements(*self.locator)
    if len(elements) >= self.number:
        return elements
    else:
        return False

class Scraper(Thread):

    def __init__(self, headless, checkpoint, folder, time, query, wait=1000):
        Thread.__init__(self)

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')

        self.time = str(time)
        self.query = str(query)
        self.wait = wait
        self.folder = folder
        self.checkpoint = checkpoint
        self.iterator = range(7,85,4)
        self.pages = 1

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)

        self.driver.get('http://rmrb.egreenapple.com/index2.html')
        self.driver.switch_to_frame('main')

        inputs = self.driver.find_elements_by_css_selector('input')
        inputs[0].send_keys(self.time)
        inputs[6].send_keys(self.query)
        self.driver.find_element_by_id('image1').click()

    def run(self):
        while self.checkpoint - self.pages > 14:
            if not self.skip_pages():
                return
            time.sleep(self.wait*(1+random.random())/1000)

        while self.pages <= self.checkpoint:
            if not self.go_to_next_page():
                return
            time.sleep(self.wait*(1+random.random())/1000)

        while self.save_pages(7):
            self.write_checkpoint()
            self.go_to_next_page()

        self.driver.quit()
        return

    def save_pages(self, numel):
        i = 0
        while i < len(self.iterator):
            time.sleep(self.wait*(1+random.random())/1000)
            try:
                links = WebDriverWait(self.driver, 20).until(
                    number_of_elements_at_least((By.CSS_SELECTOR, 'td'), numel)
                )
                link = links[self.iterator[i]].find_element_by_css_selector('a')
                i += 1
                if link.text:
                        link.click()
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[href="javascript:GoToPDF()"]'))
                        )
                        paragraphs = self.driver.find_elements_by_css_selector('p')
                        fonts = self.driver.find_elements_by_css_selector('font')
                        date = paragraphs[2].text

                        directory = self.get_directory(date)
                        filename = paragraphs[1].text
                        text = fonts[10].text

                        self.write_file(directory, filename, text)

                        time.sleep(self.wait*(1+random.random())/1000)
                        self.driver.back()
                        self.driver.switch_to_frame('main')

            except:
                self.driver.quit()
                return False


        return True

    def get_directory(self, date):
        regex = re.compile('[^0-9]+')
        _, year, month, day, _ = regex.split(date)
        return '/'.join([self.folder,year,month,day])

    def write_checkpoint(self):
        with open(str(self.time) + '.txt', 'ab') as f:
            f.write((str(self.pages)+'\n').encode('utf-8'))

    def write_file(self, directory, filename, text):
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(directory + '/' + filename + '.txt', 'wb') as f:
            f.write(text.encode('utf-8'))

    def go_to_next_page(self):
        try:
            imgs = WebDriverWait(self.driver, 20).until(
                number_of_elements_at_least((By.CSS_SELECTOR, '[alt]'), 4)
            )
            next_page = imgs[3]
            next_page.click()
            self.pages += 1

        except:
            self.driver.quit()
            return False

        return True

    def skip_pages(self):
        try:
            button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.LINK_TEXT, '>'))
            )
            button.click()
            self.pages += 15
        except:
            self.driver.quit()
            return False

        return True
