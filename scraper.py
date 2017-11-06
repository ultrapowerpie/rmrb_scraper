from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse, re, os, sys, time

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

class Scraper(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Process some integers.')

        parser.add_argument('--checkpoint', default='1600', type=int,
           help='the last completed page of search results saved (default: 0)')
        parser.add_argument('--headless', action='store_true',
           help='whether to run Chrome in headless mode (default: True)')

        args = parser.parse_args()

        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)

        self.driver.get('http://rmrb.egreenapple.com/index2.html')
        self.driver.switch_to_frame('main')

        self.driver.find_element_by_css_selector('input').send_keys('1987 to 2012')
        self.driver.find_element_by_id('image1').click()

        self.checkpoint = args.checkpoint
        self.iterator = range(7,85,4)
        self.pages = 0

    def scrape_pages(self, folder):
        while self.checkpoint - self.pages > 14:
            self.skip_pages()
            time.sleep(.100)

        while self.pages < self.checkpoint:
            self.go_to_next_page()
            time.sleep(.100)

        while self.pages < 47652:
            self.save_pages(folder,  85)
            self.go_to_next_page()

        self.save_pages(61)

        self.driver.quit()
        sys.exit()

    def save_pages(self, folder, numel):
        i = 0
        while i+1 < len(self.iterator):
            try:
                links = WebDriverWait(self.driver, 10).until(
                    number_of_elements_at_least((By.CSS_SELECTOR, 'td'), numel)
                )
                links[self.iterator[i]].find_element_by_css_selector('a').click()
                i += 1

                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[href="javascript:GoToPDF()"]'))
                    )
                    paragraphs = self.driver.find_elements_by_css_selector('p')
                    fonts = self.driver.find_elements_by_css_selector('font')
                    date = paragraphs[2].text

                    if '1987' in date:
                        continue

                    directory = self.get_directory(folder, date)
                    filename = paragraphs[1].text
                    text = fonts[10].text

                    self.write_file(directory, filename, text)

                finally:
                    self.driver.back()
                    self.driver.switch_to_frame('main')

            except:
                self.driver.quit()
                sys.exit()

    def get_directory(self, folder, date):
        regex = re.compile('[^0-9]+')
        _, year, month, day, _ = regex.split(date)
        return '/'.join([folder,year,month,day])

    def write_file(self, directory, filename, text):
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(directory + '/' + filename, 'w') as f:
            f.write(text)

    def go_to_next_page(self):
        try:
            imgs = WebDriverWait(self.driver, 10).until(
                number_of_elements_at_least((By.CSS_SELECTOR, '[alt]'), 4)
            )
            next_page = imgs[3]
            next_page.click()
            self.pages += 1
            print("search pages saved: ", self.pages)
        except:
            self.driver.quit()
            sys.exit()

    def skip_pages(self):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, '>'))
            )
            button.click()
            self.pages += 15
            print("search pages skipped: ", self.pages)
        except:
            self.driver.quit()
            sys.exit()

if __name__ == '__main__':
    folder = 'webpages'
    s = Scraper()
    s.scrape_pages(folder)
